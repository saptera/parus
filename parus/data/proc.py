# -*- coding: utf-8 -*-

"""Basic data process module

Sampling, distribution generation, and label-driven signal extraction helpers used by the data pipelines.
"""

import copy
import numpy as np
from scipy.stats import norm, laplace

__package__ = 'parus.data'
__name__ = 'parus.data.proc'

__all__ = [
    'arr_rand_samp', 'norm_lst_gen', 'laplace_lst_gen',
    'spk_merge', 'neuron_rnd_samp', 'neuron_sig_samp', 'neuron_sig_mean', 'pred_mae', 'nsd_asgnv',
    'chk_settle'
]
"""
Public function list:

- arr_rand_samp(arr, n_samp)                             : Draw a random subset from a NumPy array without replacement
- norm_lst_gen(peak, side, level)                        : Generate a list of values following a normal distribution
- laplace_lst_gen(peak, side, scale)                     : Generate a list of values following a Laplace distribution
- spk_merge(spk_data)                                    : Merge and sort channel-arranged spike timing data
- neuron_rnd_samp(sig, time, lbl, num, size)             : Random slice neural signal samples for training
- neuron_sig_samp(sig, time, lbl, num, size)             : Slice neural signal samples around labelled spikes
- neuron_sig_mean(sig, time, lbl, size, pos, ...)        : Extract the averaged neural signal around labelled spikes
- pred_mae(data, th)                                     : Score a predicted signal using mean absolute error
- nsd_asgnv(sig_data, rng_asgn, val_lst, method, ...)    : Assign a value list around the labelled signal positions
- chk_settle(sig, win)                                   : Locate the first sample where the signal settles to baseline
"""


def arr_rand_samp(arr, n_samp):
    """Draw a random subset of ``n_samp`` elements from a NumPy array without replacement.

    Args:
        arr (np.ndarray): Input array of any shape; the returned subset preserves dtype and is flattened
        n_samp (int): Number of elements to sample (must be ``<= arr.size``)

    Returns:
        np.ndarray: {1D} Sampled subset of ``arr``
    """
    mask = np.array([True] * n_samp + [False] * (arr.size - n_samp))
    np.random.shuffle(mask)
    mask = np.reshape(mask, arr.shape)
    return arr[mask]


def norm_lst_gen(peak, side, level=2):
    """Generate a list of values following a normal distribution centred at zero.

    The normal probability density is sampled at integer offsets in ``[-side, side]`` and rescaled so that
    the centre value equals ``peak``. The ``level`` argument selects the three-sigma rule that ``[-side, side]``
    should cover.

    Args:
        peak (float): Peak (centre) value of the output list
        side (int): Number of integer samples on each side of the peak; the output length is ``2 * side + 1``
        level (int): Three-sigma coverage of ``[-side, side]``; one of ``{1, 2, 3}`` (default: ``2``)

            - ``1``: ``side`` = 1-sigma, output covers P(-side, side) ≈ 68.27%
            - ``2``: ``side`` = 2-sigma, output covers P(-side, side) ≈ 95.45%
            - ``3``: ``side`` = 3-sigma, output covers P(-side, side) ≈ 99.73%

    Returns:
        list[float]: Generated values, length ``2 * side + 1``
    """
    lvl_dic = {1: 1, 2: 2, 3: 3}
    nd = norm(loc=0, scale=side / lvl_dic[level])  # Normal distribution sigma range
    fac = peak / nd.pdf(0)  # Peak stretch factor
    val = []  # INIT VAR
    for i in range(-side, side + 1, 1):
        val.append(nd.pdf(i).item() * fac)
    return val


def laplace_lst_gen(peak, side, scale=1):
    """Generate a list of values following a Laplace distribution centred at zero.

    The Laplace probability density is sampled at integer offsets in ``[-side, side]`` and rescaled so that
    the centre value equals ``peak``.

    Args:
        peak (float): Peak (centre) value of the output list
        side (int): Number of integer samples on each side of the peak; the output length is ``2 * side + 1``
        scale (int | float): Diversity of generated samples; larger values produce wider distributions (default: ``1``)

    Returns:
        list[float]: Generated values, length ``2 * side + 1``
    """
    ld = laplace(loc=0, scale=scale)  # Laplace distribution with scale
    fac = peak / ld.pdf(0)  # Peak stretch factor
    val = []  # INIT VAR
    for i in range(-side, side + 1, 1):
        val.append(ld.pdf(i).item() * fac)
    return val


