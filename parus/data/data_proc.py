import os
import warnings
import copy
import zlib
import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
from parus.utils.base_func import arr_rand_samp
from parus.data.file_io import pklz_read

"""Function list:
spk_merge(spk_data): Merge and sort channel arranged spike data for data sampling. 
neuron_rnd_samp(sig, time, lbl, num=1000, size=150): Random slice and extract neuronal signal data for training models.
neuron_sig_samp(sig, time, lbl, num=1000, size=150): Slice and extract neuronal signal data for training models.
neuron_sig_mean(sig, time, lbl, size=50, pos=None, method='none', rng_srch=10): Extract neuronal signal for archiving.
trn_plot(file, overlay=True): Plot model training related files.
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


def trn_plot(file, overlay=True):
    """ Plot model training related files.

    Args:
        file (str): File containing data generated for training or predicted by model (*.sim, *.tst).
        overlay (bool): Set [True] to plot data in one plot, [False] to plot in subplots. (default: True)

    Returns:
    """
    # Read file
    file_ext = os.path.splitext(file)[1].lstrip('.')
    data = pklz_read(file)
    # Plot type of simulated data
    if file_ext == 'sim':
        plt.figure("Plot of simulated data [%s]" % os.path.split(file)[1].lstrip('.sim'))
        if overlay:
            plt.xlabel('Data Point')
            plt.ylabel('Amplitude')
            plt.plot(data['sig'], c='r', alpha=0.5, label="Signal")
            plt.plot(data['lbl'], c='b', alpha=0.5, label="Label")
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2, mode="expand", borderaxespad=0.)
        else:
            # Plot signal
            plt.subplot(2, 1, 1)
            plt.title("Signal")
            plt.ylabel('Amplitude')
            plt.plot(data['sig'], c='r')
            # Plot label
            plt.subplot(2, 1, 2)
            plt.title("Label")
            plt.xlabel('Data Point')
            plt.ylabel('Amplitude')
            plt.plot(data['lbl'], c='b')
    # Plot type of testing data
    elif file_ext == 'tst':
        plt.figure("Plot of testing data [%s]" % os.path.split(file)[1].lstrip('.tst'))
        if overlay:
            plt.xlabel('Data Point')
            plt.ylabel('Amplitude')
            plt.plot(data['sig'], c='r', alpha=0.5, label="Signal")
            plt.plot(data['lbl'], c='b', alpha=0.5, label="Label")
            plt.plot(data['prd'], c='g', alpha=0.5, label="Prediction")
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=3, mode="expand", borderaxespad=0.)
        else:
            # Plot signal
            plt.subplot(3, 1, 1)
            plt.title("Signal")
            plt.ylabel('Amplitude')
            plt.plot(data['sig'], c='b')
            # Plot label
            plt.subplot(3, 1, 2)
            plt.title("Label")
            plt.ylabel('Amplitude')
            plt.plot(data['lbl'], c='r')
            # plot prediction
            plt.subplot(3, 1, 2)
            plt.title("Prediction")
            plt.xlabel('Data Point')
            plt.ylabel('Amplitude')
            plt.plot(data['prd'], c='g')
    else:
        warnings.warn("Invalid extension [%s] for this function, plot aborted!" % file_ext, Warning, stacklevel=2)
        return
