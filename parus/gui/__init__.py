# PARUS GUI package

import matplotlib as mpl
import matplotlib.pyplot as plt
from PySide6 import QtCore, QtWidgets
mpl.use('QtAgg')

__package__ = 'parus.gui'
__name__ = 'parus.gui'

__all__ = ['cs_dark', 'set_color_scheme']
"""
Function list:
  cs_dark(): Get current dark color scheme flag.
  set_color_scheme(app, mode='auto'): Set global application color scheme.
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
    """ Get current dark color scheme flag.

    Returns:
        bool: Dark mode on status
    """
    global __cs_dark
    return __cs_dark


def set_color_scheme(app, mode='auto'):
    """ Set global application color scheme.

    Args:
        app (QtCore.QCoreApplication | QtWidgets.QApplication): Qt application to set color scheme
        mode (str): {'light' | 'dark' | 'auto'} Color scheme mode (default: 'auto' = follow system)
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
