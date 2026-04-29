# -*- coding: utf-8 -*-

"""Spike clustering module

Waveform-based spike clustering algorithms together with pre/post-processing helpers and multichannel
cluster merging utilities.
"""

import numpy as np

__package__ = 'parus.data'
__name__ = 'parus.data.clst'

__all__ = [
    'cls_cosamp_blk', 'cls_cosamp_prg', 'cls_crscor_blk', 'cls_crscor_prg',
    'pos_ripple_flt', 'post_cls_chk', 'get_sig_nbr', 'find_crsch_sig', 'crsch_grp'
]
"""
Public function list:

- Signal clustering:

    - cls_cosamp_blk(sig, pos, asp, psp, k, w)        : Cluster spikes by cosine-amplitude similarity, block mode
    - cls_cosamp_prg(sig, pos, asp, psp, k, w, delta) : Cluster spikes by cosine-amplitude similarity, progressive mode
    - cls_crscor_blk(sig, pos, asp, psp, k)           : Cluster spikes by Pearson correlation, block mode
    - cls_crscor_prg(sig, pos, asp, psp, k, delta)    : Cluster spikes by Pearson correlation, progressive mode

- Pre/post-clustering:

    - pos_ripple_flt(sig, pos, lim, neg)              : Filter ripples from a one-hot spike position array
    - post_cls_chk(avg, mode, beta)                   : Compute the inter-cluster similarity matrix from cluster means

- Multichannel cluster merge:

    - get_sig_nbr(prb, lim)                           : Find neighbouring channels of a multichannel probe
    - find_crsch_sig(cls, grp, tot, lim, rng, th)     : Find cross-channel signal cells across neighbouring channels
    - crsch_grp(res)                                  : Group detected cross-channel cells into shared cell groups

Protected helpers:

- _gaussian_weight(asp, psp, sigma, epsilon)          : Gaussian weight vector centred at the peak index
- _get_wfm_smp(sig, pos, asp, psp)                    : Aligned waveform snippets and their source indices
"""


def _gaussian_weight(asp, psp, sigma=0.0, epsilon=2.0):
    """Build a Gaussian weight vector centred at the peak index.

    The weight at offset ``x`` is ``sqrt(Gaussian(x) / epsilon)``, with the centre value forced to ``1`` so
    that ``epsilon`` controls how strongly the peak dominates the weighted operations downstream.

    Args:
        asp (int): Anterior samples to consider (must be ``> 0``)
        psp (int): Posterior samples to consider (must be ``> 0``)
        sigma (float): Standard deviation of the Gaussian in samples; pass ``0`` (or any value ``<= 0``) to
            use ``5%`` of the total span (default: ``0.0``)
        epsilon (float): Additive emphasis applied at the peak; ``2.0`` doubles the peak weight relative to
            the Gaussian (default: ``2.0``)

    Returns:
        np.ndarray: {1D-float32} Gaussian weight vector of length ``asp + psp + 1``
    """
    num = asp + psp + 1
    sigma = sigma if sigma > 0 else num * 0.05
    dv = np.linspace(-asp / sigma, psp / sigma, num=num, endpoint=True, dtype=np.float32)  # dv = x / sigma
    wt = np.exp(-0.25 * dv ** 2) / np.sqrt(epsilon, dtype=np.float32)  # w = sqrt(Gaussian(x) / epsilon)
    wt[asp] = 1  # Normalize, peak value was emphasized with value of 2 in Gaussian
    return wt


