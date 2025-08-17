# Parus GUI plotting module

from typing import Iterable
import numpy as np
import h5py as h5
import matplotlib as mpl
from matplotlib.backends import backend_agg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib import artist
from matplotlib.legend import Legend
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

__package__ = 'parus.gui'
from ..fio import h5_load_dat

__all__ = ['BlitManager', 'WfmPosMarker', 'ResPltLoader']
"""
Class list:
  BlitManager(canvas, artists=()): Bit blit manager for data plotting.
  WfmPosMarker(canvas, axes, t, wfm=None, pos=None): Bit blit manager for assistive marking elements.
  ResPltLoader(self, file, cmap='winter'): Load Parus analysis results for manual inspection.
"""


class BlitManager:
    def __init__(self, canvas, artists=()):
        """ Bit blit manager for data plotting.

        Args:
            canvas (backend_agg.FigureCanvasAgg): The canvas to work with
            artists (Iterable[artist.Artist]): List of the artists to manage
        """
        self.cvs = canvas
        self.artists = []
        self.__bg = None
        # Verifying and adding artist
        for a in artists:
            self.add_artist(a)
        # Grab the background on every draw
        self.cid = self.cvs.mpl_connect('draw_event', self.on_draw)

    def add_artist(self, art):
        """ Add an artist to be managed.

        Args:
            art (artist.Artist): The artist to be added.
        """
        if art.figure != self.cvs.figure:
            raise RuntimeError("Requested artist not on the targeted figure!")
        art.set_animated(True)
        self.artists.append(art)

    def on_draw(self, event):
        """ Callback to register with 'draw_event'. """
        if event is not None:
            if event.canvas != self.cvs:
                raise RuntimeError("Event canvas is not managed!")
        self.__bg = self.cvs.copy_from_bbox(self.cvs.figure.bbox)
        # Draw all animated artists
        for a in self.artists:
            self.cvs.figure.draw_artist(a)

    def update(self):
        """ Update the screen with animated artists. """
        # Paranoia in case the draw event was missed
        if self.__bg is None:
            self.on_draw(None)
        else:
            # Restore the background
            self.cvs.restore_region(self.__bg)
            # Draw all animated artists
            for a in self.artists:
                self.cvs.figure.draw_artist(a)
            # Update the GUI state
            self.cvs.blit(self.cvs.figure.bbox)
        # GUI event loop process
        self.cvs.flush_events()