def spk_merge(spk_data):
    """Merge and sort channel-arranged spike timing data into a per-channel timestamp array.

    Each channel's per-cell timestamp arrays are concatenated and sorted in ascending order, producing a
    single timestamp vector per channel suitable for downstream signal extraction.

    Args:
        spk_data (dict[int, dict[int, np.ndarray]]): Channel-keyed spike timing data with layout
            ``{probe_channel: {cell_id: spike_times}}``

    Returns:
        dict[int, np.ndarray]: Mapping from probe channel to merged-and-sorted spike timestamps; channels
            with no spikes map to :data:`None`
    """
    out_data = {}  # INIT VAR
    for i in spk_data:
        spk_keys = spk_data[i].keys()
        spk_out = np.sort(np.concatenate([spk_data[i][k] for k in spk_keys]), kind='mergesort') if spk_keys else None
        out_data[i] = spk_out
    return out_data


def neuron_rnd_samp(sig, time, lbl, num=1000, size=150):
    """Random-slice neural signal samples for model training.

    Each output sample is a fixed-size window starting at a uniformly random index within ``sig``, paired
    with the matching slice of a one-hot spike label vector built from ``lbl``.

    Args:
        sig (np.ndarray): {1D-scalar} Single-channel neural signal data
        time (np.ndarray): {1D-scalar} Recording time vector aligned with ``sig`` (must be sorted and the same
            length as ``sig``)
        lbl (np.ndarray): {1D-scalar} Spike timestamp labels in seconds
        num (int): Number of samples to extract (default: ``1000``)
        size (int): Length of each sample in data points (default: ``150``)

    Returns:
        list[dict[str, np.ndarray]]: Sampled signal segments, each entry has

            - sig (np.ndarray): {1D-float64} Signal slice of length ``size``
            - lbl (np.ndarray): {1D-int8} One-hot spike position label of length ``size``
    """
    # Get label marker from time array
    tmk = np.zeros(time.shape, dtype=np.int8)
    mrk_idx = np.searchsorted(time, lbl, side='left')
    tmk[mrk_idx] = 1
    high_idx = len(sig) - size
    # Sampling with defined parameters
    sig_samp = []  # INIT VAR
    for s in range(num):
        samp = {'sig': None, 'lbl': None}  # INIT/RESET VAR
        # Get random index range
        min_idx = np.random.randint(low=0, high=high_idx)
        max_idx = min_idx + size
        # Extract data
        samp['sig'] = sig[min_idx:max_idx]
        samp['lbl'] = tmk[min_idx:max_idx]
        sig_samp.append(copy.deepcopy(samp))
    return sig_samp


def neuron_sig_samp(sig, time, lbl, num=1000, size=150):
    """Slice neural signal samples around labelled spikes for model training.

    Unlike :func:`neuron_rnd_samp`, every output sample is guaranteed to contain at least one labelled spike:
    sample windows are anchored to randomly drawn spike indices and offset within the window by a random
    fraction of ``size``.

    Args:
        sig (np.ndarray): {1D-scalar} Single-channel neural signal data
        time (np.ndarray): {1D-scalar} Recording time vector aligned with ``sig`` (must be sorted and the same
            length as ``sig``)
        lbl (np.ndarray): {1D-scalar} Spike timestamp labels in seconds
        num (int): Number of samples to extract (default: ``1000``)
        size (int): Length of each sample in data points (default: ``150``)

    Returns:
        list[dict[str, np.ndarray]]: Sampled signal segments, each entry has

            - sig (np.ndarray): {1D-float64} Signal slice of length ``size``
            - lbl (np.ndarray): {1D-int8} One-hot spike position label of length ``size``
    """
    # Get label marker from time array
    tmk = np.zeros(time.shape, dtype=np.int8)
    mrk_idx = np.searchsorted(time, lbl, side='left')
    tmk[mrk_idx] = 1
    max_len = len(sig)
    # Sampling with defined parameters
    lsp = arr_rand_samp(mrk_idx, num)
    sig_samp = []  # INIT VAR
    for s in lsp:
        samp = {'sig': None, 'lbl': None}  # INIT/RESET VAR
        # Get random index range
        min_idx = s.item() - np.random.randint(round(size * 0.8))
        min_idx = 0 if min_idx < 0 else min_idx  # Verify
        max_idx = min_idx + size
        min_idx = max_len - size if max_idx > max_len else min_idx  # Verify
        # Extract data
        samp['sig'] = sig[min_idx:max_idx]
        samp['lbl'] = tmk[min_idx:max_idx]
        sig_samp.append(copy.deepcopy(samp))
    return sig_samp