def _get_wfm_smp(sig, pos, asp, psp):
    """Extract aligned waveform snippets from a signal at every one-hot spike index.

    For each non-zero entry in ``pos``, a window of length ``asp + psp + 1`` centred on the spike is taken
    from ``sig``. Indices that fall outside the bounds of ``sig`` are clamped to the nearest valid index.

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position array
        asp (int): Anterior samples to consider (must be ``> 0``)
        psp (int): Posterior samples to consider (must be ``> 0``)

    Returns:
        tuple[np.ndarray, np.ndarray]: Aligned waveform snippets and their source indices

            - smp (np.ndarray): {2D-float (n_spikes, asp + psp + 1)} Per-spike snippets
            - loc (np.ndarray): {1D-int} Source index of each snippet within ``sig``
    """
    # Check inputs
    asp = 0 if asp < 0 else asp
    psp = 0 if psp < 0 else psp
    # Set index tiles
    num = asp + psp + 1
    blk = np.arange(-asp, psp + 1, step=1, dtype=int)
    loc = np.nonzero(pos)[0]
    # Get required index
    idx = np.repeat(loc, num) + np.tile(blk, len(loc))
    idx = np.clip(idx, a_min=0, a_max=len(sig) - 1)
    # Get data
    smp = sig[idx].reshape(-1, num)
    return smp, loc


# Signal clustering functions ---------------------------------------------------------------------------------------- #

def cls_cosamp_blk(sig, pos, asp, psp, k=0.8, w=True, **kwargs):
    """Cluster spikes by combining cosine and amplitude similarity, block mode.

    The similarity between two waveforms ``A`` and ``B`` is ``S = c * a ** beta`` where
    ``c = (A · B) / (||A|| * ||B||)`` and ``a = (2 * min(||A||, ||B||)) / (||A|| + ||B||)``. Block mode treats
    every snippet in the recording together; it is conservative and fast but can struggle with drifting
    waveforms. For a more sensitive pairwise variant, use :func:`cls_cosamp_prg`.

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position array
        asp (int): Anterior samples to consider (must be ``> 0``)
        psp (int): Posterior samples to consider (must be ``> 0``)
        k (float): Similarity threshold in ``(0, 1)`` for grouping (default: ``0.8``)
        w (bool): When :data:`True`, apply a Gaussian peak emphasis weight to the snippets (default: ``True``)
        **kwargs: See below

    Keyword Args:
        beta (int | float): Weight on the amplitude component (must be ``> 0``); default ``0.5`` gives a soft
            amplitude effect
        sigma (float): Standard deviation of the Gaussian weight in samples; default ``0`` falls back to ``5%``
            of the snippet length
        epsilon (float): Additive peak emphasis on the Gaussian weight; default ``2.0`` doubles the peak weight

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]: Grouped waveforms and their means

            - res (list[np.ndarray]): {1D-int} Indices of grouped signals (one array per cluster)
            - avg (list[np.ndarray]): {1D-float} Mean waveform of each cluster
    """
    # Get keyword arguments
    beta = kwargs.get('beta', 0.5)
    sigma = kwargs.get('sigma', 0.0)
    epsilon = kwargs.get('epsilon', 2.0)
    # Get data
    smp, loc = _get_wfm_smp(sig, pos, asp, psp)
    # Get Gaussian weight
    wt = _gaussian_weight(asp, psp, sigma, epsilon) if w else np.ones(asp + psp + 1, dtype=np.float32)
    # Initialize process variables
    stp = np.arange(len(loc))
    res = []
    avg = []
    # COS-AMP composite accuracy
    nrm = np.linalg.norm(smp, ord=2, axis=1)  # 2nd order norm
    wnm = np.linalg.norm(smp * wt, ord=2, axis=1)  # 2nd order weighted norm
    while len(stp) > 0:
        # Compute result components
        dot = smp[stp] @ smp[stp[0]]
        mag = nrm[stp] * nrm[stp[0]]
        les = np.where(wnm[stp] < wnm[stp[0]], wnm[stp], wnm[stp[0]]) * 2
        acc = wnm[stp] + wnm[stp[0]]
        # Assign results
        var = (dot / mag) * (les / acc) ** beta
        grp = np.where(var >= k)[0]
        res.append(loc[stp[grp]])
        avg.append(np.mean(smp[stp[grp]], axis=0))
        # Remove grouped indices
        stp = np.delete(stp, grp)
    return res, avg


