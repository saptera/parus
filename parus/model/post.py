# -*- coding: utf-8 -*-

"""Model inference post-process module

PyTorch helpers that convert raw model output tensors into per-sample peak detections and quantitative
position-accuracy scores.
"""

import torch

__package__ = 'parus.model'
__name__ = 'parus.model.post'

__all__ = ['peak_zsc_torch', 'peak_fwd_torch', 'eval_pos']
"""
Public function list:

- peak_zsc_torch(prd, lag, threshold, influence) : Robust signal peak detection using z-scores (PyTorch version)
- peak_fwd_torch(prd, th, neg, gap)              : Signal peak detection using forward difference (PyTorch version)
- eval_pos(prd, lbl, tol)                        : Evaluate spike-position accuracy (false negatives and positives)
"""


def peak_zsc_torch(prd, lag, threshold, influence=0.0):
    """Detect signal peaks using a robust z-score criterion (PyTorch version).

    Maintains a moving mean and standard deviation over a window of length ``lag`` along the last axis of
    ``prd``. A sample whose deviation from the moving mean exceeds ``threshold`` standard deviations is
    flagged as a positive (``+1``) or negative (``-1``) peak. The flagged sample is then mixed back into the
    moving window with weight ``influence`` to control how much detected peaks adapt the threshold.

    Inspired by `J.P.G. van Brakel <https://stackoverflow.com/a/22640362/6029703>`_.

    Args:
        prd (torch.Tensor): {3D-float, (n_ch, n_feat, n_samp)} Input prediction tensor
        lag (int): Sliding window length; larger lags assume more stationary data
        threshold (int | float): Threshold in standard deviations above which a sample is classified as a peak
        influence (float): Influence of detected peaks on the threshold in ``[0, 1]``; ``0`` assumes
            stationary signal, ``1`` treats peaks like normal data points (default: ``0.0``)

    Returns:
        torch.Tensor: {3D-int} Per-sample peak flags (``1`` positive peak, ``-1`` negative peak, ``0`` no peak)
    """
    # Initialize operational series
    det = torch.zeros_like(prd, dtype=torch.int)
    flt = torch.cat((prd[:, :, :lag].flip(dims=(2,)), prd), dim=2)
    # Compute sliding window initial values
    fac = 1 / lag
    lin = torch.sum(flt[:, :, :lag], dim=2)
    sqr = torch.sum(flt[:, :, :lag].square(), dim=2)

    for i in range(prd.shape[2]):
        # Sample tensors
        slc = prd[:, :, i]
        flo = flt[:, :, i]
        fpr = flt[:, :, i + lag - 1]
        fcr = flt[:, :, i + lag]
        # Update filter
        avg = lin * fac
        std = torch.abs(sqr * fac - avg * avg).sqrt_()  # abs() to avoid negative value caused by precision loss
        # Peak detection with influence
        chk = torch.abs(slc - avg) > threshold * std
        sgn = torch.where(slc > avg, 1, -1)
        det[:, :, i] = sgn * chk.int()
        flt[:, :, i + lag] = torch.where(chk, influence * slc + (1 - influence) * fpr, fcr)
        # Update sliding window sums
        lin.add_(fcr - flo)
        sqr.add_((fcr + flo) * (fcr - flo))
    return det


def peak_fwd_torch(prd, th, neg=True, gap=None):
    """Detect signal peaks using forward difference and a fixed threshold (PyTorch version).

    A peak is reported where the forward difference along the last axis changes sign and the signal value
    crosses ``th`` (below ``th`` when ``neg`` is :data:`True`, otherwise above ``th``). When ``gap`` is set,
    multiple peaks within a window of length ``gap`` are reduced to the single largest extremum.

    Args:
        prd (torch.Tensor): {3D-float, (n_ch, n_feat, n_samp)} Input prediction tensor
        th (int | float): Peak detection threshold
        neg (bool): When :data:`True`, look for samples below ``th``; when :data:`False`, above ``th``
            (default: ``True``)
        gap (int | None): Maximum allowed gap (in samples) between detected peaks; pass :data:`None` to
            keep every detection (default: ``None``)

    Returns:
        torch.Tensor: {3D-int} Per-sample peak flags (``1`` peak, ``0`` no peak)
    """
    diff = torch.diff(prd, n=1, dim=-1, append=prd[:, :, -1:]).sgn_()
    diff[:, :, 1:] = diff[:, :, :-1] + diff[:, :, 1:]
    det = torch.where((prd < th) & (diff == 0), 1, 0) if neg else torch.where((prd > th) & (diff == 0), 1, 0)
    if gap is not None:
        # Sample input tensors
        smp = prd.unfold(-1, gap, 2)
        prt = det.unfold(-1, gap, 2)
        # Initial multiple detection check
        chk = torch.where(prt.sum(-1) > 1)
        while chk[0].size(0) != 0:
            # Get actual peak location
            pos = torch.argmin(smp[chk[0], chk[1], chk[2], :], dim=-1) if neg \
                else torch.argmax(smp[chk[0], chk[1], chk[2], :], dim=-1)
            # Assign values to the detection
            prt[chk[0], chk[1], chk[2], :] = 0
            prt[chk[0], chk[1], chk[2], pos] = 1
            # Find multiple detection sections
            chk = torch.where(prt.sum(-1) > 1)
    return det


def eval_pos(prd, lbl, tol=2):
    """Evaluate spike-position accuracy by counting false negatives and false positives.

    Each prediction (resp. label) is dilated by ``tol`` samples on each side, and a label that is not covered
    by the dilated prediction counts as a false negative (and vice versa for false positives).

    Args:
        prd (torch.Tensor): {3D-int} One-hot spike-position prediction tensor
        lbl (torch.Tensor): {3D-int} One-hot spike-position reference tensor (same shape as ``prd``)
        tol (int): Position index tolerance in samples (default: ``2``)

    Returns:
        tuple[torch.Tensor, torch.Tensor]: Per-channel false negative and false positive counts

            - fn (torch.Tensor): False-negative counts summed along the last axis
            - fp (torch.Tensor): False-positive counts summed along the last axis
    """
    # Check false negative
    pos = prd.clone()
    for _ in range(tol):
        pos[:, :, :-1] = torch.bitwise_or(pos[:, :, :-1], pos[:, :, 1:])
        pos[:, :, 1:] = torch.bitwise_or(pos[:, :, 1:], pos[:, :, :-1])
    diff = torch.bitwise_and(lbl, pos.bitwise_not())
    fn = torch.sum(diff, dim=-1)

    # Check false positive
    ref = lbl.clone()
    for _ in range(tol):
        ref[:, :, :-1] = torch.bitwise_or(ref[:, :, :-1], ref[:, :, 1:])
        ref[:, :, 1:] = torch.bitwise_or(ref[:, :, 1:], ref[:, :, :-1])
    diff = torch.bitwise_and(prd, ref.bitwise_not())
    fp = torch.sum(diff, dim=-1)

    return fn, fp
