# PARUS real-time data processing package

from PySide6 import QtCore, QtWidgets

__package__ = 'parus.rt'
__name__ = 'parus.rt'

# Settings for high resolution monitors
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
