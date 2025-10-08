# Data processing GUI module

import os
import shutil
import json
import numpy as np
import h5py as h5
import matplotlib as mpl
from matplotlib.backend_bases import _Mode
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6 import QtCore, QtGui, QtWidgets
import warnings

__package__ = 'parus.gui'
__name__ = 'parus.gui.gui_dat'
from .. import pkg_data
from ..fio import h5_load_dat
from ..data import (sig_peak_fwd, cls_cosamp_blk, cls_crscor_blk, pos_ripple_flt, post_cls_chk,
                    tpt_spk_frq, tpt_spk_isi, tpt_spk_cv, tpt_spk_cv2)
from ..scripts import mod_inf
from . import cs_dark
from .desg_modinf import Ui_ParusInfWindow
from .desg_spksrt import Ui_ParusSrtWindow
from .desg_wfmsel import Ui_WfmSelWindow
from .desg_resver import Ui_ParusResWindow
from .elm_proc import (CellCheckbox, CellData, PyScriptExec, ProcConsole, ProgBusyDialog,
                       path_selector, table_loader, selection_operator)
from .elm_plot import LoopedColormap, ClstFeatViewer, ResPltLoader

__all__ = ['ParusInf', 'ParusSrt', 'WfmSel', 'ParusRes']
"""
Class list:
  ParusInf(parent=None): Parus data inference window.
  ParusSrt(parent=None): Parus spike sorting window.
  WfmSel(key, raw, parent=None): Result waveform channel selection window.
  ParusRes(file, parent=None): Parus inference results viewing and validation window.
"""


