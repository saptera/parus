# Application caller functions

import sys
from PySide6 import QtWidgets

__package__ = 'parus.app'
__name__ = 'parus.app.afunc'
from parus import version
from parus.gui.app_main import SysSet, ParusTrnApp, ParusDatApp
from parus.rt.app_rt import ParusRtApp

__all__ = ['ParusTrain', 'ParusData', 'ParusRT']
"""
Application functions:
  ParusTrain(): PARUS model training application.
  ParusData(): PARUS data processing application.
  ParusRT(seq_len=300): PARUS real-time pipeline application.
Protected attributes:
  _app: Qt application instance
  _set_win: PARUS settings window
"""


_app = QtWidgets.QApplication(sys.argv)  # Qt application instance

_set_win = SysSet()  # PARUS settings window


def ParusTrain():
    """ PARUS model training application. """
    window = ParusTrnApp(_set_win, version=version)
    window.show()
    _app.exec()


def ParusData():
    """ PARUS data processing application. """
    window = ParusDatApp(_set_win, version=version)
    window.show()
    _app.exec()


def ParusRT(seq_len=300):
    """ PARUS real-time pipeline application.

    Args:
        seq_len (int): Requested model sequence length (default: 300)
    """
    window = ParusRtApp(seq_len, version=version)
    window.showMaximized()
    _app.exec()
