# Data plotting related functions

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import FancyBboxPatch, PathPatch

"""Function list:
swarm_cord(data, bins=None, width=1): Compute the coordinates for swarm plot.
plot_probe(prb, ax): Plot neural recoding probe.
"""


def swarm_cord(data, bins=None, centre=0, width=1):
    """ Compute the coordinates for swarm plot.

    Args:
        data (tuple | list | np.ndarray): Input data
        bins (int | None): Number of equal-width bins in the data range (default: None -> 6 bins)
        centre (int | float): Centre of the swarm (default: 0)
        width (int | float): Width of the swarm (default: 1)

    Returns:
        np.ndarray: Computed data swarm coordinates
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
    dx = width / (lim // 2)
    for i, y in zip(ibs, ybs):
        if len(i) > 1:
            j = len(i) % 2
            i = i[np.argsort(y)]
            a = i[j::2]
            b = i[j + 1::2]
            cord[a] = (0.5 + j / 3 + np.arange(len(b))) * dx
            cord[b] = (0.5 + j / 3 + np.arange(len(b))) * -dx
    return cord + centre


def plot_prb(prb, ax):
    """ Plot neural recoding probe.

    Args:
        prb (dict): Probe information
        ax (plt.Axes): Matplotlib axis to plot on

    Returns:
        plt.Axes: Reference copy of input axis
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