def neuron_sig_mean(sig, time, lbl, size=50, pos=None, method='none', rng_srch=10):
    """Extract the averaged neural signal around labelled spikes for archiving.

    Each labelled spike contributes one fixed-size window centred at ``pos``. When ``method`` is set to
    ``'min'`` or ``'max'``, the spike index is first relocated to the local extremum within
    ``[-rng_srch, rng_srch]`` of the labelled timestamp before extracting the window.

    Args:
        sig (np.ndarray): {1D-scalar} Single-channel neural signal data
        time (np.ndarray): {1D-scalar} Recording time vector aligned with ``sig`` (must be sorted and the same
            length as ``sig``)
        lbl (np.ndarray): {1D-scalar} Spike timestamp labels in seconds
        size (int): Length of each per-spike window in data points (default: ``50``)
        pos (int | None): Index of the spike within the window; pass :data:`None` to use the window centre
            (default: ``None``)
        method (str): Local extremum relocation mode; one of ``{'min', 'max', 'none'}`` (default: ``'none'``)

            - ``'min'``: relocate to the signal minimum within ``[-rng_srch, rng_srch]``
            - ``'max'``: relocate to the signal maximum within ``[-rng_srch, rng_srch]``
            - ``'none'``: keep the original labelled index (``rng_srch`` is ignored)

        rng_srch (int): Range to search for the local extremum (default: ``10``)

    Returns:
        tuple[np.ndarray, int]: Averaged signal sample

            - mean (np.ndarray): {1D-float64} Averaged signal across all labelled spikes
            - pos (int): Index of the spike within the returned window

    Raises:
        ValueError: If ``pos`` is not a positive integer strictly less than ``size``, or if ``method`` is
            outside ``{'min', 'max', 'none'}``
    """
    pos = int(size / 2) if pos is None else pos
    # Verify inputs
    if pos <= 0 or pos >= size:
        raise ValueError("Invalid value for [pos]. [pos] must be a positive integer less than [size].")
    if method not in ['min', 'max', 'none']:
        raise ValueError("Invalid type for [method]. Expected 'min', 'max' or 'none'.")
    # Get label marker from time array
    tmk = np.zeros(time.shape, dtype=np.int8)
    mrk_idx = np.searchsorted(time, lbl, side='left')
    tmk[mrk_idx] = 1
    # Sampling with defined parameters
    sig_samp = np.zeros((len(mrk_idx), size))  # INIT VAR
    for s in range(len(mrk_idx)):
        # Relocating signal peak
        if method == 'none':
            loc = mrk_idx[s].item()
        else:
            # Get search range
            lst_min = 0 if mrk_idx[s] - rng_srch < 0 else mrk_idx[s].item() - rng_srch
            lst_max = len(sig) if mrk_idx[s] + rng_srch >= len(sig) else mrk_idx[s].item() + rng_srch + 1
            lst_srch = list(range(lst_min, lst_max))
            # Search for local extremum
            if method == 'min':
                loc = lst_srch[np.argmin(sig[lst_srch]).item()]
            else:
                loc = lst_srch[np.argmax(sig[lst_srch]).item()]
        # Get index range
        min_idx = loc - pos
        max_idx = min_idx + size
        idx = list(range(min_idx, max_idx))
        # Assign value
        sig_samp[s, :] = sig[idx]
    return np.mean(sig_samp, axis=0), pos


def pred_mae(data, th=35):
    """Score a predicted signal against its ground-truth label using mean absolute error (MAE).

    Args:
        data (dict): Denoised signal output from a model with the following entries

            - inp (np.ndarray): Input signal
            - prd (np.ndarray): Predicted signal
            - lbl (np.ndarray): Ground-truth label

        th (int | float): Quality threshold; scores strictly less than ``th`` pass the quality check
            (default: ``35``)

    Returns:
        tuple[float, bool]: Mean absolute error result of the prediction

            - score (float): MAE between ``data['lbl']`` and ``data['prd']``
            - q (bool): :data:`True` when ``score < th``, :data:`False` otherwise
    """
    score = np.mean(np.abs(np.subtract(data['lbl'], data['prd']))).item()
    q = score < th
    return score, q