class ParusInf(QtWidgets.QMainWindow, Ui_ParusInfWindow):
    def __init__(self, parent=None):
        """ Parus data inference window.

        Args:
            parent: Parent window or widget
        """
        # Initialize GUI
        super(ParusInf, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_dat.ico"))
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        if cs_dark():
            self.procButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
        else:
            self.procButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')
        # Set file table view
        self.inputTable.setColumnWidth(0, 50)
        self.inputTable.setColumnWidth(1, 50)
        self.inputTable.horizontalHeader().setStretchLastSection(True)
        # Set control variable defaults
        self.__auto_scr = True
        self.__proc_run = False

        # Set inference process
        self._proc = PyScriptExec(script=mod_inf, console=self.procConsole, trigger=self.procButton,
                                  name="Parus [Data Inference]", disp_time=True, clr_con=False,
                                  trig_txt=("Initiate Data Inference", "Stop Process"))
        self._proc.set_auto_scroll(self.__auto_scr)
        self._proc.started.connect(self.__proc_start)
        self._proc.finished.connect(self.__proc_finish)
        # Initialize console
        self._console = ProcConsole(console=self.procConsole,
                                    btn_clr=self.procConClear, btn_cpy=self.procConCopy, btn_scr=self.procConScroll,
                                    lnk_proc=[self._proc], stat_bar=self.statBar, disp_time=True,
                                    init_msg="Parus Data Inference GUI ready!")

        # Control variables
        self.lst_file = []
        self._sel_file = []
        self.lst_dirs = []
        self._sel_dirs = []
        self.ckpt = None
        self.ovlp = self.__set_ovlp_len()
        self.tmem = self.__set_to_mem()
        self.btsz = self.__set_bat_size()
        self.clvl = self.__set_comp_lvl()
        self.out_path = []

        # Connect controls
        self.addFileButton.clicked.connect(self.__set_data_file)
        self.addPathButton.clicked.connect(self.__set_data_path)
        self.selAllButton.clicked.connect(lambda: self.__set_selc('all'))
        self.selNonButton.clicked.connect(lambda: self.__set_selc('non'))
        self.selInvButton.clicked.connect(lambda: self.__set_selc('inv'))
        self.ckptButton.clicked.connect(self.__sel_mod_ckpt)
        self.ckptLine.textChanged.connect(self.__set_mod_ckpt)
        self.ovlpSpinbox.valueChanged.connect(self.__set_ovlp_len)
        self.tmemCheckbox.clicked.connect(self.__set_to_mem)
        self.btszSpinbox.valueChanged.connect(self.__set_bat_size)
        self.clvlCombo.currentIndexChanged.connect(self.__set_comp_lvl)

        # Load previous execution parameters
        self.__load_params()
        # System standby
        self.statBar.showMessage("System standby")

    def closeEvent(self, event):
        """ Clean-ups upon close. """
        self._proc.terminate()

    def ctrl_enable(self, enable=True):
        """ Set enable status of controls.

        Args:
            enable (bool): Enable status of controls (default: True)
        """
        self.addFileButton.setEnabled(enable)
        self.addPathButton.setEnabled(enable)
        self.selAllButton.setEnabled(enable)
        self.selNonButton.setEnabled(enable)
        self.selInvButton.setEnabled(enable)
        self.ckptLine.setEnabled(enable)
        self.ckptButton.setEnabled(enable)
        self.ovlpSpinbox.setEnabled(enable)
        self.tmemCheckbox.setEnabled(enable)
        self.btszSpinbox.setEnabled(enable)
        self.clvlCombo.setEnabled(enable)
        # Disable table selection checkboxes
        for cb in self._sel_file + self._sel_dirs:
            cb.setEnabled(enable)

    # Process related functions -------------------------------------------------------------------------------------- #
    def set_proc_args(self):
        """ Set arguments for model inference. """
        # Get process path lists
        flst = [s.id for s in self._sel_file if s.isChecked()]
        dlst = [s.id for s in self._sel_dirs if s.isChecked()]
        # Set arguments
        if (self.ckpt is None) or (len(flst + dlst) == 0):
            self.procButton.setEnabled(False)
            self._proc.reset_arguments()
        else:
            flst = ['-f'] + flst if flst else []
            dlst = ['-d'] + dlst if dlst else []
            args = (self.ckpt + flst + dlst + self.out_path + self.ovlp + self.tmem + self.btsz + self.clvl)
            self._proc.set_arguments(args)
            self.procButton.setEnabled(True)

    def __switch_proc_btn(self):
        """ ParusModInf button connected function. """
        if self.__proc_run:
            self.procButton.setStyleSheet('QPushButton {color: red}')
        else:
            if cs_dark():
                self.procButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
            else:
                self.procButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')

    def __proc_start(self):
        """ ParusModInf process STARTED connected function. """
        self.__proc_run = True
        self.__switch_proc_btn()
        self.ctrl_enable(False)
        self.statBar.showMessage("Parus data inference started")

    def __proc_finish(self):
        """ ParusModInf process FINISHED connected function. """
        # Reset button
        self.__proc_run = False
        self.ctrl_enable(True)
        self.__switch_proc_btn()
        # Display status
        if self._proc.fin_stop:
            # Save current successful execution params
            self.__save_params()
            self.statBar.showMessage("Data inference successfully finished")
        else:
            self.statBar.showMessage("Data inference terminated")

    # Control element related functions ------------------------------------------------------------------------------ #
    def __load_params(self):
        """ Load GUI settings from previous execution. """
        par_json = os.path.join(pkg_data, '_inf_params.json')
        if os.path.isfile(par_json):
            # Load previous settings
            with open(par_json, 'r') as fp:
                pars = json.load(fp)
            # Set to current controls
            self.ckptLine.setText(pars['model_checkpoint'])
            self.ovlpSpinbox.setValue(pars['overlap_length'])
            self.tmemCheckbox.setChecked(pars['to_memory'])
            self.btszSpinbox.setValue(pars['batch_size'])
            self.clvlCombo.setCurrentIndex(pars['compression_level'])

    def __save_params(self):
        """ Save GUI settings of current execution. """
        pars = {}  # INIT VAR
        # Read current controls
        pars['model_checkpoint'] = self.ckptLine.text()
        pars['overlap_length'] = self.ovlpSpinbox.value()
        pars['to_memory'] = self.tmemCheckbox.isChecked()
        pars['batch_size'] = self.btszSpinbox.value()
        pars['compression_level'] = self.clvlCombo.currentIndex()
        # Save to file
        with open(os.path.join(pkg_data, '_inf_params.json'), 'w') as fp:
            json.dump(pars, fp, indent=2)

    def __set_data_file(self):
        """ Add file(s) to file selection table. """
        stat, self.lst_file, self._sel_file = table_loader(
            self.inputTable, self.lst_file, self._sel_file, mode='file', caption="Select Data File(s)",
            flt="Signal Files (*.hdf *.h5 *.hdf5 *.he5)", func=self.set_proc_args, parent=self)
        self.statBar.showMessage(stat)
        # Update process arguments
        self.set_proc_args()

    def __set_data_path(self):
        """ Add directory to file selection table. """
        stat, self.lst_dirs, self._sel_dirs = table_loader(
            self.inputTable, self.lst_dirs, self._sel_dirs, mode='path', caption="Select Data Folder",
            func=self.set_proc_args, parent=self)
        self.statBar.showMessage(stat)
        # Update process arguments
        self.set_proc_args()

    def __set_selc(self, mode):
        """ Selection quick access buttons attached function. """
        stat = selection_operator(self._sel_file + self._sel_dirs, mode)
        self.statBar.showMessage(stat)
        # Update process arguments
        self.set_proc_args()

    def __sel_mod_ckpt(self):
        """ Select model trained weight file (*.ckpt). """
        mta = path_selector(self.ckptLine, mode='file', caption="Select Model Trained Weights",
                            flt="Checkpoint (*.ckpt)", parent=self)
        if mta is None:
            self.ckpt = None
            self.statBar.showMessage("Model trained weights file selection cancelled")
        else:
            self.ckpt = [mta]
            self.statBar.showMessage("Model trained weights file selected")
        # Update process arguments
        self.set_proc_args()

    def __set_mod_ckpt(self):
        """ Set model trained weight file (*.ckpt). """
        mta = self.ckptLine.text()
        if os.path.isfile(mta):
            self.ckpt = [mta]
            self.statBar.showMessage("Model trained weights file set")
        else:
            self.ckpt = None
            self.statBar.showMessage("Model trained weights file is invalid!")
        # Update process arguments
        self.set_proc_args()

    def __set_ovlp_len(self):
        """ Set sample overlapping length. """
        ovlp = self.ovlpSpinbox.value()
        self.ovlp = ['-lp', str(ovlp)]
        # Update process arguments
        self.set_proc_args()
        return self.ovlp

    def __set_to_mem(self):
        """ Set to load whole file directly to system memory. """
        self.tmem = ['-tm'] if self.tmemCheckbox.isChecked() else []
        # Update process arguments
        self.set_proc_args()
        return self.tmem

    def __set_bat_size(self):
        """ Set model process batch size. """
        btsz = self.btszSpinbox.value()
        self.btsz = ['-bs', str(btsz)]
        # Update process arguments
        self.set_proc_args()
        return self.btsz

    def __set_comp_lvl(self):
        """ Set output file data compression level. """
        clvl = self.clvlCombo.currentIndex()
        self.clvl = ['-cp', str(clvl)]
        # Update process arguments
        self.set_proc_args()
        return self.clvl


class ParusSrt(QtWidgets.QMainWindow, Ui_ParusSrtWindow):
    def __init__(self, parent=None):
        """ Parus spike sorting window.

        Args:
            parent: Parent window or widget
        """
        # Initialize GUI
        super(ParusSrt, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_dat.ico"))
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        cs_dark() and self.signalScrollBar.setStyleSheet('')
        # Timer initialization
        self.__timer_val = -1
        # Set file table view
        self.inputTable.setColumnWidth(0, 50)
        self.inputTable.setColumnWidth(1, 50)
        self.inputTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        # Set cell table view
        self.spkCidTable.setColumnWidth(0, 40)
        self.spkCidTable.setColumnWidth(1, 70)
        self.spkCidTable.setColumnWidth(2, 60)
        self.spkCidTable.setColumnWidth(3, 40)
        self.spkCidTable.setColumnWidth(4, 60)
        self.spkCidTable.setColumnWidth(5, 60)
        self.spkCidTable.setColumnWidth(6, 60)
        self.spkCidTable.setColumnWidth(7, 60)
        self.spkCidTable.setColumnWidth(8, 60)
        self.spkCidTable.setColumnWidth(9, 40)
        self.spkCidTable.setColumnWidth(10, 60)
        self.spkCidTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)

        # File control variables
        self.lst_file = []
        self._sel_file = []
        self._act_file = None
        # Data variables
        self.raw = None
        self.spk = None
        self.t = None
        # Process variables
        self.meth = {}  # Clustering method
        self.th = {}  # Detection threshold
        self.k = {}  # Grouping K value
        self.asp = {}  # Anterior samples
        self.psp = {}  # Posterior samples
        self.beta = {}  # Peak component beta factor
        self.min_cnt = self.minCutSpinbox.value()  # Minimum spikes required to save
        # Results variables
        self.clst = {}  # Spike clusters
        self.avgw = {}  # Spike mean waveform
        self.idcs = {}  # Spike cell name
        self.selc = {}  # Cluster selection
        self.__has_res = False  # Has processed results flag
        # Process control variables
        self._sel_cid = []  # Selected cluster
        self._mrg_cid = []  # Merge cluster
        self._cmp_cid = []  # Compare cluster
        self._cmp_lst = []  # Compare list
        self.__igrp = []  # Index to group mapping
        self.__arg_set = False

        # Data process variables
        self.__single = True  # Single file mode flag
        self.__save = False  # Single file save mode flag
        self.__avg_cor_table = []  # Averaged cluster waveform correlation table widget references
        # Data process thread
        self._proc_thread = self._DataProcThread(self)
        self._proc_thread.finished.connect(self.__proc_finalize)
        # Disable process related control
        self.clsMethBox.setEnabled(False)
        self.detThSpinbox.setEnabled(False)
        self.kValSlider.setEnabled(False)
        self.kValSpinbox.setEnabled(False)
        self.sampAntSpinbox.setEnabled(False)
        self.sampPstSpinbox.setEnabled(False)
        self.betaSpinbox.setEnabled(False)
        self.actProcButton.setEnabled(False)
        self.actSaveButton.setEnabled(False)
        self.spkMrgButton.setEnabled(False)

        # Create plot colour map
        cplt = ['#ebac23', '#b80058', '#008cf9', '#006e00', '#00bbad', '#d163e6', '#b24502', '#ff9287', '#5954d6',
                '#00c6f8', '#878500', '#00a76c', '#f6da9c', '#ff5caa', '#8accff', '#4bff4b', '#6efff4', '#edc1f5',
                '#feae7c', '#ffc8c3', '#bdbbef', '#bdf2ff', '#fffc43', '#65ffc8']
        self.cmap = LoopedColormap(cplt, name='ParusClstCmap')
        # Plot control variables
        self._ch = 0
        self.__ch_t = 0
        self._cfv = None  # Feature plot main class

        # Control connections
        self.prbButton.clicked.connect(self.__sel_prb)
        self.prbLine.textChanged.connect(self.__set_prb)
        self.addFileButton.clicked.connect(self.__set_data_file)
        self.addPathButton.clicked.connect(self.__set_data_path)
        self.selAllButton.clicked.connect(lambda: self.__set_selc('all'))
        self.selNonButton.clicked.connect(lambda: self.__set_selc('non'))
        self.selInvButton.clicked.connect(lambda: self.__set_selc('inv'))
        self.inputTable.itemSelectionChanged.connect(self.__set_highlight_idx)
        self.actFileBox.currentIndexChanged.connect(self.__set_highlight_row)
        self.spkWfmBox.currentIndexChanged.connect(self.__set_spk_wfm)
        self.clsMethBox.currentIndexChanged.connect(self.__set_clst_meth)
        self.detThSpinbox.valueChanged.connect(self.__set_det_th)
        self.kValSlider.valueChanged.connect(self.__set_kval_sld)
        self.kValSpinbox.valueChanged.connect(self.__set_kval_spb)
        self.sampAntSpinbox.valueChanged.connect(self.__set_ant_samp)
        self.sampPstSpinbox.valueChanged.connect(self.__set_pst_samp)
        self.betaSpinbox.valueChanged.connect(self.__set_amp_beta)
        self.minCutSpinbox.valueChanged.connect(self.__set_min_cut)
        self.spkMrgButton.clicked.connect(self.__spk_merge)
        self.actProcButton.clicked.connect(self.__proc_actfile_spksrt)
        self.actSaveButton.clicked.connect(self.__proc_actfile_save)
        self.allPrsvButton.clicked.connect(self.__proc_selfile)
        self.actChnBox.currentIndexChanged.connect(self.__set_act_chn)
        self.spkCidTable.itemSelectionChanged.connect(self.__set_act_cid)
        self.spkCidTable.cellChanged.connect(self.__set_cell_name)
        self.avgCorTab.currentChanged.connect(self.__set_wfm_grp)
        self.signalScrollBar.valueChanged.connect(self.__signal_scroll)
        self.sigTypButton.clicked.connect(self.__signal_switch)

    def timerEvent(self, event):
        """ Timer event for canvas updating. """
        self.killTimer(self.__timer_val)
        self.__timer_val = -1
        if self._cfv is not None:
            self._cfv.chn_feat.set_time(self.__ch_t)

    def keyPressEvent(self, event):
        """ Main window keyboard inputs. """
        # Cell selection escape key
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.spkCidTable.clearSelection()
        # Plot navigation keys
        elif event.key() == QtCore.Qt.Key.Key_Left:
            if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() - 1)
            elif event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() - 10)
            elif event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() - 20)
            else:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() - 5)
        elif event.key() == QtCore.Qt.Key.Key_Right:
            if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() + 1)
            elif event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() + 10)
            elif event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() + 20)
            else:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() + 5)
        else:
            QtWidgets.QMainWindow.keyPressEvent(self, event)

    def closeEvent(self, event):
        """ Close function. """
        if self.__has_res:
            reply = QtWidgets.QMessageBox.warning(
                self, "Sorting Results", "Spike sorting have been processed\nDo you want to exit?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                event.ignore()
                return
        if self._cfv is not None:
            self._cfv.close()

    def ctrl_enable(self, enable=True):
        """ Set enable status of controls.

        Args:
            enable (bool): Enable status of controls (default: True)
        """
        self.addFileButton.setEnabled(enable)
        self.addPathButton.setEnabled(enable)
        self.selAllButton.setEnabled(enable)
        self.selNonButton.setEnabled(enable)
        self.selInvButton.setEnabled(enable)
        self.prbLine.setEnabled(enable)
        self.prbButton.setEnabled(enable)
        self.spkWfmBox.setEnabled(enable)
        self.clsMethBox.setEnabled(enable)
        self.detThSpinbox.setEnabled(enable)
        self.kValSlider.setEnabled(enable)
        self.kValSpinbox.setEnabled(enable)
        self.sampAntSpinbox.setEnabled(enable)
        self.sampPstSpinbox.setEnabled(enable)
        self.betaSpinbox.setEnabled(enable)
        self.minCutSpinbox.setEnabled(enable)
        self.actProcButton.setEnabled(enable)
        self.actSaveButton.setEnabled(enable)
        self.allPrsvButton.setEnabled(enable)
        # Disable table selection checkboxes
        for cb in self._sel_file + self._sel_cid + self._mrg_cid + self._cmp_cid:
            cb.setEnabled(enable)

    # Data process members ------------------------------------------------------------------------------------------- #
    class _DataProcThread(QtCore.QThread):
        single = True  # Single file mode flag
        save = False  # Single file save mode flag

        def __init__(self, parent):
            """ Data process independent thread.

            Args:
                parent (ParusSrt):
            """
            super(ParusSrt._DataProcThread, self).__init__(parent)
            self.parent = parent
            self.success = True  # Process success flag

        def run(self):
            self.success = False  # RESET FLAG
            if self.save:
                self.proc_save()
            elif self.single:
                self.proc_single()
            else:
                self.proc_multi()

        def proc_single(self):
            """ Process spike sorting on active file. """
            # Validate file
            file = self.parent.inputTable.item(self.parent.inputTable.currentRow(), 2).text()
            if not os.path.isfile(file):
                return
            self.parent._act_file = file
            # Load data
            with h5.File(file, 'r') as fp:
                data = h5_load_dat(fp)
            self.parent.raw = data['raw']
            self.parent.spk = data['spk']
            self.parent.t = np.arange(len(self.parent.raw[0])) / data['frq']
            self.parent._ch = 0

            # Spike sorting
            self.parent.clst = {}  # RESET VAR
            self.parent.avgw = {}  # RESET VAR
            self.parent.idcs = {}  # RESET VAR
            self.parent.selc = {}  # RESET VAR
            for w in self.parent.spk:
                # Get arguments
                meth = self.parent.meth.get(w, 0)
                th = self.parent.th.get(w, -50)
                asp = self.parent.asp.get(w, 5)
                psp = self.parent.psp.get(w, 5)
                k = self.parent.k.get(w, 0.8)
                beta = self.parent.beta.get(w, 0.5)
                # Set variable
                self.parent.clst[w] = []
                self.parent.avgw[w] = []
                self.parent.idcs[w] = []
                self.parent.selc[w] = []
                for i in self.parent.spk[w]:
                    # Detect and cluster spikes
                    pos = sig_peak_fwd(i, th)
                    pos = pos_ripple_flt(i, pos, 3, True)  # Ripple filtering
                    if meth == 0:
                        cls, avg = cls_cosamp_blk(i, pos, asp, psp, k=k, beta=beta)
                    else:
                        cls, avg = cls_crscor_blk(i, pos, asp, psp, k=k)
                    # Sort clusters by size
                    sid = np.argsort([len(i) for i in cls], stable=True)[::-1]
                    self.parent.clst[w].append([cls[i] for i in sid])
                    self.parent.avgw[w].append([avg[i] for i in sid])
                    self.parent.idcs[w].append(["%s_%02d" % (w, i + 1) for i in range(len(sid))])
                    self.parent.selc[w].append([len(cls[i]) > self.parent.min_cnt for i in sid])
            # Set flag
            self.success = True

        def proc_save(self):
            """ Save result to single file. """
            fp = h5.File(self.parent._act_file, 'r+')
            if 'pos' in fp:
                del fp['pos']
            grp = fp.create_group('pos')
            for w in self.parent.clst:
                wfm = grp.create_group(w)
                for c in range(len(self.parent.clst[w])):
                    chn = wfm.create_group(str(c))
                    for i, v in enumerate(self.parent.clst[w][c]):
                        if self.parent.selc[w][c][i]:
                            name = self.parent.idcs[w][c][i]
                            dat = np.zeros_like(self.parent.t, dtype=np.int8)
                            dat[v] = 1
                            chn.create_dataset(name=name, data=dat, compression="gzip", compression_opts=9)
            fp.close()
            # Set flag
            self.success = True

        def proc_multi(self):
            """ Process spike sorting and saving on all selected file. """
            # Load data
            for cb in self.parent._sel_file:
                if cb.isChecked():
                    fp = h5.File(cb.id, 'r+')
                    data = h5_load_dat(fp)
                    spk = data['spk']

                    # Spike sorting
                    clst = {}  # RESET VAR
                    for w in spk:
                        # Get arguments
                        meth = self.parent.meth.get(w, 0)
                        th = self.parent.th.get(w, -50)
                        asp = self.parent.asp.get(w, 5)
                        psp = self.parent.psp.get(w, 5)
                        k = self.parent.k.get(w, 0.8)
                        beta = self.parent.beta.get(w, 0.5)
                        # Set variable
                        clst[w] = []
                        for i in spk[w]:
                            # Detect and cluster spikes
                            pos = sig_peak_fwd(i, th)
                            pos = pos_ripple_flt(i, pos, 3, True)  # Ripple filtering
                            if meth == 0:
                                cls, _ = cls_cosamp_blk(i, pos, asp, psp, k=k, beta=beta)
                            else:
                                cls, _ = cls_crscor_blk(i, pos, asp, psp, k=k)
                            # Sort clusters by size
                            sid = np.argsort([len(i) for i in cls], stable=True)[::-1]
                            clst[w].append([cls[i] for i in sid if len(cls[i]) >= self.parent.min_cnt])

                    # Write file
                    if 'pos' in fp:
                        del fp['pos']
                    grp = fp.create_group('pos')
                    for w in clst:
                        wfm = grp.create_group(w)
                        for c in range(len(clst[w])):
                            chn = wfm.create_group(str(c))
                            for i, v in enumerate(clst[w][c]):
                                name = '%s_%02d' % (w, i + 1)
                                dat = np.zeros_like(spk[w][c], dtype=np.int8)
                                dat[v] = 1
                                chn.create_dataset(name=name, data=dat, compression="gzip", compression_opts=9)
                    fp.close()
            # Set flag
            self.success = True

    def __proc_actfile_spksrt(self):
        """ Process single activated file. """
        self.__single = True
        self.__save = False
        self._proc_thread.single = True
        self._proc_thread.save = False
        self.ctrl_enable(False)
        self._proc_thread.start()

    def __proc_actfile_save(self):
        """ Save single activated file. """
        self.__single = True
        self.__save = True
        self._proc_thread.single = True
        self._proc_thread.save = True
        self.ctrl_enable(False)
        self._proc_thread.start()

    def __proc_selfile(self):
        """ Process all selected file. """
        self.__single = False
        self.__save = False
        self._proc_thread.single = False
        self._proc_thread.save = False
        self.ctrl_enable(False)
        self._proc_thread.start()

    def __proc_finalize(self):
        """ Data process finalized connected function. """
        self.ctrl_enable(True)
        if self.__save:
            if self._proc_thread.success:
                self.__has_res = False
                self.statBar.showMessage("File [%s] successfully saved" % self._act_file)
            else:
                self.statBar.showMessage("Error when saving file [%s]" % self._act_file)
                QtWidgets.QMessageBox.critical(self, "Error", "Error when saving file [%s]" % self._act_file,
                                               QtWidgets.QMessageBox.StandardButton.Yes)
        elif self.__single:
            if self._proc_thread.success:
                self.__has_res = True
                # Set GUI items
                self.actChnBox.blockSignals(True)
                self.actChnBox.clear()
                [self.actChnBox.addItem("CH-%03d" % i) for i in range(self.raw.shape[0])]
                self.actChnBox.blockSignals(False)
                self.signalScrollBar.blockSignals(True)
                self.__update_scroll_bar()
                self.signalScrollBar.setValue(0)
                self.signalScrollBar.blockSignals(False)
                self.actSaveButton.setEnabled(True)
                # Set figures
                if self._cfv is None:
                    self._cfv = ClstFeatViewer(self.raw, self.spk, self.t, self.asp, self.psp, self.clst,
                                               self.min_cnt, self.cmap)
                    self.chnFeatLayout.addWidget(self._cfv.chn_feat)
                    self.grpFeatLayout.addWidget(self._cfv.grp_feat)
                    self.spkFeatLayout.addWidget(self._cfv.spk_feat)
                else:
                    self._cfv.reload_data(self.raw, self.spk, self.t, self.asp, self.psp, self.clst, self.min_cnt)
                # Update tables
                self.update_spkcid_table()
                self.update_avgcor_table()
                # Show message
                self.statBar.showMessage("File [%s] processed" % self._act_file)
            else:
                self.statBar.showMessage("Failed to process file [%s]" % self._act_file)
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to process file [%s]" % self._act_file,
                                               QtWidgets.QMessageBox.StandardButton.Yes)
        else:
            if self._proc_thread.success:
                self.__has_res = False
                self.statBar.showMessage("All selected file processed")
            else:
                self.statBar.showMessage("Error occurred when process files")
                QtWidgets.QMessageBox.critical(self, "Error", "Error occurred when process files\nPlease check inputs",
                                               QtWidgets.QMessageBox.StandardButton.Yes)

    def update_spkcid_table(self):
        """ Update single cell spike information table. """
        # Clear previous table
        self.spkCidTable.setRowCount(0)
        self._sel_cid = []  # RESET VAR
        self._mrg_cid = []  # RESET VAR
        self._cmp_cid = []  # RESET VAR
        self._cmp_lst = []  # RESET VAR
        self.__igrp = []
        row = 0
        # Load new values
        self.spkCidTable.blockSignals(True)
        for n, w in enumerate(self.clst):
            for i in range(len(self.clst[w][self._ch])):
                # Compute features
                tpt = self.t[self.clst[w][self._ch][i]]
                cnt = self.clst[w][self._ch][i].size
                amp = abs(np.mean(self.spk[w][self._ch][self.clst[w][self._ch][i]]).item())
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    frq = tpt_spk_frq(tpt, org=self.t[0].item(), end=self.t[-1].item())
                    isi = tpt_spk_isi(tpt, org=self.t[0].item(), end=self.t[-1].item()) * 1000  # To millisecond
                    cv = tpt_spk_cv(tpt, org=self.t[0].item(), end=self.t[-1].item())
                    cv2 = tpt_spk_cv2(tpt, org=self.t[0].item(), end=self.t[-1].item())
                # Set table
                cid = self.idcs[w][self._ch][i]
                self.spkCidTable.insertRow(row)
                curr_sel = CellCheckbox(identifier=[cid, w, i], checked=self.selc[w][self._ch][i], func=self.__clst_sel)
                self._sel_cid.append(curr_sel)
                self.spkCidTable.setCellWidget(row, 0, curr_sel)
                self.spkCidTable.setItem(row, 1, CellData(cid, aln='c', emp='b'))
                self.spkCidTable.setItem(row, 2, CellData(str(cnt), aln='c', ro=True))
                curr_mrg = CellCheckbox(identifier=[cid, w, i, row], checked=False, func=self.__chk_merge)
                self._mrg_cid.append(curr_mrg)
                self.spkCidTable.setCellWidget(row, 3, curr_mrg)
                self.spkCidTable.setItem(row, 4, CellData("%.4f" % amp, aln='r', ro=True))
                self.spkCidTable.setItem(row, 5, CellData("%.4f" % frq, aln='r', ro=True))
                self.spkCidTable.setItem(row, 6, CellData("%.4f" % isi, aln='r', ro=True))
                self.spkCidTable.setItem(row, 7, CellData("%.4f" % cv, aln='r', ro=True))
                self.spkCidTable.setItem(row, 8, CellData("%.4f" % cv2, aln='r', ro=True))
                curr_cmp = CellCheckbox(identifier=[cid, w, i, [self._ch]], checked=False, func=self.__spk_corwfm)
                self._cmp_cid.append(curr_cmp)
                self.spkCidTable.setCellWidget(row, 9, curr_cmp)
                itm_clr = CellData("", bkg=tuple([round(c * 255) for c in self.cmap(row)[:3]]), ro=True)
                itm_clr.setFlags(~QtCore.Qt.ItemFlag.ItemIsSelectable)
                self.spkCidTable.setItem(row, 10, itm_clr)
                self.spkCidTable.setItem(row, 11, CellData("[%s] - %d" % (w, self._ch), aln='c', ro=True))
                # Counter
                self.__igrp.append([n, i])
                row += 1
        self.spkCidTable.blockSignals(False)

    def update_avgcor_table(self):
        """ Update averaged spike waveform correlation table. """
        self.avgCorTab.blockSignals(True)
        # Clear previous tab
        self.avgCorTab.clear()
        [wdg.deleteLater() for wdg in self.__avg_cor_table]
        self.__avg_cor_table = []
        # Set table
        cmap = mpl.colormaps['viridis']  # Colour-blind safe purple-green colormap
        for w in self.avgw:
            # Set new widgets
            table = QtWidgets.QTableWidget(parent=self.avgCorTab)
            self.__avg_cor_table.append(table)
            # Add widgets to UI
            self.avgCorTab.addTab(table, w)
            if self.avgw[w][self._ch]:
                # Compute correlations
                mat = post_cls_chk(self.avgw[w][self._ch], mode='cosamp')
                # Set table structure
                n_row, n_col = mat.shape
                table.setColumnCount(n_col)
                if n_col > 10:
                    table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
                else:
                    table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
                table.setRowCount(n_row)
                table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
                # Set table data
                for r in range(n_row):
                    for c in range(n_col):
                        val = mat[r, c]
                        txt = "%.2f" % abs(val)
                        clr = (255, 127, 14) if val < 0 else (255, 255, 255)  # Orange for negative value
                        bkg = tuple([round(i * 255) for i in cmap(val * 0.78125)[:3]])  # 0.78125=200/256, max in green
                        table.setItem(r, c, CellData(txt, size=9, emp='b', clr=clr, bkg=bkg, ro=True))
            else:
                table.setColumnCount(1)
                table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
                table.setRowCount(1)
                table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
                table.setItem(0, 0, CellData("No Spike", ro=True))
        self.avgCorTab.blockSignals(False)

    def __sel_prb(self):
        """ Select probe file button connected function. """
        path_selector(self.prbLine, mode='file', caption="Select Probe File", flt="Probe Geometry (*.prb)", parent=self)

    def __set_prb(self):
        """ Set defined probe geometry file. """
        prb_file = self.prbLine.text()
        chk_path = os.path.isfile(prb_file)
        chk_type = prb_file.endswith('.prb')
        if chk_path and chk_type:
            pass
        else:
            pass

    def __clst_sel(self):
        """ Cluster selection list. """
        for cb in self._sel_cid:
            self.selc[cb.id[1]][self._ch][cb.id[2]] = cb.isChecked()

    def __chk_merge(self):
        """ Spike merge checkbox linked function, validate merge option. """
        # Get list
        chk_lst = []
        for cb in self._mrg_cid:
            if cb.isChecked():
                chk_lst.append(cb.id[1])  # Get group
        # Check group
        self.spkMrgButton.setEnabled(len(chk_lst) > 1)
        if len(set(chk_lst)) > 1:
            QtWidgets.QMessageBox.warning(self, "Cross Waveform Merge", "Select cells are in different waveform\n"
                                                                        "Please check if the selections are correct",
                                          QtWidgets.QMessageBox.StandardButton.Yes)

    def __spk_merge(self):
        """ Merge spikes. """
        # Get list
        new_clst = []
        len_lst = []
        mrg_lst = []
        for cb in self._mrg_cid:
            if cb.isChecked():
                clst = self.clst[cb.id[1]][self._ch][cb.id[2]]
                new_clst.append(clst)
                len_lst.append(clst.size)
                mrg_lst.append(cb.id)
        # Sort and merge cluster
        idx = np.argsort(len_lst, stable=True)[-1]
        gw = mrg_lst[idx][1]
        gi = mrg_lst[idx][2]
        new_clst = np.sort(np.concatenate(new_clst), stable=True)
        self.clst[gw][self._ch][gi] = new_clst.copy()
        # Compute new average, recompute all due to the possible cross waveform merge
        num = self.asp.get(gw, 5) + self.psp.get(gw, 5) + 1
        blk = np.arange(-self.asp.get(gw, 5), self.psp.get(gw, 5) + 1, step=1, dtype=int)
        avg_idx = np.repeat(new_clst, num) + np.tile(blk, len(new_clst))
        avg_idx = np.clip(avg_idx, a_min=0, a_max=len(self.t) - 1).reshape(-1, num, order='C')
        self.avgw[gw][self._ch][gi] = np.mean(self.spk[gw][self._ch][avg_idx], axis=0)
        # Remove merged spikes
        mrg_lst.pop(idx)
        for i in reversed(mrg_lst):
            self.clst[i[1]][self._ch].pop(i[2])
            self.avgw[i[1]][self._ch].pop(i[2])
            self.idcs[i[1]][self._ch].pop(i[2])
            self.selc[i[1]][self._ch].pop(i[2])
            self._sel_cid.pop(i[3])
            self._mrg_cid.pop(i[3])
            self._cmp_cid.pop(i[3])
            self.spkCidTable.removeRow(i[3])
        # Update widgets
        self.update_spkcid_table()
        self.update_avgcor_table()
        if self._cfv is not None:
            self._cfv.update_cluster(self.clst)

    def __spk_corwfm(self):
        """ Plot spike correlation waveforms. """
        # Get checked item
        for cb in self._cmp_cid:
            if cb.isChecked() and (cb not in self._cmp_lst):
                self._cmp_lst.append(cb)
            if (not cb.isChecked()) and (cb in self._cmp_lst):
                self._cmp_lst.remove(cb)
        # Limit checked item length to 2
        for cb in self._cmp_lst[:-2]:
            cb.setChecked(False)
        self._cmp_lst = self._cmp_lst[-2:]
        # Trigger plot
        if len(self._cmp_lst) == 0:
            self._cfv.spk_feat.plot_correlogram(None, None)
            self._cfv.spk_feat.plot_spksamp(None, wfm=None, chs=None)
        elif len(self._cmp_lst) == 1:
            t, w, i, c = self._cmp_lst[0].id
            tx = "%s(%s)" % (t, w)
            px = self.t[self.clst[w][self._ch][i]]
            self._cfv.spk_feat.plot_correlogram(px, None, tx)
            self._cfv.spk_feat.plot_spksamp(self.clst[w][self._ch][i], wfm=w, chs=c, name=tx)
        else:
            t, w, i, c = self._cmp_lst[0].id
            tx = "%s(%s)" % (t, w)
            px = self.t[self.clst[w][self._ch][i]]
            self._cfv.spk_feat.plot_spksamp(self.clst[w][self._ch][i], wfm=w, chs=c, name=tx)
            t, w, i = self._cmp_lst[1].id[:3]
            ty = "%s(%s)" % (t, w)
            py = self.t[self.clst[w][self._ch][i]]
            self._cfv.spk_feat.plot_correlogram(px, py, tx, ty)

    def __set_cell_name(self, row, col):
        """ Set name for detected cell. """
        # Check conflicts in defined name
        name = self.spkCidTable.item(row, col).text()
        w = self._sel_cid[row].id[1]
        i = 2
        while name in self.idcs[w][self._ch]:
            name += "_n%02d" % i
            i += 1
        self.spkCidTable.blockSignals(True)
        self.spkCidTable.item(row, col).setText(name)
        self.spkCidTable.blockSignals(False)
        # Update variables
        self._sel_cid[row].id[0] = name
        self.idcs[w][self._ch][self._sel_cid[row].id[2]] = name
        self._mrg_cid[row].id[0] = name
        self._cmp_cid[row].id[0] = name
        if self._cmp_cid[row] in self._cmp_lst:
            self.__spk_corwfm()

    # File input table functions ------------------------------------------------------------------------------------- #
    def __set_data_file(self):
        """ Add file(s) to file selection table. """
        stat, self.lst_file, self._sel_file = table_loader(
            self.inputTable, self.lst_file, self._sel_file, mode='file', caption="Select Data File(s)",
            flt="Result Files (*.h5)", parent=self)
        self.statBar.showMessage(stat)
        # Update active file combobox
        item = [str(i) for i in range(self.actFileBox.count(), self.inputTable.rowCount() + 1)]
        self.actFileBox.addItems(item)

    def __set_data_path(self):
        """ Add directory to file selection table. """
        stat, self.lst_file, self._sel_file = table_loader(
            self.inputTable, self.lst_file, self._sel_file, mode='path', caption="Select Data Folder",
            flt="Result Files (*.h5)", listdir=True, parent=self)
        self.statBar.showMessage(stat)
        # Update active file combobox
        item = [str(i) for i in range(self.actFileBox.count(), self.inputTable.rowCount() + 1)]
        self.actFileBox.addItems(item)

    def __set_selc(self, mode):
        """ Selection quick access buttons attached function. """
        stat = selection_operator(self._sel_file, mode)
        self.statBar.showMessage(stat)

    def __set_highlight_row(self):
        """ Set file input table highlight row. """
        idx = self.actFileBox.currentIndex()
        if idx == 0:
            # Clear input table selection
            self.inputTable.blockSignals(True)
            self.inputTable.clearSelection()
            self.inputTable.blockSignals(False)
            # Clear waveform combobox
            self.__load_spkwfm_box(clear=True)
            # Disable button
            self.actProcButton.setEnabled(False)
        else:
            self.inputTable.blockSignals(True)
            self.inputTable.selectRow(idx - 1)
            self.inputTable.blockSignals(False)
            self.actProcButton.setEnabled(True)
            # Read info
            self.__load_spkwfm_box(clear=False)

    def __set_highlight_idx(self):
        """ Set file input table highlight row. """
        if self.inputTable.selectedItems():
            self.actFileBox.blockSignals(True)
            self.actFileBox.setCurrentIndex(self.inputTable.currentRow() + 1)
            self.actFileBox.blockSignals(False)
            self.actProcButton.setEnabled(True)
            # Read info
            self.__load_spkwfm_box(clear=False)
        else:
            # Set file combobox index
            self.actFileBox.blockSignals(True)
            self.actFileBox.setCurrentIndex(0)
            self.actFileBox.blockSignals(False)
            # Clear waveform combobox
            self.__load_spkwfm_box(clear=True)
            # Disable button
            self.actProcButton.setEnabled(False)

    def __load_spkwfm_box(self, clear=False):
        """ Load active file information to [spkWfmBox].

        Args:
            clear (bool): Clear only flag
        """
        # Disable linked controls
        self.clsMethBox.setEnabled(False)
        self.detThSpinbox.setEnabled(False)
        self.kValSlider.setEnabled(False)
        self.kValSpinbox.setEnabled(False)
        self.sampAntSpinbox.setEnabled(False)
        self.sampPstSpinbox.setEnabled(False)
        self.betaSpinbox.setEnabled(False)
        # Clear indicator
        self.__set_arg_stat(False)
        # Load box
        self.spkWfmBox.blockSignals(True)
        self.spkWfmBox.clear()
        if not clear:
            file = self.inputTable.item(self.inputTable.currentRow(), 2).text()
            with h5.File(file, 'r') as fp:
                if 'raw' not in fp:
                    QtWidgets.QMessageBox.critical(
                        self, "Invalid Data", "File [%s] missing raw data\nPlease check if the file is correct" % file,
                        QtWidgets.QMessageBox.StandardButton.Yes)
                elif 'spk' not in fp:
                    QtWidgets.QMessageBox.critical(
                        self, "Raw Data", "File [%s] only containing raw data\nPerform model inference first" % file,
                        QtWidgets.QMessageBox.StandardButton.Yes)
                else:
                    [self.spkWfmBox.addItem(k) for k in fp['spk'].keys()]
                    # Enable linked controls
                    self.clsMethBox.setEnabled(True)
                    self.detThSpinbox.setEnabled(True)
                    self.kValSlider.setEnabled(True)
                    self.kValSpinbox.setEnabled(True)
                    self.sampAntSpinbox.setEnabled(True)
                    self.sampPstSpinbox.setEnabled(True)
                    self.betaSpinbox.setEnabled(True)
        self.spkWfmBox.setCurrentIndex(-1)
        self.spkWfmBox.blockSignals(False)
        # Emit signal
        self.spkWfmBox.setCurrentIndex(0)

    # Spike clustering arguments ------------------------------------------------------------------------------------- #
    def __set_arg_stat(self, stat=True):
        """ Set clustering arguments defining status of current spike waveform.

        Args:
            stat (bool): Status to set
        """
        if self.__arg_set == stat:
            return
        else:
            self.__arg_set = stat
            if stat:
                self.argStatus.setStyleSheet('QLineEdit {background:#2ca02c; color:#ffffff}')
                self.argStatus.setText('D')
                self.argStatus.setToolTip("Clustering arguments definition status\nCurrent: [Using Customized]")
            else:
                self.argStatus.setStyleSheet('QLineEdit {background:#bcbd22; color:#000000}')
                self.argStatus.setText('U')
                self.argStatus.setToolTip("Clustering arguments definition status\nCurrent: [Using Defaults]")

    def __set_spk_wfm(self):
        """ Select spike waveform for setting arguments. """
        w = self.spkWfmBox.currentText()
        # Set arguments
        self.detThSpinbox.blockSignals(True)
        self.detThSpinbox.setValue(self.th.get(w, -50))
        self.detThSpinbox.blockSignals(False)
        self.kValSlider.blockSignals(True)
        self.kValSlider.setValue(round(self.k.get(w, 0.8) * 100))
        self.kValSlider.blockSignals(False)
        self.kValSpinbox.blockSignals(True)
        self.kValSpinbox.setValue(self.k.get(w, 0.8))
        self.kValSpinbox.blockSignals(False)
        self.sampAntSpinbox.blockSignals(True)
        self.sampAntSpinbox.setValue(self.asp.get(w, 5))
        self.sampAntSpinbox.blockSignals(False)
        self.sampPstSpinbox.blockSignals(True)
        self.sampPstSpinbox.setValue(self.psp.get(w, 5))
        self.sampPstSpinbox.blockSignals(False)
        self.betaSpinbox.blockSignals(True)
        self.betaSpinbox.setValue(self.beta.get(w, 0.5))
        self.betaSpinbox.blockSignals(False)
        # Check if default has been used
        self.__set_arg_stat(any([w in self.th, w in self.k, w in self.asp, w in self.psp, w in self.beta]))

    def __set_clst_meth(self):
        """ Spike clustering method control connected function """
        w = self.spkWfmBox.currentText()
        self.meth[w] = self.clsMethBox.currentIndex()
        # Set indicator
        self.__set_arg_stat(True)

    def __set_det_th(self):
        """ Set spike detection threshold. """
        w = self.spkWfmBox.currentText()
        self.th[w] = self.detThSpinbox.value()
        # Set indicator
        self.__set_arg_stat(True)

    def __set_kval_sld(self):
        """ Set k-value with slider. """
        w = self.spkWfmBox.currentText()
        self.k[w] = self.kValSlider.value() / 100
        # Link k-value spinbox
        self.kValSpinbox.blockSignals(True)
        self.kValSpinbox.setValue(self.k[w])
        self.kValSpinbox.blockSignals(False)
        # Set indicator
        self.__set_arg_stat(True)

    def __set_kval_spb(self):
        """ Set k-value with spinbox. """
        w = self.spkWfmBox.currentText()
        self.k[w] = self.kValSpinbox.value()
        # Link k-value slider
        self.kValSlider.blockSignals(True)
        self.kValSlider.setValue(round(self.k[w] * 100))
        self.kValSlider.blockSignals(False)
        # Set indicator
        self.__set_arg_stat(True)

    def __set_ant_samp(self):
        """ Set anterior sample number. """
        w = self.spkWfmBox.currentText()
        self.asp[w] = self.sampAntSpinbox.value()
        # Set indicator
        self.__set_arg_stat(True)

    def __set_pst_samp(self):
        """ Set posterior sample number. """
        w = self.spkWfmBox.currentText()
        self.psp[w] = self.sampPstSpinbox.value()
        # Set indicator
        self.__set_arg_stat(True)

    def __set_amp_beta(self):
        """ Set amplitude beta factor . """
        w = self.spkWfmBox.currentText()
        self.beta[w] = self.betaSpinbox.value()
        # Set indicator
        self.__set_arg_stat(True)

    def __set_min_cut(self):
        """ Set minimum number of spike required as valid cell. """
        self.min_cnt = self.minCutSpinbox.value()

    # Results visualization functions -------------------------------------------------------------------------------- #
    def __set_act_chn(self):
        """ Set active channel. """
        self._ch = self.actChnBox.currentIndex()
        # Update plots
        self._cfv.set_channel(self._ch)
        self.update_spkcid_table()
        self.update_avgcor_table()
        # Update signal scroll bar with signal blocked
        self.signalScrollBar.blockSignals(True)
        self.signalScrollBar.setValue(0)
        self.signalScrollBar.blockSignals(False)

    def __set_act_cid(self):
        """ Set active cells. """
        if self.spkCidTable.selectedItems():
            idx = list(set(index.row() for index in self.spkCidTable.selectedIndexes()))
            grp = set([self.__igrp[i][0] for i in idx])
            if len(grp) == 1:
                self.avgCorTab.setCurrentIndex(grp.pop())
            self._cfv.set_act_clst(idx)
        else:
            self._cfv.set_act_clst(None)

    def __set_wfm_grp(self):
        """ Set waveform group. """
        self._cfv.grp_feat.set_spk_grp(self.avgCorTab.currentIndex())

    def __update_scroll_bar(self):
        """ Scroll bar limits and step size updater. """
        if abs(self.t[-1] - 0.1) <= 0.005:
            self.signalScrollBar.setMaximum(0)
            self.signalScrollBar.setSingleStep(0)
            self.signalScrollBar.setPageStep(0)
            self.signalScrollBar.setEnabled(False)
        else:
            self.signalScrollBar.setMaximum(int((self.t[-1] - 0.1) * 1000 + 1))
            self.signalScrollBar.setSingleStep(50)
            self.signalScrollBar.setPageStep(100)
            self.signalScrollBar.setEnabled(True)

    def __signal_scroll(self):
        """ Scroll bar motion trigger function. """
        self.__ch_t = self.signalScrollBar.value() / 1000
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(10)

    def __signal_switch(self):
        """ Waveform source switch function. """
        if self._cfv is not None:
            text = self.sigTypButton.text()
            if text == 'Raw':
                self._cfv.chn_feat.switch_fig('spk')
                self.sigTypButton.setText('Spike')
            else:
                self._cfv.chn_feat.switch_fig('raw')
                self.sigTypButton.setText('Raw')