def cls_cosamp_prg(sig, pos, asp, psp, k=0.6, w=True, delta=0.2, **kwargs):
    """Cluster spikes by combining cosine and amplitude similarity, progressive mode.

    The similarity between two waveforms ``A`` and ``B`` is ``S = c * a ** beta`` where
    ``c = (A · B) / (||A|| * ||B||)`` and ``a = (2 * min(||A||, ||B||)) / (||A|| + ||B||)``. Progressive mode
    walks the snippets one at a time and assigns each to the most similar existing cluster (or seeds a new
    one), then drifts the cluster template by ``delta`` per assignment. It is more sensitive than block mode
    and tracks drifting waveforms better. For a fast non-broadcasting variant, use :func:`cls_cosamp_blk`.

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position array
        asp (int): Anterior samples to consider (must be ``> 0``)
        psp (int): Posterior samples to consider (must be ``> 0``)
        k (float): Similarity threshold in ``(0, 1)`` for grouping (default: ``0.6``)
        w (bool): When :data:`True`, apply a Gaussian peak emphasis weight to the snippets (default: ``True``)
        delta (float | None): Update weight on new samples in ``[0, 1]``; pass :data:`None` to use a plain
            running average across all assigned snippets (default: ``0.2``)
        **kwargs: See below

    Keyword Args:
        beta (int | float): Weight on the amplitude component (must be ``> 0``); default ``0.5`` gives a soft
            amplitude effect
        sigma (float): Standard deviation of the Gaussian weight in samples; default ``0`` falls back to ``5%``
            of the snippet length
        epsilon (float): Additive peak emphasis on the Gaussian weight; default ``2.0`` doubles the peak weight

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]: Grouped waveforms and their means

            - res (list[np.ndarray]): {1D-int} Indices of grouped signals (one array per cluster)
            - avg (list[np.ndarray]): {1D-float} Mean waveform of each cluster
    """
    # Get keyword arguments
    beta = kwargs.get('beta', 0.5)
    sigma = kwargs.get('sigma', 0.0)
    epsilon = kwargs.get('epsilon', 2.0)
    # Get data
    smp, loc = _get_wfm_smp(sig, pos, asp, psp)
    # Get Gaussian weight
    wt = _gaussian_weight(asp, psp, sigma, epsilon) if w else np.ones(asp + psp + 1, dtype=np.float32)
    # Initialize clustering history variables
    hst = smp[np.newaxis, 0]
    res = [np.array([loc[0]])]
    avg = [smp[0]]
    # Progressive COS-AMP composite accuracy
    nrm = np.linalg.norm(hst, ord=2, axis=1)
    wnm = np.linalg.norm(hst * wt, ord=2, axis=1)
    for i, s in zip(loc[1:], smp[1:]):
        nc = np.linalg.norm(s, ord=2)
        # Compute results
        dot = hst @ s
        mag = nrm * nc
        les = np.where(wnm < nc, wnm, nc) * 2
        acc = wnm + nc
        var =  (dot / mag) * (les / acc) ** beta
        # Check and assign results
        grp = np.argmax(var)
        if var[grp] < k:
            hst = np.vstack((hst, s))  # Add new history group
            res.append(np.array([i]))  # Add new result group
            avg.append(s)  # Add new average group
        else:
            res[grp] = np.append(res[grp], i)
            # Sum for all signal
            avg[grp] = avg[grp] + s
            # Update signal means
            if delta is None:
                hst[grp] = avg[grp] / len(res[grp])  # No weighting
            else:
                hst[grp] = hst[grp] * (1 - delta) + s * delta  # Weighted average for signal drifting
        # Update history norm
        nrm = np.linalg.norm(hst, ord=2, axis=1)
        wnm = np.linalg.norm(hst * wt, ord=2, axis=1)
    return res, [avg[_] / len(res[_]) for _ in range(len(res))]


