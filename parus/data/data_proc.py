import copy
import zlib
import pickle as pkl
import numpy as np
from parus.utils.base_func import arr_rand_samp


def neuron_sig_samp(sig, time, lbl, num=1000, size=150):
    """ Slice and extract neuronal signal data for training models.

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
    for a in lbl:
        tmk[np.searchsorted(time, a, side='left')] = 1
    # Sampling with defined parameters
    lsp = arr_rand_samp(lbl, num)
    sig_samp = []  # INIT VAR
    for s in lsp:
        samp = {'sig': None, 'lbl': None}  # INIT VAR
        # Get random index range
        min_idx = np.searchsorted(time, s, side='left').item() - np.random.randint(size * 0.8)
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
        nsd_file (str): File contained neuronal signal labelled data.

    Returns:
        dict[str, np.ndarray]: Labelled neuronal signal sample, structure as follows:
                               {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-int8)}
    """
    with open(nsd_file, 'rb') as infile:
        comp = pkl.load(infile)
    sig_data = pkl.loads(zlib.decompress(comp))
    return sig_data


def nsd_write(nsd_file, sig_data):
    """ Write neuronal signal labelled data file.

    Args:
        nsd_file (str): Labelling file to write HeatMap labels (*.pkl).
        sig_data (dict[str, np.ndarray]): Labelled neuronal signal sample, structure as follows:
                                          {'sig': np.ndarray(1D-float64), 'lbl': np.ndarray(1D-int8)}

    Returns:
        bool: File creation status.
    """
    if (len(sig_data) == 2) and ('sig' in sig_data) and ('lbl' in sig_data):
        comp = zlib.compress(pkl.dumps(sig_data, protocol=None))
        with open(nsd_file, 'wb') as outfile:
            pkl.dump(comp, outfile, protocol=None)
        return True
    else:
        print('Illegal data, file not created!')
        return False
