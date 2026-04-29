# -*- coding: utf-8 -*-

"""PARUS real-time application module

Top-level Qt main window for the PARUS real-time spike-detection application: streams data from a recording controller,
runs model inference on the GPU, performs progressive spike sorting on the CPU, and visualises the results live.
"""

import os
import time
import queue
import json
import numpy as np
import torch
import torch.nn as nn
from PySide6 import QtCore, QtGui, QtWidgets, QtSvgWidgets
import pyqtgraph as pg

__package__ = 'parus.rt'
__name__ = 'parus.rt.app_rt'
from .. import pkg_data
from ..model import EncoderTransformer, load_hparams, load_model
from .desg_apprtp import Ui_ParusRtpWindow
from .hwio import CircularBufferFL, CircularBufferCR,MapArrayQueue
from .intan_rhx import IntanRHXmTCP


class ParusRtApp(QtWidgets.QMainWindow, Ui_ParusRtpWindow):
    """PARUS real-time data processing application.

    Wires together the data-streaming, model-inference, and spike-sorting threads with the live PyQtGraph plots in the
    main window. Sample buffers and inter-thread queues are created on construction and released by the close handler.
    """

    def __init__(self, seq_len, version=None, parent=None):
        """Initialise the real-time window, data buffers, and worker threads.

        Args:
            seq_len (int): Model sequence length
            version (int | float | str | None): App version label shown in the title bar; defaults to
                ``"beta"`` when :data:`None` (default: ``None``)
            parent (QtCore.QObject | None): Parent window or widget (default: ``None``)
        """
        # Initialize GUI
        super(ParusRtApp, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), "assets/icon_rt.ico"))
        self.setWindowIcon(icon)
        logo = QtSvgWidgets.QSvgWidget(os.path.join(os.path.dirname(__file__), "assets/logo_rt.svg"), parent=self)
        logo.renderer().setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.logoLayout.addWidget(logo)
        self.setWindowTitle("%s [v %s]" % (self.windowTitle(), 'beta' if version is None else str(version)))
        self.__set_style()  # Set colour scheme
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)

        # Create data queues and threads
        self.seq_len = seq_len
        self.raw_queue = MapArrayQueue(seq_len, 0, dtype=np.float32, mode='fifo')
        self.spk_queue = queue.Queue()
        self.cbuf_raw = CircularBufferCR(1000, dtype=np.float32)
        self.cbuf_spk = CircularBufferCR(1000, dtype=np.float32)
        self.cbuf_pos = CircularBufferCR(1000, dtype=np.float32)
        self.mod_log = CircularBufferFL(100, dtype=np.float32)
        self.srt_log = CircularBufferFL(100, dtype=np.float32)
        self.rec_ctrl = self._WaveformReader(self)
        self.gpu_proc = self._ModelInference(self)
        self.cpu_proc = self._SpikeSorter(self)
        # Process controls
        self.act_ch = []  # Active channels
        self.act_md = False  # Model loading status
        self.ct_on = False  # Controller connection status
        self.aq_on = False  # Channel acquisition status
        self.md_on = False  # Model inference status
        self.st_on = False  # Spike sorter status

        # Visualization controls
        self.fs = 30000
        self.frm = seq_len / self.fs * 1000  # Data frame time in ms
        # Setup raw data graph
        self.plt_raw = pg.PlotWidget(name='RawCrv')
        self.plt_raw.setTitle("Raw Trace")
        self.plt_raw.getAxis('bottom').setLabel("Time Range (ms)")
        self.plt_raw.getAxis('left').setLabel("Amplitude (μV)")
        self.curve_raw = pg.PlotDataItem()
        self.plt_raw.addItem(self.curve_raw)
        self.__csr_raw = pg.InfiniteLine(-1e12, angle=90, movable=False)
        self.plt_raw.addItem(self.__csr_raw)
        self.rawFrameLayout.addWidget(self.plt_raw)
        # Setup spike data graph
        self.plt_spk = pg.PlotWidget(name='SpkCrv')
        self.plt_spk.plotItem.setXLink(self.plt_raw.plotItem)
        self.plt_spk.setTitle("Spike Data")
        self.plt_spk.getAxis('bottom').setLabel("Time Range (ms)")
        self.plt_spk.getAxis('left').setLabel("Amplitude (μV)")
        self.curve_spk = pg.PlotDataItem()
        self.plt_spk.addItem(self.curve_spk)
        self.__csr_spk = pg.InfiniteLine(-1e12, angle=90, movable=False)
        self.plt_spk.addItem(self.__csr_spk)
        self.spkFrameLayout.addWidget(self.plt_spk)
        # Setup spike position graph
        self.plt_pos = pg.PlotWidget(name='SpkLoc')
        self.plt_pos.plotItem.setXLink(self.plt_raw.plotItem)
        self.plt_pos.getAxis('bottom').setLabel("Time Range (ms)")
        self.plt_pos.setYRange(0.5, 1.5, padding=0)
        self.plt_pos.getAxis('left').setLabel("Cell ID")
        self.plt_pos.getAxis('left').setTicks([[[1, '']]])
        self.point_spk = pg.ScatterPlotItem()
        self.plt_pos.addItem(self.point_spk)
        self.spkFrameLayout.addWidget(self.plt_pos)
        self.plt_pos.hide()  # Hide initially
        # Set plot ratio
        self.spkFrameLayout.setStretch(0, 4)
        self.spkFrameLayout.setStretch(1, 1)
        # Plot status control
        self.__set_sample_length()
        self.plt_timer = QtCore.QTimer()
        self.plt_timer.timeout.connect(self.__update_plot)
        # Statistics update control
        self.msg_timer = QtCore.QTimer()
        self.plt_timer.timeout.connect(self.__update_stat)
        self.__msg_timer_block = 0  # Block message counter

        # Control initial status
        self.modLoadButton.setEnabled(False)
        self.spiCombo.setEnabled(False)
        self.chSpinbox.setEnabled(False)
        self.wfmSelectButton.setEnabled(False)
        self.initProcButton.setEnabled(False)
        self.srtWfmCombo.setEnabled(False)
        self.smpAntSpinbox.setEnabled(False)
        self.smpPstSpinbox.setEnabled(False)
        self.spkThsSpinbox.setEnabled(False)
        self.spkKvlSpinbox.setEnabled(False)
        self.srtAttachButton.setEnabled(False)
        # Connect signals
        self.svrConnectButton.clicked.connect(self.__controller_switch)
        self.spiCombo.currentIndexChanged.connect(self.__clear_spike_history)
        self.chSpinbox.valueChanged.connect(self.__clear_spike_history)
        self.wfmSelectButton.clicked.connect(self.__acquisition_switch)
        self.modelSelect.clicked.connect(self.__sel_model_ckpt)
        self.modelPath.textChanged.connect(self.__set_model_ckpt)
        self.modLoadButton.clicked.connect(self.__build_model)
        self.initProcButton.clicked.connect(self.__inference_switch)
        self.srtWfmCombo.currentIndexChanged.connect(self.__set_sort_waveform)
        self.srtWfmCombo.currentIndexChanged.connect(self.__clear_spike_history)
        self.smpAntSpinbox.valueChanged.connect(self.__set_sort_sample)
        self.smpPstSpinbox.valueChanged.connect(self.__set_sort_sample)
        self.spkThsSpinbox.valueChanged.connect(self.__set_sort_threshold)
        self.spkKvlSpinbox.valueChanged.connect(self.__set_sort_kvalue)
        self.srtAttachButton.clicked.connect(self.__sorting_switch)
        self.gpu_proc.finished.connect(self.__clear_queue)
        self.setRngButton.clicked.connect(self.__set_sample_length)
        self.yMinSpinbox.valueChanged.connect(self.__set_amplitude_range)
        self.yMaxSpinbox.valueChanged.connect(self.__set_amplitude_range)
        self.ampButtonGroup.buttonToggled.connect(self.__set_amplitude_mode)
        # Load parameters
        self.__load_params()
        self.statBar.showMessage("System standby")

    def closeEvent(self, event):
        # Save parameters
        self.__save_params()
        # Exit processes
        if self.st_on:
            self.__sorting_switch()
        if self.md_on:
            self.__inference_switch()
            # Put dummy data to processing queue to avoid blocking in processes
            if not self.aq_on:
                dum = np.zeros(self.seq_len, dtype=np.float32)
                self.raw_queue.put(dum)
            # Shut down process
            self.cpu_proc.wait(1000)  # Wait CPU thread finish, max 1000ms
            self.gpu_proc.wait(1000)  # Wait GPU thread finish, max 1000ms
        if self.aq_on:
            self.__acquisition_switch()
            self.rec_ctrl.wait(2500)  # Wait HW thread finish, max 2500ms
        if self.ct_on:
            self.__controller_switch()
            time.sleep(0.1)

    @staticmethod
    def __set_style():
        """Apply the Fusion Qt style to the running application."""
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.setStyle('fusion')

    def __load_params(self):
        """Pre-fill the form from the last successful run's saved parameters (if any)."""
        par_json = os.path.join(pkg_data, '_rtp_params.json')
        if os.path.isfile(par_json):
            # Load previous settings
            with open(par_json, 'r') as fp:
                pars = json.load(fp)
            # Set to current controls
            self.ipLine.setText(pars['device_address'])
            self.portCmdSpinbox.setValue(pars['command_port'])
            self.portWfmSpinbox.setValue(pars['waveform_port'])
            self.spiCombo.setCurrentIndex(pars['amplifier_socket'])
            self.modelPath.setText(pars['model_checkpoint'])
            self.smpAntSpinbox.setValue(pars['anterior_sample'])
            self.smpPstSpinbox.setValue(pars['posterior_sample'])
            self.spkThsSpinbox.setValue(pars['spike_threshold'])
            self.spkKvlSpinbox.setValue(pars['spike_kvalue'])

    def __save_params(self):
        """Persist the current form values so the next run can pre-fill the same configuration."""
        pars = {}  # INIT VAR
        # Read current controls
        pars['device_address'] = self.ipLine.text()
        pars['command_port'] = self.portCmdSpinbox.value()
        pars['waveform_port'] = self.portWfmSpinbox.value()
        pars['amplifier_socket'] = self.spiCombo.currentIndex()
        pars['model_checkpoint'] = self.modelPath.text()
        pars['anterior_sample'] = self.smpAntSpinbox.value()
        pars['posterior_sample'] = self.smpPstSpinbox.value()
        pars['spike_threshold'] = self.spkThsSpinbox.value()
        pars['spike_kvalue'] = self.spkKvlSpinbox.value()
        # Save to file
        with open(os.path.join(pkg_data, '_rtp_params.json'), 'w') as fp:
            json.dump(pars, fp, indent=2)

    # IO classes ----------------------------------------------------------------------------------------------------- #
    class _WaveformReader(QtCore.QThread):
        """Worker thread that streams waveform data from the recording controller via :class:`IntanRHXmTCP`."""

        def __init__(self, parent):
            """Wire the worker to the controller's TCP adapter.

            Args:
                parent (ParusRtApp): Owning real-time application window
            """
            # Connect to main GUI
            super(ParusRtApp._WaveformReader, self).__init__(parent)
            self.__app = parent
            # Setup
            self.hw = IntanRHXmTCP(self.__app.raw_queue, self.__app.cbuf_raw)

        def run(self):
            self.hw.run()
            while self.__app.aq_on:
                self.hw.read()
            self.hw.stop()
            # Deconfigure channels
            for c in self.__app.act_ch:
                self.hw.config_channel(c[0], c[1], enable=False)

    class _ModelInference(QtCore.QThread):
        """Worker thread that runs spike-detection model inference on the GPU.

        Note:
            The real-time module requires CUDA; instantiation raises :class:`OSError` when no CUDA device is available.
        """

        def __init__(self, parent):
            """Pick the CUDA device and prepare the inference state machine.

            Args:
                parent (ParusRtApp): Owning real-time application window

            Raises:
                OSError: If no CUDA device is available
            """
            # Connect to main GUI
            super(ParusRtApp._ModelInference, self).__init__(parent)
            self.__app = parent
            self.model = None
            self.wfm_idx = 0  # Spike waveform index
            self.seq_len = 0  # Input length, available after model loading
            self.t_log = np.zeros(1, dtype=np.float32)  # Time logger
            # Check CUDA availability
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
            else:
                self.device = None
                raise OSError("PARUS real-time module only support model inference on CUDA device")

        @torch.no_grad()
        def run(self):
            self.model.eval()
            while self.__app.md_on:
                inputs = self.__app.raw_queue.get()
                t0 = time.time()
                inputs = torch.from_numpy(inputs).type(torch.float32).view(1, 1, -1)
                # Process inference
                inputs = inputs.to(self.device)
                outputs = self.model(inputs)
                res = outputs.cpu().numpy()
                # Put to queue for spike sorting
                self.__app.spk_queue.put(res[0, self.wfm_idx, :])
                # Record process time
                self.t_log[0] = time.time() - t0
                self.__app.mod_log.put(self.t_log.copy())

        def build_model(self):
            """Load the configured checkpoint and its hyperparameters into memory and ready it for inference."""
            # Locate model checkpoint
            ckpt = self.__app.modelPath.text()
            if not os.path.isfile(ckpt):
                raise FileNotFoundError("Cannot find model checkpoint at defined path!")
            # Load hyperparameters
            hparam_file = os.path.join(os.path.dirname(ckpt), 'hparams.json')
            if os.path.isfile(hparam_file):
                hparams = load_hparams(hparam_file)
                model_hparams = hparams['model']
                self.seq_len = model_hparams['sequence_length']
                # Set available model outputs
                spk_grp = hparams['data']['spike_groups']
                self.__app.srtWfmCombo.blockSignals(True)
                self.__app.srtWfmCombo.clear()
                self.__app.srtWfmCombo.addItems(spk_grp)
                self.__app.srtWfmCombo.blockSignals(False)
            else:
                raise FileNotFoundError("Model hyperparameter missing!")
            # Build model
            self.model = EncoderTransformer(input_dim=model_hparams['sequence_length'],
                                            context_dim=model_hparams['d_context'],
                                            d_model=model_hparams['d_model'],
                                            nhead=model_hparams['n_head'],
                                            num_layers=model_hparams['n_layers'],
                                            dim_feedforward=model_hparams['d_feedforward'],
                                            output_channels=model_hparams['output_channels'])
            self.model = nn.DataParallel(self.model)
            self.model = load_model(ckpt, self.model, remap=self.device)
            self.model.to(self.device)
            # Initial output setting
            self.set_output_waveform()

        def set_output_waveform(self):
            """Pick which model output channel feeds the spike-data plot and the spike-sorting thread."""
            self.wfm_idx = self.__app.srtWfmCombo.currentIndex()
            # Update plot text
            self.__app.plt_spk.setTitle("Spike Data [%s]" % self.__app.srtWfmCombo.currentText())

    class _SpikeSorter(QtCore.QThread):
        """Worker thread that performs progressive spike sorting on the model's output channel."""

        def __init__(self, parent):
            """Wire the worker to its parent and initialise the sorting state.

            Args:
                parent (ParusRtApp): Owning real-time application window
            """
            # Connect to main GUI
            super(ParusRtApp._SpikeSorter, self).__init__(parent)
            self.__app = parent
            self.t_log = np.zeros(1, dtype=np.float32)  # Time logger
            # Initialize process arguments
            self.num = 0
            self.blk = None
            self.wt = None
            self.set_index_feature()
            self.th = 0
            self.set_threshold()
            self.kv = 0
            self.set_k_value()
            # Initialize process variables
            self.__proc_init = True  # Process initialization status
            self.__hst = None  # Waveform history
            self.__avg = None  # Shape average
            self.__nrm = None  # Shape norm
            self.__wnm = None  # Weighted norm
            self.__cnt = None  # Counter

        def run(self):
            while self.__app.md_on:
                spk = self.__app.spk_queue.get()
                if self.__app.st_on:
                    t0 = time.time()
                    res = np.zeros(self.__app.seq_len, dtype=np.int8)
                    # Peak detection
                    diff = np.sign(np.ediff1d(spk, to_end=spk[-1:]))
                    diff[1:] = diff[:-1] + diff[1:]
                    loc = np.where((spk < self.th) & (diff == 0))[0]
                    if len(loc) > 0:
                        # Sample data
                        idx = np.repeat(loc, self.num) + np.tile(self.blk, len(loc))
                        idx = np.clip(idx, a_min=0, a_max=self.__app.seq_len - 1)
                        smp = spk[idx].reshape(-1, self.num)
                        # Compute accuracy
                        if self.__proc_init:
                            self.__hst = smp[np.newaxis, 0]
                            self.__avg = [smp[0]]
                            self.__nrm = np.linalg.norm(self.__hst, ord=2, axis=1)
                            self.__wnm = np.linalg.norm(self.__hst * self.wt, ord=2, axis=1)
                            self.__cnt = [0]
                            self.__proc_init = False
                            # Inform plot
                            self.__app.plt_pos.getAxis('left').setTicks([[[1, 'C0']]])
                        for i, s in zip(loc, smp):
                            nc = np.linalg.norm(s, ord=2)
                            # Compute criterion
                            dot = self.__hst @ s
                            mag = self.__nrm * nc
                            les = np.where(self.__wnm < nc, self.__wnm, nc) * 2
                            acc = self.__wnm + nc
                            var = (dot / mag) * (les / acc) ** 0.5
                            # Check and assign results
                            grp = np.argmax(var)
                            if var[grp] < self.kv:
                                self.__hst = np.vstack((self.__hst, s))  # Add new history group
                                self.__avg.append(s)  # Add new average group
                                self.__cnt.append(0)
                                gi = len(self.__cnt)
                                # Inform plot
                                self.__app.plt_pos.setYRange(0.5, gi + 0.5, padding=0)
                                self.__app.plt_pos.getAxis('left').setTicks([[[g + 1, 'C%d' % g] for g in range(gi)]])
                            else:
                                self.__cnt[grp] += 1
                                self.__avg[grp] = self.__avg[grp] + s
                                self.__hst[grp] = self.__avg[grp] / self.__cnt[grp]
                                gi = grp + 1
                            res[i] = gi  # Assign group value
                            # Update history norm
                            self.__nrm = np.linalg.norm(self.__hst, ord=2, axis=1)
                            self.__wnm = np.linalg.norm(self.__hst * self.wt, ord=2, axis=1)
                        # Record process time when spikes found
                        self.t_log[0] = time.time() - t0
                        self.__app.srt_log.put(self.t_log.copy())
                    # Put position results to plotting buffer
                    self.__app.cbuf_pos.put(res)
                # Put spike results to plotting buffer
                self.__app.cbuf_spk.put(spk)

        def set_index_feature(self):
            """Recompute the per-spike sample-index tiles and the matching Gaussian peak-emphasis weights."""
            # Get values
            asp = self.__app.smpAntSpinbox.value()
            psp = self.__app.smpPstSpinbox.value()
            # Get index tiles
            self.num = asp + psp + 1
            self.blk = np.arange(-asp, psp + 1, step=1)
            # Compute sample Gaussian position weight
            sigma = self.num * 0.05
            dv = np.linspace(-asp / sigma, psp / sigma, num=self.num, endpoint=True, dtype=np.float32)  # dv = x / sigma
            self.wt = np.exp(-0.25 * dv ** 2) / np.sqrt(2, dtype=np.float32)  # w = sqrt(Gaussian(x) / 2)
            self.wt[asp] = 1  # Normalize, peak value was emphasized with value of 2 in Gaussian

        def set_threshold(self):
            """Re-read the spike-amplitude threshold from the spinbox and apply it to the worker."""
            self.th = self.__app.spkThsSpinbox.value()

        def set_k_value(self):
            """Re-read the spike-grouping ``K`` value from the spinbox and apply it to the worker."""
            self.kv = self.__app.spkKvlSpinbox.value()

        def reset_history(self):
            """Drop every cached cluster template and clear the visualisation buffer."""
            self.__hst = None
            self.__avg = None
            self.__nrm = None
            self.__wnm = None
            self.__cnt = None
            # Set flag
            self.__proc_init = True
            # Clear buffer
            self.__app.cbuf_pos.flush()

    # Data acquisition functions ------------------------------------------------------------------------------------- #
    @QtCore.Slot()
    def __controller_switch(self):
        """Toggle the connection to the recording controller and update the dependent controls."""
        if self.ct_on:
            self.statBar.showMessage("Disconnecting to recording controller")
            # Disconnect and set
            if self.aq_on:
                self.__acquisition_switch()
                self.rec_ctrl.wait(2500)  # Wait HW thread finish, max 2500ms
            self.rec_ctrl.hw.disconnect_server()
            self.fs = 0
            # Disable next controls
            self.spiCombo.setEnabled(False)
            self.chSpinbox.setEnabled(False)
            self.wfmSelectButton.setEnabled(False)
            self.wfmSelectButton.setToolTip("Connect to server first to enable channel selection")
            # Enable current controls
            self.ipLine.setEnabled(True)
            self.portCmdSpinbox.setEnabled(True)
            self.portWfmSpinbox.setEnabled(True)
            # Set flags
            self.svrConnectButton.setText("Connect")
            self.ct_on = False
            self.statBar.showMessage("Recording controller disconnected")
        else:
            self.statBar.showMessage("Connecting to recording controller")
            # Get IP information
            address = self.ipLine.text() if self.ipLine.text() else 'localhost'
            port_cmd = self.portCmdSpinbox.value()
            port_wfm = self.portWfmSpinbox.value()
            # Connect and set
            connection = self.rec_ctrl.hw.connect_to_server(address, port_cmd, port_wfm)
            if not connection:
                self.statBar.showMessage("Unable to connect to recording controller")
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to defined server\n"
                                                              "Please check if TCP control is enabled on device",
                                               QtWidgets.QMessageBox.StandardButton.Ok)
                return
            self.fs = self.rec_ctrl.hw.fs
            self.frm = self.seq_len / self.fs * 1000  # Time duration per data frame (ms)
            self.__set_sample_length()  # Update with sampling frequency defined
            # Disable current controls
            self.ipLine.setEnabled(False)
            self.portCmdSpinbox.setEnabled(False)
            self.portWfmSpinbox.setEnabled(False)
            # Enable next controls
            self.spiCombo.setEnabled(True)
            self.chSpinbox.setEnabled(True)
            self.wfmSelectButton.setEnabled(True)
            self.wfmSelectButton.setToolTip("")
            # Set flags
            self.svrConnectButton.setText("Disconnect")
            self.ct_on = True
            self.statBar.showMessage("Recording controller connected")

    def __set_sample_length(self):
        """Resize the visualisation buffers and the plot x-axis to match the requested time window."""
        lim = round(self.xRngSpinbox.value() / 1000 * self.fs)
        tick = [[[i, str(round(j))] for i, j in zip(np.linspace(0, lim, num=5, endpoint=True),
                                                    np.linspace(0, self.xRngSpinbox.value(), num=5, endpoint=True))]]
        # Set buffers
        self.cbuf_raw.resize(lim)
        self.cbuf_spk.resize(lim)
        self.cbuf_pos.resize(lim)
        # Set raw data graph
        self.plt_raw.setXRange(0, lim / 0.98, padding=0)
        self.curve_raw.setDownsampling(ds=lim // 1000, method='peak')
        self.plt_raw.getAxis('bottom').setTicks(tick)
        # Set spike data graph
        self.plt_spk.setXRange(0, lim / 0.98, padding=0)
        self.curve_spk.setDownsampling(ds=lim // 1000, method='peak')
        self.plt_spk.getAxis('bottom').setTicks(tick)
        # Set spike position graph
        None if self.st_on else self.plt_pos.show()  # Plot needs to be visible to set view properly
        self.plt_pos.setXRange(0, lim / 0.98, padding=0)
        self.plt_pos.getAxis('bottom').setTicks(tick)
        None if self.st_on else self.plt_pos.hide()  # Hide if not show before

    def __set_amplitude_range(self):
        """Apply the manual amplitude range from the spinboxes when the manual mode is selected."""
        if self.setAmpButton.isChecked():
            y_min = self.yMinSpinbox.value()
            y_max = self.yMaxSpinbox.value()
            self.plt_raw.setYRange(y_min, y_max, padding=0)
            self.plt_spk.setYRange(y_min, y_max, padding=0)

    def __set_amplitude_mode(self):
        """Switch the y-axis between the auto-fit mode and the user-defined manual range."""
        if self.autoAmpButton.isChecked():
            self.plt_raw.enableAutoRange(axis='y')
            self.plt_spk.enableAutoRange(axis='y')
        else:
            self.__set_amplitude_range()

    def __align_left_axis(self):
        """Equalise the left-axis width across the active plots so their tracks line up vertically."""
        if self.st_on:
            sw = self.plt_pos.getAxis('left').width()
            mw = self.plt_spk.getAxis('left').width()
            rw = self.plt_raw.getAxis('left').width()
            w = max(sw, mw, rw)
            self.plt_pos.getAxis('left').setWidth(w)
            self.plt_spk.getAxis('left').setWidth(w)
            self.plt_raw.getAxis('left').setWidth(w)
        elif self.md_on:
            mw = self.plt_spk.getAxis('left').width()
            rw = self.plt_raw.getAxis('left').width()
            w = mw if mw > rw else rw
            self.plt_spk.getAxis('left').setWidth(w)
            self.plt_raw.getAxis('left').setWidth(w)

    def __update_plot(self):
        """Refresh the raw, spike, and spike-position plots from the visualisation buffers (60Hz timer)."""
        # Plot spike position
        if self.st_on:
            pos = self.cbuf_pos.get()
            loc = np.nonzero(pos)[0]
            self.point_spk.setData(loc, pos[loc])
        # Plot spike waveform
        if self.md_on:
            self.curve_spk.setData(self.cbuf_spk.get())
            self.__csr_spk.setValue(self.cbuf_spk.locate())
        # Plot raw signal
        self.curve_raw.setData(self.cbuf_raw.get())
        self.__csr_raw.setValue(self.cbuf_raw.locate())
        # Align spike plot Y axis
        self.__align_left_axis()

    @QtCore.Slot()
    def __acquisition_switch(self):
        """Toggle waveform acquisition for the selected channel and update the dependent controls."""
        if self.aq_on:
            self.statBar.showMessage("Stop recording")
            self.aq_on = False
            self.plt_timer.stop()
            self.msg_timer.stop()
            # Enable current controls
            self.spiCombo.setEnabled(True)
            self.chSpinbox.setEnabled(True)
            # Process control disable
            self.initProcButton.setEnabled(False)
            if self.md_on:
                self.initProcButton.setToolTip("Data streaming required for data process")
            else:
                self.initProcButton.setToolTip("Data streaming required for data process\n"
                                               "Model need to be loaded for data process")
            # Set flags
            self.wfmSelectButton.setText("Select")
            self.statBar.showMessage("Recording stopped")
        else:
            self.statBar.showMessage("Configuring to recording channel")
            # Set channel
            port = self.spiCombo.currentText().lower()
            channel = self.chSpinbox.value()
            self.act_ch.append((port, channel))
            self.rec_ctrl.hw.config_channel(port, channel, enable=True)
            # Start acquisition
            self.aq_on = True
            self.rec_ctrl.start()
            self.plt_timer.start(16)  # 60Hz refreshing rate
            self.msg_timer.start(1000)  # 1Hz refreshing rate
            # Disable current controls
            self.spiCombo.setEnabled(False)
            self.chSpinbox.setEnabled(False)
            # Process control enable
            if self.act_md:
                self.initProcButton.setEnabled(True)
                self.initProcButton.setToolTip("")
            else:
                self.initProcButton.setEnabled(False)
                self.initProcButton.setToolTip("Model need to be loaded for data process")
            # Set flags
            self.wfmSelectButton.setText("Stop")
            self.statBar.showMessage("Recording channel configured")

    # Model and data process functions ------------------------------------------------------------------------------- #
    def __sel_model_ckpt(self):
        """Open a file picker for the model checkpoint and write the selection to the form."""
        self.__msg_timer_block = time.time() if self.aq_on else 0
        self.statBar.showMessage("Select model pretrained weights")
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Model Weights", filter="Checkpoint (*.ckpt)")
        # Update data
        self.modelPath.blockSignals(True)
        if file and os.path.isfile(file):
            self.modelPath.setText(file)
            self.modLoadButton.setEnabled(True)
            self.__msg_timer_block = time.time() if self.aq_on else 0
            self.statBar.showMessage("Model pretrained weights set")
        else:
            self.modelPath.clear()
            self.modLoadButton.setEnabled(False)
            self.__msg_timer_block = time.time() if self.aq_on else 0
            self.statBar.showMessage("Cancelled")
        self.modelPath.blockSignals(False)

    def __set_model_ckpt(self):
        """Validate the manually edited checkpoint path and toggle the Load Model button accordingly."""
        file = self.modelPath.text()
        if file and os.path.isfile(file) and file.endswith('.ckpt'):
            self.modLoadButton.setEnabled(True)
            self.__msg_timer_block = time.time() if self.aq_on else 0
            self.statBar.showMessage("Model pretrained weights set")
        else:
            self.modLoadButton.setEnabled(False)
            self.__msg_timer_block = time.time() if self.aq_on else 0
            self.statBar.showMessage("Invalid model pretrained weight file")

    def __build_model(self):
        """Trigger the GPU worker to load the model checkpoint and unlock the dependent controls."""
        self.__msg_timer_block = time.time() if self.aq_on else 0
        self.statBar.showMessage("Loading defined model")
        self.gpu_proc.build_model()
        # Check sequence length and set status
        if self.seq_len != self.gpu_proc.seq_len:
            self.statBar.showMessage("Error occurred during model building")
            QtWidgets.QMessageBox.critical(self, "Error", "Model input size different from defined sequence length\n"
                                                          "Please define the correct sequence length as the model",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            raise ValueError("Model input size (%d) different from defined sequence length (%d)" %
                             (self.gpu_proc.seq_len, self.seq_len))
        self.act_md = True
        # Enable next controls
        self.srtWfmCombo.setEnabled(True)
        self.smpAntSpinbox.setEnabled(True)
        self.smpPstSpinbox.setEnabled(True)
        self.spkThsSpinbox.setEnabled(True)
        self.spkKvlSpinbox.setEnabled(True)
        # Process control enable
        if self.aq_on:
            self.initProcButton.setEnabled(True)
            self.initProcButton.setToolTip("")
            self.__msg_timer_block = time.time()
        else:
            self.initProcButton.setEnabled(False)
            self.initProcButton.setToolTip("Data streaming required for data process")
            self.__msg_timer_block = 0
        # Notify status bar
        self.statBar.showMessage("Model successfully loaded")

    @QtCore.Slot()
    def __inference_switch(self):
        """Toggle the GPU inference and CPU sorting threads on or off."""
        if self.md_on:
            self.__msg_timer_block = time.time()
            self.statBar.showMessage("Stop data inference")
            self.md_on = False
            self.srtAttachButton.setEnabled(False)
            self.initProcButton.setText("Process")
        else:
            self.rec_ctrl.hw.write_data_queue(True)
            self.md_on = True
            self.cbuf_spk.position(self.cbuf_raw.locate())  # Align plot
            self.gpu_proc.start()
            self.cpu_proc.start()
            self.srtAttachButton.setEnabled(True)
            self.initProcButton.setText("Stop Process")
            self.__msg_timer_block = time.time()
            self.statBar.showMessage("Data inference started")

    def __set_sort_waveform(self):
        """Switch which model output channel is fed to the sorter and clear the spike-data buffer."""
        self.gpu_proc.set_output_waveform()
        # Reset buffer
        self.cbuf_spk.flush()
        self.cbuf_spk.position(self.cbuf_raw.locate())

    def __set_sort_sample(self):
        """Push the latest anterior/posterior sample widths to the sorting worker."""
        self.cpu_proc.set_index_feature()

    def __set_sort_threshold(self):
        """Push the latest amplitude threshold to the sorting worker."""
        self.cpu_proc.set_threshold()

    def __set_sort_kvalue(self):
        """Push the latest spike-grouping ``K`` value to the sorting worker."""
        self.cpu_proc.set_k_value()

    @QtCore.Slot()
    def __sorting_switch(self):
        """Attach or detach the spike sorter and adjust the dependent visualisation panels."""
        if self.st_on:
            self.st_on = False
            # Set plot widgets
            self.plt_pos.hide()
            self.plt_spk.plotItem.showAxis('bottom')
            self.cbuf_pos.flush()
            # Enable current controls
            self.srtWfmCombo.setEnabled(True)
            self.smpAntSpinbox.setEnabled(True)
            self.smpPstSpinbox.setEnabled(True)
            self.spkThsSpinbox.setEnabled(True)
            self.spkKvlSpinbox.setEnabled(True)
            # Set flags
            self.__msg_timer_block = time.time()
            self.statBar.showMessage("Stop spike sorting")
            self.srtAttachButton.setText("Attach")
            self.srtAttachButton.setToolTip("Start data process to attach spike sorter")
        else:
            self.st_on = True
            # Set plot widgets
            self.plt_pos.show()
            self.plt_spk.plotItem.hideAxis('bottom')
            self.__align_left_axis()
            self.cbuf_pos.position(self.cbuf_spk.locate())  # Align plot
            # Disable current controls
            self.srtWfmCombo.setEnabled(False)
            self.smpAntSpinbox.setEnabled(False)
            self.smpPstSpinbox.setEnabled(False)
            self.spkThsSpinbox.setEnabled(False)
            self.spkKvlSpinbox.setEnabled(False)
            # Set flags
            self.srtAttachButton.setText("Detach")
            self.srtAttachButton.setToolTip("")
            self.__msg_timer_block = time.time()
            self.statBar.showMessage("Spike sorter attached")

    def __clear_spike_history(self):
        """Drop the sorting worker's cluster history; bound to controls that change the source channel."""
        self.cpu_proc.reset_history()

    def __update_stat(self):
        # Block 2 seconds for user message
        if time.time() - self.__msg_timer_block < 2:
            return
        # Message update
        msg = "[Recording] %.1f kHz" % (self.fs / 1000)
        if self.md_on:
            if not self.mod_log.empty():
                t_mod = np.mean(self.mod_log.get()) * 1000
                s_mod = self.seq_len / max(t_mod, 5)
                l_mod = t_mod - self.frm if t_mod > self.frm else 0
                msg += "  |  [Inference] %.1f kS/s @ %.1f ms(lag)" % (s_mod, l_mod)
            if self.st_on:
                if not self.srt_log.empty():
                    t_srt = np.mean(self.srt_log.get()) * 1000 + 1e-12  # Avoid zero divisor
                    s_srt = self.seq_len / t_srt
                    l_srt = t_srt - self.frm if t_srt > self.frm else 0
                    msg += "  |  [Sorter] %.1f kS/s @ %.1f ms(lag)" % (s_srt, l_srt)
        self.statBar.showMessage(msg)

    def __clear_queue(self):
        """Stop pushing new samples to the data queue and drop every queued item."""
        self.rec_ctrl.hw.write_data_queue(False)
        self.raw_queue.clear()
        self.spk_queue.queue.clear()
