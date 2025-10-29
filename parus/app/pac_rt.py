# PARUS real-time application SCRIPT

import sys
import argparse
from PySide6 import QtWidgets

__package__ = 'parus.app'
from .. import version
from ..rt.app_rt import ParusRtApp


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusRT", description="PARUS real-time application caller",
                                 epilog="Call PARUS real-time data processing application")
parser.add_argument('-v', '--version', action='version', version="PARUS system: v%s" % str(version))
parser.add_argument('-l', '--length', dest='seq_len', type=int, default=300, metavar="[int]",
                    help="Expected sequence length of model inputs (default: %(default)s)")
# Parse inputs
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = ParusRtApp(args.seq_len, version=version)
    win.showMaximized()
    app.exec()