def cls_crscor_blk(sig, pos, asp, psp, k=0.8):
    """Cluster spikes by Pearson correlation coefficient, block mode.

    The similarity between two waveforms ``A`` and ``B`` is the Pearson correlation
    ``S = ((A - mean(A)) · (B - mean(B))) / sqrt(sum((A - mean(A)) ** 2) * sum((B - mean(B)) ** 2))``. Block
    mode treats every snippet in the recording together; it is conservative and fast but can struggle with
    drifting waveforms. For a more sensitive pairwise variant, use :func:`cls_crscor_prg`.

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position array
        asp (int): Anterior samples to consider (must be ``> 0``)
        psp (int): Posterior samples to consider (must be ``> 0``)
        k (float): Similarity threshold in ``(0, 1)`` for grouping (default: ``0.8``)

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]: Grouped waveforms and their means

            - res (list[np.ndarray]): {1D-int} Indices of grouped signals (one array per cluster)
            - avg (list[np.ndarray]): {1D-float} Mean waveform of each cluster
    """
    # Get data
    smp, loc = _get_wfm_smp(sig, pos, asp, psp)
    # Initialize process variables
    stp = np.arange(len(loc))
    res = []
    avg = []
    # Pearson's R
    sft = (smp.T - np.mean(smp, axis=1)).T  # Sample mean shift
    sqs = np.sum(sft ** 2, axis=1)  # Sum of squares of mean shift
    while len(stp) > 0:
        # Get numerator and denominator for Pearson-R
        nmr = sft[stp] @ sft[stp[0]]
        dnm = np.sqrt(sqs[stp] * sqs[stp[0]])
        # Assign results
        var = nmr / dnm
        grp = np.where(var >= k)[0]
        res.append(loc[stp[grp]])
        avg.append(np.mean(smp[stp[grp]], axis=0))
        # Remove grouped indices
        stp = np.delete(stp, grp)
    return res, avg


def cls_crscor_prg(sig, pos, asp, psp, k=0.9, delta=0.2):
    """Cluster spikes by Pearson correlation coefficient, progressive mode.

    The similarity between two waveforms ``A`` and ``B`` is the Pearson correlation
    ``S = ((A - mean(A)) · (B - mean(B))) / sqrt(sum((A - mean(A)) ** 2) * sum((B - mean(B)) ** 2))``.
    Progressive mode walks the snippets one at a time and assigns each to the most similar existing cluster
    (or seeds a new one), then drifts the cluster template by ``delta`` per assignment. It is more sensitive
    than block mode and tracks drifting waveforms better. For a fast non-broadcasting variant, use
    :func:`cls_crscor_blk`.

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position array
        asp (int): Anterior samples to consider (must be ``> 0``)
        psp (int): Posterior samples to consider (must be ``> 0``)
        k (float): Similarity threshold in ``(0, 1)`` for grouping (default: ``0.9``)
        delta (float | None): Update weight on new samples in ``[0, 1]``; pass :data:`None` to use a plain
            running average across all assigned snippets (default: ``0.2``)

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]: Grouped waveforms and their means

            - res (list[np.ndarray]): {1D-int} Indices of grouped signals (one array per cluster)
            - avg (list[np.ndarray]): {1D-float} Mean waveform of each cluster
    """
    # Get data
    smp, loc = _get_wfm_smp(sig, pos, asp, psp)
    # Initialize clustering history variables
    hst = smp[np.newaxis, 0]
    res = [np.array([loc[0]])]
    avg = [smp[0]]
    # Progressive Pearson's R
    sft = (smp.T - np.mean(smp, axis=1)).T  # Sample mean shift
    sqs = np.sum(sft ** 2, axis=1)  # Sum of squares of mean shift
    hsf = (hst.T - np.mean(hst, axis=1)).T  # Averaged history mean shift
    hss = np.sum(hsf ** 2, axis=1)  # History sum of squares of mean shift
    for i, s, f, q in zip(loc[1:], smp[1:], sft[1:], sqs[1:]):
        # Compute results
        nmr = hsf @ f
        dnm = np.sqrt(hss * q)
        var = nmr / dnm
        # Check and assign results
        grp = np.argmax(var)
        if var[grp] < k:
            hst = np.vstack((hst, s))  # Add new history group
            res.append(np.array([i]))  # Add new result group
            avg.append(s)  # Add new average group
        else:
            res[grp] = np.append(res[grp], i)
            # Sum for all signal
            avg[grp] = avg[grp] + s
            # Update signal means
            if delta is None:
                hst[grp] = avg[grp] / len(res[grp])  # No weighting
            else:
                hst[grp] = hst[grp] * (1 - delta) + s * delta  # Weighted average for signal drifting
        # Update history variables
        hsf = (hst.T - np.mean(hst, axis=1)).T
        hss = np.sum(hsf ** 2, axis=1)
    return res, [avg[_] / len(res[_]) for _ in range(len(res))]


