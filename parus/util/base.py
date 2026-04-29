# -*- coding: utf-8 -*-

"""Basic utility function module

Fundamental helpers shared across the codebase.
"""

import sys
import os

__package__ = 'parus.util'
__name__ = 'parus.util.base'

__all__ = ['make_outdir', 'altmk_outdirs', 'search_files', 'prog_print']
"""
Public function list:

- make_outdir(out_dir, err_msg)                : Recursively create an output directory if it does not already exist
- altmk_outdirs(out_dir, alt_dir, err_msg)     : Recursively create an output directory, falling back to an alternative
- search_files(base_dir, fpre, fsuf)           : Find all files under defined path matching the prefix/suffix conditions
- prog_print(iteration, total, prefix, suffix) : Render an in-place terminal progress bar for a loop
"""


def make_outdir(out_dir, err_msg="Invalid output directory!"):
    """Recursively create an output directory if it does not already exist.

    Args:
        out_dir (str): Target output directory path
        err_msg (str): Message printed when directory creation fails (default: ``"Invalid output directory!"``)

    Returns:
        str: Path of the (newly created or pre-existing) output directory

    Raises:
        SystemExit: Terminates the process with code ``-1`` if :class:`OSError` is raised during creation
    """
    if not os.path.isdir(out_dir):  # Check if folder exists
        try:
            os.makedirs(out_dir)
        except OSError:
            print(err_msg)
            exit(-1)
    return out_dir


def altmk_outdirs(out_dir, alt_dir, err_msg="Invalid output directory!"):
    """Recursively create an output directory, falling back to an alternative when none is provided.

    When ``out_dir`` is empty or :data:`None`, ``alt_dir`` is created on disk if missing. Otherwise, the function
    behaves like :func:`make_outdir` for ``out_dir``.

    Args:
        out_dir (str | None): Primary output directory path; an empty string or :data:`None` triggers the
            fallback to ``alt_dir``
        alt_dir (str): Fallback directory used when ``out_dir`` is missing
        err_msg (str): Message printed when directory creation fails (default: ``"Invalid output directory!"``)

    Returns:
        str: The original ``out_dir`` value (unchanged)

    Raises:
        SystemExit: Terminates the process with code ``-1`` if :class:`OSError` is raised during creation
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
    """Find all files under defined path matching the given prefix and suffix conditions.

    The search walks ``base_dir`` recursively and groups matching files by the leaf folder containing them.

    Args:
        base_dir (str): Root directory to search
        fpre (str): Required filename prefix; an empty string disables prefix filtering (default: ``""``)
        fsuf (str): Required filename suffix; an empty string disables suffix filtering (default: ``""``)

    Returns:
        tuple[list[list[str]], list[str]]: Two parallel lists with matching ordering

            - flst (list[list[str]]): For each leaf folder, the absolute paths of files that match
            - dlst (list[str]): Leaf folder names relative to the longest common prefix of all matched folders
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
    """Render an in-place terminal progress bar for a loop.

    Prints a fixed-width bar to ``sys.stdout`` and overwrites the current line on each call. When ``iteration``
    reaches ``total``, a final newline is emitted to release the line.

    Args:
        iteration (int): Current iteration counter (0-based)
        total (int): Total number of iterations expected
        prefix (str): Text printed before the bar (default: ``""``)
        suffix (str): Text printed after the bar (default: ``""``)
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
