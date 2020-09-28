import os
from pathlib import Path

"""Function list:
yn_query(query, default=None): Simple yes/no query.
cli_path_in(msg_ppt=None, msg_err=None): Get a command line input of path.
cli_file_in(msg_ppt=None, msg_err=None): Get a command line input of file.
cli_int_in(low=None, high=None, msg_ppt=None, msg_err=None, msg_rng=None): Get a command line input of an integer.
cli_float_in(low=None, high=None, msg_ppt=None, msg_err=None, msg_rng=None): Get a command line input of a float.
cli_list_sel(list_in, msg_ppt=None, msg_err=None): Get a command line selection of string list.
cli_outdir(msg_ppt=None, msg_err=None): Get a command line input of an output path.
"""


def yn_query(query, default=None):
    """ Simple yes/no query.

    Args:
        query (str): Query message.
        default (bool or None): Default output with [ENTER], set to None to disable default. (default: None)

    Returns:
        bool: User response.
    """
    if default is True:
        prompt = " [Y/n]: "
    elif default is False:
        prompt = " [y/N]: "
    else:
        prompt = " [y/n]: "
    choice = input(query + prompt).lower()
    while True:
        if (choice == 'y') or (choice == 'yes'):
            return True
        elif (choice == 'n') or (choice == 'no'):
            return False
        elif (choice == str()) and (default is not None):
            return default
        else:
            choice = input("    Please respond with 'yes' or 'no' (or 'y' or 'n'): ").lower()


def cli_path_in(msg_ppt=None, msg_err=None):
    """ Get a command line input of path.

    Args:
        msg_ppt (str or None): Prompt message for input.
        msg_err (str or None): Error message for invalid input.

    Returns:
        str: Inputted path.
    """
    msg_ppt = "Please define a path: " if msg_ppt is None else msg_ppt
    msg_err = "    Invalid path, please try again: " if msg_err is None else msg_err
    var_in = Path(input(msg_ppt))
    while True:
        if os.path.isdir(var_in):
            return str(var_in)
        else:
            var_in = Path(input(msg_err))


def cli_file_in(msg_ppt=None, msg_err=None):
    """ Get a command line input of file.

    Args:
        msg_ppt (str or None): Prompt message for input.
        msg_err (str or None): Error message for invalid input.

    Returns:
        str: Inputted file path.
    """
    msg_ppt = "Please define a file path: " if msg_ppt is None else msg_ppt
    msg_err = "    Invalid file path, please try again: " if msg_err is None else msg_err
    var_in = Path(input(msg_ppt))
    while True:
        if os.path.isfile(var_in):
            return str(var_in)
        else:
            var_in = Path(input(msg_err))


def cli_int_in(low=None, high=None, msg_ppt=None, msg_err=None, msg_rng=None):
    """ Get a command line input of an integer.

    Args:
        low (int or None): Minimum value for input.
        high (int or None): Maximum value for input.
        msg_ppt (str or None): Prompt message for input.
        msg_err (str or None): Error message for invalid input.
        msg_rng (str or None): Error message for invalid range.

    Returns:
        int: Inputted integer.
    """
    msg_ppt = "Please define an integer: " if msg_ppt is None else msg_ppt
    msg_err = "    Invalid input, please try again: " if msg_err is None else msg_err
    if msg_rng is None:
        if low is None:
            if high is None:
                pass
            else:
                msg_rng = "    Input must be less or equal to %d, please try again: " % high
        else:
            if high is None:
                msg_rng = "    Input must be greater or equal to %d, please try again: " % low
            else:
                msg_rng = "    Input must be between [%d, %d], please try again: " % (low, high)
    var_in = input(msg_ppt)
    while True:
        try:
            int(var_in)
        except ValueError:
            var_in = input(msg_err)
            continue
        if low is None:
            if high is None:
                return int(var_in)
            elif int(var_in) > high:
                var_in = input(msg_rng)
            else:
                return int(var_in)
        else:
            if high is None:
                if int(var_in) < low:
                    var_in = input(msg_rng)
                else:
                    return int(var_in)
            else:
                if (int(var_in) < low) or (int(var_in) > high):
                    var_in = input(msg_rng)
                else:
                    return int(var_in)


def cli_float_in(low=None, high=None, msg_ppt=None, msg_err=None, msg_rng=None):
    """ Get a command line input of a float.

    Args:
        low (float or None): Minimum value for input.
        high (float or None): Maximum value for input.
        msg_ppt (str or None): Prompt message for input.
        msg_err (str or None): Error message for invalid input.
        msg_rng (str or None): Error message for invalid range.

    Returns:
        float: Inputted float.
    """
    msg_ppt = "Please define an float number: " if msg_ppt is None else msg_ppt
    msg_err = "    Invalid input, please try again: " if msg_err is None else msg_err
    if msg_rng is None:
        if low is None:
            if high is None:
                pass
            else:
                msg_rng = "    Input must be less or equal to %f, please try again: " % high
        else:
            if high is None:
                msg_rng = "    Input must be greater or equal to %f, please try again: " % low
            else:
                msg_rng = "    Input must be between [%f, %f], please try again: " % (low, high)
    var_in = input(msg_ppt)
    while True:
        try:
            float(var_in)
        except ValueError:
            var_in = input(msg_err)
            continue
        if low is None:
            if high is None:
                return float(var_in)
            elif float(var_in) > high:
                var_in = input(msg_rng)
            else:
                return float(var_in)
        else:
            if high is None:
                if float(var_in) < low:
                    var_in = input(msg_rng)
                else:
                    return float(var_in)
            else:
                if (float(var_in) < low) or (float(var_in) > high):
                    var_in = input(msg_rng)
                else:
                    return float(var_in)


def cli_list_sel(list_in, msg_ppt=None, msg_err=None):
    """ Get a command line selection of string list.

    Args:
        list_in (list[str]): List with element to select from.
        msg_ppt (str or None): Prompt message for input.
        msg_err (str or None): Error message for invalid input.

    Returns:
        str: Inputted path.
    """
    msg_ppt = "Please select from following - " if msg_ppt is None else msg_ppt
    msg_err = "    Invalid selection, please try again: " if msg_err is None else msg_err
    var_in = input(msg_ppt + str(list_in) + ": ")
    while True:
        # Direct selection
        if var_in in list_in:
            return var_in
        # Index select
        else:
            try:
                idx = int(var_in)
            except ValueError:
                var_in = input(msg_err)
            else:
                if idx < len(list_in):
                    return list_in[idx]
                else:
                    var_in = input(msg_err)


def cli_outdir(msg_ppt=None, msg_err=None):
    """ Get a command line input of an output path.

    Args:
        msg_ppt (str or None): Prompt message for input.
        msg_err (str or None): Error message for invalid input.

    Returns:
        str: Inputted path.
    """
    msg_ppt = "Please define a path: " if msg_ppt is None else msg_ppt
    msg_err = "    Invalid path, please try again: " if msg_err is None else msg_err
    var_in = Path(input(msg_ppt))
    while True:
        if os.path.isdir(var_in):
            flag = yn_query("    Path [%s] already exist, overwrite?" % var_in, default=True)
            if flag:
                return str(var_in)
            else:
                var_in = Path(input("    Please redefine: "))
        else:
            try:
                os.makedirs(var_in)
                return str(var_in)
            except OSError:
                var_in = Path(input(msg_err))
                continue