# Pre/Post clustering functions -------------------------------------------------------------------------------------- #

def pos_ripple_flt(sig, pos, lim=3, neg=True):
    """Filter ripples from a one-hot spike position array.

    Consecutive spike indices closer than ``lim`` samples are interpreted as a single spike with ripple artefacts.
    The function keeps the index of the local extremum (minimum when ``neg`` is :data:`True`, maximum otherwise)
    and clears the surrounding ripple positions.

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position array
        lim (int): Minimum index gap required between consecutive spikes (default: ``3``)
        neg (bool): When :data:`True`, the kept index is the local minimum; when :data:`False`, the local
            maximum (default: ``True``)

    Returns:
        np.ndarray: {1D-int} Filtered one-hot spike position array (same shape as ``pos``)
    """
    # Find consecutive indices from position
    pos = pos.copy()  # Avoid overwrite
    loc = np.nonzero(pos)[0]
    chk = [i for i in np.split(loc, np.where(np.ediff1d(loc) > lim)[0] + 1) if i.size > 1]
    # Filtering
    for i in chk:
        # Find actual location
        val = i[np.argmin(sig[i])] if neg else i[np.argmax(sig[i])]
        # Set position data
        pos[i] = 0
        pos[val] = 1
    return pos


def post_cls_chk(avg, mode='cosamp', beta=0.5):
    """Compute the inter-cluster similarity matrix from cluster mean waveforms.

    Used to verify the output of a clustering function: each entry ``[i, j]`` is the similarity between the
    mean waveforms of clusters ``i`` and ``j`` under ``mode``. The matrix is symmetric with ``1`` on the diagonal.

    Args:
        avg (list[np.ndarray]): Cluster mean waveforms returned by a clustering function
        mode (str): Similarity mode; one of ``{'cossim', 'ampsim', 'cosamp', 'crscor'}`` (default: ``'cosamp'``)
        beta (int | float): Amplitude weight (must be ``> 0``); only used when ``mode == 'cosamp'`` (default: ``0.5``)

    Returns:
        np.ndarray: {2D-float32} Symmetric similarity matrix of shape ``(len(avg), len(avg))``

    Raises:
        ValueError: If ``mode`` is not one of ``{'cossim', 'ampsim', 'cosamp', 'crscor'}``
    """
    res = np.zeros((len(avg), len(avg)), dtype=np.float32)
    avg = np.asarray(avg)  # Cast type
    if mode == 'cossim':
        nrm = np.linalg.norm(avg, ord=2, axis=1)  # 2nd order norm
        for i in range(len(avg) - 1):
            dot = avg[i + 1:] @ avg[i]
            mag = nrm[i + 1:] * nrm[i]
            # Assign results
            res[i, i] = 1.0
            res[i, i + 1:] = res[i + 1:, i] = dot / mag
    elif mode == 'ampsim':
        nrm = np.linalg.norm(avg, ord=2, axis=1)  # 2nd order norm
        for i in range(len(avg) - 1):
            les = np.where(nrm[i + 1:] < nrm[i], nrm[i + 1:], nrm[i]) * 2
            acc = nrm[i + 1:] + nrm[i]
            # Assign results
            res[i, i] = 1.0
            res[i, i + 1:] = res[i + 1:, i] = les / acc
    elif mode == 'cosamp':
        nrm = np.linalg.norm(avg, ord=2, axis=1)  # 2nd order norm
        for i in range(len(avg) - 1):
            dot = avg[i + 1:] @ avg[i]
            mag = nrm[i + 1:] * nrm[i]
            les = np.where(nrm[i + 1:] < nrm[i], nrm[i + 1:], nrm[i]) * 2
            acc = nrm[i + 1:] + nrm[i]
            # Assign results
            res[i, i] = 1.0
            res[i, i + 1:] = res[i + 1:, i] = (dot / mag) * (les / acc) ** beta
    elif mode == 'crscor':
        sft = (avg.T - np.mean(avg, axis=1)).T  # Sample mean shift
        sqs = np.sum(sft ** 2, axis=1)  # Sum of squares of mean shift
        for i in range(len(avg) - 1):
            nmr = sft[i + 1:] @ sft[i]
            dnm = np.sqrt(sqs[i + 1:] * sqs[i])
            # Assign results
            res[i, i] = 1.0
            res[i, i + 1:] = res[i + 1:, i] = nmr / dnm
    else:
        raise ValueError("Invalid similarity check mode, allowed mode: ['cossim', 'ampsim', 'cosamp', 'crscor'].")
    return res


