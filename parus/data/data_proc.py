import os
import warnings
import copy
import zlib
import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from parus.utils.base_func import arr_rand_samp

"""Function list:
spk_merge(spk_data): Merge and sort channel arranged spike data for data sampling. 
neuron_rnd_samp(sig, time, lbl, num=1000, size=150): Random slice and extract neuronal signal data for training models.
neuron_sig_samp(sig, time, lbl, num=1000, size=150): Slice and extract neuronal signal data for training models.
neuron_sig_mean(sig, time, lbl, size=50, pos=None, method='none', rng_srch=10): Extract neuronal signal for archiving.
nsd_read(nsd_file): Read neuronal signal labelled data file.
nsd_write(nsd_file, sig_data): Write neuronal signal labelled data file.
nsd_lbltn(sig_data, th=None, norm=True): Thresholding and/or normalizing label values in neuronal signal labelled data.
nsd_asgnv(sig_data, rng_srch, rng_asgn, val_lst, method='min'): Assign a value list around the signal.
nsd_plot(nsd_file): Plot neuronal signal labelled data.
arc_read(arc_file): Read archival neuronal signal data file.
arc_write(arc_file, arc_data): Write archival neuronal signal data file.
arc_plot(arc_file): Plot archival neuronal signal data.
"""


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
            This function only return NumPy-Int8 0-1 type labels.
            Samples form this function are simple random slices of raw signal.

    Args:
        sig (np.ndarray): {1D} Single channel neuronal signal data.
        time (np.ndarray): {1D} Recording time data, must be sorted and the same size as [sig].
        lbl (np.ndarray): {1D} Labelled timestamp of neuron spikes.
        num (int): Number of samples to extract. (default: 1000)
        size (int): Data point length of each sample. (default: 150)

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
            This function only return NumPy-Int8 0-1 type labels.
            Samples form this function will always containing spikes.

    Args:
        sig (np.ndarray): {1D} Single channel neuronal signal data.
        time (np.ndarray): {1D} Recording time data, must be sorted and the same size as [sig].
        lbl (np.ndarray): {1D} Labelled timestamp of neuron spikes.
        num (int): Number of samples to extract. (default: 1000)
        size (int): Data point length of each sample. (default: 150)

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
        sig (np.ndarray): {1D} Single channel neuronal signal data.
        time (np.ndarray): {1D} Recording time data, must be sorted and the same size as [sig].
        lbl (np.ndarray): {1D} Labelled timestamp of neuron spikes.
        size (int): Data point length of sample. (default: 50)
        pos (int or None): Location of spike. (default: None = center of sample)
        method (str): {'min' OR 'max' OR 'none'}: Local extremum search method. (default: 'none')
                                                  'min':  detect minimum of signal within [-rng_srch, rng_srch]
                                                  'max':  detect maximum of signal within [-rng_srch, rng_srch]
                                                  'none': keep original label from [sig_data], ignoring [rng_srch]
        rng_srch (int): Range to search local extremum. (default: 10)

    Returns:
        tuple[np.ndarray, int]: np.mean(sig_samp): {1D-FLOAT64} Neuronal signal samples.
                                pos: {INT} Index of spike.
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


def sim_sig_read(sim_sig_file):
    # Read-in file data
    with open(sim_sig_file, 'rb') as infile:
        comp = pkl.load(infile)
        sig = pkl.loads(zlib.decompress(comp))
    return sig


def sim_lbl_read(sim_lbl_file):
    # Read-in file data
    with open(sim_lbl_file, 'rb') as infile:
        comp = pkl.load(infile)
    lbl_dict = pkl.loads(zlib.decompress(comp))

    lbl_len = len(lbl_dict["noise"])
    lbl = np.zeros(lbl_len, dtype=np.float64)
    for sig in lbl_dict['signal']:
        lbl = np.add(lbl, sig)
    return lbl


def nsd_read(nsd_file):
    """ Read neuronal signal labelled data file.

    Args:
        nsd_file (str): File contained neuronal signal labelled data (*.nsd).

    Returns:
        dict[str, np.ndarray]: Labelled neuronal signal sample, structure as follows:
                               {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D)}
    """
    # Read-in file data
    with open(nsd_file, 'rb') as infile:
        comp = pkl.load(infile)
    sig_data = pkl.loads(zlib.decompress(comp))
    # Check imported data structure
    if (len(sig_data) == 2) and ('sig' in sig_data) and ('lbl' in sig_data):
        return sig_data
    else:
        warnings.warn("Illegal data in [%s], file not imported!" % nsd_file, Warning, stacklevel=2)
        return None


