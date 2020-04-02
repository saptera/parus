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
neuron_sig_samp(sig, time, lbl, num=1000, size=150): Slice and extract neuronal signal data for training models.
nsd_read(nsd_file): Read neuronal signal labelled data file.
nsd_write(nsd_file, sig_data): Write neuronal signal labelled data file.
nsd_lbltn(sig_data, th=None, norm=True): Thresholding and/or normalizing label values in neuronal signal labelled data.
nsd_asgnv(sig_data, rng_srch, rng_asgn, val_lst, method='min'): Assign a value list around the signal.
nsd_plot(nsd_file): Plot neuronal signal labelled data.
"""


def neuron_sig_samp(sig, time, lbl, num=1000, size=150):
    """ Slice and extract neuronal signal data for training models.
            This function only return NumPy-Int8 0-1 type labels.

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
    # Sampling with defined parameters
    lsp = arr_rand_samp(mrk_idx, num)
    sig_samp = []  # INIT VAR
    for s in lsp:
        samp = {'sig': None, 'lbl': None}  # INIT/RESET VAR
        # Get random index range
        min_idx = s.item() - np.random.randint(size * 0.8)
        max_idx = min_idx + size
        idx = list(range(min_idx, max_idx))
        # Extract data
        samp['sig'] = sig[idx]
        samp['lbl'] = tmk[idx]
        sig_samp.append(copy.deepcopy(samp))
    return sig_samp


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
    lbl = nsd_lbltn(sig_data, th, True)['lbl']
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
        plt.scatter(mark_t, mark_sig, marker='o', c=mark_c, cmap=cm.Reds, alpha=0.75, zorder=2)
    if len(peak_t) != 0:
        plt.scatter(peak_t, peak_sig, marker='x', c='r', alpha=0.75, zorder=3)
