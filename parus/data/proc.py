# Basic data process functions

import copy
import numpy as np
from scipy.stats import norm, laplace

__all__ = [
    'arr_rand_samp', 'norm_lst_gen', 'laplace_lst_gen',
    'spk_merge', 'neuron_rnd_samp', 'neuron_sig_samp', 'neuron_sig_mean', 'pred_mae', 'nsd_asgnv'
]
"""
Function list:
  arr_rand_samp(arr, n_samp): Random sampling of unique samples from a NumPy array.
  norm_lst_gen(peak, side, level=2): Generate a list obeying normal distribution.
  laplace_lst_gen(peak, side, scale=1): Generate a list obeying laplace distribution.
  spk_merge(spk_data): Merge and sort channel arranged spike data for data sampling. 
  neuron_rnd_samp(sig, time, lbl, num=1000, size=150): Random slice and extract neuronal signal for training models.
  neuron_sig_samp(sig, time, lbl, num=1000, size=150): Slice and extract neuronal signal data for training models.
  neuron_sig_mean(sig, time, lbl, size=50, pos=None, method='none', rng_srch=10): Extract neuronal signal for archiving.
  pred_mae(data, th=35): Get evaluation score of predicted signal, by computing MAE.
  nsd_asgnv(sig_data, rng_asgn, val_lst, method='min', rng_srch=10): Assign a value list around the signal.
"""


def arr_rand_samp(arr, n_samp):
    """ Random sampling of unique samples from a NumPy array.

    Args:
        arr (np.ndarray): Input array
        n_samp (int): Number of samples

    Returns:
        np.ndarray: {1D} Samples from original array
    """
    mask = np.array([True] * n_samp + [False] * (arr.size - n_samp))
    np.random.shuffle(mask)
    mask = np.reshape(mask, arr.shape)
    return arr[mask]


def norm_lst_gen(peak, side, level=2):
    """ Generate a list obeying normal distribution.

    Args:
        peak (float): Peak (centre) value of output
        side (int): Number of samples around the peak
        level (int): {1 | 2 | 3}: Level of three-sigma rule within the [size]. (default: 2)
            - 1: [size] = 1-sigma, output list covering P(-[size], size) = 68.27%
            - 2: [size] = 2-sigma, output list covering P(-[size], size) = 95.45%
            - 3: [size] = 3-sigma, output list covering P(-[size], size) = 99.73%

    Returns:
        list[float]: Output list of generated value
    """
    lvl_dic = {1: 1, 2: 2, 3: 3}
    nd = norm(loc=0, scale=side / lvl_dic[level])  # Normal distribution sigma range
    fac = peak / nd.pdf(0)  # Peak stretch factor
    val = []  # INIT VAR
    for i in range(-side, side + 1, 1):
        val.append(nd.pdf(i).item() * fac)
    return val


def laplace_lst_gen(peak, side, scale=1):
    """ Generate a list obeying laplace distribution.

    Args:
        peak (float): Peak (centre) value of output
        side (int): Number of samples around the peak
        scale (int | float): : Diversity of generated samples (default: 1)

    Returns:
        list[float]: Output list of generated value.
    """
    ld = laplace(loc=0, scale=scale)  # Laplace distribution with scale
    fac = peak / ld.pdf(0)  # Peak stretch factor
    val = []  # INIT VAR
    for i in range(-side, side + 1, 1):
        val.append(ld.pdf(i).item() * fac)
    return val


def spk_merge(spk_data):
    """ Merge and sort channel arranged spike data for data sampling.

    Args:
        spk_data (dict[int, dict[int, np.ndarray]]): Channel type spike timing data, data structure as follows:
                                                     {prob_ch: {cell_id: spk_time}}

    Returns:
        dict[int, np.ndarray]: Merged and sorted spike timing data, data structure as: {prob_ch: merged_spk_time}
    """
    out_data = {}  # INIT VAR
    for i in spk_data:
        spk_keys = spk_data[i].keys()
        spk_out = np.sort(np.concatenate([spk_data[i][k] for k in spk_keys]), kind='mergesort') if spk_keys else None
        out_data[i] = spk_out
    return out_data


