# PARUS GUI module

import sys
import os
from PySide6 import QtCore, QtWidgets

# Set default working directory
sys.path.extend(os.path.dirname(__file__))
os.chdir(os.path.expanduser('~'))

# Settings for high resolution monitors
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
