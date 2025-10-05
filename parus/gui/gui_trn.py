# Model training GUI module

import os
import re
from datetime import datetime
import json
from PySide6 import QtCore, QtGui, QtWidgets

__package__ = 'parus.gui'
__name__ = 'parus.gui.gui_trn'
from .. import pkg_data
from ..scripts import gen_sim, gen_sta, mod_trn
from . import cs_dark
from .desg_genctl import Ui_ParusGenWindow
from .desg_modtrn import Ui_ParusTrnWindow
from .elm_proc import PyScriptExec, ProcConsole, path_selector

__all__ = ['ParusGen', 'ParusTrn']
"""
Class list:
  ParusGen(parent=None): Parus simulated signal generation window.
  ParusTrn(parent=None): Parus model training window.
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
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon.ico"))
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
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon.ico"))
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        if cs_dark():
            self.procButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
        else:
            self.procButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')
        # Set control variable defaults
        self.__auto_scr = True
        self.__proc_run = False

        # Set training process
        self._proc = PyScriptExec(script=mod_trn, console=self.procConsole, trigger=self.procButton,
                                  name="Parus [Model Train]", disp_time=True, clr_con=False,
                                  trig_txt=("Initiate Model Training", "Stop Process"))
        self._proc.set_auto_scroll(self.__auto_scr)
        self._proc.started.connect(self.__proc_start)
        self._proc.finished.connect(self.__proc_finish)
        # Initialize console
        self._console = ProcConsole(console=self.procConsole,
                                    btn_clr=self.procConClear, btn_cpy=self.procConCopy, btn_scr=self.procConScroll,
                                    lnk_proc=[self._proc], stat_bar=self.statBar, disp_time=True,
                                    init_msg="Parus Model Training GUI ready!")

        # Set data variable defaults
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

        # Connect controls
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
    def set_proc_args(self):
        """ Set arguments for model training. """
        if (self.sim_dir is None) or (self.out_dir is None):
            self.procButton.setEnabled(False)
            self._proc.reset_arguments()
        else:
            args = (self.out_dir + self.sim_dir + self.num_trn + self.num_vld + self.num_tst + self.seq_len +
                    self.mod_name + self.num_ep + self.eval_stp + self.eval_ind + self.ex_opt)
            self._proc.set_arguments(args)
            self.procButton.setEnabled(True)

    def __switch_proc_btn(self):
        """ ParusModTrn button connected function. """
        if self.__proc_run:
            self.procButton.setStyleSheet('QPushButton {color: red}')
        else:
            if cs_dark():
                self.procButton.setStyleSheet('QPushButton {color: white}' 'QPushButton:disabled {color: dimgray}')
            else:
                self.procButton.setStyleSheet('QPushButton {color: black}' 'QPushButton:disabled {color: dimgray}')

    def __proc_start(self):
        """ ParusModTrn process STARTED connected function. """
        self.__proc_run = True
        self.__switch_proc_btn()
        self.ctrl_enable(False)
        self.statBar.showMessage("Parus model training started")

    def __proc_finish(self):
        """ ParusModTrn process FINISHED connected function. """
        # Reset button
        self.__proc_run = False
        self.ctrl_enable(True)
        self.__switch_proc_btn()
        # Display status
        if self._proc.fin_stop:
            # Save current successful execution params
            self.__save_params()
            self.statBar.showMessage("Model training successfully finished")
        else:
            self.statBar.showMessage("Model training terminated")

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
        self.set_proc_args()

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
        self.set_proc_args()

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
        self.set_proc_args()

    def __sel_out_dir(self):
        """ Select model training results output folder button connection. """
        path = path_selector(self.outPath, mode='path', caption="Select Model Output Folder", parent=self)
        self.out_dir = None if path is None else [path]
        # Update process arguments
        self.set_proc_args()

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
        self.set_proc_args()

    def __set_num_trn(self):
        """ Set number of training samples. """
        num = self.trnSampSpinbox.value()
        self.num_trn = ['-dtn', str(num)]
        # Update process arguments
        self.set_proc_args()

    def __set_num_vld(self):
        """ Set number of validation samples. """
        num = self.vldSampSpinbox.value()
        self.num_vld = ['-dvl', str(num)]
        # Update process arguments
        self.set_proc_args()

    def __set_num_tst(self):
        """ Set number of testing samples. """
        num = self.tstSampSpinbox.value()
        self.num_tst = ['-dts', str(num)]
        # Update process arguments
        self.set_proc_args()

    def __set_seq_len(self):
        """ Set dataset/model sample sequence length. """
        num = self.seqLenSpinbox.value()
        self.seq_len = ['-mls', str(num)]
        # Update process arguments
        self.set_proc_args()

    def __set_mod_name(self):
        """ Set model name. """
        self.modNameLine.blockSignals(True)
        name = self.modNameLine.text()
        name = "".join(s for s in name if s.isalnum())
        self.modNameLine.setText(name)
        self.modNameLine.blockSignals(False)
        self.mod_name = ['-mid', name]
        # Update process arguments
        self.set_proc_args()

    def __set_num_ep(self):
        """ Set number of epochs. """
        num = self.nEpSpinbox.value()
        self.num_ep = ['-tep', str(num)]
        # Update process arguments
        self.set_proc_args()

    def __set_eval_stp(self):
        """ Set training steps per evaluation. """
        stp = self.stpEvalSpinbox.value()
        self.eval_stp = ['-tev', str(stp)]
        # Update process arguments
        self.set_proc_args()

    def __set_eval_ind(self):
        """ Set model evaluation results visualization method. """
        ind = ['none', 'disp', 'save'][self.indEvalCombo.currentIndex()]
        self.eval_ind = ['-t', ind]
        # Update process arguments
        self.set_proc_args()

    def __set_ex_opt(self):
        """ Model training advance option. This function DOES NOT check input, error will be handled by the script. """
        opt = self.exOptLine.text()
        self.ex_opt = [o for o in opt.split(' ') if o]
        # Update process arguments
        self.set_proc_args()