# Multichannel cluster merge functions ------------------------------------------------------------------------------- #

def get_sig_nbr(prb, lim=60):
    """Find neighbouring channels of a multichannel probe within a distance limit.

    Channels are considered neighbours when their geometric distance (Euclidean over the ``geo`` coordinates
    of each site) is at most ``lim`` micrometres. Each channel is included in its own neighbour list.

    Args:
        prb (dict): Probe geometry data with a ``'site'`` list of per-channel dictionaries holding ``'id'``
            and ``'geo'`` keys
        lim (int | float): Inclusive distance limit in micrometres (default: ``60``)

    Returns:
        dict[int, list[int]]: Mapping from probe channel ID to the list of neighbouring channel IDs
    """
    # Extract data from probe dictionary
    tot = len(prb['site'])
    c = np.zeros(tot, dtype=int)
    x = np.zeros(tot, dtype=int)
    y = np.zeros(tot, dtype=int)
    for i, s in enumerate(prb['site']):
        c[i] = s['id']
        x[i], y[i] = s['geo']
    # Compute distance
    xx = np.subtract.outer(x, x)
    yy = np.subtract.outer(y, y)
    dist = np.sqrt(xx ** 2 + yy ** 2)
    # Arrange result
    org, tgt = np.where(dist <= lim)
    return {c[i].item(): c[tgt[org == i]].tolist() for i in range(len(prb['site']))}


