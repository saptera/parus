# Basic utilities function module

import sys
import os

__package__ = 'parus.util'
__name__ = 'parus.util.base'

__all__ = ['make_outdir', 'altmk_outdirs', 'search_files', 'prog_print']
"""
Function list:
  make_outdir(out_dir, err_msg="Invalid output directory!"): Recursive create an output leaf directory for data.
  altmk_outdirs(out_dir, alt_dir, err_msg="I..."): Recursive create an output leaf directory with alternative directory.
  search_files(base_dir, fpre=str(), fsuf=str()):  Find all files meets the search conditions.
  prog_print(iteration, total, prefix=str(), suffix=str()): Create a terminal progress bar for a loop.
"""


def make_outdir(out_dir, err_msg="Invalid output directory!"):
    """ Recursive create an output leaf directory for data.

    Args:
        out_dir (str): Output directory
        err_msg (str): Error message when creation error happens

    Returns:
        str: Created output directory
    """
    if not os.path.isdir(out_dir):  # Check if folder exists
        try:
            os.makedirs(out_dir)
        except OSError:
            print(err_msg)
            exit(-1)
    return out_dir


def altmk_outdirs(out_dir, alt_dir, err_msg="Invalid output directory!"):
    """ Recursive create an output leaf directory with alternative directory.

    Args:
        out_dir (str): Output directory
        alt_dir (str): Alternative directory when [out_dir] is missing
        err_msg (str): Error message when creation error happens

    Returns:
        str: Created output directory
    """
    if (out_dir == str()) or (out_dir is None):
        out_path = alt_dir
        if not os.path.isdir(out_path):  # Check again if folder exists
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
        base_dir (str): The base folder path to search files
        fpre (str): Prefix of files to be found, use empty string to find all (default: str())
        fsuf (str): Suffix of files to be found, use empty string to find all (default: str())

    Returns:
        tuple[list[list[str]], list[str]]: File absolute path and their leaf folders, the order of elements are matched

            - flst (list[list[str]]): A list of lists (leaf-folders) with absolute path of files meets search conditions
            - dlst (list[str]): A list of all leaf folder names contains files found

    """
    # Get files and their leaf-folder path
    flst = []  # INIT VAR
    dlst = []  # INIT VAR
    for path, _, file in os.walk(base_dir):
        tmp_lst = []  # RESET VAR
        for filename in [f for f in file if f.startswith(fpre) and f.endswith(fsuf)]:
            tmp_lst.append(os.path.join(path, filename))
        if tmp_lst:
            flst.append(tmp_lst)  # Get files
            dlst.append(path)  # Get leaf-folder
    # Trim the common prefix of leaf-folders
    base = os.path.commonpath(dlst)
    for i in range(len(dlst)):
        dlst[i] = os.path.relpath(dlst[i], base)
    return flst, dlst


def prog_print(iteration, total, prefix=str(), suffix=str()):
    """Create a terminal progress bar for a loop.

    Args:
        iteration (int): Current iteration (0-based)
        total (int): Total iterations
        prefix (str): Prefix string of progress bar (default: str())
        suffix (str): Suffix string of progress bar (default: str())
    """
    # Basic settings
    decimals = 2  # Decimals in percent completed
    length = 50  # Character length of bar
    fill = '>'  # Bar fill character
    iteration += 1  # Convert to 1-based count
    # Printing operation
    if iteration == total:
        # Print at 100%
        print('\r%s |%s| %s%% %s' % (prefix, fill * length, ("{0:." + str(decimals) + "f}").format(100), suffix))
    else:
        # Create percentage bar
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / total))
        filled = int(length * iteration // total)
        bar = fill * filled + '-' * (length - filled)
        # Print session
        sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
        sys.stdout.flush()