def neuron_rnd_samp(sig, time, lbl, num=1000, size=150):
    """ Random slice and extract neuronal signal data for training models.
            This function only return NumPy-int8[0|1] (one-hot) type labels
            Samples form this function are simple random slices of raw signal

    Args:
        sig (np.ndarray): {1D-scalar} Single channel neuronal signal data
        time (np.ndarray): {1D-scalar} Recording time data, must be sorted and the same size as [sig]
        lbl (np.ndarray): {1D-scalar} Labelled timestamp of neuron spikes
        num (int): Number of samples to extract (default: 1000)
        size (int): Data point length of each sample (default: 150)

    Returns:
        list[dict[str, np.ndarray]]: Neuronal signal samples, structure as follows:
                                     list[{'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-int8)}]
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
    """ Slice and extract neuronal signal data for training models.
            This function only return NumPy-int8[0|1] (one-hot) type labels
            Samples form this function will always contain spikes

    Args:
        sig (np.ndarray): {1D-scalar} Single channel neuronal signal data
        time (np.ndarray): {1D-scalar} Recording time data, must be sorted and the same size as [sig]
        lbl (np.ndarray): {1D-scalar} Labelled timestamp of neuron spikes
        num (int): Number of samples to extract (default: 1000)
        size (int): Data point length of each sample (default: 150)

    Returns:
        list[dict[str, np.ndarray]]: Neuronal signal samples, structure as follows:
                                     list[{'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-int8)}]
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
        min_idx = s.item() - np.random.randint(size * 0.8)
        min_idx = 0 if min_idx < 0 else min_idx  # Verify
        max_idx = min_idx + size
        min_idx = max_len - size if max_idx > max_len else min_idx  # Verify
        # Extract data
        samp['sig'] = sig[min_idx:max_idx]
        samp['lbl'] = tmk[min_idx:max_idx]
        sig_samp.append(copy.deepcopy(samp))
    return sig_samp


def neuron_sig_mean(sig, time, lbl, size=50, pos=None, method='none', rng_srch=10):
    """ Extract neuronal signal for archiving.

    Args:
        sig (np.ndarray): {1D-scalar} Single channel neuronal signal data
        time (np.ndarray): {1D-scalar} Recording time data, must be sorted and the same size as [sig]
        lbl (np.ndarray): {1D-scalar} Labelled timestamp of neuron spikes
        size (int): Data point length of sample (default: 50)
        pos (int | None): Location of spike (default: None = center of sample)
        method (str): {'min' | 'max' | 'none'}: Local extremum search method. (default: 'none')
            - 'min':  detect minimum of signal within [-rng_srch, rng_srch]
            - 'max':  detect maximum of signal within [-rng_srch, rng_srch]
            - 'none': keep original label from [sig_data], ignoring [rng_srch]
        rng_srch (int): Range to search local extremum (default: 10)

    Returns:
        tuple[np.ndarray, int]: Averaged signal sample
            - mean: {1D-float64} Neuronal signal samples
            - pos: {int} Index of spike
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
    """ Get evaluation score of predicted signal, by computing mean absolute error (MAE).

    Args:
        data (dict): Denoised signal output from model, structure as below:
            - 'inp': (np.ndarray): Input signal
            - 'prd': (np.ndarray): Predicted signal
            - 'lbl': (np.ndarray): Signal label
        th (int | float): Quality threshold (default: 10)

    Returns:
        tuple[float, bool]: Mean absolute error (MAE) result of prediction
            - score: {float} Evaluation score
            - q: {bool} Quality check result
    """
    score = np.mean(np.abs(np.subtract(data['lbl'], data['prd']))).item()
    q = score < th
    return score, q


def nsd_asgnv(sig_data, rng_asgn, val_lst, method='min', rng_srch=10):
    """ Assign a value list around the signal.
            This function only accept NumPy-int8[0|1] (one-hot) type labels
            This function will return NumPy-float64 type labels
    Args:
        sig_data (dict[str, np.ndarray]): Labelled neuronal signal sample, structure as follows:
                                          {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-int8[0|1])}
        rng_asgn (int): Range to assign values
        val_lst (list | np.ndarray): List of value to be assigned
        method (str): {'min' | 'max' | 'none'}: Local extremum search method (default: 'min')
            - 'min':  detect minimum of signal within [-rng_srch, rng_srch]
            - 'max':  detect maximum of signal within [-rng_srch, rng_srch]
            - 'none': keep original label from [sig_data], ignoring [rng_srch]
        rng_srch (int): Range to search local extremum (default: 10)

    Returns:
        dict[str, np.ndarray]: Value assigned labelled neuronal signal sample, structure as follows:
                               {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-float64)}
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
