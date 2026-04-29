# -*- coding: utf-8 -*-

"""PARUS main application module

Top-level Qt main windows for the PARUS training, data, and settings applications.
"""

import os
import json
from PySide6 import QtCore, QtGui, QtWidgets, QtSvgWidgets

__package__ = 'parus.gui'
__name__ = 'parus.gui.app_main'
from .. import pkg_data
from . import set_color_scheme
from .desg_sysset import Ui_SysSetWindow
from .desg_apptrn import Ui_ParusTrnWindow
from .desg_appdat import Ui_ParusDatWindow
from .elm_proc import path_selector
from .gui_trn import ParusArc, ParusGen, ParusTrn
from .gui_dat import ParusInf, ParusSrt, ParusRes

__all__ = ['SysSet', 'ParusTrnApp', 'ParusDatApp']
"""
Public class list:

- SysSet(parent)                        : PARUS GUI general settings window
- ParusTrnApp(set_win, version, parent) : PARUS model training top-level application
- ParusDatApp(set_win, version, parent) : PARUS data pipeline top-level application
"""


class SysSet(QtWidgets.QMainWindow, Ui_SysSetWindow):
    """PARUS GUI general settings window.

    Loads, displays, and persists the user's working directory and colour scheme preferences. Settings are
    stored in ``~/.parus/_config.json`` and applied to the running Qt application on construction.
    """

    def __init__(self, parent=None):
        """Initialise the settings window and load persisted configuration from disk.

        Args:
            parent (QtCore.QObject | None): Parent window or widget (default: ``None``)
        """
        # Initialize GUI
        super(SysSet, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon.ico"))
        self.setWindowIcon(icon)
        # Load basic setting file
        self.__cfg_json = os.path.join(pkg_data, '_config.json')
        if os.path.isfile(self.__cfg_json):
            with open(self.__cfg_json, 'r') as fp:
                self.__cfg = json.load(fp)
                if (self.__cfg['cwd'] is None) or (not os.path.isdir(self.__cfg['cwd'])):
                    self.__cfg['cwd'] = os.path.expanduser('~')
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
        """Set default working directory."""
        path = path_selector(self.cwdPath, mode='path', caption="Select Default Working Directory", parent=self)
        path = path if os.path.isdir(str(path)) else os.path.expanduser('~')
        # Set path value
        self.__cfg['cwd'] = path
        os.chdir(path)
        # Save to config file
        with open(self.__cfg_json, 'w') as fp:
            json.dump(self.__cfg, fp, indent=2)

    def __set_cs(self):
        """Set GUI colour scheme."""
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


class ParusTrnApp(QtWidgets.QMainWindow, Ui_ParusTrnWindow):
    """PARUS model training top-level application.

    Hosts the entry buttons that open the archival-signal builder, dataset generator, model trainer, and
    settings windows.
    """

    def __init__(self, set_win, version=None, parent=None):
        """Initialise the training top-level window and wire its entry buttons.

        Args:
            set_win (SysSet): Shared settings window
            version (int | float | str | None): App version label shown in the title bar; defaults to
                ``"beta"`` when :data:`None` (default: ``None``)
            parent (QtCore.QObject | None): Parent window or widget (default: ``None``)
        """
        # Initialize GUI
        super(ParusTrnApp, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_trn.ico"))
        self.setWindowIcon(icon)
        logo = QtSvgWidgets.QSvgWidget(os.path.join(os.path.dirname(__file__), "assets/logo.svg"), parent=self)
        logo.renderer().setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.logoLayout.addWidget(logo)
        self.setWindowTitle("%s [v %s]" % (self.windowTitle(), 'beta' if version is None else str(version)))
        # Link windows
        self.__arc_win = None
        self.__gen_win = None
        self.__mod_win = None
        self.__set_win = set_win
        # Link buttons
        self.arcMksButton.clicked.connect(self.__arc_mks_win)
        self.datGenButton.clicked.connect(self.__dat_gen_win)
        self.modTrnButton.clicked.connect(self.__mod_trn_win)
        self.settingButton.clicked.connect(self.__sys_set)

    def __arc_mks_win(self):
        """Open PARUS archival signal file creation window."""
        self.__arc_win = ParusArc()
        self.__arc_win.show()

    def __dat_gen_win(self):
        """Open PARUS dataset generation window."""
        self.__gen_win = ParusGen()
        self.__gen_win.show()

    def __mod_trn_win(self):
        """Open PARUS model training window."""
        self.__mod_win = ParusTrn()
        self.__mod_win.show()

    def __sys_set(self):
        """Open GUI general settings window."""
        self.__set_win.show()


class ParusDatApp(QtWidgets.QMainWindow, Ui_ParusDatWindow):
    """PARUS data pipeline top-level application.

    Hosts the entry buttons that open the model inference window, the spike-sorting window, and the result
    viewer for one or more output files.
    """

    def __init__(self, set_win, version=None, parent=None):
        """Initialise the data pipeline top-level window and wire its entry buttons.

        Args:
            set_win (SysSet): Shared settings window
            version (int | float | str | None): App version label shown in the title bar; defaults to
                ``"beta"`` when :data:`None` (default: ``None``)
            parent (QtCore.QObject | None): Parent window or widget (default: ``None``)
        """
        # Initialize GUI
        super(ParusDatApp, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_dat.ico"))
        self.setWindowIcon(icon)
        logo = QtSvgWidgets.QSvgWidget(os.path.join(os.path.dirname(__file__), "assets/logo.svg"), parent=self)
        logo.renderer().setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.logoLayout.addWidget(logo)
        self.setWindowTitle("%s [v %s]" % (self.windowTitle(), 'beta' if version is None else str(version)))
        # Link windows
        self.__inf_win = None
        self.__srt_win = None
        self.__set_win = set_win
        # Link buttons
        self.modInfButton.clicked.connect(self.__mod_inf_win)
        self.spkSrtButton.clicked.connect(self.__spk_set_win)
        self.resVerButton.clicked.connect(self.__res_ver_win)
        self.settingButton.clicked.connect(self.__sys_set)

    def __mod_inf_win(self):
        """Open PARUS model inference window."""
        self.__inf_win = ParusInf()
        self.__inf_win.show()

    def __spk_set_win(self):
        """Open PARUS spike sorting window."""
        self.__srt_win = ParusSrt()
        self.__srt_win.showMaximized()

    def __res_ver_win(self):
        """Open PARUS result viewer window."""
        file, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Data File",
                                                         filter="Signal Files (*.hdf *.h5 *.hdf5 *.he5)")
        if file:
            for f in file:
                win = ParusRes(f)
                win.showMaximized()

    def __sys_set(self):
        """Open GUI general settings window."""
        self.__set_win.show()
