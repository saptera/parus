import os
import warnings
import math
import numpy as np
import matplotlib
from matplotlib.gridspec import GridSpec
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from parus.gui.scope_desg import *
from parus.data.intan_func import intan_time_read, intan_port_amp_read
from parus.data.rec_info_io import read_probe_data, read_spk_info, read_cell_type
matplotlib.use('Qt5Agg')


# GUI internal signal class
class __ComSig(QtCore.QObject):
    stat_temp_msg = QtCore.pyqtSignal(str)  # Main scope status bar temporary message
    stat_perm_msg = QtCore.pyqtSignal(str)  # Main scope status bar permanent message
    load_cmd = QtCore.pyqtSignal()  # Main scope status bar permanent message


# Announce global variables
com_sig = __ComSig()  # Internal signals
# Signal interactive plot global variables
sig_xloc = 0  # Signal data point x (time) value
sig_yloc = 0  # Signal data point y (amplitude) value
coords = ()  # Signal data point vector (sig_xloc, sig_yloc)
ano_loc = None  # Signal annotation timestamp
ano_sid = None  # Signal annotation selection ID
# Data files global variables
dat_path = str()  # Data absolute path
prb_file = str()  # Probe geometry definition file absolute path
spk_file = str()  # Signal spike timestamp CSV file absolute path
ctp_file = str()  # Spike cell type definition CSV file absolute path
rec_port = str()  # Data recording hardware port
ch_ct = 0  # Total number of recording channels
rec_freq = 0  # Signal recording sampling frequency
# Signal and annotation data global variables
prb_info = None  # Probe geometry information
sig_time = None  # Recording time array
sig_data = None  # Recording signal array
spk_data = None  # Spike timestamp
type_def = None  # Spike cell definition


def read_intan_data(data_dir, prb_path, spk_path, ctp_path, port_name, channel_count, sampling_frequency):
    """ Read annotated Intan recording data.

    Args:
        data_dir (str): Data folder absolute path.
        prb_path (str): Probe definition file absolute path.
        spk_path (str): Cell spiking timestamp CSV absolute path.
        ctp_path (str): Cell type definition CSV absolute path.
        port_name (str): Name of Intan recoding port.
        channel_count (int): Number of channels on defined port.
        sampling_frequency (int): Sampling frequency of the recording (Hertz / Hz).

    Returns:
        tuple[list[dict], np.ndarray, list, dict, dict]:
            prb_def (list[dict]): Probe definition information
            timestamp (np.ndarray): {1D} NumPy 1D array containing time data (Seconds / s).
            raw_signal (list[np.ndarray]): {LIST of 1D} NumPy 1D array containing amplifier data (microVolts / mV).
            spk_info (dict[int, dict[int, np.ndarray]]): Arranged spike timing data, {prob_ch: {cell_id: spk_time}}.
            cell_type (dict[int, str]): Arranged cell type information ({cell_id: cell_type}).
    """
    # Get required file path
    intan_time = os.path.join(data_dir, "time.dat")
    # Read data files
    prb_def = read_probe_data(prb_path)
    timestamp = intan_time_read(intan_time, sampling_frequency)
    if len(prb_def) != channel_count:
        warnings.warn(message="Channel counts / Probe sites: number MISMATCH! "
                              "Force channel counts equal to probe sites.", category=Warning, stacklevel=2)
        channel_count = len(prb_def)
    raw_signal = intan_port_amp_read(data_dir, port_name, channel_count)
    # Read annotation files
    if spk_path is None:
        spike_info = None
        cell_types = None
    else:
        spike_info = read_spk_info(spk_path, cell_mode=False, trim_negat=True, trim_noise=True)
        # Only read cell type definition CSV when cell spiking timestamp CSV exist
        if ctp_path is None:
            cell_types = None
        else:
            cell_types = read_cell_type(ctp_path)
    return prb_def, timestamp, raw_signal, spike_info, cell_types


def find_nearest(array, value):
    """ Find the index of nearest value in array.

    Args:
        array (np.ndarray): {1D} Sorted array.
        value (int or float): Value to be searched

    Returns:
        int: Index of nearest value in array.
    """
    idx = np.searchsorted(array, value, side='left').item()
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])):
        return idx - 1
    else:
        return idx


