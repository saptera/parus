import sys
from PyQt5 import QtWidgets
from parus.gui.scope_func import SignalScope

app = QtWidgets.QApplication(sys.argv)
window = SignalScope()
window.show()
app.exec_()
