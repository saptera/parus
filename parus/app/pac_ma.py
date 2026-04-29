# -*- coding: utf-8 -*-

"""PARUS main application script

Launches either the PARUS data-processing or the model-training Qt application, selected by the ``-m`` flag.
Used as the entry point for the bundled OS-level shortcuts.
"""

import sys
import argparse
from PySide6 import QtWidgets

__package__ = 'parus.app'
from .. import version
from ..gui.app_main import SysSet, ParusTrnApp, ParusDatApp


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusApp", description="PARUS main application launcher",
                                 epilog="Launch the PARUS data or training application")
parser.add_argument('-v', '--version', action='version', version="PARUS system: v%s" % str(version))
parser.add_argument('-m', '--mode', dest='mode', default='dat', type=str, choices=['trn', 'dat'], metavar="[str]",
                    help="Application selection: 'dat' (data) or 'trn' (training) (default: %(default)s)")
# Parse inputs
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    set_win = SysSet()
    if args.mode == 'trn':
      win = ParusTrnApp(set_win, version=version)
    else:
      win = ParusDatApp(set_win, version=version)
    win.show()
    app.exec()
