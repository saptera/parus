# -*- coding: utf-8 -*-

"""Application caller functions

Convenience entry points that build the shared ``SysSet`` settings window and launch the matching PARUS
Qt application.
"""

import sys
from PySide6 import QtWidgets

__package__ = 'parus.app'
__name__ = 'parus.app.afunc'
from parus import version
from parus.gui.app_main import SysSet, ParusTrnApp, ParusDatApp
from parus.rt.app_rt import ParusRtApp

__all__ = ['ParusTrain', 'ParusData', 'ParusRT']
"""
Public function list:

- ParusTrain()                   : Launch the PARUS model training application
- ParusData()                    : Launch the PARUS data processing application
- ParusRT(seq_len)               : Launch the PARUS real-time pipeline application

Protected attributes:

- _app (QtWidgets.QApplication)  : Process-wide Qt application instance
- _set_win (SysSet)              : Shared PARUS settings window
"""


_app = QtWidgets.QApplication(sys.argv)  # Qt application instance

_set_win = SysSet()  # PARUS settings window


def ParusTrain():
    """Launch the PARUS model training application."""
    window = ParusTrnApp(_set_win, version=version)
    window.show()
    _app.exec()


def ParusData():
    """Launch the PARUS data processing application."""
    window = ParusDatApp(_set_win, version=version)
    window.show()
    _app.exec()


def ParusRT(seq_len=300):
    """Launch the PARUS real-time pipeline application.

    Args:
        seq_len (int): Requested model sequence length, must match the loaded checkpoint (default: ``300``)
    """
    window = ParusRtApp(seq_len, version=version)
    window.showMaximized()
    _app.exec()
