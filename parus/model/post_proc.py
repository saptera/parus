import torch

"""Function list:
peak_det_torch(prd, lag, threshold, influence=0.0): Robust signal peak detection using z-scores, PyTorch version.
"""


def peak_det_torch(prd, lag, threshold, influence=0.0):
    """ Robust signal peak detection using z-scores, PyTorch version.
        Inspired from J.P.G. van Brakel [https://stackoverflow.com/a/22640362/6029703]

    Args:
        prd (torch.Tensor): {3D-float, (n-ch, n-feat, n-samp)} Input prediction results
        lag (int): The length of data will be smoothed, larger lags should be included for more stationary data
        threshold (int | float): Threshold of standard deviations from the moving mean above to classify as peak
        influence (float): {0 ~ 1} The influence of signals on the algorithm's detection threshold (default: 0.0)
            - 0: Signals have no influence on the threshold, implicitly assume signal is stationary
            - 1: Signals have full influence of normal data points

    Returns:
        torch.Tensor: {int} Detected peak indices -- 1 = positive peak, -1 = negative peak, 0 = no peak
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


def peak_det_diff(prd, th, neg=True, gap=None):
    """ Signal peak detection using forward difference.

    Args:
        prd (torch.Tensor): {3D-float, (n-ch, n-feat, n-samp)} Input prediction results
        th (int | float): Peak detection threshold
        neg (bool): Negative peak flag -- True = peak less than threshold, False = peak greater than threshold
        gap (int | float| None): Maximum gap between peaks (default: None)

    Returns:
        torch.Tensor: {int} Detected peak indices -- 1 = peak, 0 = no peak
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
