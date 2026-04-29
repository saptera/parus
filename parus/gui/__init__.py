# -*- coding: utf-8 -*-

"""PARUS GUI package

Qt-based desktop applications and shared widget helpers for the PARUS data, training, and inspection workflows.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from PySide6 import QtCore, QtWidgets
mpl.use('QtAgg')

__package__ = 'parus.gui'
__name__ = 'parus.gui'

__all__ = ['cs_dark', 'set_color_scheme']
"""
Public function list:

- cs_dark()                 : Get the current dark colour scheme flag
- set_color_scheme(app, mode) : Set the global application colour scheme
"""


# Settings for high resolution monitors
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# System dark mode settings
__cs_dark = False  # Dark mode flag
__cs_default = None  # Default colour scheme


def cs_dark():
    """Return the current dark colour scheme flag.

    Returns:
        bool: :data:`True` when the GUI is currently in dark mode, :data:`False` otherwise
    """
    global __cs_dark
    return __cs_dark


def set_color_scheme(app, mode='auto'):
    """Set the global application colour scheme and synchronise the Matplotlib style.

    Switches both the Qt application colour scheme and the active Matplotlib style so plots embedded in the
    GUI render with matching backgrounds. When ``mode`` is ``'auto'``, the system colour scheme captured at
    first call is reused on every subsequent call.

    Args:
        app (QtCore.QCoreApplication | QtWidgets.QApplication): Qt application to configure
        mode (str): Colour scheme mode; one of ``{'light', 'dark', 'auto'}`` (default: ``'auto'``)
    """
    global __cs_dark, __cs_default
    app.setStyle('fusion')
    __cs_default = app.styleHints().colorScheme() if __cs_default is None else __cs_default

    if mode == 'light':
        __cs_dark = False
        app.styleHints().setColorScheme(QtCore.Qt.ColorScheme.Light)
        plt.style.use('default')
    elif mode == 'dark':
        __cs_dark = True
        app.styleHints().setColorScheme(QtCore.Qt.ColorScheme.Dark)
        plt.style.use('dark_background')
    else:  # Fallback for all other modes
        app.styleHints().setColorScheme(__cs_default)
        if __cs_default == QtCore.Qt.ColorScheme.Dark:
            __cs_dark = True
            plt.style.use('dark_background')
        else:  # Fallback for unknown scheme
            __cs_dark = False
            plt.style.use('default')
