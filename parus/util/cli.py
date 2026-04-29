# -*- coding: utf-8 -*-

"""Command line interface helper module

Interactive prompt utilities for collecting validated user input from the terminal.
"""

import os
from pathlib import Path

__package__ = 'parus.util'
__name__ = 'parus.util.cli'

__all__ = ['yn_query', 'cli_path_in', 'cli_file_in', 'cli_int_in', 'cli_float_in', 'cli_list_sel', 'cli_outdir']
"""
Public function list:

- yn_query(query, default)                           : Prompt the user with a yes/no question
- cli_path_in(msg_ppt, msg_err)                      : Prompt the user for an existing directory path
- cli_file_in(msg_ppt, msg_err)                      : Prompt the user for an existing file path
- cli_int_in(low, high, msg_ppt, msg_err, msg_rng)   : Prompt the user for an integer within an inclusive range
- cli_float_in(low, high, msg_ppt, msg_err, msg_rng) : Prompt the user for a float within an inclusive range
- cli_list_sel(list_in, msg_ppt, msg_err)            : Prompt the user to choose an element from a list
- cli_outdir(msg_ppt, msg_err)                       : Prompt the user for an output directory, creating it if missing
"""


def yn_query(query, default=None):
    """Prompt the user with a yes/no question on the command line.

    Args:
        query (str): Question text shown to the user
        default (bool | None): Value returned when the user submits an empty response; pass :data:`None` to
            require an explicit answer (default: ``None``)

    Returns:
        bool: ``True`` for yes, ``False`` for no
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
    """Prompt the user for an existing directory path on the command line.

    Re-prompts until the entered path is a valid directory.

    Args:
        msg_ppt (str | None): Initial prompt message; pass :data:`None` to use the built-in default
            ``"Please define a path: "`` (default: ``None``)
        msg_err (str | None): Re-prompt message used when input is not a valid directory; pass :data:`None`
            to use the built-in default ``"    Invalid path, please try again: "`` (default: ``None``)

    Returns:
        str: Validated directory path entered by the user
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
    """Prompt the user for an existing file path on the command line.

    Re-prompts until the entered path is a valid file.

    Args:
        msg_ppt (str | None): Initial prompt message; pass :data:`None` to use the built-in default
            ``"Please define a file path: "`` (default: ``None``)
        msg_err (str | None): Re-prompt message used when input is not a valid file; pass :data:`None` to
            use the built-in default ``"    Invalid file path, please try again: "`` (default: ``None``)

    Returns:
        str: Validated file path entered by the user
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
    """Prompt the user for an integer within an optional inclusive range.

    Re-prompts until the input parses as an integer and lies within ``[low, high]`` when bounds are provided.

    Args:
        low (int | None): Inclusive lower bound; pass :data:`None` to disable the lower-bound check
            (default: ``None``)
        high (int | None): Inclusive upper bound; pass :data:`None` to disable the upper-bound check
            (default: ``None``)
        msg_ppt (str | None): Initial prompt message; pass :data:`None` to use the built-in default
            ``"Please define an integer: "`` (default: ``None``)
        msg_err (str | None): Re-prompt message used when input does not parse as an integer; pass
            :data:`None` to use the built-in default ``"    Invalid input, please try again: "`` (default: ``None``)
        msg_rng (str | None): Re-prompt message used when input is out of range; pass :data:`None` to use a
            bound-aware message generated from ``low`` and ``high`` (default: ``None``)

    Returns:
        int: Validated integer entered by the user
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
    """Prompt the user for a floating-point number within an optional inclusive range.

    Re-prompts until the input parses as a float and lies within ``[low, high]`` when bounds are provided.

    Args:
        low (float | None): Inclusive lower bound; pass :data:`None` to disable the lower-bound check
            (default: ``None``)
        high (float | None): Inclusive upper bound; pass :data:`None` to disable the upper-bound check
            (default: ``None``)
        msg_ppt (str | None): Initial prompt message; pass :data:`None` to use the built-in default
            ``"Please define an float number: "`` (default: ``None``)
        msg_err (str | None): Re-prompt message used when input does not parse as a float; pass :data:`None`
            to use the built-in default ``"    Invalid input, please try again: "`` (default: ``None``)
        msg_rng (str | None): Re-prompt message used when input is out of range; pass :data:`None` to use a
            bound-aware message generated from ``low`` and ``high`` (default: ``None``)

    Returns:
        float: Validated floating-point number entered by the user
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
    """Prompt the user to choose an element from a string list on the command line.

    Accepts either the literal element string or its zero-based index in ``list_in``. Re-prompts until a
    valid selection is made.

    Args:
        list_in (list[str]): Candidate elements to select from
        msg_ppt (str | None): Initial prompt message; pass :data:`None` to use the built-in default
            ``"Please select from following - "`` (default: ``None``)
        msg_err (str | None): Re-prompt message used when input is invalid; pass :data:`None` to use the
            built-in default ``"    Invalid selection, please try again: "`` (default: ``None``)

    Returns:
        str: Selected element from ``list_in``
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
    """Prompt the user for an output directory, creating it on disk when missing.

    If the requested directory already exists, the user is asked whether to reuse it (overwrite). On a
    declined overwrite or a creation failure, the prompt is repeated.

    Args:
        msg_ppt (str | None): Initial prompt message; pass :data:`None` to use the built-in default
            ``"Please define a path: "`` (default: ``None``)
        msg_err (str | None): Re-prompt message used when directory creation fails; pass :data:`None` to use
            the built-in default ``"    Invalid path, please try again: "`` (default: ``None``)

    Returns:
        str: Validated output directory path
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
