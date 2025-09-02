# Parus GUI plotting module

from typing import Iterable
import numpy as np
import h5py as h5
import matplotlib as mpl
from matplotlib.backend_bases import MouseButton
from matplotlib.backends import backend_agg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib import artist
from matplotlib import ticker
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
        """ Callback to register with [draw_event]. """
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
    def __init__(self, canvas, axes, t, keys, wfm=None, pos=None):
        """ Bit blit manager for assistive marking elements.

        Args:
            canvas (backend_agg.FigureCanvasAgg): The canvas to work with
            axes (plt.Axes): List of the axes to add cursor lines
            t (np.ndarray): {1D-float} Time vector of plot
            keys (dict[str, list[str]]): Position keys groups to manage
            wfm (np.ndarray | None): {1D-float} Waveform data (default: None)
            pos (tuple[np.ndarray, int] | None): {1D-int(0|1), Index} Spike position data (default: None)
        """
        # Get index search constants
        self.t = t
        self.__t_ini = t[0].item()
        self.__t_fac = 0 if t[-1] == t[0] else (len(t) - 1) / (t[-1].item() - t[0].item())
        self.idx = None  # Current plot index
        # Set data arrays
        self._wfm = wfm
        self._pos = None if pos is None else pos[0]
        self._py = 0 if pos is None else pos[1]
        # Set position correction variables
        self.cor_wfm = None  # Active waveform key for manual correction
        self.cor_pos = None  # Active spike position key for manual correction
        self.cor_dot = None  # Active spike position on select
        self.__pos_on = False
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

        # Spike position manual correction markings
        self.__cor_idx = {}  # Correction recording
        self.__cor_mkr = {}  # Correction marker
        for k in keys:
            self.__cor_idx[k] = {}
            self.__cor_mkr[k] = {}
            for p in keys[k]:
                # Set plots
                add_mrk, = axes[1].plot([None], [None], marker='P', ms=8, color='crimson', ls='none')
                self._ano_mk.append(add_mrk)
                rmv_mrk, = axes[1].plot([None], [None], marker='X', ms=9, color='crimson', ls='none')
                self._ano_mk.append(rmv_mrk)
                # Set control variables
                self.__cor_idx[k][p] = {'+': set(), '-': set()}  # Use set to keep uniqueness
                self.__cor_mkr[k][p] = {'+': add_mrk, '-': rmv_mrk}

        # Initialize parent class
        super().__init__(canvas, self._csr_ln + self._ano_mk)
        # Set marker visibility
        self.__wfm_mkr.set_visible(wfm is not None)
        self.__pos_mkr.set_visible(False)
        self.__pos_bkg.set_visible(False)
        # Connect signaling when mouse moved
        self.sid = self.cvs.mpl_connect('motion_notify_event', self.__on_motion)
        self.cid = self.cvs.mpl_connect('button_press_event', self.__on_click)

    def find_nearest(self, value):
        """ Find the index of nearest value in array.

        Args:
            value (int | float): Value to be searched

        Returns:
            int: Index of nearest value in array
        """
        return round((value - self.__t_ini) * self.__t_fac)

    def find_extremum(self, index):
        """ Find the index of nearest extremum in array, assuming the extremum have the same sign.

        Args:
            index (int): Initial index

        Returns:
            int | None: Index of nearest extremum
        """
        if self._wfm is None:
            return None
        else:
            if self._wfm[index] > 0:
                return np.argmax(self._wfm[index - 5:index + 6]).item() + index - 5
            else:
                return np.argmin(self._wfm[index - 5:index + 6]).item() + index - 5

    def set_wfm(self, wfm):
        """ Set waveform to attach interactive objects.

        Args:
            wfm (np.ndarray | None):  {1D-float} Waveform data
        """
        self._wfm = wfm
        self.__wfm_mkr.set_visible(wfm is not None)
        self.update()

    def set_pos(self, pos, y, wfm_key, pos_key):
        """ Set spike position to attach interactive objects.

        Args:
            pos (np.ndarray | None): {1D-int(0|1)} Spike position data (default: None)
            y (int): Spike position virtual Y data index
            wfm_key (str | None): Waveform name
            pos_key (str | None): Spike name
        """
        self._pos = pos
        self.cor_wfm = wfm_key
        self.cor_pos = pos_key
        # Set marking configurations
        if pos is None:
            self._py = -1
            self.__pos_mkr.set_visible(False)
            self.__pos_bkg.set_visible(False)
            self.__pos_on = False
        else:
            self._py = y
            self.__pos_bkg.set_y(y - 0.5)
            self.__pos_bkg.set_visible(True)
            self.__pos_on = True
        self.update()

    def chk_cor(self):
        """ Check if any manual correction has been made.

        Returns:
            bool: Correction made flag
        """
        flag = False
        for k in self.__cor_idx:
            if flag:
                break
            for p in self.__cor_idx[k]:
                if self.__cor_idx[k][p]['+']:
                    flag = True
                    break
                if self.__cor_idx[k][p]['-']:
                    flag = True
                    break
        return flag

    def get_cor(self):
        """ Get all manual correction data.

        Returns:
            {1D-int8(-1|0|1)} Manual correction data
        """
        cor = {}  # INIT VAR
        for k in self.__cor_idx:
            if len(self.__cor_idx[k]) == 1:
                man = np.zeros_like(self.t, dtype=np.int8)
                if self.__cor_idx[k][k]['+']:
                    man[list(self.__cor_idx[k][k]['+'])] = 1
                if self.__cor_idx[k][k]['-']:
                    man[list(self.__cor_idx[k][k]['-'])] = -1
                cor[k] = man.copy()
            else:
                cor[k] = {}
                for p in self.__cor_idx[k]:
                    man = np.zeros_like(self.t, dtype=np.int8)
                    if self.__cor_idx[k][p]['+']:
                        man[list(self.__cor_idx[k][p]['+'])] = 1
                    if self.__cor_idx[k][p]['-']:
                        man[list(self.__cor_idx[k][p]['-'])] = -1
                    cor[k][p] = man.copy()
        return cor

    def reset_cor(self):
        """ Reset all manual corrections. """
        for k in self.__cor_idx:
            for p in self.__cor_idx[k]:
                self.__cor_idx[k][p] = {'+': set(), '-': set()}  # Reset to original
        self.__plt_cor_mrk()  # Update plot


    def __plt_cor_mrk(self):
        """ Plot manual correction marker """
        # Plot added positions
        self.__cor_mkr[self.cor_wfm][self.cor_pos]['+'].set_data(
            self.t[list(self.__cor_idx[self.cor_wfm][self.cor_pos]['+'])],
            [self._py] * len(self.__cor_idx[self.cor_wfm][self.cor_pos]['+'])
        )
        # Plot removed positions
        self.__cor_mkr[self.cor_wfm][self.cor_pos]['-'].set_data(
            self.t[list(self.__cor_idx[self.cor_wfm][self.cor_pos]['-'])],
            [self._py] * len(self.__cor_idx[self.cor_wfm][self.cor_pos]['-'])
        )
        # Update plot
        self.update()

    def __on_motion(self, event):
        """ Callback to register with [motion_notify_event]. """
        if event.xdata is not None:
            # Set cursor lines
            for a in self._csr_ln:
                a.set_xdata([event.xdata, event.xdata])
            # Set plot markers
            self.idx = self.find_nearest(event.xdata)
            if self._wfm is not None:
                self.__wfm_mkr.set_ydata([self._wfm[self.idx], self._wfm[self.idx]])
            if self._pos is not None:
                # Check if inference position nearby
                p_inf = np.nonzero(self._pos[self.idx - 5:self.idx + 6])[0]
                if p_inf:
                    self.cor_dot = p_inf[0] + self.idx - 5
                    self.idx = self.cor_dot
                    self.__pos_mkr.set_data([self.t[self.cor_dot]], [self._py])
                    self.__pos_mkr.set_visible(True)
                else:
                    # Check if manual corrected position nearby
                    for i in self.__cor_idx[self.cor_wfm][self.cor_pos]['+']:
                        if self.idx - 6 < i < self.idx + 6:
                            self.cor_dot = i
                            self.idx = self.cor_dot
                            self.__pos_mkr.set_data([self.t[self.cor_dot]], [self._py])
                            self.__pos_mkr.set_visible(True)
                            break
                    # Do not mark when not found
                    else:
                        self.cor_dot = None
                        self.__pos_mkr.set_visible(False)
            self.update()

    def __on_click(self, event):
        """ Callback to register with [button_press_event]. """
        if event.button is MouseButton.LEFT:
            if self.__pos_on:
                if self.idx in self.__cor_idx[self.cor_wfm][self.cor_pos]['-']:
                    self.__cor_idx[self.cor_wfm][self.cor_pos]['-'].remove(self.idx)
                else:
                    if self.cor_dot is None:
                        exm_idx = self.find_extremum(self.idx)  # Find extremum around the index for easier usage
                        self.__cor_idx[self.cor_wfm][self.cor_pos]['+'].add(exm_idx)
                self.__plt_cor_mrk()
        elif event.button is MouseButton.RIGHT:
            if self.__pos_on:
                if self.idx in self.__cor_idx[self.cor_wfm][self.cor_pos]['+']:
                    self.__cor_idx[self.cor_wfm][self.cor_pos]['+'].remove(self.idx)
                else:
                    if self.cor_dot is not None:
                        self.__cor_idx[self.cor_wfm][self.cor_pos]['-'].add(self.idx)
                self.__plt_cor_mrk()


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
                for j, p in enumerate(self.data['pos'][k]):
                    pos = np.nonzero(self.data['pos'][k][p])[0]
                    sct = self.ax[1].scatter(self.t[pos], [cnt] * len(pos), color=self._clst_pos[cnt])
                    self.pos[k][p] = {'plt': sct, 'idx': cnt}
                    cnt += 1  # Counter
            else:
                pos = np.nonzero(self.data['pos'][k])[0]
                sct = self.ax[1].scatter(self.t[pos], [cnt] * len(pos), color=self._clst_pos[cnt])
                self.pos[k][k] = {'plt': sct, 'idx': cnt}
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
        key_wpm = {k: list(self.pos[k].keys()) for k in self.pos}
        self._wpm = WfmPosMarker(self.fig.canvas, self.ax, self.t, key_wpm)
        # Set initial view
        self.set_time(0, 0.1)  # 100ms initial view
        self.set_amp(self._y_min, self._y_max)

    def sel_wfm(self, sel, lnk_pos=True):
        """ Select waveform(s) to be visible.

        Args:
            sel (list[str]): Waveform name keys
            lnk_pos (bool): If corresponding position plot will be disabled (default: True)

        Returns:
            list[str]: Possible spike position keys
        """
        # Set waveform
        for k in self.wfm:
            self.wfm[k].set_visible(k in sel)
        # Update legends
        self.__leg.remove()
        sel_w = [k for k in self.wfm if k in sel]
        self.__leg = Legend(self.ax[0], [self.wfm[k] for k in sel_w], sel_w, loc='upper right', fontsize=16)
        self.ax[0].add_artist(self.__leg)
        # Set positions
        if lnk_pos:
            for k in self.pos:
                [self.pos[k][p]['plt'].set_visible(k in sel) for p in self.pos[k]]
            # Update position locations
            idx = sum([[self.pos[k][p]['idx'] for p in self.pos[k]] for k in self.pos if k in sel], [])
            ano = sum([list(self.pos[k].keys()) for k in self.pos if k in sel], [])
        else:
            for k in self.pos:
                [self.pos[k][p]['plt'].set_visible(True) for p in self.pos[k]]
            # Update position locations
            idx = sum([[self.pos[k][p]['idx'] for p in self.pos[k]] for k in self.pos], [])
            ano = sum([list(self.pos[k].keys()) for k in self.pos], [])
        # Update Y-axis labels
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
        # Return spike position keys with visible waveform
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
        self.ax[1].xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
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
        major = np.linspace(0, len(step) - 1, 6, endpoint=True, dtype=int)
        self.ax[0].set_yticks(np.concatenate((step[major], [0])))
        self.ax[0].yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
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
            self._wpm.set_pos(None, -1, None, None)
            if wfm_key == 'RAW':
                self.set_act_wfm(wfm_key)
        else:
            pos_grp = self.data['pos'][wfm_key]
            if isinstance(pos_grp, dict):
                self._wpm.set_pos(pos_grp[pos_key], self.pos[wfm_key][pos_key]['idx'], wfm_key, pos_key)
            else:
                self._wpm.set_pos(pos_grp, self.pos[wfm_key][pos_key]['idx'], wfm_key, pos_key)
            # Force the active waveform to be associated with spike position records
            if self.wfm[wfm_key].get_visible():
                self.set_act_wfm(wfm_key)
            else:
                self.set_act_wfm('RAW')

    def check_correction(self):
        """ Check if manual correction exist. """
        return self._wpm.chk_cor()

    def make_correction(self):
        """ Set all manual corrected position to current data. """
        cor = self._wpm.get_cor()
        for k in self.data['pos']:
            if isinstance(self.data['pos'][k], dict):
                for p in self.data['pos'][k]:
                    # Set new position data
                    self.data['pos'][k][p] += cor[k][p]
                    # Update plot
                    pos = np.nonzero(self.data['pos'][k][p])[0]
                    self.pos[k][p]['plt'].set_offsets(np.c_[self.t[pos], [self.pos[k][p]['idx']] * len(pos)])
            else:
                # Set new position data
                self.data['pos'][k] += cor[k]
                # Update plot
                pos = np.nonzero(self.data['pos'][k])[0]
                self.pos[k][k]['plt'].set_offsets(np.c_[self.t[pos], [self.pos[k][k]['idx']] * len(pos)])
        # Reset all corrections
        self._wpm.reset_cor()
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        return self.data
