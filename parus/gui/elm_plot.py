# -*- coding: utf-8 -*-

"""GUI plotting module

Matplotlib-on-Qt canvases and supporting artists used by the PARUS GUIs to render archival signal previews,
clustering features, waveform markers, and analysis results.
"""

from typing import Iterable
import numpy as np
import h5py as h5
from matplotlib.backend_bases import MouseButton
from matplotlib.backends import backend_agg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib import artist
from matplotlib import ticker
from matplotlib.colors import Colormap, to_rgba
from matplotlib.legend import Legend
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import warnings

__package__ = 'parus.gui'
__name__ = 'parus.gui.elm_plot'
from ..fio import h5_load_dat
from ..data import spk_correlogram
from . import cs_dark

__all__ = ['LoopedColormap', 'BlitManager', 'ArcPreviewPlot', 'ClstFeatViewer', 'WfmPosMarker', 'ResPltLoader']
"""
Public class list:

- LoopedColormap(clst, name)                            : Looped Matplotlib colormap with no resampling
- BlitManager(canvas, artists)                          : Blit-based animation manager for plotting
- ArcPreviewPlot(data)                                  : Archival neural signal preview canvas
- ClstFeatViewer(raw, spk, t, asp, psp, clst, ...)      : Spike-clustering feature visualiser
- WfmPosMarker(canvas, axes, t, wfm, pos)               : Blit manager for assistive waveform-marking artists
- ResPltLoader(file, cmap)                              : Load PARUS analysis results for manual inspection
"""


class LoopedColormap(Colormap):
    """Looped Matplotlib colormap that cycles through a fixed colour list without resampling.

    Lookup wraps modulo the list length so values larger than ``N - 1`` reuse the earlier colours rather
    than being clamped or resampled.
    """

    def __init__(self, clst, name='loop_cmap'):
        """Build the colormap from a colour list.

        Args:
            clst (list): Colour list passed to :class:`~matplotlib.colors.Colormap`
            name (str): Colormap name (default: ``'loop_cmap'``)
        """
        self.colors = clst
        self.monochrome = len(clst) == 1
        super(LoopedColormap, self).__init__(name=name, N=len(clst))

    def __call__(self, x, alpha=None, *args):
        """Sample the colormap at one or many positions, looping modulo the colour count.

        Args:
            x (int | float | list[int | float] | np.ndarray): Sampling position(s)
            alpha (float | None): Alpha level in ``[0, 1]`` (default: ``None``)
            *args: Extra arguments accepted by the parent class signature; ignored

        Returns:
            tuple[float, float, float, float] | np.ndarray: RGBA colour for a scalar ``x``, or an array of
                RGBA colours for an iterable ``x``
        """
        if np.iterable(x):
            cnt = np.rint(x).astype(int) % self.N
            shape = np.append(cnt.shape, 4)  # Append RGBA size
            clr = np.asarray([to_rgba(self.colors[c]) for c in cnt.flatten()])
            return clr.reshape(shape)
        else:
            c = x % self.N
            return to_rgba(self.colors[c])

    def __getitem__(self, item):
        """Return the colour at the given list index (looped modulo the colour count)."""
        return self.__call__(item, alpha=None)