def nsd_write(nsd_file, sig_data):
    """ Write neuronal signal labelled data file.

    Args:
        nsd_file (str): Labelling file to write neuronal signal labelled data (*.nsd).
        sig_data (dict[str, np.ndarray]): Labelled neuronal signal sample, structure as follows:
                                          {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D)}

    Returns:
        bool: File creation status.
    """
    # Check data structure
    if (len(sig_data) == 2) and ('sig' in sig_data) and ('lbl' in sig_data):
        comp = zlib.compress(pkl.dumps(sig_data, protocol=None))
        with open(nsd_file, 'wb') as outfile:
            pkl.dump(comp, outfile, protocol=None)
        return True
    # Handel illegal data
    else:
        warnings.warn("Illegal data in [%s], file not created!" % nsd_file, Warning, stacklevel=2)
        return False


def nsd_lbltn(sig_data, th=None, norm=True):
    """ Thresholding and/or normalizing label values in neuronal signal labelled data.

    Args:
        sig_data (dict[str, np.ndarray]): Labelled neuronal signal sample, structure as follows:
                                          {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D)}
        th (int or float or None): Threshold value for the labels. (default: None)
        norm (bool): Flag to define if the label will be normalized. (default: True)

    Returns:
        dict[str, np.ndarray]: Data after thresholding and/or normalization, structure as follows:
                               {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D)}
    """
    sig_data_out = copy.deepcopy(sig_data)  # Make copy, avoid unexpected changes
    lbl_temp = sig_data_out['lbl']
    # Threshold label
    if (th is not None) and (th > 0):
        lbl_temp = np.where(lbl_temp < th, 0, lbl_temp)
    # Normalize label
    if norm:
        lbl_temp = np.divide(lbl_temp, np.amax(lbl_temp))
    # Assign and return
    sig_data_out['lbl'] = lbl_temp
    return sig_data_out


