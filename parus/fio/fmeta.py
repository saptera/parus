# Parus customized meta file IO functions

import warnings
import csv
import json
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import FancyBboxPatch, PathPatch

"""Function list:
conv_lin_prb(prb_file): Convert linear probe definition file to standard probe data structure.
plot_probe(prb, ax): Plot neural recoding probe.
read_spk_info(spk_info_csv, cell_mode, trim_negat, trim_noise): Import spike timing data form JRClust output.
read_cell_type(cell_type_csv): Read cell type definition CSV file.
"""


def conv_lin_prb(prb_file):
    """ Convert linear probe definition file to standard probe data structure.

    Args:
        prb_file (str): Probe definition file (*.prb)

    Returns:
        list[dict] | None: Probe definition information, structure as follows:
                           list[{'id': int, 'shk': int, 'col': int, 'geo': (float, float), 'pad': (float, float)}]
    """
    # Read in file
    with open(prb_file) as infile:
        try:
            prb_dat = json.load(infile)
        except json.decoder.JSONDecodeError:
            warnings.warn("Invalid probe definition file format.", Warning, 2)
            return None
    # Checking for keys
    miss_key = str()
    for k in ['channel', 'n_chs', 'n_shk', 'n_col', 'gap_chs', 'gap_shk', 'sft_shk', 'gap_col', 'sft_col', 'pad']:
        if k not in prb_dat:
            miss_key += "'" + k + "', "
    if miss_key:
        miss_key = miss_key.rstrip(", ")
        warnings.warn("Key [%s] missing in probe definition file, please verify file integrity." % miss_key, Warning, 2)
        return None

    # Read basic information of the probe sites
    channel = prb_dat['channel']
    n_chs = prb_dat['n_chs']
    n_shk = prb_dat['n_shk']
    n_col = prb_dat['n_col']
    # Read geometry parameters in micrometers
    gap_chs = prb_dat['gap_chs']
    gap_shk = prb_dat['gap_shk']
    sft_shk = prb_dat['sft_shk']
    gap_col = prb_dat['gap_col']
    sft_col = prb_dat['sft_col']
    # Recording contact pad size in micrometers (height X width)
    pad = prb_dat['pad']

    # Compute group definition
    n_grp = int(n_col * n_shk)
    grp_lst = []  # INIT VAR
    for i in range(n_shk):
        for j in range(n_col):
            grp_lst.append((i + 1, j + 1))

    # Arrange probe information
    prb_def = []  # INIT VAR
    ch_dat_temp = {'id': int, 'shk': int, 'col': int, 'geo': (float, float), 'pad': (float, float)}  # INIT VAR
    for i in range(n_chs):
        # Assign basic information
        ch_dat_temp['id'] = channel[i] - 1
        ch_dat_temp['pad'] = (pad[0], pad[1])
        # Compute and assign group information
        grp_idx = i % n_grp
        ch_shk = grp_lst[grp_idx][0]
        ch_col = grp_lst[grp_idx][1]
        ch_dat_temp['shk'] = ch_shk
        ch_dat_temp['col'] = ch_col
        # Compute channel geometric information
        grp_cnt = i // n_grp
        ch_xlc = gap_col * (ch_col - 1) + gap_shk * (ch_shk - 1)
        ch_ylc = gap_chs * grp_cnt + sft_col * (ch_col - 1) + sft_shk * (ch_shk - 1)
        ch_dat_temp['geo'] = (ch_xlc, ch_ylc)
        # Assign to output array
        prb_def.append(copy.deepcopy(ch_dat_temp))

    return prb_def


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


def read_spk_info(spk_info_csv, cell_mode=True, trim_negat=True, trim_noise=False):
    """ Import spike timing data form JRClust output.

     Args:
          spk_info_csv (str): Cell spike timing CSV file generated by [JRClust]
          cell_mode (bool): Arrange data with cell ID if [True]; arrange with channel ID if [False] (default: True)
          trim_negat (bool): Remove negative (manual deleted cells) IDs if [True] (default: True)
          trim_noise (bool): Remove noise information (cell ID: 0) from output (default: False)

    Returns:
        dict[int, dict[int, np.ndarray]]: Arranged spike timing data, data structure as follows:
                                          CELL: {cell_id: {prob_ch: spk_time}}; CHANNEL: {prob_ch: {cell_id: spk_time}}
    """
    with open(spk_info_csv, "r") as csv_file:
        jrc_data = np.loadtxt(csv_file, delimiter=",")
    spk_data = {}  # INIT VAR
    # Read and arrange data with cell ID
    if cell_mode:
        cell_id = np.unique(jrc_data[:, 1])  # Get unique cell numbers
        for cid in cell_id:
            if (not trim_negat) or (int(cid.item()) >= 0):
                prob_ch = np.unique(jrc_data[:, 2][jrc_data[:, 1] == cid])  # Get probe channels have cell
                spk_temp = {}  # INIT/RESET VAR
                for pch in prob_ch:
                    spk = jrc_data[:, 0][(jrc_data[:, 1] == cid) & (jrc_data[:, 2] == pch)]  # Get spike timings
                    spk_temp[int(pch.item()) - 1] = spk
                spk_data[int(cid.item())] = spk_temp
        if trim_noise:
            spk_data.pop(0, None)
    # Read and arrange data with channel ID
    else:
        prob_ch = np.unique(jrc_data[:, 2])  # Get unique probe channels
        for pch in prob_ch:
            cell_id = np.unique(jrc_data[:, 1][jrc_data[:, 2] == pch])  # Get cell IDs within channel
            spk_temp = {}  # INIT/RESET VAR
            for cid in cell_id:
                if (not trim_negat) or (int(cid.item()) >= 0):
                    spk = jrc_data[:, 0][(jrc_data[:, 2] == pch) & (jrc_data[:, 1] == cid)]  # Get spike timings
                    spk_temp[int(cid.item())] = spk
                if trim_noise:
                    spk_temp.pop(0, None)
            spk_data[int(pch.item()) - 1] = spk_temp
    # Set output
    return spk_data


def read_cell_type(cell_type_csv):
    """ Read cell type definition CSV file.

    Args:
        cell_type_csv (str): Cell type CSV file

    Returns:
        dict[int, str]: Arranged cell type information ({cell_id: cell_type})
    """
    # Read data in CSV file
    with open(cell_type_csv, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        no = []  # INIT VAR
        tp = []  # INIT VAR
        for row in csv_reader:
            no.append(int(row[0]))
            tp.append(row[1])
    # Initialize output dictionary
    cell_type = {}
    for n in no:
        cell_type[n] = str()
    # Arrange data for output
    for s in set(tp):
        i = 0
        for t in range(len(tp)):
            if tp[t] == s:
                cell_type[no[t]] = tp[t] + "_%03d" % i
                i += 1
    return cell_type