def find_crsch_sig(cls, grp, tot, lim=0, rng=5, th=0.8):
    """Find cross-channel signal cells for multichannel probes.

    For every cluster in a main channel, the function searches its neighbouring channels (according to ``grp``)
    for sub-clusters whose spike indices overlap with the main cluster's by at least ``th`` after expanding
    each main spike to a ``2 * rng + 1`` window.

    Args:
        cls (dict[int, list[np.ndarray]]): Per-channel clusters; each value is a list of one-hot spike index
            arrays
        grp (dict[int, list[int]]): Per-channel neighbour lists from :func:`get_sig_nbr`
        tot (int): Total length of the source signal
        lim (int): Minimum size for a sub-cluster to be considered (default: ``0``)
        rng (int): Allowed index range for the overlap check (default: ``5``)
        th (float): Inclusive overlap threshold in ``[0, 1]`` (default: ``0.8``)

    Returns:
        list[dict[str, dict[str, int]]]: One entry per detected cross-channel match with layout
            ``[{'main': {'ch': int, 'id': int}, 'sub': {'ch': int, 'id': int}}, ...]``
    """
    res = []  # INIT VAR
    # Get search indices range
    num = 2 * rng + 1
    blk = np.arange(-rng, rng + 1, step=1, dtype=int)
    # Process scan
    for g in grp:
        chs = [c for c in grp[g] if c != g]
        # Exclude empty channels
        if (len(cls[g]) == 0) or (sum([len(cls[c]) for c in chs]) == 0):
            continue
        # Get cells in main channel
        for i, ref in enumerate(cls[g]):
            # Get indices
            idx = np.repeat(ref, num) + np.tile(blk, len(ref))
            idx = np.clip(idx, a_min=0, a_max=tot - 1).reshape(-1, num, order='C')
            # Search in neighbouring channels
            for c in chs:
                # Exclude empty channel
                if len(cls[c]) == 0:
                    continue
                for j, tgt in enumerate(cls[c]):
                    # Limit minimum cluster size
                    if len(tgt) < lim:
                        continue
                    # Find match clusters
                    loc = np.zeros(tot, dtype=np.int8)
                    loc[tgt] = 1
                    match = np.sum(np.sum(loc[idx], axis=1) == 1)
                    # Compute synchronized rate
                    score = match / len(tgt)
                    if score > th:
                        res.append({'main': {'ch': g, 'id': i}, 'sub': {'ch': c, 'id': j}})
    return res


def crsch_grp(res):
    """Group detected cross-channel cells into shared cell groups.

    Walks the pairwise matches returned by :func:`find_crsch_sig` and merges any two clusters that share at
    least one channel-and-index pair into a single group. A second pass produces a per-group sequence count
    that flags channels that contribute multiple clusters within the same group.

    Args:
        res (list[dict[str, dict[str, int]]]): Pairwise cross-channel match list returned by :func:`find_crsch_sig`

    Returns:
        tuple[list[list[tuple[int, int]]], list[list[int]]]: Grouping result

            - grp (list[list[tuple[int, int]]]): Each entry lists the ``(channel, cluster_id)`` pairs that
              belong to the same group
            - cnt (list[list[int]]): Parallel list of per-pair occurrence counters (``0`` for unique pairs,
              ``1`` for duplicates that should be retained)
    """
    if not res:
        return [], []
    # Initialize variables
    pm = (res[0]['main']['ch'], res[0]['main']['id'])
    ps = (res[0]['sub']['ch'], res[0]['sub']['id'])
    grp = [[pm, ps]]
    reg = [{pm[0]: [1, 0], ps[0]: [1, 1]}]
    cnt = [[0, 0]]
    # Find grouping pairs
    for p in res[1:]:
        pm = (p['main']['ch'], p['main']['id'])
        ps = (p['sub']['ch'], p['sub']['id'])
        for i, g in enumerate(grp):
            ck_gm = pm in g
            ck_gs = ps in g
            if ck_gm or ck_gs:
                pt = ps if ck_gm else pm
                g.append(pt)
                # Count for group in the same channel
                if pt[0] in reg[i]:
                    reg[i][pt[0]] = [reg[i][pt[0]][0] + 1, reg[i][pt[0]][1]]
                    cnt[i].append(reg[i][pt[0]][0])
                else:
                    reg[i][pt[0]] = [1, len(g) - 1]
                    cnt[i].append(0)
                break
        else:
            grp.append([pm, ps])
            reg.append({pm[0]: [1, 0], ps[0]: [1, 1]})
            cnt.append([0, 0])
    # Final fittings for counting
    for i, r in enumerate(reg):
        for k in r:
            if r[k][0] > 1:
                cnt[i][r[k][1]] = 1
    return grp, cnt