class BlitManager:
    """Blit-based animation manager that captures the canvas background and selectively redraws artists.

    Stores the static background of a canvas after each draw event so dynamic artists can be cheaply
    redrawn without repainting the rest of the figure.
    """

    def __init__(self, canvas, artists=()):
        """Attach the manager to a canvas and register an initial set of dynamic artists.

        Args:
            canvas (backend_agg.FigureCanvasAgg): Canvas whose background is captured between draws
            artists (Iterable[artist.Artist]): Initial artists to manage (default: ``()``)
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
        """Register an artist as animated and start managing it.

        Args:
            art (artist.Artist): Artist to add (must belong to the manager's canvas)
        """
        if art.figure != self.cvs.figure:
            warnings.warn("Requested artist not on the targeted figure!", RuntimeWarning, stacklevel=2)
        art.set_animated(True)
        self.artists.append(art)

    def remove_artist(self, art):
        """Stop managing an artist and reset its animated flag.

        Args:
            art (artist.Artist): Artist to remove
        """
        if art.figure != self.cvs.figure:
            warnings.warn("Requested artist not on the targeted figure!", RuntimeWarning, stacklevel=2)
        if art in self.artists:
            art.set_animated(False)
            self.artists.remove(art)
        else:
            warnings.warn("Requested artist not managed!", RuntimeWarning, stacklevel=2)

    def on_draw(self, event):
        """Capture the canvas background and redraw the managed artists; bound to ``draw_event``."""
        if event is not None:
            if event.canvas != self.cvs:
                raise RuntimeError("Event canvas is not managed!")
        self.__bg = self.cvs.copy_from_bbox(self.cvs.figure.bbox)
        # Draw all animated artists
        for a in self.artists:
            self.cvs.figure.draw_artist(a)

    def update(self):
        """Restore the cached background and blit every managed artist on top of it."""
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


class ArcPreviewPlot(FigureCanvasQTAgg):
    """Qt canvas that renders an archival neural signal sample with its spike peak and refined range marked."""

    def __init__(self, data):
        """Build the figure, render the trace, and connect it to the Qt backend.

        Args:
            data (dict): Archival signal data; see the ARC data structure definition in :mod:`parus.fio.fdata`
        """
        t = list(range(len(data['sig'])))
        # Get spike peak labels
        peak_t = t[data['pos']]
        peak_sig = data['sig'][data['pos']]
        # Get signal range
        sig_rng = data['rng'] if data['rng'] is not None else None
        # Setup plot
        self.fig, self.ax = plt.subplots(1, 1)
        self.fig.set_layout_engine(layout='tight')
        self.ax.set_title("Preview Archival Signal", fontsize=12, fontweight='bold')
        self.ax.set_xlabel("Data Point", fontsize=12)
        self.ax.set_ylabel("Amplitude", fontsize=12)
        # Plotting
        self.ax.plot(t, data['sig'], lw=1.5, zorder=1)
        self.ax.scatter(peak_t, peak_sig, marker='x', c='r', s=64, alpha=0.75, zorder=4)
        # Add reference lines
        self.ax.axhline(0, c='white' if cs_dark() else 'darkgray', lw=0.5, alpha=0.75, zorder=2)
        if sig_rng is not None:
            self.ax.axvline(sig_rng[0], c='azure' if cs_dark() else'gray', ls='-.', lw=1, alpha=0.75, zorder=3)
            self.ax.axvline(sig_rng[1], c='azure' if cs_dark() else'gray', ls='-.', lw=1, alpha=0.75, zorder=3)
        # Connect to Qt backend
        super(ArcPreviewPlot, self).__init__(self.fig)

    def close(self):
        """Close the embedded Matplotlib figure to release its resources."""
        plt.close(self.fig)


class ClstFeatViewer:
    """Spike-clustering feature visualiser that aggregates per-cluster waveform and timing plots.

    Builds the figure layout used by the spike-sorting GUI to display per-cluster waveforms, mean
    waveforms, inter-spike interval histograms, and other derived features for one recording.
    """

    def __init__(self, raw, spk, t, asp, psp, clst, min_cnt=50, cmap=None):
        """Pre-aggregate per-cluster data and prepare the plot layout.

        Args:
            raw (np.ndarray): {2D-float32} Raw signal data
            spk (dict[str, np.ndarray]): {2D-float32} Spike signal data
            t (np.ndarray): {1D-float32} Time data
            asp (dict[str, int]): Anterior sample count per spike type
            psp (dict[str, int]): Posterior sample count per spike type
            clst (dict[str, list[list[np.ndarray]]]): {1D-int64} Cluster indices per spike type
            min_cnt (int): Minimum number of elements required for a cluster to be plotted (default: ``50``)
            cmap (LoopedColormap | None): Plotting colormap (default: ``None``)
        """
        # Get inputs
        self.raw = raw
        self.spk = spk
        self.clst = clst
        self.t = t
        # Set sampling features
        self.fs = (len(t) - 1) / t[-1].item()
        self.num = {w: asp.get(w, 5) + psp.get(w, 5) + 1 for w in spk}
        self.blk = {w: np.arange(-asp.get(w, 5), psp.get(w, 5) + 1, step=1, dtype=int) for w in spk}
        self.min_cnt = min_cnt
        # Channel control
        self.max_ch = raw.shape[0] - 1
        self.chn = 0

        # Create plot colour map
        self.cmap = LoopedColormap(
            ['#ebac23', '#b80058', '#008cf9', '#006e00', '#00bbad', '#d163e6', '#b24502', '#ff9287', '#5954d6',
             '#00c6f8', '#878500', '#00a76c', '#f6da9c', '#ff5caa', '#8accff', '#4bff4b', '#6efff4', '#edc1f5',
             '#feae7c', '#ffc8c3', '#bdbbef', '#bdf2ff', '#fffc43', '#65ffc8'], name='ParusClstCmap'
        ) if cmap is None else cmap

        # Create internal classes
        self.chn_feat = self._ChnFeat(self)
        self.grp_feat = self._GrpFeat(self)
        self.spk_feat = self._SpkFeat(self)

    class _ChnFeat(FigureCanvasQTAgg):
        """Per-channel cluster feature canvas: amplitude scatter and waveform overlay."""

        def __init__(self, parent):
            """Build the two-axis canvas, prepare per-cluster artists, and render the initial frame.

            Args:
                parent (ClstFeatViewer): Owning :class:`ClstFeatViewer` instance
            """
            # Get inputs
            self._cfv = parent
            # Flatten clusters
            self.ftc = sum([self._cfv.clst[w][self._cfv.chn] for w in self._cfv.clst], [])
            self.isc = np.concatenate(self.ftc) if self.ftc else []
            # Flatten inference results
            con = np.asarray([self._cfv.spk[w][self._cfv.chn] for w in self._cfv.spk])
            sel = np.argmax(np.abs(con), axis=0)
            self.inf = np.take_along_axis(con, sel[np.newaxis, :], axis=0)[0]
            # Initialize figure
            self.fig, self.ax = plt.subplots(2, 1, sharex='none', sharey='none', height_ratios=(1, 3))
            self.fig.set_layout_engine(layout='tight', h_pad=-0.1)
            self.fig.align_ylabels()
            # Setup axes
            for a in self.ax:
                a.spines[['top', 'bottom', 'right']].set_visible(False)
                a.tick_params(axis='both', left=True, top=False, right=False, bottom=False,
                              labelleft=True, labeltop=False, labelright=False, labelbottom=True)
            # Figure data
            self.__typ = 'spk'
            self.bkg = self.inf
            self.src = {w: self._cfv.spk[w][self._cfv.chn] for w in self._cfv.spk}
            self.__sct_frm = -1
            self._rp = {}  # Raw plot artists
            self._st = []  # Amplitude scatter artists
            self._lt = []  # Waveform line artists
            self._ac = [len(i) >= self._cfv.min_cnt for i in self.ftc]  # Active cluster list
            self.__rct = None  # Signal position rectangle
            # Initial plot
            self.plot_fig(start=0, reset_axes=True)
            # Connect to Qt backend
            super(ClstFeatViewer._ChnFeat, self).__init__(self.fig)

        def plot_fig(self, start=0, reset_axes=True):
            """Render the amplitude-scatter and waveform views starting at ``start`` seconds.

            Args:
                start (int | float): Plot start time in seconds (default: ``0``)
                reset_axes (bool): When :data:`True`, reset the axis ticks and labels (default: ``True``)
            """
            # Get time
            sct_ti = start // 30 * 30.0
            sct_te = min(sct_ti + 30, self._cfv.t[-1].item())
            i_si = round(sct_ti * self._cfv.fs)
            i_se = round(sct_te * self._cfv.fs)
            i_li = round(start * self._cfv.fs)
            i_le = round((start + 0.1) * self._cfv.fs)

            # Plot amplitude scatter background
            if sct_ti != self.__sct_frm:
                # Clean up previous data
                [[s.remove() for s in st] for st in self._st]  # Remove unused plots
                self._st = []  # RESET VAR
                # Plot new amplitude scatter background
                if len(self.isc) > 0:
                    idx = self.isc[(self.isc >= i_si) & (self.isc < i_se)]
                    if 's' in self._rp:
                        self._rp['s'].set_offsets(np.c_[self._cfv.t[idx], self.bkg[idx]])
                    else:
                        self._rp['s'] = self.ax[0].scatter(self._cfv.t[idx], self.bkg[idx], s=6, c='gray', zorder=1)
                self.ax[0].set_xlim(sct_ti, sct_te)  # Set X-axis
            # Plot waveform background
            [[l.remove() for l in lt] for lt in self._lt]  # Remove unused plots
            self._lt = []  # RESET VAR
            if 'l' in self._rp:
                self._rp['l'].set_data(self._cfv.t[i_li:i_le], self.bkg[i_li:i_le])
            else:
                self._rp['l'], = self.ax[1].plot(self._cfv.t[i_li:i_le], self.bkg[i_li:i_le], c='gray', zorder=1)
            self.ax[1].set_xlim(start, start + 0.1)  # Set X-axis

            # Plot clusters
            i = 0  # Index counter
            for w in self.src:
                plt_src = self.src[w]
                for c in self._cfv.clst[w][self._cfv.chn]:
                    # Plot amplitude scatter map
                    if sct_ti != self.__sct_frm:
                        idx = c[(c >= i_si) & (c < i_se)]
                        s = self.ax[0].scatter(self._cfv.t[idx], plt_src[idx], s=4, color=self._cfv.cmap[i], zorder=2)
                        s.set_visible(self._ac[i])
                        self._st.append([s])
                    # Plot waveform
                    idx = c[(c >= i_li) & (c < i_le)]
                    idx = np.repeat(idx, self._cfv.num[w]) + np.tile(self._cfv.blk[w], len(idx))
                    idx = np.clip(idx, a_min=0, a_max=len(plt_src) - 1).reshape(self._cfv.num[w], -1, order='F')
                    l = self.ax[1].plot(self._cfv.t[idx], plt_src[idx], c=self._cfv.cmap[i], zorder=2)
                    [_.set_visible(self._ac[i]) for _ in l]
                    self._lt.append(l)
                    # Counter
                    i += 1

            # Reset axes features
            if reset_axes:
                self.ax[0].set_ylabel("Amplitude", fontsize=8, fontweight='bold')
                if len(self.isc) > 0:
                    y_min, y_max = np.min(self.bkg[self.isc]), np.max(self.bkg[self.isc])
                    y_mag = (y_max - y_min) * 0.05
                    y_min, y_max = y_min - y_mag, y_max + y_mag
                else:
                    y_min, y_max = -5, 5
                self.ax[1].set_ylabel("Waveform", fontsize=8, fontweight='bold')
                self.ax[1].set_ylim(min(np.min(self.bkg), -5), max(np.max(self.bkg), 5))
                # Position marker for amplitude scatter plot
                self.__rct = Rectangle(xy=(self._cfv.t[0].item(), y_min), width=0.1, height=y_max - y_min,
                                       ec='none', fc='slategray', alpha=0.5, zorder=0)
                self.ax[0].add_patch(self.__rct)
            # Annotations
            self.ax[0].set_xticks(ticks=[self.ax[0].get_xlim()[1]], labels=["%.0f s" % self.ax[0].get_xlim()[1]])
            self.ax[0].set_yticks([int(y) for y in self.ax[0].get_ylim()])
            self.ax[1].set_xticks(ticks=[self.ax[1].get_xlim()[1]], labels=["%.2f s" % self.ax[1].get_xlim()[1]])
            self.ax[1].set_yticks([int(y) for y in self.ax[1].get_ylim()] + [0])

            # Force figure update
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            # Set control variables
            self.__sct_frm = sct_ti

        def __clear_fig(self):
            """Clear axes and reset the per-cluster artist registries."""
            # Clear axes
            self.ax[0].clear()
            self.ax[1].clear()
            # Reset figure data variables
            self.__sct_frm = -1
            self._rp = {}
            self._st = []
            self._lt = []
            self.__rct = None

        def replot_fig(self):
            """Refresh data caches and redraw the figure from scratch (used after a cluster merge)."""
            # Flatten inference results
            con = np.asarray([self._cfv.spk[w][self._cfv.chn] for w in self._cfv.spk])
            sel = np.argmax(np.abs(con), axis=0)
            self.inf = np.take_along_axis(con, sel[np.newaxis, :], axis=0)[0]
            # Set data
            self.bkg = self.inf if self.__typ == 'spk' else self._cfv.raw[self._cfv.chn]
            self.src = {w: self._cfv.spk[w][self._cfv.chn] if self.__typ == 'spk' else self._cfv.raw[self._cfv.chn]
                        for w in self._cfv.spk}
            # Flatten clusters
            self.ftc = sum([self._cfv.clst[w][self._cfv.chn] for w in self._cfv.clst], [])
            self.isc = np.concatenate(self.ftc) if self.ftc else []
            # Active cluster list
            self._ac = [len(i) >= self._cfv.min_cnt for i in self.ftc]
            # Replot figure
            self.__clear_fig()
            self.plot_fig(start=0, reset_axes=True)

        def switch_fig(self, typ='raw'):
            """Switch the underlying source between the raw signal and the inferred spike signal.

            Args:
                typ (str): Source data type; one of ``{'raw', 'spk'}`` (default: ``'raw'``)
            """
            if typ != self.__typ:
                self.__typ = typ
                # Set data
                self.bkg = self.inf if self.__typ == 'spk' else self._cfv.raw[self._cfv.chn]
                self.src = {w: self._cfv.spk[w][self._cfv.chn] if self.__typ == 'spk' else self._cfv.raw[self._cfv.chn]
                            for w in self._cfv.spk}
                time = self.ax[1].get_xlim()[0]
                # Replot figure
                self.__clear_fig()
                self.plot_fig(start=time, reset_axes=True)

        def set_time(self, start):
            """Move the x-axis window to start at ``start`` seconds (scatter marker tracks the change).

            Args:
                start (int | float): Plot start time in seconds
            """
            # Set amplitude scatter position marker
            if self.__rct is not None:
                self.__rct.set_x(start)
            # Plot with new axis bound
            self.plot_fig(start=start, reset_axes=False)

        def set_act_clst(self, idx=None):
            """Restrict visible clusters to the indices in ``idx`` (or apply the size threshold).

            Args:
                idx (list[int] | None): Cluster indices to show; pass :data:`None` to fall back to the
                    ``min_cnt`` size threshold (default: ``None``)
            """
            for i in range(len(self.ftc)):
                flag = (len(self.ftc[i]) >= self._cfv.min_cnt) if idx is None else (i in idx)
                self._ac[i] = flag
                [s.set_visible(flag) for s in self._st[i]]
                [l.set_visible(flag) for l in self._lt[i]]
            # Force figure update
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    class _GrpFeat(FigureCanvasQTAgg):
        """Per-group canvas showing the mean (± std) waveform of every cluster in the active group."""

        def __init__(self, parent):
            """Build the canvas and render the initial mean-waveform overlay.

            Args:
                parent (ClstFeatViewer): Owning :class:`ClstFeatViewer` instance
            """
            # Get inputs
            self._cfv = parent
            self.__grp = list(self._cfv.spk.keys())[0]

            # Initialize figure
            self.fig, self.ax = plt.subplots(1, 1)
            self.fig.set_layout_engine(layout='tight')
            # Setup axes
            self.ax.spines[['top', 'bottom', 'left', 'right']].set_visible(False)
            self.ax.tick_params(axis='both', left=False, top=False, right=False, bottom=False,
                                labelleft=False, labeltop=False, labelright=False, labelbottom=False)
            # Figure data
            self.__wfm_lst = []  # Waveform line artists
            self.__mrk_txt = None  # No spike marker texts
            # Initial plot
            self.plot_fig()
            # Connect to Qt backend
            super(ClstFeatViewer._GrpFeat, self).__init__(self.fig)

        def __update_axis(self):
            """Refresh the axis title, limits, and the no-spike fallback marker."""
            # Remove previous marker
            if self.__mrk_txt is not None:
                self.__mrk_txt.remove()
                self.__mrk_txt = None
            # Set axis
            self.ax.set_title("Averaged Waveform [%s]" % self.__grp, fontsize=9, fontweight='bold')
            if len(self._cfv.clst[self.__grp][self._cfv.chn]) == 0:
                self.ax.set_xbound(0, 1)
                self.ax.set_ybound(0, 1)
                self.__mrk_txt = self.ax.text(0.5, 0.5, "No Spike", size=9, ha='center', va='center')
            else:
                self.ax.set_xlim(0, self._cfv.num[self.__grp] - 1)
                self.ax.margins(y=0)
            # Force figure update
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        def plot_fig(self):
            """Compute mean and ±1-std waveform per cluster and draw them on the canvas."""
            self.__wfm_lst = []  # RESET VAR
            i = 0
            for w in self._cfv.spk:
                xx = np.arange(self._cfv.num[w])
                for c in self._cfv.clst[w][self._cfv.chn]:
                    # Sample and stats
                    idx = np.repeat(c, self._cfv.num[w]) + np.tile(self._cfv.blk[w], len(c))
                    idx = np.clip(idx, a_min=0, a_max=len(self._cfv.spk[w][self._cfv.chn]) - 1).reshape(
                        self._cfv.num[w], -1, order='F')
                    avg = np.mean(self._cfv.spk[w][self._cfv.chn][idx], axis=1)
                    std = np.std(self._cfv.spk[w][self._cfv.chn][idx], axis=1)
                    # Plot trace
                    y_lo, y_hi = avg - std, avg + std
                    clr, zod = ('gray', 0) if len(c) < self._cfv.min_cnt else (self._cfv.cmap[i], 2)
                    vis = w == self.__grp
                    f = self.ax.fill_between(xx, y1=y_hi, y2=y_lo, fc=clr, ec='none', alpha=0.5, zorder=zod)
                    f.set_visible(vis)
                    l, = self.ax.plot(xx, avg, c=clr, zorder=zod + 1)
                    l.set_visible(vis)
                    self.__wfm_lst.append({'f': f, 'l': l, 'c': self._cfv.cmap[i], 'g': w, 'n': len(c)})
                    # Counter
                    i += 1
            # Set axis
            self.__update_axis()

        def replot_fig(self):
            """Clear the axes and redraw the figure (used after a cluster merge)."""
            # Clear axes
            self.ax.clear()
            self.__mrk_txt = None
            # Plot new data
            self.plot_fig()

        def set_spk_grp(self, grp):
            """Switch which waveform group's mean traces are visible.

            Args:
                grp (int): Index into the spike-group keys of the parent viewer
            """
            grp = list(self._cfv.spk.keys())[grp]
            if grp != self.__grp:
                self.__grp = grp
                # Set artists visibility
                for i in self.__wfm_lst:
                    vis = i['g'] == grp
                    i['f'].set_visible(vis)
                    i['l'].set_visible(vis)
                # Set axis
                self.__update_axis()

        def set_act_clst(self, idx=None):
            """Highlight the listed clusters in colour, dimming everything else to grey.

            Args:
                idx (list[int] | None): Cluster indices to highlight; pass :data:`None` to fall back to
                    the ``min_cnt`` size threshold (default: ``None``)
            """
            for i in range(len(self.__wfm_lst)):
                flag = (self.__wfm_lst[i]['n'] >= self._cfv.min_cnt) if idx is None else (i in idx)
                c, z = (self.__wfm_lst[i]['c'], 2) if flag else ('gray', 0)
                self.__wfm_lst[i]['f'].set_color(c)
                self.__wfm_lst[i]['f'].set_zorder(z)
                self.__wfm_lst[i]['l'].set_color(c)
                self.__wfm_lst[i]['l'].set_zorder(z + 1)
            # Force figure update
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    class _SpkFeat(FigureCanvasQTAgg):
        """Spike-train feature canvas: correlogram on top and per-cluster sample plot below."""

        def __init__(self, parent):
            """Build the canvas, clear initial state, and connect to the Qt backend.

            Args:
                parent (ClstFeatViewer): Owning :class:`ClstFeatViewer` instance
            """
            # Get inputs
            self._cfv = parent

            # Initialize figure
            self.fig, self.ax = plt.subplots(2, 1, sharex='none', sharey='none', height_ratios=(1, 3))
            self.fig.set_layout_engine(layout='tight')
            self.ax[0].spines[['top', 'right']].set_visible(False)
            self.ax[0].tick_params(axis='both', labelsize=6)
            self.ax[1].spines[['top', 'bottom', 'left', 'right']].set_visible(False)
            self.ax[1].tick_params(axis='both', left=False, top=False, right=False, bottom=False,
                                   labelleft=False, labeltop=False, labelright=False, labelbottom=False)
            # Initialize plots
            self.__chs = []
            self.reset_fig()
            # Connect to Qt backend
            super(ClstFeatViewer._SpkFeat, self).__init__(self.fig)

        def plot_correlogram(self, px, py=None, tx="Trigger", ty="Triggered"):
            """Render a spike-train correlogram (or autocorrelogram when ``py`` is :data:`None`).

            Args:
                px (np.ndarray | None): Trigger spike train; pass :data:`None` to display a placeholder
                py (np.ndarray | None): Triggered spike train; pass :data:`None` for an autocorrelogram of
                    ``px`` (default: ``None``)
                tx (str): Trigger spike train label (default: ``"Trigger"``)
                ty (str): Triggered spike train label (default: ``"Triggered"``)
            """
            # Remove previous artist
            self.ax[0].clear()
            # Plot text when nothing selected
            if px is None:
                if py is None:
                    self.ax[0].spines[['bottom', 'left']].set_visible(False)
                    self.ax[0].tick_params(axis='both', left=False, top=False, right=False, bottom=False,
                                           labelleft=False, labeltop=False, labelright=False, labelbottom=False)
                    self.ax[0].set_xbound(0, 1)
                    self.ax[0].set_ybound(0, 1)
                    self.ax[0].text(0.5, 0.5, "No Spike Selected", size=9, ha='center', va='center')
                    # Force figure update
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                    return
                else:
                    px = py
                    py = None
            # Set annotation visible
            self.ax[0].spines[['bottom', 'left']].set_visible(True)
            self.ax[0].tick_params(axis='both', left=True, top=False, right=False, bottom=True,
                                   labelleft=True, labeltop=False, labelright=False, labelbottom=True)
            self.ax[0].set_xlabel("Time (ms)", fontsize=8, fontweight='bold')
            self.ax[0].set_ylabel("Counts", fontsize=8, fontweight='bold')
            # Compute correlogram
            count = [0]
            edge = []
            t = 0.05
            s = 0.001
            while (np.sum(count) == 0) and (t <= 5):
                count, edge = spk_correlogram(px, py, t=t, s=s)
                t *= 10
                s *= 10
            edge *= 1000  # Convert to ms
            # Plot correlogram
            title = "Autocorrelogram [%s]" % tx if py is None else "Correlogram [%s -> %s]" % (tx, ty)
            self.ax[0].stairs(count, edge, fill=True)
            self.ax[0].set_title(title, fontsize=9, fontweight='bold')
            self.ax[0].margins(x=0.01, y=0.05)
            # Force figure update
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        def plot_spksamp(self, pos, wfm, chs, name=None):
            """Render per-channel spike samples in a tiled layout below the correlogram.

            Args:
                pos (np.ndarray | None): {1D-int | 2D-int} Spike position indices; pass :data:`None` to
                    display a placeholder
                wfm (str | None): Waveform group name to draw samples from
                chs (list[int] | None): Channel indices to sample
                name (str | None): Spike cell label used in the axis title (default: ``None``)
            """
            # Remove previous artist
            self.ax[1].clear()
            # Plot text when nothing selected
            if pos is None:
                self.ax[1].set_xbound(0, 1)
                self.ax[1].set_ybound(0, 1)
                self.ax[1].text(0.5, 0.5, "No Spike Selected", size=9, ha='center', va='center')
                # Force figure update
                self.__chs = []
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                return
            # Get spike samples
            if pos.ndim == 1:
                if len(chs) == 1:
                    ch = chs[0]
                    sel = np.unique(np.rint(np.linspace(0, len(pos) - 1, 8, endpoint=True)).astype(int))
                    idx = np.repeat(pos[sel], self._cfv.num[wfm]) + np.tile(self._cfv.blk[wfm], len(sel))
                    idx = np.clip(idx, a_min=0, a_max=len(self._cfv.spk[wfm][ch]) - 1).reshape(
                        self._cfv.num[wfm], -1, order='F')
                    smp = self._cfv.spk[wfm][ch][idx]
                    txt = ["%.4f s" % t for t in self._cfv.t[pos[sel]]]
                else:
                    smp = np.zeros((self._cfv.num[wfm], len(chs)), dtype=np.float32)
                    idx = np.repeat(pos, self._cfv.num[wfm]) + np.tile(self._cfv.blk[wfm], len(pos))
                    idx = np.clip(idx, a_min=0, a_max=len(self._cfv.spk[wfm][chs[0]]) - 1).reshape(
                        self._cfv.num[wfm], -1, order='F')
                    for i, ch in enumerate(chs):
                        smp[:, i] = np.mean(self._cfv.spk[wfm][ch][idx], axis=1)
                    txt = ["CH-%04d" % t for t in chs]
            else:
                if pos.ndim != len(chs):
                    self.ax[1].set_xbound(0, 1)
                    self.ax[1].set_ybound(0, 1)
                    self.ax[1].text(0.5, 0.5, "Unmatched Dimension!", size=9, ha='center', va='center', color='r')
                    # Force figure update
                    self.__chs = []
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                    return
                else:
                    smp = np.zeros((self._cfv.num[wfm], len(chs)), dtype=np.float32)
                    for i, (ps, ch) in enumerate(zip(pos, chs)):
                        idx = np.repeat(ps, self._cfv.num[wfm]) + np.tile(self._cfv.blk[wfm], len(ps))
                        idx = np.clip(idx, a_min=0, a_max=len(self._cfv.spk[wfm][ch]) - 1).reshape(
                            self._cfv.num[wfm], -1, order='F')
                        smp[:, i] = np.mean(self._cfv.spk[wfm][ch][idx], axis=1)
                    txt = ["CH-%04d" % t for t in chs]
            self.__chs = chs
            # Compute plot grid
            rng = (np.max(smp) - np.min(smp)) * 1.05
            bsl = np.min(smp) * 1.1
            sx, sn = smp.shape
            if sn < 5:
                row = list(reversed(range(sn)))
                col = [0] * sn
            else:
                dv, md = divmod(sn, 2)
                row = list(reversed(range(sn - dv))) + list(reversed(range(md, sn - dv)))
                col = [0] * (sn - dv) + [1] * dv
            # Adjust sample
            xx = np.zeros_like(smp)
            yy = np.zeros_like(smp)
            tt = []
            for i, (r, c) in enumerate(zip(row, col)):
                xx[:, i] = np.arange(sx) + c * sx * 1.1
                yy[:, i] = smp[:, i] + r * rng
                tt.append(((xx[0, i] + xx[-1, i]) / 2, bsl + r * rng))
            # Plot
            self.ax[1].plot(xx, yy)
            for t, v in zip(txt, tt):
                self.ax[1].text(v[0], v[1], t, size=6, ha='center', va='center')
            self.ax[1].set_title("Sample [%s]" % name, fontsize=9, fontweight='bold')
            self.ax[0].margins(x=0, y=0)
            # Force figure update
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        def reset_fig(self):
            """Reset both axes to the empty/placeholder state."""
            self.plot_correlogram(None, None)
            self.plot_spksamp(None, None, None)

        def chk_channel(self, ch):
            """Reset the figure when ``ch`` is not in the currently plotted channel set.

            Args:
                ch (int): Active channel index to verify against the cached selection
            """
            if ch not in self.__chs:
                self.reset_fig()

    # Main class functions ------------------------------------------------------------------------------------------- #
    def reload_data(self, raw, spk, t, asp, psp, clst, min_cnt=50):
        """Replace the underlying recording data and redraw every embedded figure.

        Args:
            raw (np.ndarray): {2D-float32} Raw signal data
            spk (dict[str, np.ndarray]): {2D-float32} Spike signal data
            t (np.ndarray): {1D-float32} Time vector
            asp (dict[str, int]): Anterior sample count per spike type
            psp (dict[str, int]): Posterior sample count per spike type
            clst (dict[str, list[list[np.ndarray]]]): {1D-int64} Cluster indices per spike type
            min_cnt (int): Minimum elements required for a cluster to be plotted (default: ``50``)
        """
        # Get inputs
        self.raw = raw
        self.spk = spk
        self.t = t
        self.clst = clst
        # Set sampling features
        self.fs = (len(t) - 1) / t[-1].item()
        self.num = {w: asp.get(w, 5) + psp.get(w, 5) + 1 for w in spk}
        self.blk = {w: np.arange(-asp.get(w, 5), psp.get(w, 5) + 1, step=1, dtype=int) for w in spk}
        self.min_cnt = min_cnt
        # Channel control
        self.max_ch = raw.shape[0] - 1
        self.chn = 0
        # Replot figures
        self.chn_feat.replot_fig()
        self.grp_feat.replot_fig()
        self.spk_feat.reset_fig()

    def close(self):
        """Close every embedded Matplotlib figure to release their resources."""
        plt.close(self.chn_feat.fig)
        plt.close(self.grp_feat.fig)
        plt.close(self.spk_feat.fig)

    def set_channel(self, ch):
        """Set the active channel index for all embedded plots and refresh them.

        Args:
            ch (int): Channel index to activate; clamped to ``[0, max_ch]``
        """
        if ch != self.chn:
            # Validate input
            self.chn = 0 if ch < 0 else ch
            self.chn = self.max_ch if ch > self.max_ch else ch
            # Update figure
            self.chn_feat.replot_fig()
            self.grp_feat.replot_fig()
            self.spk_feat.chk_channel(ch)

    def set_act_clst(self, idx):
        """Highlight the listed clusters across the channel and group canvases.

        Args:
            idx (list[int] | None): Cluster indices to highlight; pass :data:`None` to fall back to the
                ``min_cnt`` size threshold
        """
        self.chn_feat.set_act_clst(idx)
        self.grp_feat.set_act_clst(idx)

    def update_cluster(self, clst):
        """Replace the cluster indices and redraw the embedded figures (used after a merge).

        Args:
            clst (dict[str, list[list[np.ndarray]]]): {1D-int64} Updated per-channel cluster indices
        """
        self.clst = clst
        # Replot figures
        self.chn_feat.replot_fig()
        self.grp_feat.replot_fig()
        self.spk_feat.reset_fig()


class WfmPosMarker(BlitManager):
    """Blit manager that maintains assistive cursor and waveform/position marker artists across axes.

    Extends :class:`BlitManager` with a cursor line, waveform-amplitude marker, and spike-position marker
    that follow the user's interaction with the plot (e.g. for the manual labelling workflow).
    """

    def __init__(self, canvas, axes, t, keys, wfm=None, pos=None):
        """Build the cursor and marker artists and attach them to the supplied axes.

        Args:
            canvas (backend_agg.FigureCanvasAgg): Canvas whose background is captured between draws
            axes (list[plt.Axes]): Axes that share the cursor/marker overlay
            t (np.ndarray): {1D-float} Time vector of the plot
            keys (dict[str, dict[str, list[str]]]): Per-channel waveform/position key groups managed by this marker
            wfm (np.ndarray | None): {1D-float} Waveform data displayed at the cursor (default: ``None``)
            pos (tuple[np.ndarray, int] | None): One-hot spike position data and the current channel
                index (default: ``None``)
        """
        # Get index search constants
        self.t = t
        self.lim = len(t) - 1
        self.__t_ini = t[0].item()
        self.__t_fac = 0 if t[-1] == t[0] else self.lim / (t[-1].item() - t[0].item())
        self.idx = None  # Current plot index
        # Set data arrays
        self._wfm = wfm
        self._pos = None if pos is None else pos[0]
        self._py = 0 if pos is None else pos[1]
        # Set position correction variables
        self.cor_wfm = None  # Active waveform key for manual correction
        self.cor_chn = '0' # Active channel index for manual correction
        self.cor_pos = None  # Active spike position key for manual correction
        self.cor_dot = None  # Active spike position on select
        self.__pos_on = False
        # Retrieve cursor lines for all axes
        c_cl = 'azure' if cs_dark() else 'darkslategray'
        self._csr_ln = []
        for ax in axes:
            self._csr_ln.append(ax.axvline(x=self.__t_ini, linewidth=0.5, color=c_cl))
        # Retrieve data markers
        self.__wfm_mkr = axes[0].axhline(y=0, linewidth=0.5, color=c_cl)
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
            for c in keys[k]:
                self.__cor_idx[k][c] = {}
                self.__cor_mkr[k][c] = {}
                for p in keys[k][c]:
                    # Set plots
                    add_mrk, = axes[1].plot([None], [None], marker='P', ms=8, color='crimson', ls='none')
                    self._ano_mk.append(add_mrk)
                    rmv_mrk, = axes[1].plot([None], [None], marker='X', ms=9, color='crimson', ls='none')
                    self._ano_mk.append(rmv_mrk)
                    # Set control variables
                    self.__cor_idx[k][c][p] = {'+': set(), '-': set()}  # Use set to keep uniqueness
                    self.__cor_mkr[k][c][p] = {'+': add_mrk, '-': rmv_mrk}

        # Initialize parent class
        super().__init__(canvas, self._csr_ln + self._ano_mk)
        self.__ax = axes
        # Set marker visibility
        self.__wfm_mkr.set_visible(wfm is not None)
        self.__pos_mkr.set_visible(False)
        self.__pos_bkg.set_visible(False)
        # Connect signaling when mouse moved
        self.sid = self.cvs.mpl_connect('motion_notify_event', self.__on_motion)
        self.cid = self.cvs.mpl_connect('button_press_event', self.__on_click)

    def find_nearest(self, value):
        """Return the index of the time vector closest to ``value``.

        Args:
            value (int | float): Time value (in seconds) to locate

        Returns:
            int: Sample index nearest to ``value``
        """
        return round((value - self.__t_ini) * self.__t_fac)

    def find_extremum(self, index):
        """Return the index of the local extremum near ``index`` with the same sign as the waveform there.

        Args:
            index (int): Seed index from which the search starts

        Returns:
            int | None: Index of the nearest extremum within ``±5`` samples; :data:`None` when no
                waveform has been attached
        """
        if self._wfm is None:
            return None
        else:
            if self._wfm[index] > 0:
                return np.argmax(self._wfm[index - 5:index + 6]).item() + index - 5
            else:
                return np.argmin(self._wfm[index - 5:index + 6]).item() + index - 5

    def set_chn(self, chn):
        """Make the marker artists of one channel visible and hide the rest.

        Args:
            chn (int | str): Channel index of the active correction target
        """
        self.cor_chn = str(chn)
        # Set visibility of correction markers
        for k in self.__cor_mkr:
            for c in self.__cor_mkr[k]:
                flag = c == self.cor_chn
                for p in self.__cor_mkr[k][c]:
                    self.__cor_mkr[k][c][p]['+'].set_visible(flag)
                    self.__cor_mkr[k][c][p]['-'].set_visible(flag)
        # Update plot
        self.update()

    def set_wfm(self, wfm):
        """Attach the active waveform trace used by :meth:`find_extremum`.

        Args:
            wfm (np.ndarray | None): {1D-float} Waveform data; pass :data:`None` to detach
        """
        self._wfm = wfm
        self.__wfm_mkr.set_visible(wfm is not None)
        self.update()

    def set_pos(self, pos, y, wfm_key, pos_key):
        """Attach the active spike-position vector and enable position-correction marking.

        Args:
            pos (np.ndarray | None): {1D-int(0|1)} One-hot spike-position vector; pass :data:`None` to
                disable position correction
            y (int): Virtual y-axis index where the position marker is drawn
            wfm_key (str | None): Active waveform key (None when ``pos`` is :data:`None`)
            pos_key (str | None): Active position key (None when ``pos`` is :data:`None`)
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

    def add_pos(self, wfm_key, chn_key, pos_key):
        """Register a new ``(waveform, channel, position)`` triple and attach its correction artists.

        Args:
            wfm_key (str): Waveform key (group name)
            chn_key (str): Channel key
            pos_key (str): Position key (spike name)
        """
        # Add insertion artist
        add_mrk, = self.__ax[1].plot([None], [None], marker='P', ms=8, color='crimson', ls='none')
        self._ano_mk.append(add_mrk)
        self.add_artist(add_mrk)
        # Add removal artist
        rmv_mrk, = self.__ax[1].plot([None], [None], marker='X', ms=9, color='crimson', ls='none')
        self._ano_mk.append(rmv_mrk)
        self.add_artist(rmv_mrk)
        # Set control variables
        self.__cor_idx[wfm_key][chn_key][pos_key] = {'+': set(), '-': set()}  # Use set to keep uniqueness
        self.__cor_mkr[wfm_key][chn_key][pos_key] = {'+': add_mrk, '-': rmv_mrk}

    def del_pos(self, wfm_key, chn_key, pos_key):
        """Deregister a ``(waveform, channel, position)`` triple and remove its correction artists.

        Args:
            wfm_key (str): Waveform key (group name)
            chn_key (str): Channel key
            pos_key (str): Position key (spike name)
        """
        # Remove from control variables
        self.__cor_idx[wfm_key][chn_key].pop(pos_key)
        mkr = self.__cor_mkr[wfm_key][chn_key].pop(pos_key)
        # Remove insertion artist
        self._ano_mk.remove(mkr['+'])
        self.remove_artist(mkr['+'])
        mkr['+'].remove()
        # Remove removal artist
        self._ano_mk.remove(mkr['-'])
        self.remove_artist(mkr['-'])
        mkr['-'].remove()

    def chk_cor(self):
        """Return :data:`True` when any manual addition or removal has been recorded.

        Returns:
            bool: :data:`True` when at least one position has been added or removed manually
        """
        flag = False
        for k in self.__cor_idx:
            if flag:
                break
            for c in self.__cor_idx[k]:
                if flag:
                    break
                for p in self.__cor_idx[k][c]:
                    if self.__cor_idx[k][c][p]['+']:
                        flag = True
                        break
                    if self.__cor_idx[k][c][p]['-']:
                        flag = True
                        break
        return flag

    def get_cor(self):
        """Snapshot every manual correction as nested per-position one-hot trinary vectors.

        Returns:
            dict[str, dict[str, dict[str, np.ndarray]]]: Nested ``{wfm: {chn: {pos: vector}}}`` with each
                vector storing ``+1`` for added positions, ``-1`` for removed positions, and ``0`` elsewhere
        """
        cor = {}  # INIT VAR
        for k in self.__cor_idx:
            cor[k] = {}
            for c in self.__cor_idx[k]:
                cor[k][c] = {}
                for p in self.__cor_idx[k][c]:
                    man = np.zeros_like(self.t, dtype=np.int8)
                    if self.__cor_idx[k][c][p]['+']:
                        man[list(self.__cor_idx[k][c][p]['+'])] = 1
                    if self.__cor_idx[k][c][p]['-']:
                        man[list(self.__cor_idx[k][c][p]['-'])] = -1
                    cor[k][c][p] = man.copy()
        return cor

    def reset_cor(self):
        """Discard every manual correction and clear the matching marker artists."""
        for k in self.__cor_idx:
            for c in self.__cor_idx[k]:
                for p in self.__cor_idx[k][c]:
                    self.__cor_idx[k][c][p] = {'+': set(), '-': set()}  # Reset to original
                    self.__cor_mkr[k][c][p]['+'].set_data([None], [None])
                    self.__cor_mkr[k][c][p]['-'].set_data([None], [None])
        # Update plot
        self.update()

    def __plt_cor_mrk(self):
        """Refresh the ``+``/``-`` correction markers for the active waveform/channel/position."""
        # Plot added positions
        self.__cor_mkr[self.cor_wfm][self.cor_chn][self.cor_pos]['+'].set_data(
            self.t[list(self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['+'])],
            [self._py] * len(self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['+'])
        )
        # Plot removed positions
        self.__cor_mkr[self.cor_wfm][self.cor_chn][self.cor_pos]['-'].set_data(
            self.t[list(self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['-'])],
            [self._py] * len(self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['-'])
        )
        # Update plot
        self.update()

    def __on_motion(self, event):
        """Track mouse motion: update cursor, waveform marker, and snap-to-spike marker accordingly."""
        if event.xdata is not None:
            # Set cursor lines
            for a in self._csr_ln:
                a.set_xdata([event.xdata, event.xdata])
            # Set plot markers
            self.idx = self.find_nearest(event.xdata)
            self.idx = self.lim if self.idx > self.lim else self.idx  # Avoid IndexError
            if self._wfm is not None:
                self.__wfm_mkr.set_ydata([self._wfm[self.idx], self._wfm[self.idx]])
            if self._pos is not None:
                # Check if inference position nearby
                p_inf = np.nonzero(self._pos[self.idx - 5:self.idx + 6])[0]
                if p_inf.size == 0:
                    # Check if manual corrected position nearby
                    for i in self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['+']:
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
                else:
                    self.cor_dot = p_inf[0] + self.idx - 5
                    self.idx = self.cor_dot
                    self.__pos_mkr.set_data([self.t[self.cor_dot]], [self._py])
                    self.__pos_mkr.set_visible(True)
            self.update()

    def __on_click(self, event):
        """Record a manual addition (left click) or removal (right click) of a spike position."""
        if event.button is MouseButton.LEFT:
            if self.__pos_on:
                if self.idx in self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['-']:
                    self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['-'].remove(self.idx)
                else:
                    if self.cor_dot is None:
                        exm_idx = self.find_extremum(self.idx)  # Find extremum around the index for easier usage
                        self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['+'].add(exm_idx)
                self.__plt_cor_mrk()
        elif event.button is MouseButton.RIGHT:
            if self.__pos_on:
                if self.idx in self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['+']:
                    self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['+'].remove(self.idx)
                else:
                    if self.cor_dot is not None:
                        self.__cor_idx[self.cor_wfm][self.cor_chn][self.cor_pos]['-'].add(self.idx)
                self.__plt_cor_mrk()


class ResPltLoader(FigureCanvasQTAgg):
    """Qt canvas that loads a PARUS analysis result file and renders it for manual inspection.

    Reads the recording, the model's spike-signal predictions, and the detected spike positions from a
    PARUS analysis HDF5 file, then composes them on a multi-axis figure ready for interactive review.

    Note:
        The HDF5 file is opened in read mode and stays open for the lifetime of the canvas.
    """

    def __init__(self, file, cplt=None):
        """Open the HDF5 file, build the figure layout, and render the initial view.

        Args:
            file (str): Path to the PARUS analysis result HDF5 file
            cplt (str | list[str] | None): Colour HEX codes used for plotting (default: ``None``)
        """
        init_len = 0.1  # 100ms initial view time length
        # Load result data
        self.fp = h5.File(file, 'r')
        self.nch, sig_len = self.fp['raw'].shape[:2]
        self.fs = self.fp['frq'][()]
        self.t = np.arange(sig_len) / self.fs
        # Initialize data attributes
        self._raw = None  # Raw waveform data
        self._spk = {}  # Spike waveform data
        self.wfm = {}  # Waveforms in the data
        self.pos = {}  # Detected spike positions
        self._pos_add = {}  # Added spike positions
        self._pos_del = {}  # Removed spike positions
        # Initialize plot control attributes
        self.__plt_init = False  # Plot initialize status
        self.__ch = 0  # Current channel index
        self._ixi = 0  # X-axis data initial index
        self._ixf = round(init_len * self.fs)  # X-axis data final index
        self._y_min = -1  # Y-axis lower bound
        self._y_max = 1  # Y-axis upper bound
        self.__leg = None  # Plot legend
        self.__act_leg = None  # Active trace legend

        # Get plot colour dictionary
        cplt = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf'
        ] if cplt is None else cplt
        cmap = LoopedColormap(cplt, name='ParusResCmap')
        self._cdct = {k: cmap(i) for i, k in enumerate(self.fp['spk'])} if 'spk' in self.fp else {}
        # Initialize figure
        self.fig, self.ax = plt.subplots(2, 1, sharex='all', sharey='none', height_ratios=(5, 1))
        self.fig.set_layout_engine(layout='tight', h_pad=-0.6)
        self.fig.align_ylabels()
        self.ax[0].spines[['top', 'right', 'bottom']].set_visible(False)
        self.ax[1].spines[['top', 'right']].set_visible(False)
        self.ax[1].spines['left'].set(linestyle=(8, (8, 8)))

        # Plot data
        self.plt_ch(self.__ch)
        # Set X axis features
        self.ax[0].tick_params(axis='x', which='both', top=False, bottom=False, labelbottom=False)
        self.ax[1].set_xlabel("Time (s)", fontsize=14, fontweight='bold')
        self.ax[1].tick_params(axis='x', which='major', labelsize=12)
        # Set Y axis features
        self.ax[0].set_ylabel("Amplitude", fontsize=16, fontweight='bold')
        self.ax[0].tick_params(axis='y', which='major', labelsize=10)
        self.ax[1].tick_params(axis='y', which='major', direction='inout', length=12, labelsize=14)
        # Set legends
        self.__leg = Legend(self.ax[0], list(self.wfm.values()), list(self.wfm.keys()), loc='upper right', fontsize=16)
        self.ax[0].add_artist(self.__leg)
        # Set 100ms initial view
        self.set_time(0, init_len)

        # Connect to Qt backend
        super(ResPltLoader, self).__init__(self.fig)
        # Connect to BlitManager
        key_wpm = {
            k: {c: list(self.fp['pos'][k][c].keys()) for c in self.fp['pos'][k]} for k in self.fp['pos']
        } if 'pos' in self.fp else {}
        self._wpm = WfmPosMarker(self.fig.canvas, self.ax, self.t, key_wpm)
        self._wpm.set_chn(self.__ch)

    def close(self):
        """Close the underlying HDF5 file and the embedded Matplotlib figure."""
        self.fp.close()
        plt.close(self.fig)

    def set_time(self, start, stop):
        """Update the x-axis range and reload the slice of every waveform that falls inside it.

        Args:
            start (int | float): Start time in seconds
            stop (int | float): Stop time in seconds
        """
        # Set axis bound
        self.ax[1].set_xlim(start, stop)
        self._ixi = round(start * self.fs)
        self._ixf = round(stop * self.fs)
        # Set data
        self.wfm['RAW'].set_data(self.t[self._ixi:self._ixf], self._raw[self._ixi:self._ixf])
        for k in self._spk:
            self.wfm[k].set_data(self.t[self._ixi:self._ixf], self._spk[k][self._ixi:self._ixf])
        # Set tick locations
        self.ax[1].set_xticks(np.linspace(start, stop, 5, endpoint=True))
        self.ax[1].xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def set_amp(self, low, high, reset=False):
        """Update the signal-amplitude y-axis range and refresh the major/minor tick layout.

        Args:
            low (int | float): Minimum amplitude
            high (int | float): Maximum amplitude
            reset (bool): When :data:`True`, restore the channel's default amplitude range and ignore
                ``low``/``high`` (default: ``False``)
        """
        # Set axis bound
        if reset:
            low = self._y_min
            high = self._y_max
        self.ax[0].set_ylim(low, high)
        # Set tick locations
        rn = 1 if (high - low) < 60 else 10
        span = [round(min(abs(low) / (t + 1e-12), abs(high) / (6 + 1e-12 - t))) // rn * rn for t in range(7)]
        t = np.argmax(span)
        step = [(k - t) * span[t] for k in range(7)]
        self.ax[0].set_yticks(step)
        self.ax[0].yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def plt_ch(self, ch):
        """Switch the canvas to a different recording channel and reload its waveforms and positions.

        Args:
            ch (int): Channel index to activate; clamped to ``[0, nch - 1]``
        """
        # Check channel input
        ch = 0 if ch < 0 else ch if ch < self.nch else self.nch - 1
        self.__ch = ch
        # Get amplitude limits based on raw data
        self._raw = self.fp['raw'][self.__ch]
        self._spk = {}  # Reset data store
        self._y_min = np.round(np.min(self._raw) - 5, decimals=-1).item()  # Round down to tens
        self._y_max = np.round(np.max(self._raw) + 5, decimals=-1).item()  # Round up to tens

        if self.__plt_init:
            # Disable previous active annotations
            self.set_act_wfm(None)
            self.set_act_pos(None, None)
            # Update waveforms
            self.wfm['RAW'].set_data(self.t[self._ixi:self._ixf], self._raw[self._ixi:self._ixf])
            if 'spk' in self.fp:
                for k in self.fp['spk']:
                    spk = self.fp['spk'][k][self.__ch]
                    self._spk[k] = spk
                    self.wfm[k].set_data(self.t[self._ixi:self._ixf], spk[self._ixi:self._ixf])
            # Always remove previous positions
            for k in self.pos:
                for p in self.pos[k]:
                    self.pos[k][p]['plt'].remove()
            self.pos = {}  # RESET VAR
        else:
            # Plot raw data
            self.wfm['RAW'], = self.ax[0].plot(self.t[self._ixi:self._ixf], self._raw[self._ixi:self._ixf],
                                               color='w' if cs_dark() else 'k', alpha=0.8, label="RAW")
            # Plot spike waveforms
            if 'spk' in self.fp:
                for k in self.fp['spk']:
                    spk = self.fp['spk'][k][self.__ch]
                    self._spk[k] = spk
                    self.wfm[k], = self.ax[0].plot(self.t[self._ixi:self._ixf], spk[self._ixi:self._ixf],
                                                   color=self._cdct[k], label=k)

        # Plot position
        cnt = 0  # Position data counter
        if 'pos' in self.fp:
            for k in self.fp['pos']:
                self.pos[k] = {}
                for p in self.fp['pos'][k][str(self.__ch)]:
                    pos = np.nonzero(self.fp['pos'][k][str(self.__ch)][p][()])[0]
                    sct = self.ax[1].scatter(self.t[pos], [cnt] * len(pos), color=self._cdct[k])
                    self.pos[k][p] = {'plt': sct, 'idx': cnt}
                    cnt += 1  # Counter
        # Plot added position
        for name in self._pos_add:
            k, c, p = name
            if c == str(self.__ch):
                # Plot an empty row
                sct = self.ax[1].scatter([], [], color=self._cdct[k])
                self.pos[k][p] = {'plt': sct, 'idx': cnt}
                cnt += 1  # Counter
        # Plot removed position markers
        for name in self._pos_del:
            k, c, p = name
            self._pos_del[name].set_visible(c == str(self.__ch))

        # Update signal Y axis limits
        self.set_amp(self._y_min, self._y_max)
        # Update position Y axis
        plbl, pclr = ("No Spike", 'r') if cnt == 0 else ("Spike", 'w' if cs_dark() else 'k')
        self.ax[1].set_ylabel(plbl, fontsize=14, fontweight='bold', color=pclr)
        self.ax[1].set_ylim(-1, cnt)
        self.ax[1].set_yticks(sum([[self.pos[k][p]['idx'] for p in self.pos[k]] for k in self.pos], []))
        self.ax[1].set_yticklabels(sum([list(self.pos[k].keys()) for k in self.pos], []))

        # Force figure update
        if self.__plt_init:
            self._wpm.set_chn(-1)  # Hide all markers
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self._wpm.set_chn(self.__ch)  # Inform marker manager
        else:
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.__plt_init = True

    def sel_wfm(self, sel, lnk_pos=True):
        """Toggle waveform visibility and (optionally) the matching spike-position rows.

        Args:
            sel (list[str]): Waveform keys to keep visible
            lnk_pos (bool): When :data:`True`, also hide the position rows of the hidden waveforms
                (default: ``True``)

        Returns:
            list[str]: ``"<wfm> - <pos>"`` keys whose waveform is visible after the call
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

    def set_act_wfm(self, wfm_key):
        """Mark a waveform as the active inspection target and refresh the active-trace legend.

        Args:
            wfm_key (str | None): Waveform key to activate; pass :data:`None` to deactivate
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
                self._wpm.set_wfm(self.fp['raw'][self.__ch])
            else:
                self._wpm.set_wfm(self.fp['spk'][wfm_key][self.__ch])
            # Add new legend
            self.__act_leg = Legend(self.ax[0], [self.wfm[wfm_key]], [wfm_key], title="Active Trace", loc='upper left',
                                    fontsize=8, title_fontsize=8, facecolor='green')
            self.ax[0].add_artist(self.__act_leg)
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def set_act_pos(self, wfm_key, pos_key):
        """Mark a spike-position row as the active correction target.

        Args:
            wfm_key (str | None): Waveform key; ``'RAW'`` or :data:`None` deactivates correction
            pos_key (str | None): Position key; :data:`None` deactivates correction
        """
        if (wfm_key is None) or (wfm_key == 'RAW') or (pos_key is None):
            self._wpm.set_pos(None, -1, None, None)
            if wfm_key == 'RAW':
                self.set_act_wfm(wfm_key)
        else:
            if (wfm_key, str(self.__ch), pos_key) in self._pos_add:
                pos_dat = self._pos_add[(wfm_key, str(self.__ch), pos_key)]
            else:
                pos_dat = self.fp['pos'][wfm_key][str(self.__ch)][pos_key][()]
            self._wpm.set_pos(pos_dat, self.pos[wfm_key][pos_key]['idx'], wfm_key, pos_key)
            # Force the active waveform to be associated with spike position records
            if self.wfm[wfm_key].get_visible():
                self.set_act_wfm(wfm_key)
            else:
                self.set_act_wfm('RAW')

    def add_pos(self, wfm_key, pos_key):
        """Add a new spike-position row for the user to fill in via manual correction.

        Args:
            wfm_key (str): Waveform key under which the position belongs
            pos_key (str): Position (spike cell) key for the new row
        """
        # Record added cell
        name = (wfm_key, str(self.__ch), pos_key)
        if name not in self._pos_add:
            self._pos_add[name] = np.zeros_like(self._raw, dtype=np.int8)
            # Update annotation list
            ano = sum([list(self.pos[k].keys()) for k in self.pos], []) + [pos_key]
            # Plot an empty row
            sct = self.ax[1].scatter([], [], color=self._cdct[wfm_key])
            self.pos[wfm_key][pos_key] = {'plt': sct, 'idx': len(ano) - 1}
            # Update position Y axis
            self.ax[1].set_ylabel("Spike", fontsize=14, fontweight='bold', color='w' if cs_dark() else 'k')
            self.ax[1].set_ylim(-1, len(ano))
            self.ax[1].set_yticks(np.arange(len(ano)))
            self.ax[1].set_yticklabels(ano)
            # Inform BlitManager
            self._wpm.add_pos(wfm_key, str(self.__ch), pos_key)
            # Force figure update
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def del_rcv_pos(self, wfm_key, pos_key):
        """Toggle the strikethrough marker that flags a cell for removal (clicking again restores it).

        Args:
            wfm_key (str): Waveform key under which the position belongs
            pos_key (str): Position (spike cell) key to mark or unmark
        """
        name = (wfm_key, str(self.__ch), pos_key)
        if name in self._pos_del:
            mk = self._pos_del.pop(name)
            mk.remove()
        else:
            mk = self.ax[1].axhline(y=self.pos[wfm_key][pos_key]['idx'], linewidth=10, color='r', alpha=0.5, zorder=255)
            self._pos_del[name] = mk
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def check_correction(self):
        """Return :data:`True` when any pending correction (deletion or position edit) exists."""
        flag = (len(self._pos_del) > 0) or self._wpm.chk_cor()
        return flag

    def make_correction(self):
        """Apply every pending correction to the underlying HDF5 file and refresh the canvas."""
        cor = self._wpm.get_cor()
        p_bin = h5_load_dat(self.fp['pos'])
        for k in p_bin:
            for c in p_bin[k]:
                for p in p_bin[k][c]:
                    # Set new position data
                    p_bin[k][c][p] += cor[k][c][p]
                    # Update plot
                    if c == str(self.__ch):
                        p_idx = np.nonzero(p_bin[k][c][p])[0]
                        self.pos[k][p]['plt'].set_offsets(np.c_[self.t[p_idx], [self.pos[k][p]['idx']] * len(p_idx)])
        # Set added cells
        for name in self._pos_add:
            k, c, p = name
            cor_data = self._pos_add[name] + cor[k][c][p]
            p_idx = np.nonzero(cor_data)[0]
            # Record valid addition
            if len(p_idx) > 0:
                p_bin[k][c][p] = cor_data.copy()
                if c == str(self.__ch):
                    self.pos[k][p]['plt'].set_offsets(np.c_[self.t[p_idx], [self.pos[k][p]['idx']] * len(p_idx)])
        self._pos_add = {}  # Reset
        # Set removed cells
        for name in self._pos_del:
            k, c, p = name
            p_bin[k][c].pop(p)  # Remove data
            self._pos_del[name].remove()  # Remove marker
            self._wpm.del_pos(k, c, p)  # Inform BlitManager
        self._pos_del = {}  # Reset
        # Reset all corrections
        self._wpm.reset_cor()
        # Force figure update
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        return p_bin
