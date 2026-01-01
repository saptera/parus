# Model training GUI module

import os
import re
from datetime import datetime
import json
import numpy as np
import h5py as h5
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6 import QtCore, QtGui, QtWidgets

__package__ = 'parus.gui'
__name__ = 'parus.gui.gui_trn'
from .. import pkg_data
from ..fio import arc_write, noi_write
from ..scripts import gen_sim, gen_sta, mod_trn, prd_dsp
from . import cs_dark
from .desg_arcmrk import Ui_ParusArcWindow
from .desg_genctl import Ui_ParusGenWindow
from .desg_modtrn import Ui_ParusTrnWindow
from .elm_proc import PyScriptExec, ProcConsole, ProgBusyDialog, path_selector
from .elm_plot import ArcPreviewPlot

__all__ = ['ArcPrv', 'ParusArc', 'ParusGen', 'ParusTrn']
"""
Class list:
  ArcPrv(data, parent=None): Archival signal data preview dialog.
  ParusArc(parent=None): Parus archival file creation window.
  ParusGen(parent=None): Parus simulated signal generation window.
  ParusTrn(parent=None): Parus model training window.
"""


class ArcPrv(QtWidgets.QDialog):
    def __init__(self, data, parent=None):
        """ Archival signal data preview dialog.

        Args:
            data (dict): Archival signal data, refer to [parus.fio.fdata -> ARC data structure definition]
            parent (QtCore.QObject | None): Parent Qt object
        """
        # Initialize GUI
        super().__init__(parent)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon.ico"))
        self.setWindowIcon(icon)
        self.setWindowTitle("Signal Preview")
        # Set window feature
        self.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        # Set figure
        self._arcplot = ArcPreviewPlot(data)
        self._toolbar = NavigationToolbar2QT(self._arcplot, self)
        # Set layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._arcplot)
        self.setLayout(layout)

    def closeEvent(self, event):
        """ Close clean-up. """
        self._arcplot.close()