def nsd_asgnv(sig_data, rng_asgn, val_lst, method='min', rng_srch=10):
    """ Assign a value list around the signal.
            This function only accept NumPy-Int8 0-1 type labels.
            This function will return NumPy-Float64 type labels.

    Args:
        sig_data (dict[str, np.ndarray]): Labelled neuronal signal sample, structure as follows:
                                          {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-int8)}
        rng_asgn (int): Range to assign values.
        val_lst (tuple or list or np.ndarray): List of value to be assigned.
        method (str): {'min' OR 'max' OR 'none'}: Local extremum search method. (default: 'min')
                                                  'min':  detect minimum of signal within [-rng_srch, rng_srch]
                                                  'max':  detect maximum of signal within [-rng_srch, rng_srch]
                                                  'none': keep original label from [sig_data], ignoring [rng_srch]
        rng_srch (int): Range to search local extremum. (default: 10)

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


def nsd_plot(nsd_file, th=None):
    """ Plot neuronal signal labelled data.

    Args:
        nsd_file (str): File contained neuronal signal labelled data (*.nsd).
        th (int or float or None): Threshold value for labels.
    """
    # Import data
    sig_data = nsd_read(nsd_file)
    t = np.asarray(list(range(len(sig_data['sig']))))
    lbl = nsd_lbltn(sig_data, th, True)['lbl'] if np.amax(sig_data['lbl']) > 0 else 0
    # Get annotation labels
    mark_idx = (lbl != 0) & (lbl != 1)
    mark_t = t[mark_idx]
    mark_sig = sig_data['sig'][mark_idx]
    mark_c = sig_data['lbl'][mark_idx]
    peak_idx = lbl == 1
    peak_t = t[peak_idx]
    peak_sig = sig_data['sig'][peak_idx]
    # Setup plot
    plt.figure("Signal of [%s]" % os.path.split(nsd_file)[1].rstrip('.nsd'))
    plt.xlabel('Data Point')
    plt.ylabel('Amplitude')
    # Plotting
    plt.plot(t, sig_data['sig'], zorder=1)
    if len(mark_t) != 0:
        flk = plt.scatter(mark_t, mark_sig, marker='o', c=mark_c, cmap=cm.Reds, alpha=0.75, zorder=2)
        plt.colorbar(flk)
    if len(peak_t) != 0:
        plt.scatter(peak_t, peak_sig, marker='x', c='r', alpha=0.75, zorder=3)


def arc_read(arc_file):
    """ Read archival neuronal signal data file.

    Args:
        arc_file (str): File contained archival neuronal signal data (*.arc).

    Returns:
        dict: Archival neuronal signal sample, structure as follows:
              {'sig': [np.ndarray(1D-float64)] neuronal signal data,
               'pos': [int] index of spike location in 'sig',
               'rng': [tuple or None] 2 indices to define refined signal range,
               'freq': [int or float] recording frequency of 'sig',
               'cid': [dict] cell info {'typ': [str] cell type, 'spk': [str] spike type, 'note': [str]},
               'prb': [dict] recording probe {'mfr': [str], 'typ': [str], 'note': [str]},
               'sys': [dict] recording system {'mfr': [str], 'typ': [str], 'note': [str]},
               'date': [datetime.datetime] recording date and time information}
    """
    # Read-in file data
    with open(arc_file, 'rb') as infile:
        comp = pkl.load(infile)
    arc_data = pkl.loads(zlib.decompress(comp))
    # Check imported data structure
    if sorted(list(arc_data.keys())) == sorted(['sig', 'pos', 'rng', 'freq', 'cid', 'prb', 'sys', 'date']):
        return arc_data
    else:
        warnings.warn("Illegal data in [%s], file not imported!" % arc_file, Warning, stacklevel=2)
        return None


def arc_write(arc_file, arc_data):
    """ Write archival neuronal signal data file.

    Args:
        arc_file (str): File to write archival neuronal signal data (*.arc).
        arc_data (dict): Archival neuronal signal sample, structure as follows:
                         {'sig': [np.ndarray(1D-float64)] neuronal signal data,
                          'pos': [int] index of spike location in 'sig',
                          'rng': [tuple or None] 2 indices to define refined signal range,
                          'freq': [int or float] recording frequency of 'sig',
                          'cid': [dict] cell info {'typ': [str] cell type, 'spk': [str] spike type, 'note': [str]},
                          'prb': [dict] recording probe {'mfr': [str], 'typ': [str], 'note': [str]},
                          'sys': [dict] recording system {'mfr': [str], 'typ': [str], 'note': [str]},
                          'date': [datetime.datetime] recording date and time information}

    Returns:
        bool: File creation status.
    """
    # Check data structure
    if sorted(list(arc_data.keys())) == sorted(['sig', 'pos', 'rng', 'freq', 'cid', 'prb', 'sys', 'date']):
        comp = zlib.compress(pkl.dumps(arc_data, protocol=None))
        with open(arc_file, 'wb') as outfile:
            pkl.dump(comp, outfile, protocol=None)
        return True
    # Handel illegal data
    else:
        warnings.warn("Illegal data in [%s], file not created!" % arc_file, Warning, stacklevel=2)
        return False


def arc_plot(arc_file):
    """ Plot archival neuronal signal data.

    Args:
        arc_file (str): File contained archival neuronal signal data (*.arc).
    """
    # Import data
    arc_data = arc_read(arc_file)
    t = np.asarray(list(range(len(arc_data['sig']))))
    # Get spike peak labels
    peak_t = t[arc_data['pos']]
    peak_sig = arc_data['sig'][arc_data['pos']]
    # Get signal range
    sig_rng = np.asarray(arc_data['rng']) if arc_data['rng'] is not None else None
    # Setup plot
    plt.figure("Archival Signal of [%s]" % os.path.split(arc_file)[1].rstrip('.arc'))
    plt.xlabel('Data Point')
    plt.ylabel('Amplitude')
    # Plotting
    plt.plot(t, arc_data['sig'], zorder=1)
    plt.scatter(peak_t, peak_sig, marker='x', c='r', alpha=0.75, zorder=3)
    if sig_rng is not None:
        plt.axvline(sig_rng[0], c='gray', ls='-.', alpha=0.75, zorder=2)
        plt.axvline(sig_rng[1], c='gray', ls='-.', alpha=0.75, zorder=2)
