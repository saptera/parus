# PARUS main application SCRIPT

import sys
import argparse
from PySide6 import QtWidgets

__package__ = 'parus.app'
from .. import version
from ..gui.app_main import SysSet, ParusTrnApp, ParusDatApp


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusApp", description="PARUS main application caller",
                                 epilog="Call PARUS data and training applications")
parser.add_argument('-v', '--version', action='version', version="PARUS system: v%s" % str(version))
parser.add_argument('-m', '--mode', dest='mode', default='dat', type=str, choices=['trn', 'dat'], metavar="[str]",
                    help="Application selection (default: %(default)s)")
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