class WfmSel(QtWidgets.QMainWindow, Ui_WfmSelWindow):
    sel_sig = QtCore.Signal(list)  # Channel selection signal

    def __init__(self, key, raw, parent=None):
        """ Result waveform channel selection window.

        Args:
            key (list[str]): Waveform channel name list
            raw (list[bool]): Waveform raw type flag
            parent: Parent window or widget
        """
        # Initialize GUI
        super(WfmSel, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_dat.ico"))
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.__sel_lst = []
        # Generate buttons for each channel
        self.ch_btn = {}
        for i, (k, r) in enumerate(zip(key, raw)):
            if r:
                btn = QtWidgets.QCheckBox(k)
                btn.setObjectName("Ch_%02d" % i)
                btn.setChecked(True)
                self.chRawLayout.addWidget(btn)
                self.ch_btn[i] = btn
                btn.clicked.connect(self.__select_channel)
            else:
                btn = QtWidgets.QCheckBox(k)
                btn.setObjectName("Ch_%02d" % i)
                btn.setChecked(True)
                self.chSpkLayout.addWidget(btn)
                self.ch_btn[i] = btn
                btn.clicked.connect(self.__select_channel)
        # Fix window height
        self.window().setFixedHeight(self.layout().sizeHint().height())

    def emit_sig(self):
        """ Force emit selection signal. """
        self.__select_channel()

    def __select_channel(self):
        """ Verify and send channel selection signal. """
        chk_wfm_lst = []  # INIT VAR
        # Get selection list by check box values
        for k in self.ch_btn:
            if self.ch_btn[k].isChecked():
                chk_wfm_lst.append(self.ch_btn[k].text())
        # Check for null selection
        if not chk_wfm_lst:
            QtWidgets.QMessageBox.warning(self, "Warning", "At least 1 channel required!",
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            # Set to the first waveform
            self.ch_btn[0].setChecked(True)
            self.__sel_lst = [self.ch_btn[0].text()]
        else:
            # Update selection
            self.__sel_lst = chk_wfm_lst
        # Send signal
        self.sel_sig.emit(self.__sel_lst)

    def toggle_channel(self, idx):
        """ Toggle selected channel. """
        if idx < len(self.ch_btn):
            stat = self.ch_btn[idx].isChecked()
            self.ch_btn[idx].setChecked(not stat)
            self.__select_channel()
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Selected channel not exceeding total channels!",
                                          QtWidgets.QMessageBox.StandardButton.Ok)


class ParusRes(QtWidgets.QMainWindow, Ui_ParusResWindow):
    def __init__(self, file, parent=None):
        """ Parus inference results viewing and validation window.

        Args:
            file (str): Parus result HDF5 file
            parent: Parent window or widget
        """
        # Initialize main UI
        super(ParusRes, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_dat.ico"))
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        cs_dark() and self.signalScrollBar.setStyleSheet('')
        self.file = file
        # Timer initialization
        self.__timer_val = -1
        # Key sequence recoder for recoding channel selection
        self.__ch_ks = ''
        # File saving process
        self._save_proc = self.SaveResThread()
        self._save_proc.src = file
        self._save_proc.finished.connect(self.__save_finalize)
        self.__save_msg = ProgBusyDialog(self, "<b>Corrections being saved<br><br>Please wait...</b>")
        self.__safe_close = True  # Check changes before close flag

        # Load and plot data
        self._result = ResPltLoader(file)
        self._toolbar = NavigationToolbar2QT(self._result, self)
        self.signalLayout.addWidget(self._toolbar)
        self.signalLayout.addWidget(self._result)
        self._toolbar.setVisible(False)  # Disable toolbar by default
        # Set file name
        self.fileLine.setText(file.replace('\\', '/'))
        self.setWindowTitle("%s [%s]" % (self.windowTitle(), os.path.basename(file)))
        # Set valid channel names
        [self.actchnComboBox.addItem("CH-%04d" % i) for i in range(self._result.nch)]
        # Set valid position names
        pos_key = sum([[k + ' - ' + p for p in self._result.pos[k]] for k in self._result.pos], [])
        [self.actanoComboBox.addItem(k) for k in pos_key]

        # Set up waveform selection window
        wfm_key = [k for k in self._result.wfm]
        wfm_raw = ['RAW' in k for k in wfm_key]
        self.__wfm_sel_win = WfmSel(wfm_key, wfm_raw, self)
        self.__wfm_sel_win.sel_sig.connect(self.__sel_wfm)
        # Set active waveform to be raw
        self.__act_wfm = 'RAW'
        self._result.set_act_wfm(self.__act_wfm)

        # Set time controls
        self.__upd_time = True  # Plot time range update flag
        self.__t_init = self._result.t[0].item()
        self.__t_stop = self.__t_init + 0.1  # Initial view of 100 milliseconds
        self.__t_all = self._result.t[-1].item() - self._result.t[0].item()  # Maximum time range
        self.xrangeSpinBox.setMaximum(min(self.__t_all, 10) * 1000)  # Max 10 seconds
        self.__update_scroll_bar()
        # Set amplitude controls
        self.yminSpinBox.setMinimum(self._result.ax[0].get_ylim()[0])
        self.yminSpinBox.setValue(self._result.ax[0].get_ylim()[0])
        self.ymaxSpinBox.setMaximum(self._result.ax[0].get_ylim()[1])
        self.ymaxSpinBox.setValue(self._result.ax[0].get_ylim()[1])

        # Set control connection
        self.toolbarBox.clicked.connect(self.__ctrl_mode_switch)
        self.signalScrollBar.valueChanged.connect(self.__signal_scroll)
        self.xrangeSpinBox.valueChanged.connect(self.__update_plot_rng)
        self.yminSpinBox.valueChanged.connect(self.__update_plot_amp)
        self.ymaxSpinBox.valueChanged.connect(self.__update_plot_amp)
        self.actchnComboBox.currentIndexChanged.connect(self.__set_act_chn)
        self.actanoComboBox.currentIndexChanged.connect(self.__set_act_pos)
        self.lnkAnoBox.clicked.connect(self.__toggle_lnk_ano)
        self.wfmselButton.clicked.connect(self.__wfm_sel_win.show)
        self.cxSaveButton.clicked.connect(lambda: self.save_correction(False))
        self.cxSvasButton.clicked.connect(lambda: self.save_correction(True))
        self.cxDiscardButton.clicked.connect(self.__discard_exit)
        # Control key press override
        self.xrangeSpinBox.keyPressEvent = self.__keybypass_xrange
        self.yminSpinBox.keyPressEvent = self.__keybypass_ymin
        self.ymaxSpinBox.keyPressEvent = self.__keybypass_ymax
        self.actchnComboBox.keyPressEvent = self.__keybypass_actchn
        self.actanoComboBox.keyPressEvent = self.__keybypass_actano

    class SaveResThread(QtCore.QThread):
        """ Data process independent thread for file saving. """
        src = None  # Source file
        dst = None  # Destination file
        data = None

        def run(self):
            if (self.src is None) or (self.data is None):
                return
            # Set output path
            if (self.src == self.dst) or (self.dst is None):
                self.dst = self.src  # Make sure the [dst] value is valid
            else:
                shutil.copy2(self.src, self.dst)  # Make copy
            # Write to output file
            fp = h5.File(self.dst, 'r+')
            del fp['pos']  # Delete original position data
            # Save corrected positions
            grp = fp.create_group('pos')
            for k in self.data:
                skg = grp.create_group(k)
                for c in self.data[k]:
                    chg = skg.create_group(c)
                    for p in self.data[k][c]:
                        new_pos = self.data[k][c][p]
                        chg.create_dataset(name=p, data=new_pos, compression="gzip", compression_opts=9)
            # Close file
            fp.close()

    def timerEvent(self, event):
        """ Timer event for canvas updating. """
        self.killTimer(self.__timer_val)
        self.__timer_val = -1
        self.__draw_canvas()

    def closeEvent(self, event):
        """ Window closed cleaning and signaling. """
        if self.__safe_close:
            if self._result.check_correction():
                reply = QtWidgets.QMessageBox.warning(
                    self, "Corrected Results", "Manual corrections have been made\nDo you want to exit?",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.No
                )
                if reply == QtWidgets.QMessageBox.StandardButton.No:
                    event.ignore()
                    return
        self.__save_msg.allow_close = True  # Unblock close lock for dialog
        self.__save_msg.close()  # Close process informing dialog
        self._result.close()  # Close result plot
        event.accept()

    def keyPressEvent(self, event) -> bool:
        """ Main window keyboard inputs. """
        # Plot navigation keys
        if (event.key() == QtCore.Qt.Key.Key_Left) or (event.key() == QtCore.Qt.Key.Key_A):
            if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() - 1)
            elif event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() - 10)
            elif event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() - 20)
            else:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() - 5)
        elif (event.key() == QtCore.Qt.Key.Key_Right) or (event.key() == QtCore.Qt.Key.Key_D):
            if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() + 1)
            elif event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() + 10)
            elif event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() + 20)
            else:
                self.signalScrollBar.setSliderPosition(self.signalScrollBar.sliderPosition() + 5)
        # Recording channel selection
        elif event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
            num_lst = [
                QtCore.Qt.Key.Key_0, QtCore.Qt.Key.Key_1, QtCore.Qt.Key.Key_2, QtCore.Qt.Key.Key_3, QtCore.Qt.Key.Key_4,
                QtCore.Qt.Key.Key_5, QtCore.Qt.Key.Key_6, QtCore.Qt.Key.Key_7, QtCore.Qt.Key.Key_8, QtCore.Qt.Key.Key_9
            ]
            if event.key() in num_lst:
                self.__ch_ks += str(num_lst.index(event.key()))
        elif event.key() == QtCore.Qt.Key.Key_PageUp:
            ch_idx = self.actchnComboBox.currentIndex()
            if ch_idx == 0:
                QtWidgets.QMessageBox.warning(self, "Warning", "The FIRST recoding channel reached!",
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            else:
                self.actchnComboBox.setCurrentIndex(ch_idx - 1)
        elif event.key() == QtCore.Qt.Key.Key_PageDown:
            ch_idx = self.actchnComboBox.currentIndex()
            if ch_idx == (self.actchnComboBox.count() - 1):
                QtWidgets.QMessageBox.warning(self, "Warning", "The LAST recoding channel reached!",
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            else:
                self.actchnComboBox.setCurrentIndex(ch_idx + 1)
        # Waveform toggle key combinations
        elif (event.key() == QtCore.Qt.Key.Key_0) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(0)
        elif (event.key() == QtCore.Qt.Key.Key_1) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(1)
        elif (event.key() == QtCore.Qt.Key.Key_2) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(2)
        elif (event.key() == QtCore.Qt.Key.Key_3) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(3)
        elif (event.key() == QtCore.Qt.Key.Key_4) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(4)
        elif (event.key() == QtCore.Qt.Key.Key_5) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(5)
        elif (event.key() == QtCore.Qt.Key.Key_6) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(6)
        elif (event.key() == QtCore.Qt.Key.Key_7) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(7)
        elif (event.key() == QtCore.Qt.Key.Key_8) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(8)
        elif (event.key() == QtCore.Qt.Key.Key_9) and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(9)
        # Spike annotation keys
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self.actanoComboBox.setCurrentIndex(0)
        elif event.key() == QtCore.Qt.Key.Key_F1:
            self.__act_pos_key_control(1)
        elif event.key() == QtCore.Qt.Key.Key_F2:
            self.__act_pos_key_control(2)
        elif event.key() == QtCore.Qt.Key.Key_F3:
            self.__act_pos_key_control(3)
        elif event.key() == QtCore.Qt.Key.Key_F4:
            self.__act_pos_key_control(4)
        elif event.key() == QtCore.Qt.Key.Key_F5:
            self.__act_pos_key_control(5)
        elif event.key() == QtCore.Qt.Key.Key_F6:
            self.__act_pos_key_control(6)
        elif event.key() == QtCore.Qt.Key.Key_F7:
            self.__act_pos_key_control(7)
        elif event.key() == QtCore.Qt.Key.Key_F8:
            self.__act_pos_key_control(8)
        elif event.key() == QtCore.Qt.Key.Key_F9:
            self.__act_pos_key_control(9)
        elif event.key() == QtCore.Qt.Key.Key_F10:
            self.__act_pos_key_control(10)
        elif event.key() == QtCore.Qt.Key.Key_F11:
            self.__act_pos_key_control(11)
        elif event.key() == QtCore.Qt.Key.Key_F12:
            self.__act_pos_key_control(12)
        elif event.key() == QtCore.Qt.Key.Key_H:
            self.help_window()
        else:
            QtWidgets.QMainWindow.keyPressEvent(self, event)
            return True
        return False

    def keyReleaseEvent(self, event):
        """ Main window keyboard releasing action. """
        if event.key() == QtCore.Qt.Key.Key_Alt:
            if self.__ch_ks:
                ch_idx = int(self.__ch_ks)
                if ch_idx < self.actchnComboBox.count():
                    self.actchnComboBox.setCurrentIndex(int(self.__ch_ks))
                else:
                    QtWidgets.QMessageBox.warning(
                        self, "Warning", "Set recoding channel exceeding total channel!\n"
                        "Input channel is [%d], total available channels [%d]" % (ch_idx, self.actchnComboBox.count()),
                        QtWidgets.QMessageBox.StandardButton.Ok)
                self.__ch_ks = ''
        else:
            QtWidgets.QMainWindow.keyReleaseEvent(self, event)

    def __keybypass_xrange(self, event):
        """ Override function for [xrangeSpinBox] keyPressEvent. """
        if self.keyPressEvent(event):
            QtWidgets.QDoubleSpinBox.keyPressEvent(self.xrangeSpinBox, event)

    def __keybypass_ymin(self, event):
        """ Override function for [yminSpinBox] keyPressEvent. """
        if self.keyPressEvent(event):
            QtWidgets.QDoubleSpinBox.keyPressEvent(self.yminSpinBox, event)

    def __keybypass_ymax(self, event):
        """ Override function for [ymaxSpinBox] keyPressEvent. """
        if self.keyPressEvent(event):
            QtWidgets.QDoubleSpinBox.keyPressEvent(self.ymaxSpinBox, event)

    def __keybypass_actchn(self, event):
        """ Override function for [actchnComboBox] keyPressEvent. """
        if self.keyPressEvent(event):
            QtWidgets.QComboBox.keyPressEvent(self.actanoComboBox, event)

    def __keybypass_actano(self, event):
        """ Override function for [actanoComboBox] keyPressEvent. """
        if self.keyPressEvent(event):
            QtWidgets.QComboBox.keyPressEvent(self.actanoComboBox, event)

    def __draw_canvas(self):
        """ Canvas updating function. """
        if self.__upd_time:
            self._result.set_time(self.__t_init, self.__t_stop)
        else:
            self._result.set_amp(self.yminSpinBox.value(), self.ymaxSpinBox.value())

    def __ctrl_mode_switch(self):
        """ Switch between standard and advanced control mode. """
        if self.toolbarBox.isChecked():
            # Disable standard controls
            self.xrangeSpinBox.setEnabled(False)
            self.yminSpinBox.setEnabled(False)
            self.ymaxSpinBox.setEnabled(False)
            # Enable toolbar control
            self._toolbar.setVisible(True)
        else:
            # Reset canvas and view
            self._toolbar.home()
            self._toolbar.update()
            # Uncheck navigation button
            if self._toolbar.mode == _Mode.PAN:
                self._toolbar.pan()
            elif self._toolbar.mode == _Mode.ZOOM:
                self._toolbar.zoom()
            # Disable toolbar control
            self._toolbar.setVisible(False)
            # Enable standard controls
            self.xrangeSpinBox.setEnabled(True)
            self.yminSpinBox.setEnabled(True)
            self.ymaxSpinBox.setEnabled(True)

    def __update_scroll_bar(self):
        """ Scroll bar limits and step size updater. """
        if abs(self.__t_all - self.xrangeSpinBox.value() / 1000) <= 0.005:
            self.signalScrollBar.setMaximum(0)
            self.signalScrollBar.setSingleStep(0)
            self.signalScrollBar.setPageStep(0)
            self.signalScrollBar.setEnabled(False)
        else:
            self.signalScrollBar.setMaximum(int((self.__t_all - self.xrangeSpinBox.value() / 1000) * 1000 + 1))
            self.signalScrollBar.setSingleStep(int(self.xrangeSpinBox.value() * 0.5))
            self.signalScrollBar.setPageStep(int(self.xrangeSpinBox.value()))
            self.signalScrollBar.setEnabled(True)

    def __signal_scroll(self):
        """ Scroll bar motion trigger function. """
        self.__upd_time = True
        # Update time range
        self.__t_init = self.signalScrollBar.value() / 1000
        self.__t_stop = self.__t_init + self.xrangeSpinBox.value() / 1000
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(5)

    def __update_plot_rng(self):
        """ Plot time range update trigger function. """
        self.__upd_time = True
        # Update time range
        self.__t_init = self._result.ax[0].get_xbound()[0]
        self.__t_stop = self._result.ax[0].get_xbound()[0] + self.xrangeSpinBox.value() / 1000
        # Update scroll bar
        self.__update_scroll_bar()
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(500)

    def __update_plot_amp(self):
        """ Plot signal amplitude update trigger function. """
        self.__upd_time = False
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(50)

    def __set_act_chn(self):
        """ Plot selected data channel. """
        # Reset active position
        self.actanoComboBox.setCurrentIndex(0)
        # Update plot
        chn = self.actchnComboBox.currentIndex()
        self._result.plt_ch(chn)
        # Update annotation list
        self.actanoComboBox.clear()
        pos_key = sum([[k + ' - ' + p for p in self._result.pos[k]] for k in self._result.pos], ['NONE'])
        [self.actanoComboBox.addItem(k) for k in pos_key]
        # Update amplitude controls
        self.yminSpinBox.setMinimum(self._result.ax[0].get_ylim()[0])
        self.yminSpinBox.setValue(self._result.ax[0].get_ylim()[0])
        self.ymaxSpinBox.setMaximum(self._result.ax[0].get_ylim()[1])
        self.ymaxSpinBox.setValue(self._result.ax[0].get_ylim()[1])
        # Set active waveform back to [RAW]
        self.__act_wfm = 'RAW'
        self._result.set_act_wfm(self.__act_wfm)

    def __set_act_pos(self):
        """ Set active spike position to verify. """
        key = self.actanoComboBox.currentText()
        if key:
            if key == 'NONE':
                self.__act_wfm = 'RAW'
                pos = None
            else:
                self.__act_wfm, pos = key.split(' - ')
            self._result.set_act_pos(self.__act_wfm, pos)

    def __act_pos_key_control(self, idx):
        """ Set active spike position with function keys. """
        tot = self.actanoComboBox.count()
        if tot > idx:
            self.actanoComboBox.setCurrentIndex(idx)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Selected index [%d] exceed total number of cells [%d]\n"
                                                           "Set to maximum available cell!" % (idx, tot - 1),
                                          QtWidgets.QMessageBox.StandardButton.Ok)

    def __sel_wfm(self, sel):
        """ Select waveform(s) to be visible.

        Args:
            sel (list[str]): Waveform name keys
        """
        lnk_pos = self.lnkAnoBox.isChecked()
        pos_key = self._result.sel_wfm(sel, lnk_pos)
        # Check if active waveform is selected
        if self.__act_wfm not in sel:
            self.__act_wfm = 'RAW'
        self._result.set_act_wfm(self.__act_wfm)
        if lnk_pos:
            # Check if current active position should be removed
            try:
                idx = pos_key.index(self.actanoComboBox.currentText()) + 1
            except ValueError:
                idx = 0
            self.actanoComboBox.setCurrentIndex(0)
            # Update active position combobox
            self.actanoComboBox.clear()
            for p in ['NONE'] + pos_key:
                self.actanoComboBox.addItem(p)
            # Set back index if previous selection is still valid
            if idx != 0:
                self.actanoComboBox.setCurrentIndex(idx)

    def __toggle_lnk_ano(self):
        """ Force re-emit waveform selection signal with linked annotation check box. """
        self.__wfm_sel_win.emit_sig()

    def save_correction(self, new):
        """ Save manual made corrections.

        Args:
            new (bool): Linked with [Save As], get file path with dialog
        """
        if self._result.check_correction():
            # File dialog
            if new:
                dst, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Corrections", dir=os.path.dirname(self.file),
                                                               filter="Result File (*.h5)")
                # Checking dialog return
                if dst == '':
                    reply = QtWidgets.QMessageBox.warning(
                        self, "Warning", "Save operation cancelled",
                        QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Retry,
                        QtWidgets.QMessageBox.StandardButton.Retry
                    )
                    if reply == QtWidgets.QMessageBox.StandardButton.Retry:
                        self.save_correction(True)
                    return
            else:
                reply = QtWidgets.QMessageBox.warning(
                    self, "Warning", "Sure to overwrite source file?",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.No
                )
                if reply == QtWidgets.QMessageBox.StandardButton.No:
                    return
                # Set overwrite
                dst = self.file
            # Disable buttons
            self.cxDiscardButton.setEnabled(False)
            self.cxSaveButton.setEnabled(False)
            # Block user interaction with dialog
            self.__save_msg.show()
            # Link file saving process
            self._save_proc.data = self._result.make_correction()
            self._result.fp.close()  # Close source file to avoid process lock
            self._save_proc.dst = dst
            self._save_proc.start()
        else:
            QtWidgets.QMessageBox.warning(self, "Saving", "No changes made!\nFile not saved")

    def __save_finalize(self):
        """ Save process finalize function. """
        # Update GUI display
        self.file = self._save_proc.dst
        if self.file != self._save_proc.src:
            self.fileLine.setText(self.file.replace('\\', '/'))
            self.setWindowTitle("%s -> [%s]" % (self.windowTitle(), os.path.basename(self.file)))
        # Reset process
        self._save_proc.src = self.file
        self._save_proc.dst = None
        self._save_proc.data = None
        self._result.fp = h5.File(self.file, 'r')  # Reopen source file
        # Inform user with dialogs
        self.__save_msg.hide()
        QtWidgets.QMessageBox.information(self, "Saving", "Results saved to [%s]" % self.file)
        # Enable buttons
        self.cxDiscardButton.setEnabled(True)
        self.cxSaveButton.setEnabled(True)

    def __discard_exit(self):
        """ Discard all changes and exit. """
        self.__safe_close = False
        self.close()

    def help_window(self):
        """ Keyboard control help info. """
        QtWidgets.QMessageBox.information(
            self, "Keyboard and Mouse Inputs",
            "[Arrow Left], [A], [Arrow Right] & [D]:    Navigate signal\n        + [Control Modifier]:    Move slower\n"
            "        + [Shift Modifier]:    Move faster\n        + [Alt Modifier]:    Move fastest\n\n"
            "[Page Up] & [Page Down]:    Switch to consecutive recording channel\n"
            "[Alt] + [Number Key] sequence:    Switch to recording channel number\n\n"
            "[Control] + [Number Key]:    Toggle waveform\n\n"
            "[F1] ~ [F12]:    Activate annotation index\n        [Left Mouse Button]:    Add spike to annotation\n"
            "        [Right Mouse Button]:    Remove spike from annotation\n\n"
            "[H]:    Show this help information"
        )