class WfmPosMarker(BlitManager):
    def __init__(self, canvas, axes, t, wfm=None, pos=None):
        """ Bit blit manager for assistive marking elements.

        Args:
            canvas (backend_agg.FigureCanvasAgg): The canvas to work with
            axes (plt.Axes): List of the axes to add cursor lines
            t (np.ndarray): {1D-float} Time vector of plot
            wfm (np.ndarray | None): {1D-float} Waveform data (default: None)
            pos (tuple[np.ndarray, int] | None): {1D-int(0|1), Index} Spike position data (default: None)
        """
        # Get index search constants
        self.t = t
        self.__t_ini = t[0].item()
        self.__t_fac = 0 if t[-1] == t[0] else (len(t) - 1) / (t[-1].item() - t[0].item())
        # Set data arrays
        self._wfm = wfm
        self._pos = None if pos is None else pos[0]
        self._py = 0 if pos is None else pos[1]
        # Retrieve cursor lines for all axes
        self._csr_ln = []
        for ax in axes:
            self._csr_ln.append(ax.axvline(x=t[0], linewidth=0.5, color='darkslategray'))
        # Retrieve data markers
        self.__wfm_mkr = axes[0].axhline(y=0, linewidth=0.5, color='darkslategray')
        self.__pos_mkr, = axes[1].plot([None], [None], marker='o', ms=12, mec='r', mfc='none', mew=2, alpha=0.8)
        self._ano_mk = [self.__wfm_mkr, self.__pos_mkr]
        # Active spike position background indicator
        self.__pos_bkg = Rectangle(xy=(t[0].item(), -0.5), width=t[-1].item() - t[0].item(), height=1.0,
                                   ec='none', fc='slategray', alpha=0.5, zorder=-1)
        axes[1].add_patch(self.__pos_bkg)
        # Initialize parent class
        super().__init__(canvas, self._csr_ln + self._ano_mk)
        # Set marker visibility
        self.__wfm_mkr.set_visible(wfm is not None)
        self.__pos_mkr.set_visible(False)
        self.__pos_bkg.set_visible(False)
        # Connect signaling when mouse moved
        self.sid = self.cvs.mpl_connect('motion_notify_event', self.__on_motion)

    def find_nearest(self, value):
        """ Find the index of nearest value in array.

        Args:
            value (int or float): Value to be searched

        Returns:
            int: Index of nearest value in array
        """
        return round((value - self.__t_ini) * self.__t_fac)

    def set_wfm(self, wfm):
        """ Set waveform to attach interactive objects.

        Args:
            wfm (np.ndarray | None):  {1D-float} Waveform data
        """
        self._wfm = wfm
        self.__wfm_mkr.set_visible(wfm is not None)
        self.update()

    def set_pos(self, pos, y):
        """ Set spike position to attach interactive objects.

        Args:
            pos: {1D-int(0|1)} Spike position data (default: None)
            y (int): Spike position virtual Y data index
        """
        self._pos = pos
        # Set marking configurations
        if pos is None:
            self._py = -1
            self.__pos_mkr.set_visible(False)
            self.__pos_bkg.set_visible(False)
        else:
            self._py = y
            self.__pos_bkg.set_y(y - 0.5)
            self.__pos_bkg.set_visible(True)
        self.update()

    def __on_motion(self, event):
        if event.xdata is not None:
            # Set cursor lines
            for a in self._csr_ln:
                a.set_xdata([event.xdata, event.xdata])
            # Set plot markers
            idx = self.find_nearest(event.xdata)
            if self._wfm is not None:
                self.__wfm_mkr.set_ydata([self._wfm[idx], self._wfm[idx]])
            if self._pos is not None:
                pr = np.nonzero(self._pos[idx - 5:idx + 6])[0]
                if pr:
                    ps = pr[0] + idx - 5
                    self.__pos_mkr.set_data([self.t[ps]], [self._py])
                    self.__pos_mkr.set_visible(True)
                else:
                    self.__pos_mkr.set_visible(False)
            self.update()


