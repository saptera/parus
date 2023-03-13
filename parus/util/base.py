# Basic utilities functions

import sys
import os
import numpy as np
from scipy.stats import norm, laplace

"""Function list:
x64_sys(): Check if current system architecture is 64-bit based.
make_outdir(out_dir, err_msg): Recursive create an output leaf directory for data.
altmk_outdirs(out_dir, alt_dir, err_msg): Recursive create an output leaf directory with alternative directory.
search_files(base_dir, fpre, fsuf):  Find all files meets the search conditions.
prog_print(iteration, total, prefix, suffix): Create a terminal progress bar for a loop.
arr_rand_samp(arr, n_samp): Random sampling of unique samples from a NumPy array.
norm_lst_gen(peak, side, level=2): Generate a list obeying normal distribution.
laplace_lst_gen(peak, side, scale=1): Generate a list obeying laplace distribution.
"""


def x64_sys():
    """ Check if current system architecture is 64-bit based.
    Args:

    Returns:
        bool: True (if system is x64); False (if system is x32)
    """
    return sys.maxsize > 4294967296    # Max size for 32-bit system: 2**32 = 4294967296


def make_outdir(out_dir, err_msg='Invalid output directory!'):
    """ Recursive create an output leaf directory for data.

    Args:
        out_dir (str): Output directory.
        err_msg (str): Error message when creation error happens.

    Returns:
        str: Created output directory.
    """
    if not os.path.isdir(out_dir):    # Check if folder exists
        try:
            os.makedirs(out_dir)
        except OSError:
            print(err_msg)
            exit(-1)
    return out_dir


def altmk_outdirs(out_dir, alt_dir, err_msg='Invalid output directory!'):
    """ Recursive create an output leaf directory with alternative directory.

    Args:
        out_dir (str): Output directory.
        alt_dir (str): Alternative directory when [out_dir] is missing.
        err_msg (str): Error message when creation error happens.

    Returns:
        str: Created output directory.
    """
    if (out_dir == str()) or (out_dir is None):
        out_path = alt_dir
        if not os.path.isdir(out_path):    # Check again if folder exists
            os.makedirs(out_path)
    elif not os.path.isdir(out_dir):
        try:
            os.makedirs(out_dir)
        except OSError:
            print(err_msg)
            exit(-1)
    return out_dir


def search_files(base_dir, fpre=str(), fsuf=str()):
    """ Find all files meets the search conditions.

    Args:
        base_dir (str): The base folder path to search files.
        fpre (str): Prefix of files to be found, use empty string to find all. (default: str())
        fsuf (str): Suffix of files to be found, use empty string to find all. (default: str())

    Returns:
        tuple[list[list[str]], list[str]]:
            flst (list[list[str]]): A list of lists(leaf-folders) with absolute path of files meets search conditions.
            dlst (list[str]): A list of all leaf folder names contains files found.
            --  [flst] and [dlst] have same length, the order of elements are matched.
    """
    # Get files and their leaf-folder path
    flst = []    # INIT VAR
    dlst = []    # INIT VAR
    for path, _, file in os.walk(base_dir):
        tmp_lst = []    # RESET VAR
        for filename in [f for f in file if f.startswith(fpre) and f.endswith(fsuf)]:
            tmp_lst.append(os.path.join(path, filename))
        if tmp_lst:
            flst.append(tmp_lst)    # Get files
            dlst.append(path)    # Get leaf-folder
    # Trim the common prefix of leaf-folders
    base = os.path.commonpath(dlst)
    for i in range(len(dlst)):
        dlst[i] = os.path.relpath(dlst[i], base)
    return flst, dlst


def prog_print(iteration, total, prefix=str(), suffix=str()):
    """Create a terminal progress bar for a loop.

    Args:
        iteration (int): Current iteration.
        total (int): Total iterations.
        prefix (str): Prefix string of progress bar. (default: str())
        suffix (str): Suffix string of progress bar. (default: str())

    Returns:
    """
    # Basic settings
    decimals = 2  # Decimals in percent completed
    length = 50  # Character length of bar
    fill = '>'  # Bar fill character
    # Create percentage bar
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / total))
    filled = int(length * iteration // total)
    bar = fill * filled + '-' * (length - filled)
    # Print session
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    if iteration == total:  # Print a new line at 100%
        print('')


def arr_rand_samp(arr, n_samp):
    """ Random sampling of unique samples from a NumPy array.

    Args:
        arr (np.ndarray): Input array.
        n_samp (int): Number of samples.

    Returns:
        np.ndarray: {1D} Samples from original array.
    """
    mask = np.array([True]*n_samp + [False]*(arr.size - n_samp))
    np.random.shuffle(mask)
    mask = np.reshape(mask, arr.shape)
    return arr[mask]


def norm_lst_gen(peak, side, level=2):
    """ Generate a list obeying normal distribution.

    Args:
        peak (float): Peak (centre) value of output.
        side (int): Number of samples around the peak.
        level (int): {1 OR 2 OR 3}: Level of three-sigma rule within the [size]. (default: 2)
                     1: [size] = 1-sigma, output list covering P(-[size], size) = 68.27%
                     2: [size] = 2-sigma, output list covering P(-[size], size) = 95.45%
                     3: [size] = 3-sigma, output list covering P(-[size], size) = 99.73%

    Returns:
        list[float]: Output list of generated value.
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
        peak (float): Peak (centre) value of output.
        side (int): Number of samples around the peak.
        scale (int or float): : Diversity of generated samples. (default: 1)

    Returns:
        list[float]: Output list of generated value.
    """
    ld = laplace(loc=0, scale=scale)  # Laplace distribution with scale
    fac = peak / ld.pdf(0)  # Peak stretch factor
    val = []  # INIT VAR
    for i in range(-side, side + 1, 1):
        val.append(ld.pdf(i).item() * fac)
    return val