class ParusArc(QtWidgets.QMainWindow, Ui_ParusArcWindow):
    def __init__(self, parent=None):
        """ Parus archival file creation window.

        Args:
            parent: Parent window or widget
        """
        # Initialize GUI
        super(ParusArc, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_trn.ico"))
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.recDate.setDate(QtCore.QDate.currentDate())
        self.recTime.setTime(QtCore.QTime.currentTime())

        # Archive file data variables
        self.sig = None
        self.pos = -1
        self.rng = None
        self.freq = 0
        self.meta = self.__set_meta_dict()
        # Control variables
        self.__loaded = False
        self.__dst_ok = False
        self.__ch_wfm = None
        self.__ch_pos = None
        self.__arc_win = None
        # Data process thread
        self.out_file = None
        self.__prw_ok = False
        self._proc_thread = self._DataProcThread(self)
        self._proc_thread.finished.connect(self.__proc_finalize)
        self.__save_msg = ProgBusyDialog(self, "<b>Archival data being processed<br><br>Please wait...</b>", bar=False)

        # Connect file IO controls
        self.srcFilePath.textChanged.connect(self.__set_src_file)
        self.srcFileSelect.clicked.connect(self.__sel_src_file)
        self.dstDirPath.textChanged.connect(self.__set_dst_path)
        self.dstDirSelect.clicked.connect(self.__sel_dst_path)
        self.datChnCombo.currentIndexChanged.connect(self.__set_data_chn)
        self.datWfmCombo.currentIndexChanged.connect(self.__set_data_wfm)
        # Connect organism data controls
        self.ognGenLine.textChanged.connect(self.__set_meta_dict)
        self.ognSpcLine.textChanged.connect(self.__set_meta_dict)
        self.ognStrLine.textChanged.connect(self.__set_meta_dict)
        self.ognModLine.textChanged.connect(self.__set_meta_dict)
        self.ognNoteLine.textChanged.connect(self.__set_meta_dict)
        # Connect signal data controls
        self.sigRegLine.textChanged.connect(self.__set_meta_dict)
        self.sigTypLine.textChanged.connect(self.__set_meta_dict)
        self.sigCelLine.textChanged.connect(self.__set_meta_dict)
        self.sigNoteLine.textChanged.connect(self.__set_meta_dict)
        # Connect system data controls
        self.sysTypCombo.currentIndexChanged.connect(self.__set_meta_dict)
        self.sysMfrLine.textChanged.connect(self.__set_meta_dict)
        self.sysPrtLine.textChanged.connect(self.__set_meta_dict)
        self.sysSrnLine.textChanged.connect(self.__set_meta_dict)
        self.sysSocLine.textChanged.connect(self.__set_meta_dict)
        self.sysNoteLine.textChanged.connect(self.__set_meta_dict)
        # Connect probe data controls
        self.prbTypLine.textChanged.connect(self.__set_meta_dict)
        self.prbMfrLine.textChanged.connect(self.__set_meta_dict)
        self.prbPrtLine.textChanged.connect(self.__set_meta_dict)
        self.prbSrnLine.textChanged.connect(self.__set_meta_dict)
        self.prbChnSpinbox.valueChanged.connect(self.__set_meta_dict)
        self.prbNoteLine.textChanged.connect(self.__set_meta_dict)
        # Connect date time buttons
        self.recDate.dateChanged.connect(self.__set_meta_dict)
        self.recTime.timeChanged.connect(self.__set_meta_dict)
        # Connect process buttons
        self.previewButton.clicked.connect(self.__preview)
        self.saveButton.clicked.connect(self.__save)

        # Set control initial status
        self.previewButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        # Load control values
        self.__load_params()

    def closeEvent(self, event):
        """ Window closed cleaning. """
        # Close process informing dialog
        self.__save_msg.allow_close = True
        self.__save_msg.close()
        # Close preview window
        try:
            if self.__arc_win is not None:
                self.__arc_win.close()
        except RuntimeError:
            pass

    def ctrl_enable(self, enable=True):
        """ Set enable status of controls.

        Args:
            enable (bool): Enable status of controls (default: True)
        """
        # Source data IO controls
        self.srcFilePath.setEnabled(enable)
        self.srcFileSelect.setEnabled(enable)
        self.datChnCombo.setEnabled(enable)
        self.datWfmCombo.setEnabled(enable)
        self.datSpkCombo.setEnabled(enable)
        self.smpAntSpinbox.setEnabled(enable)
        self.smpPstSpinbox.setEnabled(enable)
        self.dstDirPath.setEnabled(enable)
        self.dstDirSelect.setEnabled(enable)
        # Organism data controls
        self.ognGenLine.setEnabled(enable)
        self.ognSpcLine.setEnabled(enable)
        self.ognStrLine.setEnabled(enable)
        self.ognModLine.setEnabled(enable)
        self.ognNoteLine.setEnabled(enable)
        # Signal data controls
        self.sigRegLine.setEnabled(enable)
        self.sigTypLine.setEnabled(enable)
        self.sigCelLine.setEnabled(enable)
        self.sigNoteLine.setEnabled(enable)
        # System data controls
        self.sysTypCombo.setEnabled(enable)
        self.sysMfrLine.setEnabled(enable)
        self.sysPrtLine.setEnabled(enable)
        self.sysSrnLine.setEnabled(enable)
        self.sysSocLine.setEnabled(enable)
        self.sysNoteLine.setEnabled(enable)
        # Probe data controls
        self.prbTypLine.setEnabled(enable)
        self.prbMfrLine.setEnabled(enable)
        self.prbPrtLine.setEnabled(enable)
        self.prbSrnLine.setEnabled(enable)
        self.prbChnSpinbox.setEnabled(enable)
        self.prbNoteLine.setEnabled(enable)

    # Data process members ------------------------------------------------------------------------------------------- #
    class _DataProcThread(QtCore.QThread):
        save = False  # Save mode flag

        def __init__(self, parent):
            """ Data process independent thread.

            Args:
                parent (ParusArc): Parus archival signal creation window caller
            """
            super(ParusArc._DataProcThread, self).__init__(parent)
            self.parent = parent
            self.file_saved = False

        def run(self):
            self.file_saved = False
            file = self.parent.srcFilePath.text()
            chn = self.parent.datChnCombo.currentIndex()
            wfm = self.parent.datWfmCombo.currentText()
            # Archival noise creation
            if wfm == 'raw':
                with h5.File(file, 'r') as fp:
                    noi = fp['raw'][chn].tolist()
                if self.save:
                    name = "_".join([self.parent.meta['probe']['typ'], self.parent.meta['system']['typ'],
                                     self.parent.meta['feature']['typ'],
                                     self.parent.meta['datetime'].replace('-', '').replace(':', ''),
                                     "%04d" % self.parent.meta['probe']['chn']]) + '.noi'
                    self.parent.out_file = os.path.join(self.parent.dstDirPath.text(), name)
                    data = {'data': {'noi': noi, 'freq': self.parent.freq}, 'meta': self.parent.meta}
                    self.file_saved = noi_write(self.parent.out_file, data)
            # Archival signal creation
            else:
                # Get control inputs
                asp = round(self.parent.smpAntSpinbox.value() * 1.1)
                psp = round(self.parent.smpPstSpinbox.value() * 1.2)
                spk = self.parent.datSpkCombo.currentText()
                # Read data
                with h5.File(file, 'r') as fp:
                    raw = fp['raw'][chn]
                    ano = np.nonzero(fp['pos'][wfm][str(chn)][spk][()])[0]
                # Get required indices
                num = asp + psp + 1
                blk = np.arange(-asp, psp + 1, step=1, dtype=int)
                idx = np.repeat(ano, num) + np.tile(blk, len(ano))
                idx = np.clip(idx, a_min=0, a_max=len(raw) - 1).reshape(-1, num, order='C')
                # Compute data
                self.parent.sig = np.mean(raw[idx], axis=0).tolist()
                ra = asp - self.parent.smpAntSpinbox.value()
                re = ra + self.parent.smpPstSpinbox.value() + 1
                self.parent.rng = [ra, re]
                self.parent.pos = np.argmin(self.parent.sig[ra:re]).item() + ra
                # Save results
                if self.save:
                    name = "_".join([self.parent.meta['probe']['typ'], self.parent.meta['system']['typ'],
                                     self.parent.meta['neuron']['spk'],
                                     self.parent.meta['datetime'].replace('-', '').replace(':', ''),
                                     "%04d" % self.parent.meta['probe']['chn']]) + '.arc'
                    self.parent.out_file = os.path.join(self.parent.dstDirPath.text(), name)
                    data = {'data':{'sig': self.parent.sig, 'pos': self.parent.pos,
                                    'rng': self.parent.rng, 'freq': self.parent.freq},
                            'meta': self.parent.meta}
                    self.file_saved = arc_write(self.parent.out_file, data)

    def __load_src_info(self, file):
        """ Load current source file information. """
        # Block signals
        self.datChnCombo.blockSignals(True)
        self.datWfmCombo.blockSignals(True)
        self.datSpkCombo.blockSignals(True)
        # Clear controls
        self.datChnCombo.clear()
        self.datWfmCombo.clear()
        self.datSpkCombo.clear()
        if os.path.isfile(file) and file.endswith(('.hdf', '.h5', '.hdf5', '.he5')):
            fp = h5.File(file, 'r')
            # Load frequency information
            if 'frq' in fp:
                self.freq = fp['frq'][()].item()
            else:
                self.previewButton.setEnabled(False)
                self.saveButton.setEnabled(False)
                self.__loaded = False
                self.statBar.showMessage("Recoding frequency missing in file, cannot process further")
                QtWidgets.QMessageBox.warning(
                    self, "Warning", "Recoding frequency missing in file", QtWidgets.QMessageBox.StandardButton.Ok)
                return
            # Check raw trace availability
            if 'raw' in fp:
                self.__ch_wfm = {}
                self.__ch_pos = {}
                for i in range(fp['raw'].shape[0]):
                    self.datChnCombo.addItem("CH_%03d" % i)
                    self.__ch_wfm[i] = ['raw']
                    self.__ch_pos[i] = {}
            else:
                self.previewButton.setEnabled(False)
                self.saveButton.setEnabled(False)
                self.__loaded = False
                self.statBar.showMessage("Raw recoding missing in file, cannot process further")
                QtWidgets.QMessageBox.warning(
                    self, "Warning", "Raw recoding missing in file", QtWidgets.QMessageBox.StandardButton.Ok)
                return
            # Check annotation position
            if 'pos' in fp:
                for w in fp['pos']:
                    for c in fp['pos'][w]:
                        ano = list(fp['pos'][w][c].keys())
                        if ano:
                            self.__ch_wfm[int(c)].append(w)
                            self.__ch_pos[int(c)][w] = ano
            else:
                self.__ch_pos = None
                self.statBar.showMessage("No spike annotation in current file")
            # Close file
            fp.close()
        # Enable controls
        self.previewButton.setEnabled(True)
        self.__loaded = True
        # Relink signals
        self.datChnCombo.setCurrentIndex(-1)
        self.datChnCombo.blockSignals(False)
        self.datChnCombo.setCurrentIndex(0)
        self.datWfmCombo.setCurrentIndex(-1)
        self.datWfmCombo.blockSignals(False)
        self.datWfmCombo.setCurrentIndex(0)
        self.datSpkCombo.blockSignals(False)
        # Trigger metadata check
        self.__set_meta_dict()

    def __preview(self):
        """ Preview archived signal results. """
        self.__save_msg.show()
        self._proc_thread.save = False
        self._proc_thread.start()

    def __save(self):
        """ Save archived signal to file. """
        # Disable controls
        self.__prw_ok = self.previewButton.isEnabled()
        self.ctrl_enable(False)
        self.previewButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        # Initiate process
        self.__save_msg.show()
        self._proc_thread.save = True
        self._proc_thread.start()

    def __proc_finalize(self):
        """ Process finished linked function. """
        self.__save_msg.hide()
        # Save finalize
        if self._proc_thread.save:
            # Re-enable controls
            self.ctrl_enable(True)
            self.previewButton.setEnabled(self.__prw_ok)
            self.saveButton.setEnabled(True)
            # Display message
            if self._proc_thread.file_saved:
                self.__save_params()
                self.statBar.showMessage("Archival file saved to [%s]" % self.out_file)
            else:
                self.statBar.showMessage("Save archival file failed")
        # Show preview
        else:
            data = {'sig': self.sig, 'pos': self.pos, 'rng': self.rng, 'freq': self.freq}
            self.__arc_win = ArcPrv(data)
            self.__arc_win.show()
            self.statBar.showMessage("Preview ready")

    # Control element related functions ------------------------------------------------------------------------------ #
    def __load_params(self):
        """ Load GUI settings from previous execution. """
        par_json = os.path.join(pkg_data, '_arc_params.json')
        if os.path.isfile(par_json):
            # Load previous settings
            with open(par_json, 'r') as fp:
                pars = json.load(fp)
            # Set source data IO controls
            self.smpAntSpinbox.setValue(pars['anterior_samples'])
            self.smpPstSpinbox.setValue(pars['posterior_samples'])
            self.dstDirPath.setText(pars['archive_folder'])
            # Set organism data controls
            self.ognGenLine.setText(pars['organism_genus'])
            self.ognSpcLine.setText(pars['organism_species'])
            self.ognStrLine.setText(pars['organism_strain'])
            self.ognModLine.setText(pars['organism_modification'])
            self.ognNoteLine.setText(pars['organism_note'])
            # Set signal data controls
            self.sigRegLine.setText(pars['recording_region'])
            self.sigTypLine.setText(pars['signal_type'])
            self.sigCelLine.setText(pars['cell_type'])
            self.sigNoteLine.setText(pars['signal_note'])
            # Set system data controls
            self.sysTypCombo.setCurrentIndex(pars['system_type'])
            self.sysMfrLine.setText(pars['system_manufacturer'])
            self.sysPrtLine.setText(pars['system_part_number'])
            self.sysSrnLine.setText(pars['system_serial_number'])
            self.sysSocLine.setText(pars['system_socket'])
            self.sysNoteLine.setText(pars['system_note'])
            # Set probe data controls
            self.prbTypLine.setText(pars['probe_type'])
            self.prbMfrLine.setText(pars['probe_manufacturer'])
            self.prbPrtLine.setText(pars['probe_part_number'])
            self.prbSrnLine.setText(pars['probe_serial_number'])
            self.prbNoteLine.setText(pars['probe_note'])

    def __save_params(self):
        """ Save GUI settings of current execution. """
        pars = {}  # INIT VAR
        # Read source data IO controls
        pars['anterior_samples'] = self.smpAntSpinbox.value()
        pars['posterior_samples'] = self.smpPstSpinbox.value()
        pars['archive_folder'] = self.dstDirPath.text()
        # Read organism data controls
        pars['organism_genus'] = self.ognGenLine.text()
        pars['organism_species'] = self.ognSpcLine.text()
        pars['organism_strain'] = self.ognStrLine.text()
        pars['organism_modification'] = self.ognModLine.text()
        pars['organism_note'] = self.ognNoteLine.text()
        # Read signal data controls
        pars['recording_region'] = self.sigRegLine.text()
        pars['signal_type'] = self.sigTypLine.text()
        pars['cell_type'] = self.sigCelLine.text()
        pars['signal_note'] = self.sigNoteLine.text()
        # Read system data controls
        pars['system_type'] = self.sysTypCombo.currentIndex()
        pars['system_manufacturer'] = self.sysMfrLine.text()
        pars['system_part_number'] = self.sysPrtLine.text()
        pars['system_serial_number'] = self.sysSrnLine.text()
        pars['system_socket'] = self.sysSocLine.text()
        pars['system_note'] = self.sysNoteLine.text()
        # Read probe data controls
        pars['probe_type'] = self.prbTypLine.text()
        pars['probe_manufacturer'] = self.prbMfrLine.text()
        pars['probe_part_number'] = self.prbPrtLine.text()
        pars['probe_serial_number'] = self.prbSrnLine.text()
        pars['probe_note'] = self.prbNoteLine.text()
        # Save to file
        with open(os.path.join(pkg_data, '_arc_params.json'), 'w') as fp:
            json.dump(pars, fp, indent=2)

    def __set_src_file(self):
        """ Set source file path. """
        file = self.srcFilePath.text()
        self.__load_src_info(file)

    def __sel_src_file(self):
        """ Select source file path button connection. """
        file = path_selector(self.srcFilePath, mode='file', caption="Select Source File",
                             flt="Signal Files (*.hdf *.h5 *.hdf5 *.he5)", parent=self)
        if file is not None:
            self.__load_src_info(file)

    def __set_dst_path(self):
        """ Set output file path. """
        path = self.dstDirPath.text()
        if os.path.isdir(path):
            self.__dst_ok = True
            self.statBar.showMessage("Output folder set")
        else:
            self.__dst_ok = False
            self.statBar.showMessage("In valid output folder")
        # Trigger metadata check
        self.__set_meta_dict()

    def __sel_dst_path(self):
        """ Select output file path button connection. """
        path_selector(self.dstDirPath, mode='path', caption="Select Output Folder", parent=self)

    def __set_data_chn(self):
        """ Set current source data channel. """
        idx = self.datChnCombo.currentIndex()
        self.prbChnSpinbox.setValue(idx)
        # Block signals
        self.datWfmCombo.blockSignals(True)
        self.datSpkCombo.blockSignals(True)
        # Clear controls
        self.datWfmCombo.clear()
        self.datSpkCombo.clear()
        # Update controls
        if self.__ch_wfm[idx]:
            self.datWfmCombo.addItems(self.__ch_wfm[idx])
        # Relink signals
        self.datWfmCombo.setCurrentIndex(-1)
        self.datWfmCombo.blockSignals(False)
        self.datWfmCombo.setCurrentIndex(0)
        self.datSpkCombo.blockSignals(False)

    def __set_data_wfm(self):
        """ Set current source data waveform. """
        # Set control enable
        flag = self.datWfmCombo.currentIndex() != 0
        self.smpAntSpinbox.setEnabled(flag)
        self.smpPstSpinbox.setEnabled(flag)
        self.sigCelLine.setEnabled(flag)
        self.previewButton.setEnabled(flag)
        # Set spike combobox
        if self.__ch_pos is not None:
            idx = self.datChnCombo.currentIndex()
            txt = self.datWfmCombo.currentText()
            # Block signals
            self.datSpkCombo.blockSignals(True)
            # Clear controls
            self.datSpkCombo.clear()
            # Update controls
            if txt in self.__ch_pos[idx]:
                self.datSpkCombo.addItems(self.__ch_pos[idx][txt])
            # Relink signals
            self.datSpkCombo.blockSignals(False)
        # Trigger metadata check
        self.__set_meta_dict()

    def __set_meta_dict(self):
        """ Set archival signal metadata. """
        # Get value
        ogn_dat = {
            'gn': self.ognGenLine.text(),
            'se': self.ognSpcLine.text(),
            'st': self.ognStrLine.text(),
            'mod': None if self.ognModLine.text() == '' else self.ognModLine.text(),
            'note': None if self.ognNoteLine.text() == '' else self.ognNoteLine.text()
        }
        rgn_dat = '' if self.sigRegLine.text() == '' else self.sigRegLine.text().split(' ')
        sys_dat = {
            'typ': ['d', 'a'][self.sysTypCombo.currentIndex()],
            'mfr': self.sysMfrLine.text(),
            'pn': self.sysPrtLine.text(),
            'sn': self.sysSrnLine.text(),
            'soc': self.sysSocLine.text(),
            'note': None if self.sysNoteLine.text() == '' else self.sysNoteLine.text()
        }
        prb_dat = {
            'typ': self.prbTypLine.text(),
            'mfr': self.prbMfrLine.text(),
            'pn': self.prbPrtLine.text(),
            'sn': self.prbSrnLine.text(),
            'chn': self.prbChnSpinbox.value(),
            'note': None if self.prbNoteLine.text() == '' else self.prbNoteLine.text()
        }
        date_time = self.recDate.date().toString('yyyy-MM-dd') + 'T' + self.recTime.time().toString('hh:mm:ss')
        # Set value
        if self.datWfmCombo.currentText() == 'raw':
            self.meta = {
                'organism': ogn_dat,
                'region': rgn_dat,
                'feature': {
                    'typ': self.sigTypLine.text(),
                    'note': None if self.sigNoteLine.text() == '' else self.sigNoteLine.text()
                },
                'system': sys_dat,
                'probe': prb_dat,
                'datetime': date_time
            }
        else:
            self.meta = {
                'organism': ogn_dat,
                'region': rgn_dat,
                'neuron': {
                    'typ': self.sigCelLine.text(),
                    'spk': self.sigTypLine.text(),
                    'note': None if self.sigNoteLine.text() == '' else self.sigNoteLine.text()
                },
                'system': sys_dat,
                'probe': prb_dat,
                'datetime': date_time
            }
        # Check value
        for k in self.meta:
            if k in ['region', 'datetime']:
                if self.meta[k] == '':
                    self.saveButton.setEnabled(False)
                    self.saveButton.setToolTip("Please define all required field before save")
                    break
            else:
                if any([i == '' for i in self.meta[k].values()]):
                    self.saveButton.setEnabled(False)
                    self.saveButton.setToolTip("Please define all required field before save")
                    break
        else:
            self.saveButton.setEnabled(self.__loaded and self.__dst_ok)
            self.saveButton.setToolTip("Save archival signal to defined path")
        return self.meta


class ParusGen(QtWidgets.QMainWindow, Ui_ParusGenWindow):
    def __init__(self, parent=None):
        """ Parus simulated signal generation window.

        Args:
            parent: Parent window or widget
        """
        # Initialize main UI
        super(ParusGen, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_trn.ico"))
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        if cs_dark():
            self.genSimButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
            self.genStaButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
        else:
            self.genSimButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')
            self.genStaButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')
        self.__timer_val = -1  # Timer initialization
        # Set control variable defaults
        self.__auto_scr = True
        self.__sim_run = False
        self.__sta_run = False

        # Set generation process
        self._sim_proc = PyScriptExec(script=gen_sim, console=self.procConsole, trigger=self.genSimButton,
                                      name="Parus [Simulated Signal Generation]", disp_time=True, clr_con=False,
                                      trig_txt=("Start Generation", "Stop Process"))
        self._sim_proc.set_auto_scroll(self.__auto_scr)
        self._sim_proc.started.connect(self.__gen_sim_start)
        self._sim_proc.finished.connect(self.__gen_sim_finish)
        # Set view statistics process
        self._sta_proc = PyScriptExec(script=gen_sta, console=self.procConsole, trigger=self.genStaButton,
                                      name="Parus [View Generation Statistics]", disp_time=True, clr_con=False,
                                      trig_txt=("View Statistics", "Close View"))
        self._sta_proc.set_auto_scroll(self.__auto_scr)
        self._sta_proc.started.connect(self.__gen_sta_start)
        self._sta_proc.finished.connect(self.__gen_sta_finish)
        # Process control button extra settings
        self.genSimButton.clicked.connect(self.__switch_gen_sim)
        self.genStaButton.clicked.connect(self.__switch_gen_sta)
        # Initialize console
        self._console = ProcConsole(console=self.procConsole,
                                    btn_clr=self.procConClear, btn_cpy=self.procConCopy, btn_scr=self.procConScroll,
                                    lnk_proc=[self._sim_proc, self._sta_proc], stat_bar=self.statBar, disp_time=True,
                                    init_msg="Parus Signal Generation GUI ready!")

        # Set data variable defaults
        self.arc_dir = None
        self.noi_dir = None
        self.out_dir = None
        self.num_sim = self.__set_num_sim()
        self.tot_len = self.__set_tot_len()
        self.freq = self.__set_freq()
        self.min_gap = self.__set_min_gap()
        self.max_gap = self.__set_max_gap()
        self.sig_grp = self.__set_sig_grp()
        self.grp_rat = self.__set_grp_rat()
        self.no_rat = self.__set_no_rat()
        self.sig_fac = self.__set_sig_fac()
        self.noi_fac = self.__set_noi_fac()
        self.bsl_meth, self.bsl_comp = self.__set_bsl_aug()
        self.bsl_amps = self.__set_bsl_amps()
        self.bsl_freq = self.__set_bsl_freq()
        self.num_eg = self.__set_num_eg()
        self.set_typ = self.__set_set_typ()
        self.__set_stat_path()  # None return statistic file check function

        # IO path control
        self.sigSelect.clicked.connect(self.__sel_sig_dir)
        self.sigPath.textChanged.connect(self.__set_sig_dir)
        self.noiSelect.clicked.connect(self.__sel_noi_dir)
        self.noiPath.textChanged.connect(self.__set_noi_dir)
        self.outSelect.clicked.connect(self.__sel_out_dir)
        self.outPath.textChanged.connect(self.__set_out_dir)
        # Basic sample feature control
        self.sampCnt.valueChanged.connect(self.__set_num_sim)
        self.sampFreq.valueChanged.connect(self.__set_freq)
        self.sampLen.valueChanged.connect(self.__set_tot_len)
        self.sampFreq.valueChanged.connect(self.__set_tot_len)
        # Spike gap control
        self.minSpkFreq.valueChanged.connect(self.__set_min_gap)
        self.sampFreq.valueChanged.connect(self.__set_min_gap)
        self.chnCellCnt.valueChanged.connect(self.__set_min_gap)
        self.maxSpkFreq.valueChanged.connect(self.__set_max_gap)
        self.sampFreq.valueChanged.connect(self.__set_max_gap)
        # Grouping control
        self.spkGrpMthd.currentIndexChanged.connect(self.__set_sig_grp)
        self.spkGrpRate.textChanged.connect(self.__set_grp_rat)
        # Noise only ratio control
        self.noiOnlyRate.valueChanged.connect(self.__set_no_rat)
        # Inputs multiplication control
        self.sigMultMin.valueChanged.connect(self.__set_sig_fac)
        self.sigMultMax.valueChanged.connect(self.__set_sig_fac)
        self.noiMultMin.valueChanged.connect(self.__set_noi_fac)
        self.noiMultMax.valueChanged.connect(self.__set_noi_fac)
        # Baseline augmentation control
        self.bslCst.valueChanged.connect(self.__set_bsl_aug)
        self.bslLin.valueChanged.connect(self.__set_bsl_aug)
        self.bslSin.valueChanged.connect(self.__set_bsl_aug)
        self.bslNos.valueChanged.connect(self.__set_bsl_aug)
        self.bslAmpMin.valueChanged.connect(self.__set_bsl_amps)
        self.bslAmpMax.valueChanged.connect(self.__set_bsl_amps)
        self.bslFrqMin.valueChanged.connect(self.__set_bsl_freq)
        self.bslFrqMax.valueChanged.connect(self.__set_bsl_freq)
        # Extra settings control
        self.exEg.valueChanged.connect(self.__set_num_eg)
        self.setTypBox.currentIndexChanged.connect(self.__set_set_typ)
        # Generation statistics control
        self.statFileSelect.clicked.connect(self.__sel_stat_path)
        self.statFilePath.textChanged.connect(self.__set_stat_path)
        # Reset controls
        self.clrSetButton.clicked.connect(lambda: self.reset_all(True))

        # Load previous execution parameters
        self.__load_params()
        # System standby
        self.statBar.showMessage("System standby")

    def timerEvent(self, event):
        """ Timer event for controls with delayed updating. """
        self.killTimer(self.__timer_val)
        self.__timer_val = -1
        self.spkGrpRate.setText(' '.join(self.grp_rat[1:]))

    def closeEvent(self, event):
        """ Clean-ups upon close. """
        self._sim_proc.terminate()
        self._sta_proc.terminate()

    def gen_ctrl_enable(self, enable=True):
        """ Set enable status of all generation related controls.

        Args:
            enable (bool): Enable status of controls (default: True)
        """
        # Reset argument button
        self.clrSetButton.setEnabled(enable)
        # Generation path controls
        self.sigPath.setEnabled(enable)
        self.sigSelect.setEnabled(enable)
        self.noiPath.setEnabled(enable)
        self.noiSelect.setEnabled(enable)
        self.setTypBox.setEnabled(enable)
        self.outPath.setEnabled(enable)
        self.outSelect.setEnabled(enable)
        # Generation basic controls
        self.sampCnt.setEnabled(enable)
        self.sampLen.setEnabled(enable)
        self.sampFreq.setEnabled(enable)
        self.exEg.setEnabled(enable)
        # Generation grouping controls
        self.spkGrpMthd.setEnabled(enable)
        self.spkGrpRate.setEnabled(enable)
        self.noiOnlyRate.setEnabled(enable)
        # Generation spike occurrence controls
        self.minSpkFreq.setEnabled(enable)
        self.maxSpkFreq.setEnabled(enable)
        self.chnCellCnt.setEnabled(enable)
        # Generation sample multiplication controls
        self.sigMultMin.setEnabled(enable)
        self.sigMultMax.setEnabled(enable)
        self.noiMultMin.setEnabled(enable)
        self.noiMultMax.setEnabled(enable)
        # Generation baseline augmentation controls
        self.bslNos.setEnabled(enable)
        self.bslCst.setEnabled(enable)
        self.bslLin.setEnabled(enable)
        self.bslSin.setEnabled(enable)
        self.bslAmpMin.setEnabled(enable)
        self.bslAmpMax.setEnabled(enable)
        self.bslFrqMin.setEnabled(enable)
        self.bslFrqMax.setEnabled(enable)

    # Process related functions -------------------------------------------------------------------------------------- #
    def set_gensim_args(self):
        """ Set arguments for simulated signal generation. """
        if (self.arc_dir is None) or (self.noi_dir is None) or (self.out_dir is None) or (self.sampCnt.value() <= 0):
            self.genSimButton.setEnabled(False)
            self._sim_proc.reset_arguments()
        else:
            # Check signal grouping
            grouping = [] if self.sig_grp is None else self.sig_grp + self.grp_rat
            # Check baseline methods
            if self.bsl_meth is None:
                baseline = []
            else:
                baseline = self.bsl_meth + self.bsl_comp
                if any([i in self.bsl_meth for i in ['cst', 'lin', 'sin']]):
                    baseline += self.bsl_amps
                if 'sin' in self.bsl_meth:
                    baseline += self.bsl_freq
            # Finalize argument list
            args = (self.arc_dir + self.noi_dir + self.out_dir + self.num_sim + self.tot_len + self.freq +
                    self.min_gap + self.max_gap + grouping + self.no_rat + self.sig_fac + self.noi_fac +
                    baseline + self.num_eg + self.set_typ)
            self._sim_proc.set_arguments(args)
            self.genSimButton.setEnabled(True)

    def __switch_gen_sim(self):
        """ ParusGenSim button connected function. """
        if self.__sim_run:
            self.genSimButton.setStyleSheet('QPushButton {color: red}')
        else:
            if cs_dark():
                self.genSimButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
            else:
                self.genSimButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')

    def __gen_sim_start(self):
        """ ParusGenSim process STARTED connected function. """
        self.__sim_run = True
        self.__switch_gen_sim()
        self.gen_ctrl_enable(False)
        self.statBar.showMessage("Simulated signal generation started")

    def __gen_sim_finish(self):
        """ ParusGenSim process FINISHED connected function. """
        # Reset button
        self.__sim_run = False
        self.gen_ctrl_enable(True)
        self.__switch_gen_sim()
        # Finalizing
        if self._sim_proc.fin_stop:
            # Save current successful execution params
            self.__save_params()
            # Set generation statistics file path
            stat_line = re.search(r'(?<=\[)[^]]+(?=])', self._sim_proc.last_line).group()
            stat_path = ' '.join(stat_line.split(' ')[2:])
            self.statFilePath.setText(stat_path)
            # Show status bar message
            self.statBar.showMessage("Simulated signal generation successfully finished")
        else:
            self.statBar.showMessage("Simulated signal generation terminated")

    def __switch_gen_sta(self):
        """ ParusGenSta button connected function. """
        if self.__sta_run:
            self.genStaButton.setStyleSheet('QPushButton {color: red}')
        else:
            if cs_dark():
                self.genStaButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
            else:
                self.genStaButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')

    def __gen_sta_start(self):
        """ ParusGenSta process STARTED connected function. """
        self.__sta_run = True
        self.__switch_gen_sta()
        self.statBar.showMessage("Viewing generation statistics")

    def __gen_sta_finish(self):
        """ ParusGenSta process FINISHED connected function. """
        self.__sta_run = False
        self.__switch_gen_sta()
        self.statBar.showMessage("Generation statistics file closed")

    # Control element related functions ------------------------------------------------------------------------------ #
    def reset_all(self, notify=True):
        """  Reset all controls to defaults.

        Args:
            notify (bool): Console/Statusbar notification flag (default: True)
        """
        self.arc_dir = self.sigPath.clear()
        self.noi_dir = self.noiPath.clear()
        self.out_dir = self.outPath.clear()
        self.sampCnt.setValue(100000)
        self.sampLen.setValue(15.0)
        self.sampFreq.setValue(20000)
        self.exEg.setValue(100)
        self.spkGrpMthd.setCurrentIndex(2)
        self.spkGrpRate.clear()
        self.noiOnlyRate.setValue(5.0)
        self.minSpkFreq.setValue(50)
        self.maxSpkFreq.setValue(100)
        self.chnCellCnt.setValue(5)
        self.sigMultMin.setValue(50)
        self.sigMultMax.setValue(500)
        self.noiMultMin.setValue(1.0)
        self.noiMultMax.setValue(2.5)
        self.bslNos.setValue(2.0)
        self.bslCst.setValue(1.0)
        self.bslLin.setValue(1.0)
        self.bslSin.setValue(1.0)
        self.bslAmpMin.setValue(-20.0)
        self.bslAmpMax.setValue(20.0)
        self.bslFrqMin.setValue(2.0)
        self.bslFrqMax.setValue(50.0)
        self.statFilePath.clear()
        # Reset argument
        self.set_gensim_args()
        self._sta_proc.reset_arguments()
        # Set notification
        if notify:
            # Inform console
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            time = "<span style=\"color:%s;white-space:pre;\">[%s] </span>" % ('skyblue' if cs_dark() else 'blue', time)
            message = time + "<span style=\"font-weight:bold;\">All parameters reset to defaults!</span>"
            self.procConsole.append(message)
            # Inform status bar
            self.statBar.showMessage("All parameters reset")

    def __load_params(self):
        """ Load GUI settings from previous execution. """
        par_json = os.path.join(pkg_data, '_gen_params.json')
        if os.path.isfile(par_json):
            # Load previous settings
            with open(par_json, 'r') as fp:
                pars = json.load(fp)
            # Set to current controls
            self.sigPath.setText(pars['archival_signal_folder'])
            self.noiPath.setText(pars['archival_noise_folder'])
            self.sampCnt.setValue(pars['sample_number'])
            self.sampLen.setValue(pars['sample_length'])
            self.sampFreq.setValue(pars['sample_frequency'])
            self.exEg.setValue(pars['sample_extra'])
            self.spkGrpMthd.setCurrentIndex(pars['group_method'])
            self.noiOnlyRate.setValue(pars['noise_only_ratio'])
            self.minSpkFreq.setValue(pars['spike_freq_min'])
            self.maxSpkFreq.setValue(pars['spike_freq_max'])
            self.chnCellCnt.setValue(pars['max_cell_per_channel'])
            self.sigMultMin.setValue(pars['spike_multiplier_min'])
            self.sigMultMax.setValue(pars['spike_multiplier_max'])
            self.noiMultMin.setValue(pars['noise_multiplier_min'])
            self.noiMultMax.setValue(pars['noise_multiplier_max'])
            self.bslNos.setValue(pars['baseline_no_shift_magnitude'])
            self.bslCst.setValue(pars['baseline_constant_shift_magnitude'])
            self.bslLin.setValue(pars['baseline_linear_ramp_magnitude'])
            self.bslSin.setValue(pars['baseline_sinusoid_oscillation_magnitude'])
            self.bslAmpMin.setValue(pars['baseline_shift_value_min'])
            self.bslAmpMax.setValue(pars['baseline_shift_value_max'])
            self.bslFrqMin.setValue(pars['baseline_oscillation_freq_min'])
            self.bslFrqMax.setValue(pars['baseline_oscillation_freq_min'])
            # Update group rate with signal blocked
            self.spkGrpRate.blockSignals(True)
            self.spkGrpRate.setText(pars['group_magnitude'])
            self.spkGrpRate.blockSignals(False)
            self.__set_grp_rat()  # Re-trigger filtering
        else:
            self.reset_all(notify=False)

    def __save_params(self):
        """ Save GUI settings of current execution. """
        pars = {}  # INIT VAR
        # Read current controls
        pars['archival_signal_folder'] = self.sigPath.text()
        pars['archival_noise_folder'] = self.noiPath.text()
        pars['sample_number'] = self.sampCnt.value()
        pars['sample_length'] = self.sampLen.value()
        pars['sample_frequency'] = self.sampFreq.value()
        pars['sample_extra'] = self.exEg.value()
        pars['group_method'] = self.spkGrpMthd.currentIndex()
        pars['group_magnitude'] = self.spkGrpRate.text()
        pars['noise_only_ratio'] = self.noiOnlyRate.value()
        pars['spike_freq_min'] = self.minSpkFreq.value()
        pars['spike_freq_max'] = self.maxSpkFreq.value()
        pars['max_cell_per_channel'] = self.chnCellCnt.value()
        pars['spike_multiplier_min'] = self.sigMultMin.value()
        pars['spike_multiplier_max'] = self.sigMultMax.value()
        pars['noise_multiplier_min'] = self.noiMultMin.value()
        pars['noise_multiplier_max'] = self.noiMultMax.value()
        pars['baseline_no_shift_magnitude'] = self.bslNos.value()
        pars['baseline_constant_shift_magnitude'] = self.bslCst.value()
        pars['baseline_linear_ramp_magnitude'] = self.bslLin.value()
        pars['baseline_sinusoid_oscillation_magnitude'] = self.bslSin.value()
        pars['baseline_shift_value_min'] = self.bslAmpMin.value()
        pars['baseline_shift_value_max'] = self.bslAmpMax.value()
        pars['baseline_oscillation_freq_min'] = self.bslFrqMin.value()
        pars['baseline_oscillation_freq_min'] = self.bslFrqMax.value()
        # Save to file
        with open(os.path.join(pkg_data, '_gen_params.json'), 'w') as fp:
            json.dump(pars, fp, indent=2)

    def __sel_sig_dir(self):
        """ Select archived signal file (*.arc) folder button connection. """
        path = path_selector(self.sigPath, mode='path', caption="Select Archived Signal Folder", parent=self)
        self.arc_dir = None if path is None else [path]
        # Update process arguments
        self.set_gensim_args()

    def __set_sig_dir(self):
        """ Select archived signal file (*.arc) folder line edit connection. """
        path = self.sigPath.text()
        if os.path.isdir(path):
            self.arc_dir = [path]
            self.statBar.showMessage("Archival signal folder defined")
        else:
            self.arc_dir = None
            self.statBar.showMessage("Archival signal folder is invalid!")
        # Update process arguments
        self.set_gensim_args()
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(1000)
        return self.arc_dir

    def __sel_noi_dir(self):
        """ Select archived noise file (*.noi) folder button connection. """
        path = path_selector(self.noiPath, mode='path', caption="Select Archived Noise Folder", parent=self)
        self.noi_dir = None if path is None else [path]
        # Update process arguments
        self.set_gensim_args()

    def __set_noi_dir(self):
        """ Select archived noise file (*.noi) folder line edit connection. """
        path = self.noiPath.text()
        if os.path.isdir(path):
            self.noi_dir = [path]
            self.statBar.showMessage("Archival noise folder defined")
        else:
            self.noi_dir = None
            self.statBar.showMessage("Archival noise folder is invalid!")
        # Update process arguments
        self.set_gensim_args()
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(1000)
        return self.noi_dir

    def __sel_out_dir(self):
        """ Select generation output folder button connection. """
        path = path_selector(self.outPath, mode='path', caption="Select Output Folder", parent=self)
        self.out_dir = None if path is None else [path]
        # Update process arguments
        self.set_gensim_args()

    def __set_out_dir(self):
        """ Select generation output folder line edit connection. """
        path = self.outPath.text()
        if os.path.isdir(path):
            self.out_dir = [path]
            self.statBar.showMessage("Generation output folder defined")
        else:
            self.out_dir = None
            self.statBar.showMessage("Generation output folder is invalid!")
        # Update process arguments
        self.set_gensim_args()
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(1000)
        return self.out_dir

    def __set_num_sim(self):
        """ Set number of simulated data to be generated. """
        self.num_sim = [str(self.sampCnt.value())]
        # Update process arguments
        self.set_gensim_args()
        return self.num_sim

    def __set_freq(self):
        """" Set sampling frequency of the system. """
        self.freq = ['-f', str(self.sampFreq.value())]
        # Update process arguments
        self.set_gensim_args()
        return self.freq

    def __set_tot_len(self):
        """ Set total length of final signal sample. """
        self.tot_len = ['-l', str(round(self.sampLen.value() * self.sampFreq.value() / 1000))]
        # Update process arguments
        self.set_gensim_args()
        return self.tot_len

    def __set_min_gap(self):
        """ Set minimum index gap of signal events. """
        self.min_gap = ['-ig', str(round(self.sampFreq.value() / self.minSpkFreq.value() / self.chnCellCnt.value()))]
        # Update process arguments
        self.set_gensim_args()
        return self.min_gap

    def __set_max_gap(self):
        """ Set minimum index gap of signal events. """
        self.max_gap = ['-xg', str(round(self.sampFreq.value() / self.maxSpkFreq.value()))]
        # Update process arguments
        self.set_gensim_args()
        return self.max_gap

    def __set_sig_grp(self):
        """ Set signal grouping method. """
        if self.spkGrpMthd.currentIndex() == 0:
            self.sig_grp = None
        else:
            self.sig_grp = ['-gp', [None, 'typ', 'spk'][self.spkGrpMthd.currentIndex()]]
        # Update process arguments
        self.set_gensim_args()
        return self.sig_grp

    def __set_grp_rat(self):
        """ Set occurrence ratio of groups. """
        text = self.spkGrpRate.text()
        clr = re.sub(r'[^\d.\s\-]', "", text)
        num = re.findall(r'-?\d+(?:\.\d+)?', clr)
        self.grp_rat = ['-gr'] + [str(round(float(n))) for n in num] if num else []
        # Update process arguments
        self.set_gensim_args()
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(500)
        return self.grp_rat

    def __set_no_rat(self):
        """ Set occurrence ratio of noise only data. """
        self.no_rat = ['-no', str(self.noiOnlyRate.value() / 100)]
        # Update process arguments
        self.set_gensim_args()
        return self.no_rat

    def __set_sig_fac(self):
        """ Set signal amplitude multiplication factor. """
        self.sig_fac = ['-sf', str(self.sigMultMin.value()), str(self.sigMultMax.value())]
        self.sigMultMin.setMaximum(self.sigMultMax.value() - 0.1)
        self.sigMultMax.setMinimum(self.sigMultMin.value() + 0.1)
        # Update process arguments
        self.set_gensim_args()
        return self.sig_fac

    def __set_noi_fac(self):
        """ Set noise amplitude multiplication factor. """
        self.noi_fac = ['-nf', str(self.noiMultMin.value()), str(self.noiMultMax.value())]
        self.noiMultMin.setMaximum(self.noiMultMax.value() - 0.1)
        self.noiMultMax.setMinimum(self.noiMultMin.value() + 0.1)
        # Update process arguments
        self.set_gensim_args()
        return self.noi_fac

    def __set_bsl_aug(self):
        """ Set baseline augmentation. """
        # Initialize temporary variables
        meth = []
        comp = []
        # Check constant shift
        if self.bslCst.value() > 0:
            meth.append('cst')
            comp.append(str(round(self.bslCst.value())))
        # Check linear shift
        if self.bslLin.value() > 0:
            meth.append('lin')
            comp.append(str(round(self.bslLin.value())))
        # Check sinusoid shift
        if self.bslSin.value() > 0:
            meth.append('sin')
            comp.append(str(round(self.bslSin.value())))
        # Finish with zero shift check
        if meth and (self.bslNos.value() > 0):
            meth.append('nos')
            comp.append(str(round(self.bslNos.value())))
        # Set to main variables
        if meth and comp:
            self.bsl_meth = ['-bs'] + meth
            self.bsl_comp = ['-bp'] + comp
        else:
            self.bsl_meth = None
            self.bsl_comp = []
        # Update process arguments
        self.set_gensim_args()
        return self.bsl_meth, self.bsl_comp

    def __set_bsl_amps(self):
        """ Set baseline shift amplitude. """
        self.bsl_amps = ['-ba', str(self.bslAmpMin.value()), str(self.bslAmpMax.value())]
        self.bslAmpMin.setMaximum(self.bslAmpMax.value() - 1)
        self.bslAmpMax.setMinimum(self.bslAmpMin.value() + 1)
        # Update process arguments
        self.set_gensim_args()
        return self.bsl_amps

    def __set_bsl_freq(self):
        """ Set baseline shift frequency. """
        self.bsl_freq = ['-bf', str(self.bslFrqMin.value()), str(self.bslFrqMax.value())]
        self.bslFrqMin.setMaximum(self.bslFrqMax.value() - 5)
        self.bslFrqMax.setMinimum(self.bslFrqMin.value() + 5)
        # Update process arguments
        self.set_gensim_args()
        return self.bsl_freq

    def __set_num_eg(self):
        """ Number of extra examples to be generated. """
        self.num_eg = ['-eg', str(self.exEg.value())] if self.exEg.value() > 0 else []
        # Update process arguments
        self.set_gensim_args()
        return self.num_eg

    def __set_set_typ(self):
        """ Set generation dataset type string. """
        if self.setTypBox.currentIndex() == 0:
            self.set_typ = []
        else:
            self.set_typ = ['-tp', ['trn', 'vld', 'tst'][self.setTypBox.currentIndex() - 1]]
        # Update process arguments
        self.set_gensim_args()
        return self.set_typ

    def __sel_stat_path(self):
        """ Select generation statistic file (*.cjh) button connection. """
        path_selector(self.statFilePath, mode='file', caption="Select Generation Statistic File",
                      flt="Generation Statistic File (*.cjh)", parent=self)

    def __set_stat_path(self):
        """ Set defined generation statistics file. """
        stat_path = self.statFilePath.text()
        chk_path = os.path.isfile(stat_path)
        chk_type = stat_path.endswith('.cjh')
        if chk_path and chk_type:
            self._sta_proc.set_arguments([stat_path])
            self.genStaButton.setEnabled(True)
        else:
            self._sta_proc.reset_arguments()
            self.genStaButton.setEnabled(False)


class ParusTrn(QtWidgets.QMainWindow, Ui_ParusTrnWindow):
    def __init__(self, parent=None):
        """ Parus model training window.

        Args:
            parent: Parent window or widget
        """
        # Initialize main UI
        super(ParusTrn, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_trn.ico"))
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        if cs_dark():
            self.trnProcButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
        else:
            self.trnProcButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')
        # Set control variable defaults
        self.__auto_scr = True
        self.__trn_run = False

        # Set training process
        self._trn_proc = PyScriptExec(script=mod_trn, console=self.procConsole, trigger=self.trnProcButton,
                                      name="Parus [Model Train]", disp_time=True, clr_con=False,
                                      trig_txt=("Initiate Model Training", "Abort Training"))
        self._trn_proc.set_auto_scroll(self.__auto_scr)
        self._trn_proc.started.connect(self.__trn_proc_start)
        self._trn_proc.finished.connect(self.__trn_proc_finish)
        # Set testing view process
        self._tst_view = PyScriptExec(script=prd_dsp, console=self.procConsole, trigger=self.tstViewButton,
                                      name="Parus [Testing View]", disp_time=True, clr_con=False,
                                      trig_txt=("View Testing Results", "Close View"))
        self._tst_view.set_auto_scroll(self.__auto_scr)
        self._tst_view.started.connect(self.__tst_view_start)
        self._tst_view.finished.connect(self.__tst_view_finish)
        # Initialize console
        self._console = ProcConsole(console=self.procConsole,
                                    btn_clr=self.procConClear, btn_cpy=self.procConCopy, btn_scr=self.procConScroll,
                                    lnk_proc=[self._trn_proc, self._tst_view], stat_bar=self.statBar, disp_time=True,
                                    init_msg="Parus Model Training GUI ready!")

        # Set training variable defaults
        self.sim_dir = None
        self.out_dir = None
        self.num_trn = []
        self.num_vld = []
        self.num_tst = []
        self.seq_len = []
        self.mod_name = []
        self.num_ep = []
        self.eval_stp = []
        self.eval_ind = ['-t', 'disp']
        self.ex_opt = []
        # Set test viewing variable defaults
        self.tst_dir = None
        self.tst_typ = None
        self.__set_tst_type()  # Update test model type
        self.__art_prf = None  # Current model artifacts folder prefix

        # Connect model training controls
        self.simSelect.clicked.connect(self.__sel_sim_dir)
        self.simPath.textChanged.connect(self.__set_sim_dir)
        self.outSelect.clicked.connect(self.__sel_out_dir)
        self.outPath.textChanged.connect(self.__set_out_dir)
        self.trnSampSpinbox.valueChanged.connect(self.__set_num_trn)
        self.vldSampSpinbox.valueChanged.connect(self.__set_num_vld)
        self.tstSampSpinbox.valueChanged.connect(self.__set_num_tst)
        self.seqLenSpinbox.valueChanged.connect(self.__set_seq_len)
        self.modNameLine.textChanged.connect(self.__set_mod_name)
        self.nEpSpinbox.valueChanged.connect(self.__set_num_ep)
        self.stpEvalSpinbox.valueChanged.connect(self.__set_eval_stp)
        self.indEvalCombo.currentIndexChanged.connect(self.__set_eval_ind)
        self.exOptLine.textChanged.connect(self.__set_ex_opt)
        # Connect test view controls
        self.tstPathSelect.clicked.connect(self.__sel_tst_path)
        self.tstPathLine.textChanged.connect(self.__set_tst_path)
        self.tstTypeBox.currentIndexChanged.connect(self.__set_tst_type)

        # Load previous execution parameters
        self.__load_params()
        self.set_view_args()
        # System standby
        self.statBar.showMessage("System standby")

    def closeEvent(self, event):
        """ Clean-ups upon close. """
        self._trn_proc.terminate()

    def ctrl_enable(self, enable=True):
        """ Set enable status of controls.

        Args:
            enable (bool): Enable status of controls (default: True)
        """
        self.simPath.setEnabled(enable)
        self.outPath.setEnabled(enable)
        self.trnSampSpinbox.setEnabled(enable)
        self.vldSampSpinbox.setEnabled(enable)
        self.tstSampSpinbox.setEnabled(enable)
        self.seqLenSpinbox.setEnabled(enable)
        self.modNameLine.setEnabled(enable)
        self.nEpSpinbox.setEnabled(enable)
        self.stpEvalSpinbox.setEnabled(enable)
        self.indEvalCombo.setEnabled(enable)

    # Process related functions -------------------------------------------------------------------------------------- #
    def set_train_args(self):
        """ Set arguments for model training. """
        if (self.sim_dir is None) or (self.out_dir is None):
            self.trnProcButton.setEnabled(False)
            self._trn_proc.reset_arguments()
        else:
            args = (self.out_dir + self.sim_dir + self.num_trn + self.num_vld + self.num_tst + self.seq_len +
                    self.mod_name + self.num_ep + self.eval_stp + self.eval_ind + self.ex_opt)
            self._trn_proc.set_arguments(args)
            self.trnProcButton.setEnabled(True)

    def __switch_trn_btn(self):
        """ ParusModTrn button connected function. """
        if self.__trn_run:
            self.trnProcButton.setStyleSheet('QPushButton {color: red}')
        else:
            if cs_dark():
                self.trnProcButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
            else:
                self.trnProcButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')

    def __trn_proc_start(self):
        """ ParusModTrn process STARTED connected function. """
        self.__trn_run = True
        self.__switch_trn_btn()
        self.ctrl_enable(False)
        # Get artifacts prefix
        name = "parus" if self.modNameLine.text() == '' else self.modNameLine.text()
        dset = os.path.basename(self.simPath.text().rstrip('/\\'))
        time = datetime.now().strftime('%Y%m%d')
        self.__art_prf = '__'.join([name, dset, time])
        # Inform status bar
        self.statBar.showMessage("Parus model training started")

    def __trn_proc_finish(self):
        """ ParusModTrn process FINISHED connected function. """
        # Reset button
        self.__trn_run = False
        self.ctrl_enable(True)
        self.__switch_trn_btn()
        # Display status
        if self._trn_proc.fin_stop:
            # Save current successful execution params
            self.__save_params()
            self.statBar.showMessage("Model training successfully finished")
            # Set test view parameters
            path = max([os.path.join(self.outPath.text(), d) for d in next(os.walk(self.outPath.text()))[1]
                        if d.startswith(self.__art_prf)], key=os.path.getmtime)
            self.tstPathLine.setText(path)
            self.tstTypeBox.setCurrentIndex(1)
            self.__art_prf = None  # Reset prefix
        else:
            self.statBar.showMessage("Model training terminated")

    def set_view_args(self):
        """ Set arguments for test results viewing. """
        if self.tst_dir is None:
            self.tstViewButton.setEnabled(False)
            self._tst_view.reset_arguments()
        else:
            file = os.path.join(self.tst_dir, self.tst_typ)
            if os.path.isfile(file):
                self._tst_view.set_arguments([file])
                self.tstViewButton.setEnabled(True)
            else:
                self.statBar.showMessage("Invalid test results file")
                self.tstViewButton.setEnabled(False)
                self._tst_view.reset_arguments()
                QtWidgets.QMessageBox.critical(self, "File Not Found",
                                               "Defined testing results group [%s]\n"
                                               "cannot be located at defined folder [%s]\nPlease check you inputs." %
                                               (self.tstTypeBox.currentText(), self.tst_dir),
                                               QtWidgets.QMessageBox.StandardButton.Ok)

    def __tst_view_start(self):
        """ ParusPrdDsp process STARTED connected function. """
        # Set button style
        self.tstViewButton.setStyleSheet('QPushButton {color: red}')
        # Inform status bar
        self.statBar.showMessage("Testing results view started")

    def __tst_view_finish(self):
        """ ParusPrdDsp process FINISHED connected function. """
        # Set button style
        if cs_dark():
            self.tstViewButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
        else:
            self.tstViewButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')
        # Inform status bar
        if self._tst_view.fin_stop:
            self.statBar.showMessage("Testing results view closed")
        else:
            self.statBar.showMessage("Testing results view terminated")

    # Control element related functions ------------------------------------------------------------------------------ #
    def __load_params(self):
        """ Load GUI settings from previous execution. """
        par_json = os.path.join(pkg_data, '_trn_params.json')
        if os.path.isfile(par_json):
            # Load previous settings
            with open(par_json, 'r') as fp:
                pars = json.load(fp)
            # Set to current controls
            self.simPath.setText(pars['dataset_path'])
            self.trnSampSpinbox.setValue(pars['n_trn_samples'])
            self.vldSampSpinbox.setValue(pars['n_vld_samples'])
            self.tstSampSpinbox.setValue(pars['n_tst_samples'])
            self.seqLenSpinbox.setValue(pars['sequence_length'])
            self.modNameLine.setText(pars['model_name'])
            self.nEpSpinbox.setValue(pars['total_epoch'])
            self.stpEvalSpinbox.setValue(pars['steps_per_eval'])
            self.indEvalCombo.setCurrentIndex(pars['eval_visual_method_index'])
            self.exOptLine.setText(pars['advanced_options'])
        self.set_train_args()

    def __save_params(self):
        """ Save GUI settings of current execution. """
        pars = {}  # INIT VAR
        # Read current controls
        pars['dataset_path'] = self.simPath.text()
        pars['n_trn_samples'] = self.trnSampSpinbox.value()
        pars['n_vld_samples'] = self.vldSampSpinbox.value()
        pars['n_tst_samples'] = self.tstSampSpinbox.value()
        pars['sequence_length'] = self.seqLenSpinbox.value()
        pars['model_name'] = self.modNameLine.text()
        pars['total_epoch'] = self.nEpSpinbox.value()
        pars['steps_per_eval'] = self.stpEvalSpinbox.value()
        pars['eval_visual_method_index'] = self.indEvalCombo.currentIndex()
        pars['advanced_options'] = ' '.join(self.ex_opt)
        # Save to file
        with open(os.path.join(pkg_data, '_trn_params.json'), 'w') as fp:
            json.dump(pars, fp, indent=2)

    def __sel_sim_dir(self):
        """ Select dataset (*.sim) folder button connection. """
        path = path_selector(self.simPath, mode='path', caption="Select Dataset Folder", parent=self)
        self.sim_dir = None if path is None else [path]
        # Update process arguments
        self.set_train_args()

    def __set_sim_dir(self):
        """ Select dataset (*.sim) folder line edit connection. """
        path = self.simPath.text()
        if os.path.isdir(path):
            self.sim_dir = [path]
            self.statBar.showMessage("Dataset folder defined")
        else:
            self.sim_dir = None
            self.statBar.showMessage("Dataset folder is invalid!")
        # Update process arguments
        self.set_train_args()

    def __sel_out_dir(self):
        """ Select model training results output folder button connection. """
        path = path_selector(self.outPath, mode='path', caption="Select Model Output Folder", parent=self)
        self.out_dir = None if path is None else [path]
        # Update process arguments
        self.set_train_args()

    def __set_out_dir(self):
        """ Select model training results output folder line edit connection. """
        path = self.outPath.text()
        if os.path.isdir(path):
            self.out_dir = [path]
            self.statBar.showMessage("Model output folder defined")
        else:
            self.out_dir = None
            self.statBar.showMessage("Model output folder is invalid!")
        # Update process arguments
        self.set_train_args()

    def __set_num_trn(self):
        """ Set number of training samples. """
        num = self.trnSampSpinbox.value()
        self.num_trn = ['-dtn', str(num)]
        # Update process arguments
        self.set_train_args()

    def __set_num_vld(self):
        """ Set number of validation samples. """
        num = self.vldSampSpinbox.value()
        self.num_vld = ['-dvl', str(num)]
        # Update process arguments
        self.set_train_args()

    def __set_num_tst(self):
        """ Set number of testing samples. """
        num = self.tstSampSpinbox.value()
        self.num_tst = ['-dts', str(num)]
        # Update process arguments
        self.set_train_args()

    def __set_seq_len(self):
        """ Set dataset/model sample sequence length. """
        num = self.seqLenSpinbox.value()
        self.seq_len = ['-mls', str(num)]
        # Update process arguments
        self.set_train_args()

    def __set_mod_name(self):
        """ Set model name. """
        self.modNameLine.blockSignals(True)
        name = self.modNameLine.text()
        name = "".join(s for s in name if s.isalnum())
        self.modNameLine.setText(name)
        self.modNameLine.blockSignals(False)
        self.mod_name = ['-mid', name]
        # Update process arguments
        self.set_train_args()

    def __set_num_ep(self):
        """ Set number of epochs. """
        num = self.nEpSpinbox.value()
        self.num_ep = ['-tep', str(num)]
        # Update process arguments
        self.set_train_args()

    def __set_eval_stp(self):
        """ Set training steps per evaluation. """
        stp = self.stpEvalSpinbox.value()
        self.eval_stp = ['-tev', str(stp)]
        # Update process arguments
        self.set_train_args()

    def __set_eval_ind(self):
        """ Set model evaluation results visualization method. """
        ind = ['none', 'disp', 'save'][self.indEvalCombo.currentIndex()]
        self.eval_ind = ['-t', ind]
        # Update process arguments
        self.set_train_args()

    def __set_ex_opt(self):
        """ Model training advance option. This function DOES NOT check input, error will be handled by the script. """
        opt = self.exOptLine.text()
        self.ex_opt = [o for o in opt.split(' ') if o]
        # Update process arguments
        self.set_train_args()

    def __sel_tst_path(self):
        """ Select test results (*.pklz) folder button connection. """
        self.tstPathLine.blockSignals(True)
        path = path_selector(self.tstPathLine, mode='path', caption="Select Test Results Folder", parent=self)
        self.tstPathLine.blockSignals(False)
        self.tst_dir = None if path is None else path
        # Update process arguments
        self.set_view_args()

    def __set_tst_path(self):
        """ Select test results (*.pklz) folder line edit connection. """
        path = self.tstPathLine.text()
        if os.path.isdir(path):
            self.tst_dir = path
            self.statBar.showMessage("Test results folder defined")
        else:
            self.tst_dir = None
            self.statBar.showMessage("Test results folder is invalid!")
        # Update process arguments
        self.set_view_args()

    def __set_tst_type(self):
        """ Set test results linked model type. """
        idx = self.tstTypeBox.currentIndex()
        self.tst_typ = ['tst_opt.pklz', 'tst_fin.pklz'][idx]
        # Update process arguments
        self.set_view_args()