class ResPltLoader(FigureCanvasQTAgg):
    def __init__(self, file, cmap='winter'):
        """ Load Parus analysis results for manual inspection.

        Args:
            file (str): Parus analysis result HDF5 file
            cmap (str): Matplotlib colour maps to plot
        """
        # Load result data
        with h5.File(file, 'r') as fp:
            self.data = h5_load_dat(fp)
        self.t = np.arange(self.data['inp'].size) / self.data['frq']
        # Initialize data attributes
        self.wfm = {}  # Waveforms in the data
        self.pos = {}  # Detected spike positions
        self.cor = {}  # Manual corrected spike positions
        # Initialize figure
        self.fig, self.ax = plt.subplots(2, 1, sharex='all', sharey='none', height_ratios=(5, 1))
        self.fig.set_layout_engine(layout='tight', h_pad=-0.6)
        self.fig.align_ylabels()
        self.ax[0].spines[['top', 'right', 'bottom']].set_visible(False)
        self.ax[1].spines[['top', 'right']].set_visible(False)
        self.ax[1].spines['left'].set(linestyle=(8, (8, 8)))

        # Get spike colour list
        cm = mpl.colormaps[cmap]
        if len(self.data['spk']) == 1:
            self._clst_spk = [cm(round(cm.N / 2))]
        else:
            cp = np.linspace(0, cm.N, len(self.data['spk']), endpoint=True, dtype=int)
            self._clst_spk = [cm(_) for _ in cp]
        # Get position colour list
        cnt = 0  # Position data counter
        for k in self.data['pos']:
            cnt += len(self.data['pos'][k]) if isinstance(self.data['pos'][k], dict) else 1
        self._clst_pos = [cm(_) for _ in np.linspace(0, cm.N, cnt, endpoint=True, dtype=int)]

        # Plot raw data
        self.wfm['RAW'] = self.ax[0].plot(self.t, self.data['inp'], color='k', alpha=0.8, label="RAW")[0]
        # Plot results
        cnt = 0  # Position data counter
        for i, (k, c) in enumerate(zip(self.data['spk'], self._clst_spk)):
            # Plot spike
            self.wfm[k] = self.ax[0].plot(self.t, self.data['spk'][k], color=c, label=k)[0]
            # Plot position and initialize correction arrays
            self.pos[k] = {}
            if isinstance(self.data['pos'][k], dict):
                self.cor[k] = {}
                for j, p in enumerate(self.data['pos'][k]):
                    pos = np.nonzero(self.data['pos'][k][p])[0]
                    sct = self.ax[1].scatter(self.t[pos], [cnt] * len(pos), color=self._clst_pos[cnt])
                    self.pos[k][p] = {'plt': sct, 'idx': cnt}
                    self.cor[k][p] = np.zeros_like(self.data['pos'][k][p], dtype='int8')
                    cnt += 1  # Counter
            else:
                pos = np.nonzero(self.data['pos'][k])[0]
                sct = self.ax[1].scatter(self.t[pos], [cnt] * len(pos), color=self._clst_pos[cnt])
                self.pos[k][k] = {'plt': sct, 'idx': cnt}
                self.cor[k] = np.zeros_like(self.data['pos'][k], dtype='int8')
                cnt += 1  # Counter

        # Set X axis
        self.ax[0].tick_params(axis='x', which='both', top=False, bottom=False, labelbottom=False)
        self.ax[1].set_xlabel("Time (s)", fontsize=14, fontweight='bold')
        self.ax[1].tick_params(axis='x', which='major', labelsize=12)
        # Set signal Y axis
        self.ax[0].set_ylabel("Amplitude (mV)", fontsize=16, fontweight='bold')
        self._y_min, self._y_max = self.ax[0].get_ylim()
        self._y_min = np.round(self._y_min - 50, decimals=-2)  # Round down to hundreds
        self._y_max = np.round(self._y_max + 50, decimals=-2)  # Round up to hundreds
        self.ax[0].set_ylim(self._y_min, self._y_max)
        self.ax[0].tick_params(axis='y', which='major', labelsize=10)
        # Set position Y axis
        self.ax[1].set_ylabel("Spike", fontsize=14, fontweight='bold')
        self.ax[1].tick_params(axis='y', which='major', direction='inout', length=12, labelsize=14)
        self.ax[1].set_ylim(-1, cnt + 1)
        # Set legends
        self.__leg = Legend(self.ax[0], list(self.wfm.values()), list(self.wfm.keys()), loc='upper right', fontsize=16)
        self.ax[0].add_artist(self.__leg)
        self.__act_leg = None  # Active trace legend
        ano = sum([list(self.pos[k].keys()) for k in self.pos], [])
        self.ax[1].set_yticks(np.arange(len(ano)))
        self.ax[1].set_yticklabels(ano)

        # Connect to Qt backend
        super(ResPltLoader, self).__init__(self.fig)
        # Connect to BlitManager
        self._wpm = WfmPosMarker(self.fig.canvas, self.ax, self.t)
        # Set initial view
        self.set_time(0, 0.1)  # 100ms initial view
        self.set_amp(self._y_min, self._y_max)

    def sel_wfm(self, sel):
        """ Select waveform(s) to be visible.

        Args:
            sel (list[str]): Waveform name keys

        Returns:
            list[str]: Possible spike position keys
        """
        # Select artists
        for k in self.wfm:
            self.wfm[k].set_visible(k in sel)
        for k in self.pos:
            [self.pos[k][p]['plt'].set_visible(k in sel) for p in self.pos[k]]
        # Update legends
        self.__leg.remove()
        sel_w = [k for k in self.wfm if k in sel]
        self.__leg = Legend(self.ax[0], [self.wfm[k] for k in sel_w], sel_w, loc='upper right', fontsize=16)
        self.ax[0].add_artist(self.__leg)
        # Update position plots
        idx = sum([[self.pos[k][p]['idx'] for p in self.pos[k]] for k in self.pos if k in sel], [])
        ano = sum([list(self.pos[k].keys()) for k in self.pos if k in sel], [])
        if idx:
            self.ax[1].set_ylim(min(idx) - 1, max(idx) + 1)
            self.ax[1].set_yticks(idx)
            self.ax[1].set_yticklabels(ano)
        else:
            self.ax[1].set_ylim(-1, 1)
            self.ax[1].set_yticklabels([])
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        # Return possible spike position keys
        pos_key = sum([[k + ' - ' + p for p in self.pos[k]] for k in self.pos if k in sel], [])
        return pos_key

    def set_time(self, start, stop):
        """ Set x-axis (time) range.

        Args:
            start (int | float): Start time
            stop (int | float): Stop time
        """
        # Set axis bound
        self.ax[1].set_xbound(start, stop)
        # Set tick locations
        self.ax[1].set_xticks(np.linspace(start, stop, 5, endpoint=True))
        self.ax[1].xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(5))
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def set_amp(self, low, high, reset=False):
        """ Set y-axis (signal amplitude) range.

        Args:
            low (int | float): Minimum amplitude
            high (int | float): Maximum amplitude
            reset (bool): Reset range to default, ignore [low] and [high] (default: False)
        """
        # Set axis bound
        if reset:
            low = self._y_min
            high = self._y_max
        self.ax[0].set_ybound(low, high)
        # Set tick locations
        step = np.arange(low, high, step=100)
        major = np.linspace(0, len(step) - 1, 5, endpoint=True, dtype=int)
        minor = (step[major[1]] - step[major[0]]) // 100
        self.ax[0].set_yticks(np.concatenate((step[major], [0])))
        self.ax[0].yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(minor))
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def set_act_wfm(self, wfm_key):
        """ Set active waveform to inspect.

        Args:
            wfm_key (str | None): Waveform name key
        """
        # Remove existing active waveform legend
        if self.__act_leg is not None:
            self.__act_leg.remove()
        # Set new active waveform
        if (wfm_key is None) or (not self.wfm[wfm_key].get_visible()):
            self._wpm.set_wfm(None)
            self.__act_leg = None
        else:
            if wfm_key == 'RAW':
                self._wpm.set_wfm(self.data['inp'])
            else:
                self._wpm.set_wfm(self.data['spk'][wfm_key])
            # Add new legend
            self.__act_leg = Legend(self.ax[0], [self.wfm[wfm_key]], [wfm_key], title="Active Trace", loc='upper left',
                                    fontsize=8, title_fontsize=8, facecolor='green')
            self.ax[0].add_artist(self.__act_leg)
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def set_act_pos(self, wfm_key, pos_key):
        """ Set active spike position to verify.

        Args:
            wfm_key (str | None): Waveform name key
            pos_key (str | None): Spike position name key
        """
        if (wfm_key is None) or (wfm_key == 'RAW') or (pos_key is None):
            self._wpm.set_pos(None, -1)
            if wfm_key == 'RAW':
                self.set_act_wfm(wfm_key)
        else:
            if isinstance(self.data['pos'][wfm_key], dict):
                self._wpm.set_pos(self.data['pos'][wfm_key][pos_key], self.pos[wfm_key][pos_key]['idx'])
            else:
                self._wpm.set_pos(self.data['pos'][wfm_key], self.pos[wfm_key][pos_key]['idx'])
            # Force the active waveform to be associated with spike position records
            self.set_act_wfm(wfm_key)
