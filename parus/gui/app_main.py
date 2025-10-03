import os
import json
from PySide6 import QtCore, QtWidgets, QtSvgWidgets

__package__ = 'parus.gui'
from .. import pkg_data
from . import set_color_scheme
from .desg_sysset import Ui_SysSetWindow
from .desg_appdat import Ui_ParusDatWindow
from .elm_proc import path_selector
from .gui_dat import ParusInf, ParusSrt, ParusRes

__all__ = ['SysSet', 'ParusDatApp']
"""
Class list:
  SysSet(parent=None): Parus GUI general settings.
  ParusDatApp(version=None, parent=None): Parus data pipeline toplevel application.
"""


class SysSet(QtWidgets.QMainWindow, Ui_SysSetWindow):
    def __init__(self, parent=None):
        """ Parus GUI general settings.

        Args:
            parent: Parent window or widget
        """
        # Initialize GUI
        super(SysSet, self).__init__(parent)
        self.setupUi(self)
        # Load basic setting file
        self.__cfg_json = os.path.join(pkg_data, '_config.json')
        if os.path.isfile(self.__cfg_json):
            with open(self.__cfg_json, 'r') as fp:
                self.__cfg = json.load(fp)
                self.__cfg['cwd'] = os.path.expanduser('~') if self.__cfg['cwd'] is None else self.__cfg['cwd']
        else:
            self.__cfg = {'cwd': os.path.expanduser('~'), 'cs': 'auto'}
            with open(self.__cfg_json, 'w') as fp:
                json.dump(self.__cfg, fp, indent=2)
        # Set working directory
        os.chdir(self.__cfg['cwd'])
        self.cwdPath.setText(self.__cfg['cwd'])
        # Set colour scheme
        set_color_scheme(QtWidgets.QApplication.instance(), self.__cfg['cs'])
        if self.__cfg['cs'] == 'light':
            self.csLight.setChecked(True)
        elif self.__cfg['cs'] == 'dark':
            self.csDark.setChecked(True)
        else:
            self.csAuto.setChecked(True)
        # Link controls
        self.cwdSelect.clicked.connect(self.__sel_cwd)
        self.csButtonGroup.buttonReleased.connect(self.__set_cs)

    def __sel_cwd(self):
        """ Set default working directory. """
        path = path_selector(self.cwdPath, mode='path', caption="Select Default Working Directory", parent=self)
        path = path if os.path.isdir(path) else os.path.expanduser('~')
        # Set path value
        self.__cfg['cwd'] = path
        os.chdir(path)
        # Save to config file
        with open(self.__cfg_json, 'w') as fp:
            json.dump(self.__cfg, fp, indent=2)

    def __set_cs(self):
        """ Set GUI colour scheme. """
        btn = self.csButtonGroup.checkedButton().objectName()
        app = QtWidgets.QApplication.instance()
        if app is not None:
            if btn == "csLight":
                set_color_scheme(app, 'light')
                self.__cfg['cs'] = 'light'
            elif btn == "csDark":
                set_color_scheme(app, 'dark')
                self.__cfg['cs'] = 'dark'
            else:
                set_color_scheme(app, 'auto')
                self.__cfg['cs'] = 'auto'
        # Save to config file
        with open(self.__cfg_json, 'w') as fp:
            json.dump(self.__cfg, fp, indent=2)


class ParusDatApp(QtWidgets.QMainWindow, Ui_ParusDatWindow):
    def __init__(self, set_win, version=None, parent=None):
        """ Parus data pipeline toplevel application.

        Args:
            set_win (SysSet): Setting window
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
        # Link setting window
        self.__set_win = set_win
        # Link buttons
        self.modInfButton.clicked.connect(self.__mod_inf_win)
        self.spkSrtButton.clicked.connect(self.__spk_set_win)
        self.resVerButton.clicked.connect(self.__res_ver_win)
        self.settingButton.clicked.connect(self.__sys_set)

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

    def __sys_set(self):
        """ Open GUI general settings window. """
        self.__set_win.show()