class MplSigCanvas(FigureCanvasQTAgg):
    """ Class for displaying signal with annotations.

    Methods:
        set_tlim(tmin, tmax): Update signal time range.
        reset_tlim(): Reset signal time range.
        upd_sig(t, v): Update main signal.
        uns_ano(): Unselect annotated timestamp locations of signal.
        sel_ano(name): Select annotated timestamp locations of signal.
        del_ano(name): Delete annotated timestamp locations of signal.
        add_ano(pt, name): Add annotated timestamp locations of signal.
    """

    def __init__(self, t, v, width=6.4, height=4.8, dpi=100):
        """ Signal plot initializer.

        Args:
            t (np.ndarray): {1D} Timestamp array of signal.
            v (np.ndarray): {1D} Value array of signal.
            width (int or float): Figure width in inches (default: 6.4).
            height (int or float): Figure height in inches (default: 4.8).
            dpi (int): Resolution of the figure (default: 100).
        """
        # Main plot definition
        self.__fig = Figure(figsize=(width, height), dpi=dpi)
        self.__fig.set_tight_layout(True)  # Set tight layout for signals
        spec = GridSpec(ncols=1, nrows=2, height_ratios=[4, 1])

        # Setup and plotting signal data
        self.__t = t
        self.__t_search = t  # Array for mouse [onmove] searching
        self.__v = v
        self.__v_search = v  # Array for mouse [onmove] searching
        self.__sig_ax = self.__fig.add_subplot(spec[0])
        self.__main_sig = self.__sig_ax.plot(self.__t, self.__v)
        self.__sig_ax.minorticks_on()
        self.__sig_ax.set_xlabel("Time (s)")
        self.__sig_ax.set_ylabel("Amplitude (mV)")

        # Setup annotation data subplot
        self.__ano_ax = self.__fig.add_subplot(spec[1], sharex=self.__sig_ax, frameon=False)
        self.__ano_ax.get_xaxis().set_visible(False)
        self.__ano_ax.minorticks_off()
        self.__ano_ax.set_ylim(ymax=0.5, ymin=-0.5)
        self.__ano_ax.set_yticks([], minor=False)

        # Initialize annotation related variables
        self.__ano_count = 0  # Total number of annotation
        self.__ano_name = []  # Annotated signal type name list
        self.__ano_rect = Rectangle(xy=(0, 0), width=0, height=0)  # Initialize empty select rectangle
        self.__ano_mvcid = 0  # Initialize annotation mouse motion event ID
        self.__ano_search = None  # Annotation marker search array
        self.__ano_trh = (t[-1] - t[0]) * 0.005  # Annotation marker detection threshold

        # Cursor assistive elements definition
        self.__sig_vl = self.__sig_ax.axvline(x=t[0], color='k', alpha=0.2)  # Cursor vertical line for signal data
        self.__ano_vl = self.__ano_ax.axvline(color='k', alpha=0.2)  # Cursor vertical line for annotation data
        self.__sig_mkr, = self.__sig_ax.plot(t[0], v[0], marker='o', ms=5, mew=0, mfc='r', alpha=0.6, zorder=3)  # SigMk
        self.__ano_mkr, = self.__ano_ax.plot([None], [None], marker='x', mec='r', mfc='r', alpha=0.8, zorder=3)  # AnoMk
        self.__ano_mkr.set_visible(False)  # Hide annotation marker before selection

        # Initialize plot
        self.__ano_vl.set_xdata(None)  # Hide cursor vertical line at initialization
        super(MplSigCanvas, self).__init__(self.__fig)

        # Mouse left button click event definition
        def onclick(event):
            if not event.inaxes:
                return
            # Get closest data points from cursor position
            global coords, sig_xloc, sig_yloc, ano_loc, ano_sid
            coords = (sig_xloc, sig_yloc)
            if ano_sid is not None:
                print(ano_loc)
            print(coords)
        self.__fig.canvas.mpl_connect('button_press_event', onclick)

        # Mouse cursor moving event definition
        def onmove(event):
            if not event.inaxes:
                return
            # Get closest data points from cursor position
            global sig_xloc, sig_yloc
            cur_idx = find_nearest(self.__t_search, event.xdata)
            sig_xloc = self.__t_search[cur_idx]
            sig_yloc = self.__v_search[cur_idx]
            self.__sig_mkr.set_data([sig_xloc], [sig_yloc])
            # Set vertical line reference to cursor position
            self.__sig_vl.set_xdata(event.xdata)
            if self.__ano_count == 0:
                self.__ano_vl.set_xdata(None)
            else:
                self.__ano_vl.set_xdata(event.xdata)
            self.__sig_ax.figure.canvas.draw_idle()
        self.__fig.canvas.mpl_connect('motion_notify_event', onmove)

    def set_tlim(self, tmin, tmax):
        """ Update signal time range.

        Args:
            tmin (int or float): Lower bound of time.
            tmax (int or float): Higher bound of time.
        """
        global sig_xloc, sig_yloc, ano_loc, ano_sid
        # Set axis range
        self.__sig_ax.set_xlim(xmin=tmin, xmax=tmax)  # Set new x range
        # Set signal search range
        sig_idx = (self.__t >= tmin) & (self.__t <= tmax)
        self.__t_search = self.__t[sig_idx]
        self.__v_search = self.__v[sig_idx]
        # Set annotation
        if ano_sid is not None:
            # Re-plot selected annotation
            sid_temp = ano_sid
            self.uns_ano()
            self.sel_ano(self.__ano_name[sid_temp])
            # Set annotation search range
            self.__ano_search = self.__ano_search[(self.__ano_search >= tmin) & (self.__ano_search <= tmax)]
        self.__ano_trh = (tmax - tmin) * 0.005  # Set new threshold for annotation searching
        # Update for assistive vertical line location
        if type(self.__sig_vl.get_xdata()) == list:
            if not (tmin < self.__sig_vl.get_xdata()[0] < tmax):
                self.__sig_vl.set_xdata([tmin])
                self.__ano_vl.set_xdata([tmin])
        else:
            if not (tmin < self.__sig_vl.get_xdata() < tmax):
                self.__sig_vl.set_xdata(tmin)
                self.__ano_vl.set_xdata(tmin)
        # Update for signal marker location
        if not (tmin < sig_xloc < tmax):
            cur_idx = find_nearest(self.__t, tmin)
            sig_xloc = self.__t[cur_idx]
            sig_yloc = self.__v[cur_idx]
            self.__sig_mkr.set_data([sig_xloc], [sig_yloc])

    def reset_tlim(self):
        """ Reset signal time range.
        """
        temi = (self.__t[-1] - self.__t[0]) * 0.05
        tmin = self.__t[0] - temi
        tmax = self.__t[-1] + temi
        self.set_tlim(tmin, tmax)

    def upd_sig(self, t, v):
        """ Update main signal.

        Args:
            t (np.ndarray): {1D} New timestamp array of signal.
            v (np.ndarray): {1D} New value array of signal.
        """
        global sig_xloc, sig_yloc
        # Delete original line
        self.__main_sig[0].remove()
        # Update for the new data
        self.__main_sig = self.__sig_ax.plot(t, v)
        self.__t = t
        self.__v = v
        # Update for the new search data
        sig_idx = (t >= self.__sig_ax.get_xlim()[0]) & (t <= self.__sig_ax.get_xlim()[1])
        self.__t_search = t[sig_idx]
        self.__v_search = v[sig_idx]
        # Update for signal marker location
        cur_idx = np.searchsorted(self.__t, sig_xloc, side='left').item()
        sig_xloc = self.__t[cur_idx]
        sig_yloc = self.__v[cur_idx]
        self.__sig_mkr.set_data([sig_xloc], [sig_yloc])

    def __mrk_ano(self, event):
        """ Selected annotation marker detect mouse movement function.
        """
        if not event.inaxes:
            return
        if self.__ano_search.size == 0:
            return
        global ano_loc, ano_sid
        # Get closest data points from cursor position
        cur_idx = find_nearest(self.__ano_search, event.xdata)
        ano_loc = self.__ano_search[cur_idx]
        # Threshold for tolerance (x_range * 0.005)
        if abs(ano_loc - event.xdata) > self.__ano_trh:
            self.__ano_mkr.set_data([None], [None])
            ano_loc = None
        else:
            self.__ano_mkr.set_data([ano_loc], [-ano_sid])

    def uns_ano(self):
        """ Unselect annotated timestamp locations of signal.
        """
        global ano_sid
        if ano_sid is None:
            return
        # Remove rectangle
        self.__ano_rect.remove()
        # Hide marker
        self.__ano_mkr.set_data([None], [None])
        self.__ano_mkr.set_visible(False)
        self.__fig.canvas.mpl_disconnect(self.__ano_mvcid)
        # Reset annotation data
        ano_sid = None
        self.__ano_search = None

    def sel_ano(self, name):
        """ Select annotated timestamp locations of signal.

        Args:
            name (str): Name of the annotated signal.
        """
        global ano_sid
        # Check if defined [name] exist
        if name not in self.__ano_name:
            print("Annotation name not found!")
            return
        # Get and check annotation index
        if ano_sid is None:
            ano_sid = self.__ano_name.index(name)
        elif ano_sid != self.__ano_name.index(name):
            self.uns_ano()
            ano_sid = self.__ano_name.index(name)
        else:
            return
        # Set rectangle on annotated data from name
        left, right = self.__ano_ax.get_xlim()
        self.__ano_rect = Rectangle(xy=(left, -0.5 - ano_sid), width=right - left, height=1, ec='b', fc='b', alpha=0.1)
        self.__ano_ax.add_patch(self.__ano_rect)
        # Set marker
        self.__ano_mkr.set_visible(True)
        self.__ano_mvcid = self.__fig.canvas.mpl_connect('motion_notify_event', self.__mrk_ano)
        # Get timestamps for marking
        ano_x = np.sort(np.ma.asarray(self.__ano_ax.collections[ano_sid].get_offsets()[:, 0]))
        ano_idx = (ano_x >= self.__sig_ax.get_xlim()[0]) & (ano_x <= self.__sig_ax.get_xlim()[1])
        self.__ano_search = ano_x[ano_idx]

    def del_ano(self, name):
        """ Delete annotated timestamp locations of signal.

        Args:
            name (str): Name of the annotated signal.
        """
        global ano_sid
        # Check if defined [name] exist
        if name not in self.__ano_name:
            print("Annotation name not found!")
            return
        # Get annotation ID for deletion
        ano_del = self.__ano_name.index(name)
        # Handel un-selection
        sid_temp = None
        if ano_sid is None:
            pass
        elif ano_del < ano_sid:
            sid_temp = ano_sid - 1
            self.uns_ano()
        elif ano_del == ano_sid:
            self.uns_ano()
        else:
            pass
        # Delete annotated data from name
        del self.__ano_ax.collections[ano_del]
        self.__ano_count -= 1
        # Re-plot annotations with new order
        for i in range(ano_del, self.__ano_count):
            temp_dat = self.__ano_ax.collections[i].get_offsets()
            temp_dat[:, 1] += 1
            self.__ano_ax.collections[i].set_offsets(temp_dat)
        # Set annotation range and ticks
        if self.__ano_count == 0:
            self.__ano_ax.set_ylim(ymax=0.5, ymin=-0.5)
            self.__ano_ax.set_yticks([], minor=False)
            self.__ano_vl.set_xdata(None)
        else:
            self.__ano_ax.set_ylim(ymax=0.5, ymin=0.5 - self.__ano_count)
            self.__ano_ax.set_yticks([-t for t in range(self.__ano_count)], minor=False)
        # Set annotation names
        self.__ano_name.pop(ano_del)
        self.__ano_ax.set_yticklabels(self.__ano_name, minor=False)
        # Re-select
        if sid_temp is not None:
            self.sel_ano(self.__ano_name[sid_temp])

    def add_ano(self, pt, name):
        """ Add annotated timestamp locations of signal.

        Args:
            pt (np.ndarray): {1D} Annotated timestamp locations.
            name (str): Name of the annotated signal.
        """
        # Check the uniqueness of [name]
        self.__ano_name.append(name)
        if len(self.__ano_name) != len(set(self.__ano_name)):
            self.__ano_name.pop(-1)
            print("Annotation name not unique!")
            return
        # Plot annotated data
        self.__ano_ax.scatter(pt, np.full(pt.shape, -self.__ano_count), s=5)
        self.__ano_count += 1
        # Set annotation y-axis legends
        self.__ano_ax.set_ylim(ymax=0.5, ymin=0.5 - self.__ano_count)
        self.__ano_ax.set_yticks([-t for t in range(self.__ano_count)], minor=False)
        self.__ano_ax.set_yticklabels(self.__ano_name, minor=False)
        # Set annotation cursor vertical line
        if self.__ano_vl.get_xdata() is None:
            self.__ano_vl.set_xdata(pt[0])


