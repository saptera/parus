# Parus GUI main windows

import os
import re
from datetime import datetime
import shutil
import h5py as h5
import matplotlib as mpl
from matplotlib.backend_bases import _Mode
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
import matplotlib.pyplot as plt
from PySide6 import QtCore, QtWidgets
mpl.use('QtAgg')

__package__ = 'parus.gui'
from ..scripts import gen_sim, gen_sta
from .desg_genctrl import Ui_ParusGenWindow
from .desg_wfmsel import Ui_WfmSelWindow
from .desg_resver import Ui_ParusResWindow
from .elm_proc import PyScriptExec, path_selector
from .elm_plot import ResPltLoader

__all__ = ['ParusGen', 'WfmSel', 'ParusRes']
"""
Class list:
  ParusGen(parent=None): Parus simulated signal generation window.
  WfmSel(key, raw, parent=None): Result waveform channel selection window.
  ParusRes(file, parent=None): Parus inference results viewing and validation window.
"""


class ParusGen(QtWidgets.QMainWindow, Ui_ParusGenWindow):
    def __init__(self, parent=None):
        """ Parus simulated signal generation window.

        Args:
            parent: Parent window or widget
        """
        # Initialize main UI
        super(ParusGen, self).__init__(parent)
        self.setupUi(self)
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
        self.__set_stat_path()  # None return statistic file check function

        # IO path control
        self.sigSelect.clicked.connect(self.__sel_sig_dir)
        self.noiSelect.clicked.connect(self.__sel_noi_dir)
        self.outSelect.clicked.connect(self.__sel_out_dir)
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
        # Extra example control
        self.exEg.valueChanged.connect(self.__set_num_eg)
        # Generation statistics control
        self.statFileSelect.clicked.connect(self.__sel_stat_path)
        self.statFilePath.textChanged.connect(self.__set_stat_path)
        # Reset controls
        self.clrSetButton.clicked.connect(self.reset_all)

        # Initialize console
        self.console_init()
        self.set_auto_scroll(self.__auto_scr)
        # Console easy access function control connection
        self.procConClear.clicked.connect(self.console_init)
        self.procConCopy.clicked.connect(self.console_copy)
        # Console auto scroll to end features control connection
        self.procConScroll.clicked.connect(self.__switch_auto_scroll)
        self.procConsole.verticalScrollBar().sliderPressed.connect(self.__manual_slider_press)
        self.procConsole.verticalScrollBar().sliderReleased.connect(self.__manual_slider_release)

        # System standby
        self.statBar.showMessage("Ready!")

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
                    baseline + self.num_eg)
            self._sim_proc.set_arguments(args)

    def __switch_gen_sim(self):
        """ ParusGenSim button connected function. """
        if self.__sim_run:
            self.genSimButton.setStyleSheet('QPushButton {color: red}')
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
    def reset_all(self):
        """ Reset all controls to defaults. """
        self.arc_dir = self.sigPath.clear()
        self.noi_dir = self.noiPath.clear()
        self.out_dir = self.outPath.clear()
        self.sampCnt.setValue(100000)
        self.sampLen.setValue(15.0)
        self.sampFreq.setValue(20000)
        self.exEg.setValue(100)
        self.spkGrpMthd.setCurrentIndex(0)
        self.spkGrpRate.clear()
        self.noiOnlyRate.setValue(5.0)
        self.minSpkFreq.setValue(50)
        self.maxSpkFreq.setValue(100)
        self.chnCellCnt.setValue(5)
        self.sigMultMin.setValue(0.8)
        self.sigMultMax.setValue(1.5)
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
        # Inform console
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        text = "<span style=\"color:black;font-weight:bold;\">All parameters reset to defaults!</span>"
        message = "<span style=\"color:blue;white-space:pre;\">[%s] </span>" % time + text
        self.procConsole.append(message)
        # Inform status bar
        self.statBar.showMessage("All parameters reset")

    def __sel_sig_dir(self):
        """ Select archived signal file (*.arc) folder button connection. """
        path = path_selector(self.sigPath, mode='path', caption="Select Archived Signal Folder", parent=self)
        self.arc_dir = None if path is None else [path]
        # Update process arguments
        self.set_gensim_args()
        # Set availability of generation start button
        flag = (self.arc_dir is None) or (self.noi_dir is None) or (self.out_dir is None) or (self.sampCnt.value() <= 0)
        self.genSimButton.setEnabled(not flag)

    def __sel_noi_dir(self):
        """ Select archived noise file (*.noi) folder button connection. """
        path = path_selector(self.noiPath, mode='path', caption="Select Archived Noise Folder", parent=self)
        self.noi_dir = None if path is None else [path]
        # Update process arguments
        self.set_gensim_args()
        # Set availability of generation start button
        flag = (self.arc_dir is None) or (self.noi_dir is None) or (self.out_dir is None) or (self.sampCnt.value() <= 0)
        self.genSimButton.setEnabled(not flag)

    def __sel_out_dir(self):
        """ Select generation output folder button connection. """
        path = path_selector(self.outPath, mode='path', caption="Select Output Folder", parent=self)
        self.out_dir = None if path is None else [path]
        # Update process arguments
        self.set_gensim_args()
        # Set availability of generation start button
        flag = (self.arc_dir is None) or (self.noi_dir is None) or (self.out_dir is None) or (self.sampCnt.value() <= 0)
        self.genSimButton.setEnabled(not flag)

    def __set_num_sim(self):
        """ Set number of simulated data to be generated. """
        self.num_sim = [str(self.sampCnt.value())]
        # Update process arguments
        self.set_gensim_args()
        # Set availability of generation start button
        flag = (self.arc_dir is None) or (self.noi_dir is None) or (self.out_dir is None) or (self.sampCnt.value() <= 0)
        self.genSimButton.setEnabled(not flag)
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

    def __sel_stat_path(self):
        """ Select archived noise file (*.noi) folder button connection. """
        path = path_selector(self.statFilePath, mode='file', caption="Select Generation Statistic File",
                             flt="Generation Statistic File (*.cjh)", parent=self)
        self.noi_dir = None if path is None else [path]

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

    # Console related functions -------------------------------------------------------------------------------------- #
    def console_init(self):
        """ Initialize process system console. """
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        text = "<span style=\"color:black;font-weight:bold;\">Parus Signal Generation GUI ready!</span>"
        message = "<span style=\"color:blue;white-space:pre;\">[%s] </span>" % time + text
        self.procConsole.clear()
        self.procConsole.append(message)
        self.procConsole.append('')  # Extra blank line
        # Show status bar message
        self.statBar.showMessage("Console cleared")

    def console_copy(self):
        """ Copy all texts in console to clipboard. """
        pos = self.procConsole.verticalScrollBar().value()
        # Copy all available messages
        self.procConsole.selectAll()
        self.procConsole.copy()
        # Clear selection
        tc = self.procConsole.textCursor()
        tc.clearSelection()
        self.procConsole.setTextCursor(tc)
        self.procConsole.verticalScrollBar().setValue(pos)
        # Show status bar message
        self.statBar.showMessage("Console information successfully copied")

    def set_auto_scroll(self, mode):
        """ Set console auto scroll to end status.

        Args:
            mode (bool): Auto scroll to end status
        """
        self.__auto_scr = mode
        # Set auto scroll button features
        self.procConScroll.setChecked(mode)
        if mode:
            self.procConScroll.setStyleSheet('QPushButton{color:green;}')
            self.procConScroll.setText("Auto Scroll\nON")
        else:
            self.procConScroll.setStyleSheet('QPushButton{color:red;}')
            self.procConScroll.setText("Auto Scroll\nOFF")
        # Set connected process auto scroll functions
        self._sim_proc.set_auto_scroll(mode)
        self._sta_proc.set_auto_scroll(mode)

    def __switch_auto_scroll(self):
        """ Auto scroll button connected function. """
        self.set_auto_scroll(not self.__auto_scr)

    def __manual_slider_press(self):
        """ Console vertical slider user PRESSED connected function. """
        self.set_auto_scroll(False)

    def __manual_slider_release(self):
        """ Console vertical slider user RELEASED connected function. """
        if self.procConsole.verticalScrollBar().value() == self.procConsole.verticalScrollBar().maximum():
            self.set_auto_scroll(True)


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
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        # Timer initialization
        self.__timer_val = -1
        # File saving process
        self._save_proc = self.SaveResThread()
        self._save_proc.file = file
        self._save_proc.finished.connect(self.__save_finalize)
        self.__safe_close = True  # Check changes before close flag

        # Load and plot data
        self._result = ResPltLoader(file)
        self._toolbar = NavigationToolbar2QT(self._result, self)
        self.signalLayout.addWidget(self._toolbar)
        self.signalLayout.addWidget(self._result)
        self._toolbar.setVisible(False)  # Disable toolbar by default
        # Update to curren class
        self.data = self._result.data
        self.fileLine.setText(file.replace('\\', '/'))
        # Set valid position names
        pos_key = sum([[k + ' - ' + p for p in self._result.pos[k]] for k in self._result.pos], [])
        [self.actanoComboBox.addItem(k) for k in pos_key]

        # Set up channel selection window
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
        self.yminSpinBox.setMinimum(self._result.ax[0].get_ybound()[0])
        self.yminSpinBox.setValue(self._result.ax[0].get_ybound()[0])
        self.ymaxSpinBox.setMaximum(self._result.ax[0].get_ybound()[1])
        self.ymaxSpinBox.setValue(self._result.ax[0].get_ybound()[1])

        # Set control connection
        self.toolbarBox.clicked.connect(self.__ctrl_mode_switch)
        self.signalScrollBar.valueChanged.connect(self.__signal_scroll)
        self.xrangeSpinBox.valueChanged.connect(self.__update_plot_rng)
        self.yminSpinBox.valueChanged.connect(self.__update_plot_amp)
        self.ymaxSpinBox.valueChanged.connect(self.__update_plot_amp)
        self.actanoComboBox.currentIndexChanged.connect(self.__set_act_pos)
        self.wfmselButton.clicked.connect(self.__wfm_sel_win.show)
        self.cxSaveButton.clicked.connect(self.save_correction)
        self.cxDiscardButton.clicked.connect(self.__discard_exit)
        # Control key press override
        self.xrangeSpinBox.keyPressEvent = self.__keybypass_xrange
        self.yminSpinBox.keyPressEvent = self.__keybypass_ymin
        self.ymaxSpinBox.keyPressEvent = self.__keybypass_ymax
        self.actanoComboBox.keyPressEvent = self.__keybypass_actano

    class SaveResThread(QtCore.QThread):
        """ Data process independent thread for file saving. """
        file = None
        data = None
        __dst = None

        def run(self):
            if (self.file is None) or (self.data is None):
                return
            # Set file name, avoid overwrite
            stm, ext = os.path.splitext(self.file)
            self.__dst = stm + '_cor' + ext
            i = 0
            while os.path.isfile(self.__dst):
                self.__dst = stm + '_cor%03d' % i + ext
                i += 1
            # Prepare output file
            shutil.copy2(self.file, self.__dst)  # Make copy
            fp = h5.File(self.__dst, 'r+')
            del fp['pos']  # Delete original position data
            # Save corrected positions
            grp = fp.create_group('pos')
            for k in self.data['pos']:
                if isinstance(self.data['pos'][k], dict):
                    ctp = grp.create_group(k)
                    for p in self.data['pos'][k]:
                        ctp.create_dataset(name=p, data=self.data['pos'][k][p], compression="gzip", compression_opts=9)
                else:
                    grp.create_dataset(name=k, data=self.data['pos'][k], compression="gzip", compression_opts=9)
            # Close file
            fp.close()

        def get_last_dst(self):
            """ Get last file saved location. """
            return self.__dst

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
                elif reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    plt.close(self._result.fig)
                    event.accept()
        else:
            plt.close(self._result.fig)
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
        # Waveform toggle key combinations
        elif (event.key() == QtCore.Qt.Key.Key_0) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(0)
        elif (event.key() == QtCore.Qt.Key.Key_1) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(1)
        elif (event.key() == QtCore.Qt.Key.Key_2) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(2)
        elif (event.key() == QtCore.Qt.Key.Key_3) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(3)
        elif (event.key() == QtCore.Qt.Key.Key_4) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(4)
        elif (event.key() == QtCore.Qt.Key.Key_5) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(5)
        elif (event.key() == QtCore.Qt.Key.Key_6) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(6)
        elif (event.key() == QtCore.Qt.Key.Key_7) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(7)
        elif (event.key() == QtCore.Qt.Key.Key_8) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
            self.__wfm_sel_win.toggle_channel(8)
        elif (event.key() == QtCore.Qt.Key.Key_9) and (event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
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
        else:
            QtWidgets.QMainWindow.keyPressEvent(self, event)
            return True
        return False

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
            self.signalScrollBar.setMaximum(int((self.__t_all - self.xrangeSpinBox.value() / 1000) * 1000 + 50))
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
        pos_key = self._result.sel_wfm(sel)
        # Check if active waveform is selected
        if self.__act_wfm not in sel:
            self.__act_wfm = 'RAW'
        self._result.set_act_wfm(self.__act_wfm)
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

    def save_correction(self):
        """ Save manual made corrections. """
        if self._result.check_correction():
            # Disable buttons
            self.cxDiscardButton.setEnabled(False)
            self.cxSaveButton.setEnabled(False)
            # Link file saving process
            self._save_proc.data = self._result.make_correction()
            self._save_proc.start()
        else:
            QtWidgets.QMessageBox.warning(self, "Saving", "No changes made!\nFile not saved")

    def __save_finalize(self):
        """ Save process finalize function. """
        # Reset process
        dst = self._save_proc.get_last_dst()
        self._save_proc.data = None
        QtWidgets.QMessageBox.information(self, "Saving", "Results saved to [%s]" % dst)
        # Enable buttons
        self.cxDiscardButton.setEnabled(True)
        self.cxSaveButton.setEnabled(True)

    def __discard_exit(self):
        """ Discard all changes and exit. """
        self.__safe_close = False
        self.close()
