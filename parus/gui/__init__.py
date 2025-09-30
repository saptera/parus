# PARUS GUI module

import matplotlib as mpl
import matplotlib.pyplot as plt
from PySide6 import QtCore, QtWidgets
mpl.use('QtAgg')

__package__ = 'parus.gui'
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
__dark = False  # Dark mode flag


def cs_dark():
    """ Get current dark color scheme flag.

    Returns:
        bool: Dark mode on status
    """
    global __dark
    return __dark


def set_color_scheme(app, mode='auto'):
    """ Set global application color scheme.

    Args:
        app (QtWidgets.QApplication): Qt application to set color scheme
        mode (str): {'light' | 'dark' | 'auto'} Color scheme mode (default: 'auto' = follow system)
    """
    global __dark
    app.setStyle('fusion')

    if mode == 'light':
        __dark = False
        app.styleHints().setColorScheme(QtCore.Qt.ColorScheme.Light)
        plt.style.use('default')
    elif mode == 'dark':
        __dark = True
        app.styleHints().setColorScheme(QtCore.Qt.ColorScheme.Dark)
        plt.style.use('dark_background')
    else:  # Fallback for all other modes
        scheme = app.styleHints().colorScheme()
        if scheme == QtCore.Qt.ColorScheme.Dark:
            __dark = True
            plt.style.use('dark_background')
        else:  # Fallback for unknown scheme
            __dark = False
            plt.style.use('default')
