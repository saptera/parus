# Parus GUI main windows

import os
import re
from datetime import datetime
import shutil
import json
import h5py as h5
import matplotlib as mpl
from matplotlib.backend_bases import _Mode
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
import matplotlib.pyplot as plt
from PySide6 import QtCore, QtWidgets
mpl.use('QtAgg')

__package__ = 'parus.gui'
from .. import pkg_data
from ..scripts import gen_sim, gen_sta, mod_inf
from .desg_genctl import Ui_ParusGenWindow
from .desg_modinf import Ui_ParusInfWindow
from .desg_wfmsel import Ui_WfmSelWindow
from .desg_resver import Ui_ParusResWindow
from .elm_proc import PyScriptExec, ProcConsole, ProgBusyDialog, path_selector, table_loader, selection_operator
from .elm_plot import ResPltLoader

__all__ = ['ParusGen', 'ParusInf', 'WfmSel', 'ParusRes']
"""
Class list:
  ParusGen(parent=None): Parus simulated signal generation window.
  ParusInf(parent=None): Parus data inference window.
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
        self.clrSetButton.clicked.connect(self.reset_all)

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
        # Set notification
        if notify:
            # Inform console
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            text = "<span style=\"color:black;font-weight:bold;\">All parameters reset to defaults!</span>"
            message = "<span style=\"color:blue;white-space:pre;\">[%s] </span>" % time + text
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


class ParusInf(QtWidgets.QMainWindow, Ui_ParusInfWindow):
    def __init__(self, parent=None):
        """ Parus data inference window.

        Args:
            parent: Parent window or widget
        """
        # Initialize GUI
        super(ParusInf, self).__init__(parent)
        self.setupUi(self)
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
        self.btsz = self.__set_bat_size()
        self.clvl = self.__set_comp_lvl()
        self.out_path = []

        # Connect buttons
        self.addFileButton.clicked.connect(self.__set_data_file)
        self.addPathButton.clicked.connect(self.__set_data_path)
        self.selAllButton.clicked.connect(lambda: self.__set_selc('all'))
        self.selNonButton.clicked.connect(lambda: self.__set_selc('non'))
        self.selInvButton.clicked.connect(lambda: self.__set_selc('inv'))
        self.ckptButton.clicked.connect(self.__sel_mod_ckpt)
        self.ckptLine.textChanged.connect(self.__set_mod_ckpt)
        self.ovlpSpinbox.valueChanged.connect(self.__set_ovlp_len)
        self.btszSpinbox.valueChanged.connect(self.__set_bat_size)
        self.clvlCombo.currentIndexChanged.connect(self.__set_comp_lvl)
        self.outputButton.clicked.connect(self.__sel_out_path)
        self.outputLine.textChanged.connect(self.__set_out_path)

        # Load previous execution parameters
        self.__load_params()
        # System standby
        self.statBar.showMessage("System standby")

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
        self.btszSpinbox.setEnabled(enable)
        self.clvlCombo.setEnabled(enable)
        self.outputLine.setEnabled(enable)
        self.outputButton.setEnabled(enable)
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
            args = (self.ckpt + flst + dlst + self.out_path + self.ovlp + self.btsz + self.clvl)
            self._proc.set_arguments(args)
            self.procButton.setEnabled(True)

    def __switch_proc_btn(self):
        """ ParusModInf button connected function. """
        if self.__proc_run:
            self.procButton.setStyleSheet('QPushButton {color: red}')
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
            self.btszSpinbox.setValue(pars['batch_size'])
            self.clvlCombo.setCurrentIndex(pars['compression_level'])

    def __save_params(self):
        """ Save GUI settings of current execution. """
        pars = {}  # INIT VAR
        # Read current controls
        pars['model_checkpoint'] = self.ckptLine.text()
        pars['overlap_length'] = self.ovlpSpinbox.value()
        pars['batch_size'] = self.btszSpinbox.value()
        pars['compression_level'] = self.clvlCombo.currentIndex()
        # Save to file
        with open(os.path.join(pkg_data, '_inf_params.json'), 'w') as fp:
            json.dump(pars, fp, indent=2)

    def __set_data_file(self):
        """ Add file(s) to file selection table. """
        stat, self.lst_file, self._sel_file = table_loader(
            self.inputTable, self.lst_file, self._sel_file, mode='file', caption="Select Data File(s)",
            flt="Signal Files (*.sig *.pkl *.pklz)", func=self.set_proc_args, parent=self)
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

    def __sel_out_path(self):
        """ Select result output directory. """
        otp = path_selector(self.outputLine, mode='path', caption="Select Output Directory", parent=self)
        if otp is None:
            self.out_path = []
            self.statBar.showMessage("Output path selection cancelled")
        else:
            self.out_path = ['-o', otp]
            self.statBar.showMessage("Output path selected")
        # Update process arguments
        self.set_proc_args()

    def __set_out_path(self):
        """ Set result output directory.  """
        otp = self.outputLine.text()
        if os.path.isdir(otp):
            self.out_path = ['-o', otp]
            self.statBar.showMessage("Output path set")
        else:
            self.out_path = []
            self.statBar.showMessage("Output path is invalid!")
        # Update process arguments
        self.set_proc_args()


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
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.file = file
        # Timer initialization
        self.__timer_val = -1
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
                elif reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    self.__save_msg.allow_close = True  # Unblock close lock for dialog
                    self.__save_msg.close()  # Close process informing dialog
                    self._result.close()  # Close result plot
                    event.accept()
        else:
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
