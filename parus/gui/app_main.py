import os
from PySide6 import QtCore, QtWidgets, QtSvgWidgets

__package__ = 'parus.gui'
from .desg_appdat import Ui_ParusDatWindow
from .gui_dat import ParusInf, ParusSrt, ParusRes

__all__ = ['ParusDatApp']
"""
Class list:
  ParusDatApp(version=None, parent=None): Parus data pipeline toplevel application.
"""


class ParusDatApp(QtWidgets.QMainWindow, Ui_ParusDatWindow):
    def __init__(self, version=None, parent=None):
        """ Parus data pipeline toplevel application.

        Args:
            version (int | float | str | None): App version
            parent: Parent window or widget
        """
        # Initialize GUI
        super(ParusDatApp, self).__init__(parent)
        self.setupUi(self)
        logo = QtSvgWidgets.QSvgWidget(os.path.join(os.path.dirname(__file__), "assets/logo.svg"), parent=self)
        logo.renderer().setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.logoLayout.addWidget(logo)
        self.setWindowTitle("%s [v %s]" % (self.windowTitle(), 'beta' if version is None else str(version)))
        # Link buttons
        self.modInfButton.clicked.connect(self.__mod_inf_win)
        self.spkSrtButton.clicked.connect(self.__spk_set_win)
        self.resVerButton.clicked.connect(self.__res_ver_win)

    @staticmethod
    def __mod_inf_win():
        """ Open Parus model inference window. """
        win = ParusInf()
        win.show()

    @staticmethod
    def __spk_set_win():
        """ Open Parus spike sorting window. """
        win = ParusSrt()
        win.show()

    def __res_ver_win(self):
        """ Open Parus result viewer window. """
        file, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Data File",
                                                         filter="Signal Files (*.hdf *.h5 *.hdf5 *.he5)")
        if file:
            for f in file:
                win = ParusRes(f)
                win.show()