def nsd_asgnv(sig_data, rng_asgn, val_lst, method='min', rng_srch=10):
    """Assign a value list around the labelled positions of a one-hot signal sample.

    For each labelled spike, the function optionally relocates the position to a local extremum and writes
    the values from ``val_lst`` over the ``2 * rng_asgn + 1`` surrounding indices.

    Args:
        sig_data (dict[str, np.ndarray]): Labelled neural signal sample with layout
            ``{'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-int8[0|1])}``
        rng_asgn (int): One-sided range of indices to assign values to; the assignment span is ``2 * rng_asgn + 1``
        val_lst (list | np.ndarray): Values to assign across the span; must have length ``2 * rng_asgn + 1``
        method (str): Local extremum relocation mode; one of ``{'min', 'max', 'none'}`` (default: ``'min'``)

            - ``'min'``: relocate to the signal minimum within ``[-rng_srch, rng_srch]``
            - ``'max'``: relocate to the signal maximum within ``[-rng_srch, rng_srch]``
            - ``'none'``: keep the original labelled index (``rng_srch`` is ignored)

        rng_srch (int): Range to search for the local extremum (default: ``10``)

    Returns:
        dict[str, np.ndarray]: Value-assigned labelled signal sample with layout
            ``{'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-float64)}``

    Raises:
        ValueError: If ``len(val_lst) != 2 * rng_asgn + 1`` or ``method`` is outside ``{'min', 'max', 'none'}``
    """
    sig_data_out = copy.deepcopy(sig_data)  # Make copy, avoid unexpected changes
    # Verify inputs
    if len(val_lst) != rng_asgn * 2 + 1:
        raise ValueError("Length of [val_lst] must be equal to [rng_asgn] * 2 + 1.")
    if method not in ['min', 'max', 'none']:
        raise ValueError("Invalid type for [method]. Expected 'min', 'max' or 'none'.")
    # Search around the labels
    idx = sig_data['lbl'].nonzero()[0]
    lbl = np.zeros(sig_data['lbl'].shape, dtype=np.float64)  # INIT VAR
    for i in idx:
        if method == 'none':
            loc = i.item()
        else:
            # Get search range
            lst_min = 0 if i - rng_srch < 0 else i.item() - rng_srch
            lst_max = len(sig_data['sig']) if i + rng_srch >= len(sig_data['sig']) else i.item() + rng_srch + 1
            lst_srch = list(range(lst_min, lst_max))
            # Search for local extremum
            if method == 'min':
                loc = lst_srch[np.argmin(sig_data['sig'][lst_srch]).item()]
            else:
                loc = lst_srch[np.argmax(sig_data['sig'][lst_srch]).item()]
        # Assign value to original
        for j in range(rng_asgn * 2 + 1):
            curr_idx = loc - rng_asgn + j
            if curr_idx < 0:
                continue
            elif curr_idx >= len(sig_data['sig']):
                break
            else:
                lbl[curr_idx] = val_lst[j]
    # Return values
    sig_data_out['lbl'] = lbl
    return sig_data_out


def chk_settle(sig, win=10):
    """Locate the first sample where the signal settles to baseline.

    Walks a sliding window of length ``win`` along ``sig`` and combines the windowed mean (with a linear
    distance penalty) and standard deviation, normalised by the global statistics of ``sig``. The minimum of
    the combined score marks the settle point.

    Args:
        sig (list[int | float] | np.ndarray): Input signal
        win (int): Sliding window size in samples (default: ``10``)

    Returns:
        int: Sample index of the estimated settle point

    Note:
        The result is sensitive to ``win`` and therefore not safe to use without supervision; pick ``win``
        with the expected baseline timescale in mind and inspect the output before relying on it.
    """
    # Compute sliding window initial values
    step = len(sig) - win
    win_fac = 1 / win
    lin_sum = np.sum(sig[:win], axis=None)
    sqr_sum = np.sum(np.square(sig[:win]), axis=None)
    # Compute global effects
    abs_glob = abs(np.mean(sig))
    std_glob = np.std(sig)

    abs_rec = np.zeros(step, dtype=float)  # INIT VAR
    std_rec = np.zeros(step, dtype=float)  # INIT VAR
    for i in range(step):
        # Update filter
        avg = lin_sum * win_fac
        std = np.sqrt(abs(sqr_sum * win_fac - avg * avg))  # abs() to avoid negative value caused by precision loss
        # Update sliding window sums
        lin_sum = lin_sum + sig[i + win] - sig[i]
        sqr_sum = sqr_sum + (sig[i + win] + sig[i]) * (sig[i + win] - sig[i])
        # Record value
        abs_rec[i] = abs(avg) + i  # Plus distance penalty
        std_rec[i] = std

    # Compare and return
    comp = abs_rec / abs_glob + std_rec / std_glob
    return np.argmin(comp).item() + win // 2