class IntanDataLoader(QtWidgets.QDialog, Ui_IntanDataLoaderDialog):
    """ Intan data loading dialog.
    """
    global com_sig

    def __init__(self, parent=None):
        super(IntanDataLoader, self).__init__(parent)
        self.setupUi(self)
        # Attribute settings
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setModal(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # Button connections
        self.dataButton.clicked.connect(self.__data_selection)
        self.probeButton.clicked.connect(self.__probe_selection)
        self.spikeButton.clicked.connect(self.__spkinfo_selection)
        self.typeButton.clicked.connect(self.__celltyp_selection)
        self.loadButton.clicked.connect(self.__load_btn)
        self.cancelButton.clicked.connect(self.__cancel_btn)

    # Button functions
    def __data_selection(self):
        """ Data selection button function.
        """
        global dat_path
        dat_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Recording Data Directory")
        self.dataPath.setText(dat_path)

    def __probe_selection(self):
        """ Probe definition selection button function.
        """
        global prb_file
        prb_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Probe Definition", filter="Probe (*.prb)")
        self.probePath.setText(prb_file)

    def __spkinfo_selection(self):
        """ Spike data button function.
        """
        global spk_file
        spk_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Spike Data", filter="Spike Data (*.csv)")
        self.spikePath.setText(spk_file)

    def __celltyp_selection(self):
        """ Cell type selection button function.
        """
        global ctp_file
        ctp_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Cell Type File", filter="Cell Type (*.csv)")
        self.typePath.setText(ctp_file)

    def __load_btn(self):
        """ Load button function: verify inputs; load data.
        """
        global dat_path, prb_file, spk_file, ctp_file, rec_port, ch_ct, rec_freq
        global prb_info, sig_time, sig_data, spk_data, type_def
        # Verify GUI inputs
        err_flag = False
        err_msg = "Missing recording information:"
        wrn_flag = False
        wrn_msg = "Missing annotation information:"
        if os.path.isdir(self.dataPath.text()):
            dat_path = self.dataPath.text()
        else:
            err_flag = True
            err_msg += "\n    Invalid recording data directory!"
        if os.path.isfile(self.probePath.text()):
            prb_file = self.probePath.text()
        else:
            err_flag = True
            err_msg += "\n    Invalid probe definition file!"
        if os.path.isfile(self.spikePath.text()):
            spk_file = self.spikePath.text()
        else:
            spk_file = None
            wrn_flag = True
            wrn_msg += "\n    Invalid spike data file!"
        if os.path.isfile(self.typePath.text()):
            ctp_file = self.typePath.text()
        else:
            ctp_file = None
            wrn_flag = True
            wrn_msg += "\n    Invalid cell type file!"
        # Handel main file missing situation
        if err_flag:
            QtWidgets.QMessageBox.critical(self, "Error", err_msg)
            return
        # Handel annotation file missing situation
        if wrn_flag:
            wrn_msg += "\n\nImply from data directory?\nYes: Imply | No: Keep | Cancel: Return"
            choice = QtWidgets.QMessageBox.warning(self, "Warning", wrn_msg, QtWidgets.QMessageBox.Yes
                                                   | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            if choice == QtWidgets.QMessageBox.Yes:
                if spk_file is None:
                    spk_file = os.path.join(dat_path, "spk_data.csv")
                    spk_file = spk_file if os.path.isfile(spk_file) else None  # Check again
                if ctp_file is None:
                    ctp_file = os.path.join(dat_path, "cell_typ.csv")
                    ctp_file = ctp_file if os.path.isfile(ctp_file) else None  # Check again
            elif choice == QtWidgets.QMessageBox.No:
                pass
            else:
                return
        # Loading remaining data and sending signal
        rec_port = self.portTag.currentText()
        ch_ct = self.channelValue.value()
        rec_freq = self.frequencyValue.value()
        self.close()
        com_sig.stat_temp_msg.emit("Loading...")
        prb_info, sig_time, sig_data, spk_data, type_def =\
            read_intan_data(dat_path, prb_file, spk_file, ctp_file, rec_port, ch_ct, rec_freq)
        com_sig.load_cmd.emit()

    def __cancel_btn(self):
        """ Cancel button function.
        """
        com_sig.stat_temp_msg.emit("Waiting command")
        com_sig.stat_perm_msg.emit("System Ready!")
        self.close()


class SignalScope(QtWidgets.QMainWindow, Ui_SigScopeWindow):
    """ Main window for Parus signal scope.
    """
    # TODO: use QThread to avoid freezing
    global com_sig
    global sig_xloc, sig_yloc, coords, ano_loc, ano_sid
    global dat_path, prb_file, spk_file, ctp_file, rec_port, ch_ct, rec_freq
    global prb_info, sig_time, sig_data, spk_data, type_def

    def __init__(self, parent=None):
        super(SignalScope, self).__init__(parent)
        self.setupUi(self)
        # Status bar initialization
        self.__stat_perm_msg = QtWidgets.QLabel()
        self.statusbar.addPermanentWidget(self.__stat_perm_msg)
        # Timer initialization
        self.__timer_val = -1

        # Announce private variables
        self.__sys_lbl = str()  # Recording system information
        self.__t_rng = self.rangeValue.value() / 1000  # Display time range
        self.__t_stp = self.stepValue.value() / 1000  # Scroller time step
        self.__t_max = 10  # Signal maximum time
        self.__t_frm = []  # Current time window steps
        self.__ano_lst = []  # Annotation cell name list
        self.__data_loader = None  # Data loader container
        self.__loaded = False  # Data loading status

        # File menu setups
        self.menuFile.menuAction().setStatusTip("File menu")
        # Load Intan action
        self.actionExit.setIcon(QtGui.QIcon("open.png"))
        self.actionLoadIntan.setShortcut('Ctrl+Alt+I')
        self.actionLoadIntan.setStatusTip("Load Intan recording files")
        self.actionLoadIntan.triggered.connect(self.__load_intan_data)
        # Exit action
        self.actionExit.setIcon(QtGui.QIcon("exit.png"))
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.setStatusTip("Exit application")
        self.actionExit.triggered.connect(QtCore.QCoreApplication.instance().quit)

        # Controller settings
        self.rangeValue.valueChanged.connect(self.__update_trng_val)
        self.stepValue.valueChanged.connect(self.__update_tstp_val)
        self.__update_slider()
        self.signalSlider.setEnabled(False)
        self.signalSlider.valueChanged.connect(self.__set_win_sig)
        self.channelBox.setEnabled(False)
        self.channelBox.currentIndexChanged.connect(self.__sel_sig_ch)
        self.annotationBox.setEnabled(False)
        self.annotationBox.currentIndexChanged.connect(self.__sel_ano_tp)

        # Connect signals
        com_sig.stat_temp_msg.connect(self.__statbar_temp_msg)
        com_sig.stat_perm_msg.connect(self.__statbar_perm_msg)
        com_sig.load_cmd.connect(self.__load)

        # Status bar announcements
        self.statusbar.showMessage("Waiting command")
        self.__stat_perm_msg.setText("System ready!")

    def timerEvent(self, event):
        """ Timer event for updating canvas time range change.
        """
        self.killTimer(self.__timer_val)
        self.__timer_val = -1
        idx = self.signalSlider.value()
        self.canvas.set_tlim(self.__t_frm[idx][0], self.__t_frm[idx][1])

    def __statbar_temp_msg(self, msg):
        """ Status bar temporary message signal connection.
        """
        self.statusbar.showMessage(msg)

    def __statbar_perm_msg(self, msg):
        """ Status bar permanent message signal connection.
        """
        self.__stat_perm_msg.setText(msg)

    def __update_slider(self):
        """ Time window slider update function.
        """
        # Update current time window steps
        self.__t_frm = []  # RESET VAR
        i = - round(self.__t_stp, 2)  # INIT VAR
        while i + self.__t_rng < self.__t_max:
            i = round(i + self.__t_stp, 2)
            self.__t_frm.append((i, round(i + self.__t_rng, 2)))
        # Update slider value
        self.signalSlider.setMaximum(len(self.__t_frm) - 1)

    def __update_trng_val(self):
        """ Display time range update function.
        """
        self.__t_rng = self.rangeValue.value() / 1000
        # Setup related controls
        self.stepValue.setMaximum(self.rangeValue.value())
        self.__update_slider()
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(2000)

    def __update_tstp_val(self):
        """ Time window step update function.
        """
        self.__t_stp = self.stepValue.value() / 1000
        # Setup related controls
        self.__update_slider()
        # Execute timer
        if self.__timer_val != -1:
            self.killTimer(self.__timer_val)
        self.__timer_val = self.startTimer(2000)

    def __update_chs_lst(self):
        """ Channel list update function.
        """
        # Clear previous data
        self.channelBox.setEnabled(False)
        self.channelBox.clear()
        # Setting new data
        self.channelBox.addItems(["Channel-%03d" % i for i in range(ch_ct)])
        self.channelBox.setEnabled(True)

    def __update_ano_lst(self, n):
        """ Annotation list update function.
        """
        # Clear previous data
        self.annotationBox.setEnabled(False)
        self.annotationBox.clear()
        # Setting new data
        self.annotationBox.addItem("[None]")  # [None] always at first
        if spk_data is not None:
            if type_def is None:
                self.__ano_lst = ["Cell-%03d" % i for i in list(spk_data[n].keys())]
            else:
                self.__ano_lst = [type_def[i] for i in list(spk_data[n].keys())]
        self.annotationBox.addItems(self.__ano_lst)
        self.annotationBox.setEnabled(True)

    def __set_win_sig(self):
        """ Slider value connected function.
        """
        if self.signalSlider.isEnabled():
            # Execute timer
            if self.__timer_val != -1:
                self.killTimer(self.__timer_val)
            self.__timer_val = self.startTimer(500)

    def __sel_sig_ch(self):
        """ Signal channel selection function.
        """
        if self.channelBox.isEnabled():
            ch = self.channelBox.currentIndex()
            # Update signal
            self.canvas.upd_sig(sig_time, sig_data[prb_info[ch]['id']])
            # Remove previous annotation
            for i in self.__ano_lst:
                self.canvas.del_ano(i)
            # Update for current annotation
            self.__update_ano_lst(ch)
            if spk_data is not None:
                i = 0
                for a in spk_data[ch]:
                    self.canvas.add_ano(spk_data[ch][a], self.__ano_lst[i])
                    i += 1
            # Sending status
            self.statusbar.showMessage("Canvas updated!")
            self.__stat_perm_msg.setText("Current channel: %s" % self.channelBox.currentText())

    def __sel_ano_tp(self):
        """ Signal annotation selection function.
        """
        if self.annotationBox.isEnabled():
            an = self.annotationBox.currentIndex()
            if an == 0:
                self.canvas.uns_ano()
            else:
                self.canvas.sel_ano(self.__ano_lst[an - 1])

    def __load(self):
        """ Data GUI loading function.
        """
        if not self.__loaded:
            self.__loaded = True
            self.canvas = MplSigCanvas(t=np.asarray([0]), v=np.asarray([0]), width=4, height=3, dpi=150)
            toolbar = NavigationToolbar2QT(self.canvas, self)
            self.signalLayout.addWidget(toolbar)
            self.signalLayout.addWidget(self.canvas)
        # Load tags
        self.nameLine.setText(os.path.split(dat_path.rstrip("/"))[1])
        self.probeLine.setText(os.path.split(prb_file)[1].rstrip(".prb"))
        self.systemLine.setText(self.__sys_lbl)
        self.countLine.setText(str(ch_ct))
        # Set combo boxes
        self.__update_chs_lst()
        self.__update_ano_lst(0)
        # Set data
        self.__t_max = sig_time[-1]
        self.__win = (0, self.__t_rng)
        self.__update_slider()
        self.signalSlider.setEnabled(True)
        self.canvas.set_tlim(0, self.__t_rng)
        self.__sel_sig_ch()

    def __load_intan_data(self):
        """ Intan data loading dialog caller.
        """
        self.statusbar.showMessage("Waiting for loading dialog input...")
        self.__stat_perm_msg.setText("System prepared for loading")
        self.__sys_lbl = "Intan"
        self.__data_loader = IntanDataLoader(self)
        self.__data_loader.show()
