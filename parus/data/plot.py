# -*- coding: utf-8 -*-

"""Data plotting module

Helpers for plotting and data visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import FancyBboxPatch, PathPatch

__package__ = 'parus.data'
__name__ = 'parus.data.plot'

__all__ = ['swarm_cord', 'stat_plvl', 'spk_correlogram', 'plot_prb']
"""
Public function list:

- swarm_cord(data, bins, centre, width)                                  : Compute the coordinates for a swarm plot
- stat_plvl(ax, p, lt, rb, pos, brk, ast_lim, ver, lineprops, textprops) : Draw statistical-significance bars on an axis
- spk_correlogram(px, py, t, s)                                          : Compute a spike-train auto/cross correlogram
- plot_prb(prb, ax)                                                      : Draw a recording probe geometry on an axis
"""


def swarm_cord(data, bins=None, centre=0, width=1):
    """Compute the perpendicular coordinates for a swarm-plot layout of a 1D dataset.

    The values of ``data`` are first binned along the perpendicular axis, then within each bin the
    perpendicular positions are alternated around the centre to spread overlapping points out.

    Args:
        data (tuple | list | np.ndarray): Input 1D dataset
        bins (int | None): Number of equal-width bins along the data axis; pass :data:`None` to use
            ``ceil(size / 6)`` (default: ``None``)
        centre (int | float): Centre coordinate of the swarm (default: ``0``)
        width (int | float): Total width of the swarm (default: ``1``)

    Returns:
        np.ndarray: Per-point perpendicular coordinates aligned with ``data``
    """
    # Adapt inputs
    data = data.copy() if isinstance(data, np.ndarray) else np.asarray(data)
    size = data.size
    bins = np.ceil(size / 6).astype(int) if bins is None else round(bins)

    # Get upper bounds of bins
    lo, hi = np.min(data), np.max(data)
    dy = (hi - lo) / bins
    bs = np.linspace(lo + dy, hi - dy, bins - 1)

    # Divide indices into bins
    idx = np.arange(size)
    ibs = [[]] * bins
    ybs = [[]] * bins
    for i, b in enumerate(bs):
        # Assign current bin
        f = data <= b
        ibs[i], ybs[i] = idx[f], data[f]
        # Trim data
        f = ~f
        idx, data = idx[f], data[f]
    # Assign last bin and get maximum width
    ibs[-1], ybs[-1] = idx, data
    lim = max(len(_) for _ in ibs)

    # Assign X-axis indices
    cord = np.zeros(size)
    dx = width / 2 / (lim // 2)
    for i, y in zip(ibs, ybs):
        if len(i) > 1:
            j = len(i) % 2
            i = i[np.argsort(y)]
            a = i[j::2]
            b = i[j + 1::2]
            cord[a] = (0.5 + j / 3 + np.arange(len(b))) * dx
            cord[b] = (0.5 + j / 3 + np.arange(len(b))) * -dx
    return cord + centre


def stat_plvl(ax, p, lt, rb, pos, brk=0.5, ast_lim=3, vert=True, lineprops=None, textprops=None):
    """Draw statistical-significance bars and asterisk annotations on a Matplotlib axis.

    For each ``(lt, rb, pos)`` triple, a U-shaped bar is drawn with annotation text derived from the matching
    ``p`` value. Numeric ``p`` values produce ``'*' * ceil(log10(0.05 / p))`` (capped at ``ast_lim``) or
    ``'n.s.'`` when not significant; non-numeric values are stringified directly.

    Args:
        ax (plt.Axes): Matplotlib axes to draw on
        p (float | tuple[float] | list[float] | np.ndarray): Statistical p-value(s) for each bar
        lt (int | float | tuple | list | np.ndarray): Left-or-top coordinate(s) of each bar
        rb (int | float | tuple | list | np.ndarray): Right-or-bottom coordinate(s) of each bar
        pos (int | float | tuple | list | np.ndarray): Starting coordinate(s) of each bar (along the ``brk`` direction)
        brk (int | float | tuple | list | np.ndarray): Bar height(s) (default: ``0.5``)
        ast_lim (int | None): Maximum number of asterisks per bar; pass :data:`None` to remove the cap (default: ``3``)
        vert (bool): When :data:`True`, the bar grows along the y-axis; when :data:`False`, along the x-axis
            (default: ``True``)
        lineprops (dict | None): Extra keyword arguments for :meth:`matplotlib.axes.Axes.plot` (default: ``None``)
        textprops (dict | None): Extra keyword arguments for :meth:`matplotlib.axes.Axes.text`; alignment
            keys (``ha``, ``va``, ``rotation``) are overridden by the function (default: ``None``)

    Returns:
        tuple[list[plt.Line2D], list[plt.Text]]: Plotted bar artist(s) and annotation text artist(s)
    """

    def __get_txt(v):
        """Compute the annotation string from a single p-value.

        Args:
            v (float | Any): p-value or arbitrary annotation source

        Returns:
            str: Asterisk string for significant numeric ``v``, ``'n.s.'`` for non-significant numeric ``v``,
                or ``str(v)`` for non-numeric values
        """
        # Compute number of asterisks for numeric p-value
        if isinstance(v, (float, np.floating)):
            lvl = np.ceil(np.log10(0.05 / v)).astype(int) if v > 0 else 0
            if ast_lim is None:
                return '*' * lvl if lvl > 0 else 'n.s.'
            else:
                return '*' * min(ast_lim, lvl) if lvl > 0 else 'n.s.'
        # Try to convert to string for other types
        else:
            return str(v)

    # Adapt inputs
    lt = lt if isinstance(lt, np.ndarray) else np.asarray(lt if isinstance(lt, (tuple, list)) else [lt])
    rb = rb if isinstance(rb, np.ndarray) else np.asarray(rb if isinstance(rb, (tuple, list)) else [rb])
    pos = pos if isinstance(pos, np.ndarray) else np.asarray(pos if isinstance(pos, (tuple, list)) else [pos])
    brk = brk if isinstance(brk, np.ndarray) else np.asarray(brk if isinstance(brk, (tuple, list)) else [brk])
    # Compute lines coordinates
    cnl = pos + brk
    if vert:
        xs = np.vstack((lt, lt, rb, rb))
        ys = np.vstack((pos, cnl, cnl, pos))
    else:
        xs = np.vstack((pos, cnl, cnl, pos))
        ys = np.vstack((lt, lt, rb, rb))
    # Get features and plot line
    lineprops = {} if lineprops is None else lineprops
    if not (('c' in lineprops) or ('color' in lineprops)):
        lineprops['c'] = 'black'
    line = ax.plot(xs, ys, **lineprops)

    # Get annotation texts
    if isinstance(p, (tuple, list, np.ndarray)):
        txt = [__get_txt(_) for _ in p]
    else:
        txt = [__get_txt(p)]
    # Get text features
    if vert:
        ctr = (lt + rb) / 2
        bsl = cnl + brk / 10
        textprops = {} if textprops is None else textprops
        textprops.update({'ha': 'center', 'va': 'bottom'})  # Override
    else:
        ctr = cnl + brk / 10
        bsl = (lt + rb) / 2
        textprops = {} if textprops is None else textprops
        textprops.update({'ha': 'left', 'va': 'center', 'rotation': 'vertical'})  # Override
    # Draw texts
    text = []  # INIT VAR
    for c, b, t in zip(ctr, bsl, txt):
        tp = ax.text(c, b, t, **textprops)
        text.append(tp)
    return line, text


def spk_correlogram(px, py=None, t=0.05, s=0.001):
    """Compute the auto- or cross-correlogram of one or two spike trains.

    Builds the inter-spike interval matrix between ``py`` (or ``px`` for the autocorrelogram) and ``px``, drops the
    diagonal in the autocorrelogram case, then bins the differences into a histogram on ``[-t, t]`` with step ``s``.

    Args:
        px (list[int | float] | np.ndarray): First spike train (used as the trigger train)
        py (list[int | float] | np.ndarray | None): Second spike train; pass :data:`None` to compute the
            autocorrelogram of ``px`` (default: ``None``)
        t (int | float): One-sided time range in seconds; the actual window spans ``[-t, t]`` (default: ``0.05``)
        s (int | float): Bin step in seconds (default: ``0.001``)

    Returns:
        tuple[np.ndarray, np.ndarray]: Histogram counts and bin edges as returned by :func:`numpy.histogram`
    """
    # Autocorrelogram
    if py is None:
        isi = np.subtract.outer(px, px)
        # Trim ISI diagonal
        n = isi.shape[0]
        si, se = isi.strides
        isi = np.lib.stride_tricks.as_strided(isi.ravel()[1:], shape=(n - 1, n), strides=(si + se, se)).flatten()
    # Correlogram
    else:
        isi = np.subtract.outer(py, px)
    # Create histogram
    b = round(t * 2 / s) + 1
    count, edge = np.histogram(isi, bins=b, range=(-t, t), density=False)
    return count, edge


def plot_prb(prb, ax):
    """Draw a recording probe geometry on a Matplotlib axis.

    Renders the contact pads as rounded rectangles, the shanks as filled polygons, and adds annotations for
    shank labels, channel IDs, and inter-shank distances. The shank shape style is selected by
    ``prb['info']['sty']`` from ``{'left', 'right', 'edge'}`` (anything else falls back to a straight shank).

    Args:
        prb (dict): Probe geometry dictionary with the following entries

            - info (dict): At least ``sty``, ``typ`` and ``mfr`` keys for styling and annotations
            - site (list[dict]): One entry per recording site with ``id``, ``shk``, ``geo`` and ``pad`` keys

        ax (plt.Axes): Matplotlib axes to draw on

    Returns:
        plt.Axes: The same axis ``ax`` with the probe drawn (returned for chaining convenience)
    """
    # Plotting channel sites
    pos = {}  # INIT VAR
    csz = {'w': [], 'h': []}  # INIT VAR
    txt = {}  # INIT VAR
    for c in prb['site']:
        # Check shank information
        if c['shk'] not in pos:
            pos[c['shk']] = np.empty((0, 2), dtype=float)
            txt[c['shk']] = {'v': [], 'x': float('-inf')}
        # Get site position
        lft = c['geo'][0] - c['pad'][0] / 2
        btm = c['geo'][1] - c['pad'][1] / 2
        rgt = c['geo'][0] + c['pad'][0] / 2
        top = c['geo'][1] + c['pad'][1] / 2
        pos[c['shk']] = np.append(pos[c['shk']], [[lft, btm], [lft, top], [rgt, btm], [rgt, top]], axis=0)
        # Get site size
        csz['w'].append(c['pad'][0])
        csz['h'].append(c['pad'][1])
        # Get channel IDs
        txt[c['shk']]['v'].append([c['geo'][0], c['geo'][1], c['id'] + 1])
        txt[c['shk']]['x'] = c['geo'][0] if c['geo'][0] > txt[c['shk']]['x'] else txt[c['shk']]['x']
        # Plot site patch
        site = FancyBboxPatch((lft, btm), c['pad'][0], c['pad'][1], boxstyle='round, pad=1', ec='w', zorder=1)
        ax.add_patch(site)
    # Get site limits
    pad = {k: max(csz[k]) for k in csz}
    lim = {}  # INIT VAR
    exm = {}  # INIT VAR
    for s in pos:
        # Get shank anchors
        lim_l = np.min(pos[s][:, 0])
        lim_r = np.max(pos[s][:, 0])
        lim_b = np.min(pos[s][:, 1])
        lim_t = np.max(pos[s][:, 1])
        lim_m = np.mean(pos[s][:, 0])
        # Get shank bottom values of each side
        btm_l = np.min(pos[s][pos[s][:, 0] < lim_m, 1])
        btm_r = np.min(pos[s][pos[s][:, 0] > lim_m, 1])
        # Get required extrema points
        low_l = pos[s][pos[s][:, 1] == btm_l][np.argmin(pos[s][pos[s][:, 1] == btm_l, 0])]
        low_r = pos[s][pos[s][:, 1] == btm_r][np.argmax(pos[s][pos[s][:, 1] == btm_r, 0])]
        exm_l = pos[s][pos[s][:, 0] == lim_l][np.argmin(pos[s][pos[s][:, 0] == lim_l, 0])]
        exm_r = pos[s][pos[s][:, 0] == lim_r][np.argmax(pos[s][pos[s][:, 0] == lim_r, 0])]
        # Assign values
        lim[s] = {'l': lim_l, 'r': lim_r, 'b': lim_b, 't': lim_t, 'm': lim_m}
        exm[s] = {'ll': low_l, 'lr': low_r, 'xl': exm_l, 'xr': exm_r}

    # Plotting shanks
    tip = {}  # INIT VAR
    for s in pos:
        if prb['info']['sty'] == 'left':
            # Get left anchors
            lb = [lim[s]['l'] - pad['w'] / 2, lim[s]['b'] - pad['h'] / 2]
            lt = [lim[s]['l'] - pad['w'] / 2, lim[s]['t'] + pad['h']]
            # Compute right anchors
            diff_x = exm[s]['xr'][0] - exm[s]['lr'][0]
            if abs(diff_x) < 0.001:
                rb = [exm[s]['lr'][0] + pad['w'], exm[s]['lr'][1] - pad['h'] / 2]
                rt = [lim[s]['r'] + pad['w'] * 3, lim[s]['t'] + pad['h']]
            else:
                ln_k = (exm[s]['xr'][1] - exm[s]['lr'][1]) / (diff_x + pad['w'])
                ln_h = (exm[s]['xr'][0] * exm[s]['lr'][1] - exm[s]['lr'][0] * exm[s]['xr'][1]) / (diff_x + pad['w'])
                rb = [(exm[s]['lr'][0] - ln_h) / ln_k + pad['w'], exm[s]['lr'][1] - pad['h'] / 2]
                rt = [(lim[s]['t'] - ln_h) / ln_k + pad['w'], lim[s]['t'] + pad['h']]
            # Get tip anchor
            tp = [lim[s]['m'] + pad['w'], lim[s]['b'] - pad['h'] * 3.5]
        elif prb['info']['sty'] == 'right':
            # Compute left anchors
            diff_x = exm[s]['xl'][0] - exm[s]['ll'][0]
            if abs(diff_x) < 0.001:
                lb = [exm[s]['ll'][0] - pad['w'], exm[s]['ll'][1] - pad['h'] / 2]
                lt = [lim[s]['l'] - pad['w'] * 3, lim[s]['t'] + pad['h']]
            else:
                ln_k = (exm[s]['xl'][1] - exm[s]['ll'][1]) / (diff_x - pad['w'])
                ln_h = (exm[s]['xl'][0] * exm[s]['ll'][1] - exm[s]['ll'][0] * exm[s]['xl'][1]) / (diff_x - pad['w'])
                lb = [(exm[s]['ll'][0] - ln_h) / ln_k - pad['w'], exm[s]['ll'][1] - pad['h'] / 2]
                lt = [(lim[s]['t'] - ln_h) / ln_k - pad['w'], lim[s]['t'] + pad['h']]
            # Get right anchors
            rb = [lim[s]['r'] + pad['w'] / 2, lim[s]['b'] - pad['h'] / 2]
            rt = [lim[s]['r'] + pad['w'] / 2, lim[s]['t'] + pad['h']]
            # Get tip anchor
            tp = [lim[s]['m'] - pad['w'], lim[s]['b'] - pad['h'] * 3.5]
        elif prb['info']['sty'] == 'edge':
            # Compute left anchors
            diff_x = exm[s]['xl'][0] - exm[s]['ll'][0]
            if abs(diff_x) < 1:
                lb = [exm[s]['ll'][0] - pad['w'] / 1.5, exm[s]['ll'][1] - pad['h'] / 2]
                lt = [lim[s]['l'] - pad['w'] / 1.5, lim[s]['t'] + pad['h']]
            else:
                ln_k = (exm[s]['xl'][1] - exm[s]['ll'][1]) / diff_x
                ln_h = (exm[s]['xl'][0] * exm[s]['ll'][1] - exm[s]['ll'][0] * exm[s]['xl'][1]) / diff_x
                lb = [(exm[s]['ll'][0] - ln_h) / ln_k - pad['w'] / 1.5, exm[s]['ll'][1] - pad['h'] / 2]
                lt = [(lim[s]['t'] - ln_h) / ln_k - pad['w']/ 1.5, lim[s]['t'] + pad['h']]
            # Compute right anchors
            diff_x = exm[s]['xr'][0] - exm[s]['lr'][0]
            if abs(diff_x) < 1:
                rb = [exm[s]['lr'][0] + pad['w'] / 1.5, exm[s]['lr'][1] - pad['h'] / 2]
                rt = [lim[s]['r'] + pad['w'] / 1.5, lim[s]['t'] + pad['h']]
            else:
                ln_k = (exm[s]['xr'][1] - exm[s]['lr'][1]) / diff_x
                ln_h = (exm[s]['xr'][0] * exm[s]['lr'][1] - exm[s]['lr'][0] * exm[s]['xr'][1]) / diff_x
                rb = [(exm[s]['lr'][0] - ln_h) / ln_k + pad['w'] / 1.5, exm[s]['lr'][1] - pad['h'] / 2]
                rt = [(lim[s]['t'] - ln_h) / ln_k + pad['w'] / 1.5, lim[s]['t'] + pad['h']]
            # Get tip anchor
            tp = [lim[s]['m'], lim[s]['b'] - pad['h'] * 3.5]
        else:
            # Get left anchors
            lb = [lim[s]['l'] - pad['w'] / 1.5, lim[s]['b'] - pad['h'] / 2]
            lt = [lim[s]['l'] - pad['w'] / 1.5, lim[s]['t'] + pad['h']]
            # Get right anchors
            rb = [lim[s]['r'] + pad['w'] / 1.5, lim[s]['b'] - pad['h'] / 2]
            rt = [lim[s]['r'] + pad['w'] / 1.5, lim[s]['t'] + pad['h']]
            # Get tip anchor
            tp = [lim[s]['m'], lim[s]['b'] - pad['h'] * 3.5]

        # Plot shank patch
        tip[tp[0]] = tp[1]
        cd, vt = zip(*[
            (Path.MOVETO, lb), (Path.LINETO, tp), (Path.LINETO, rb), (Path.LINETO, rt), (Path.LINETO, lt),
            (Path.CLOSEPOLY, lb)])
        shk = PathPatch(Path(vt, cd), fc='grey', ls='none', zorder=0)
        ax.add_patch(shk)
        # Plot shank annotation
        ax.text((rt[0] + lt[0]) / 2, lt[1] + pad['h'] / 2, 'Shank %d' % s, size=12, weight=600, ha='center', zorder=3)
        cd, vt = zip(*[
            (Path.MOVETO, [rt[0] + pad['w'] * 0.5, lim[s]['b']]),
            (Path.LINETO, [rt[0] + pad['w'] * 1.5, lim[s]['b']]),
            (Path.LINETO, [rt[0] + pad['w'] * 1.5, lim[s]['t']]),
            (Path.LINETO, [rt[0] + pad['w'] * 0.5, lim[s]['t']])])
        ax.add_patch(PathPatch(Path(vt, cd), fill=False, lw=2, zorder=2))
        ax.text(rt[0] + pad['w'] * 2, (lim[s]['t'] + lim[s]['b']) / 2, '%d μm' % abs(lim[s]['t'] - lim[s]['b']),
                size=12, rotation=90, va='center', zorder=3)

        # Plot channel annotation
        for c in txt[s]['v']:
            sft = txt[s]['x'] - lt[0] + pad['w'] / 2
            ax.text(c[0] - sft, c[1], c[2], size=10, ha='right', va='center', zorder=3)

    # Probe annotation
    ax.set_title(r"$\bf{" + prb['info']['typ'].replace(' ', '\ ') + "}$\n" +
                 r"$\it{" + prb['info']['mfr'].replace(' ', '\ ') + "}$", size=14)
    idx = sorted(tip)
    for i in range(len(idx) - 1):
        if abs(idx[i] - idx[i + 1]) > 1:
            ya = min(tip[idx[i]], tip[idx[i + 1]]) - pad['w']
            cd, vt = zip(*[
                (Path.MOVETO, [idx[i], ya]), (Path.LINETO, [idx[i], ya - pad['w']]),
                (Path.LINETO, [idx[i + 1], ya - pad['w']]), (Path.LINETO, [idx[i + 1], ya])])
            ax.add_patch(PathPatch(Path(vt, cd), fill=False, lw=2, zorder=2))
            ax.text((idx[i + 1] + idx[i]) / 2, ya - pad['w'] * 1.5, '%d μm' % abs(idx[i + 1] - idx[i]),
                    size=12, ha='center', va='top', zorder=3)
        if abs(tip[idx[i]] - tip[idx[i + 1]]) > 1:
            xa = idx[i] + pad['w'] if tip[idx[i]] > tip[idx[i + 1]] else idx[i + 1] + pad['w']
            cd, vt = zip(*[
                (Path.MOVETO, [xa, tip[idx[i + 1]]]), (Path.LINETO, [xa + pad['w'], tip[idx[i + 1]]]),
                (Path.LINETO, [xa + pad['w'], tip[idx[i]]]), (Path.LINETO, [xa, tip[idx[i]]])])
            ano = PathPatch(Path(vt, cd), fill=False, lw=2, zorder=2)
            ax.add_patch(ano)
            ax.text(xa + pad['w'] * 1.5, (tip[idx[i + 1]] + tip[idx[i]]) / 2, '%d μm' %
                    abs(tip[idx[i + 1]] - tip[idx[i]]), rotation=90, size=12, ha='left', va='center', zorder=3)

    # Set axis feature
    ax.axis('equal')
    ax.set_axis_off()
    return ax
