import os
import argparse
import copy
import matplotlib.pyplot as plt
import numpy as np
from parus.fio import pklz_read


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusPrdDsp", description="Display model prediction results versus its inputs")
parser.add_argument('-v', '--version', action='version', version="Parus - Display inference results: v3.1")
parser.add_argument('path', type=str, metavar="resultPath", help="[%(type)s] Prediction results location")
parser.add_argument('-i', '--inp', dest='inp', default=True, action='store_false', help="Hide input data plot")
parser.add_argument('-s', '--spk', dest='spk', default=True, action='store_false', help="Hide all spike plots")
parser.add_argument('-sr', '--spkrf', dest='spkrf', default=True, action='store_false', help="Hide spike reference")
parser.add_argument('-sp', '--spkpd', dest='spkpd', default=True, action='store_false', help="Hide spike prediction")
parser.add_argument('-p', '--pos', dest='pos', default=True, action='store_false', help="Hide all position plots")
parser.add_argument('-pr', '--posrf', dest='posrf', default=True, action='store_false', help="Hide position reference")
parser.add_argument('-pp', '--pospd', dest='pospd', default=True, action='store_false', help="Hide position prediction")
parser.add_argument('-n', '--norm', dest='norm', default=False, action='store_true', help="Enable data normalization")
parser.add_argument('-c', '--cont', dest='cont', default=False, action='store_true', help="Enable continuous sampling")
parser.add_argument('-o', '--ovlp', dest='ovlp', type=int, default=0, metavar="[int]", help="Sample overlapping length")
parser.add_argument('-f', '--freq', dest='freq', type=float, default=None, metavar="[float]", help="Sampling frequency")
parser.add_argument('-yx', '--ymax', dest='ymax', type=float, default=None, metavar="[float]", help="Y-axis max value")
parser.add_argument('-yi', '--ymin', dest='ymin', type=float, default=None, metavar="[float]", help="Y-axis min value")
parser.add_argument('-lm', '--lims', dest='lims', default=False, action='store_true', help="Enable global y-axis limit")
parser.add_argument('-sb', '--sub', dest='sub', default=False, action='store_true', help="Enable subplot mode")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


# Signal normalization function
def sig_norm_plt(sig: np.ndarray):
    nrm = max(abs(np.min(sig)), abs(np.max(sig)))
    dst = sig if nrm == 0 else sig / nrm
    return dst


# Spike position acquisition function
def spk_pos_plt(spk: np.ndarray, pos: np.ndarray, sft: float, fix: bool):
    # Detect spike position
    px = np.where(pos > 0.8)[0]
    if px.size == 0:
        py = np.empty(0)
    else:
        if fix:
            # Set Y positions for marker
            py = spk[px] + sft
        else:
            # Get spike trend
            grd = np.gradient(spk, 2, edge_order=1)
            idx = px - 1
            idx[0] = 0 if idx[0] < 0 else idx[0]  # Avoid negative index
            sp = np.sign(grd[idx])
            # Set Y positions for marker
            py = spk[px] + sp * sft
    px = px if args.freq is None else px / (args.freq / 1000)
    return {'x': px, 'y': py}


# Label and prediction arrangement function
def lbl_prd_plt(dat, inp: np.ndarray, sft: float, spk_on: bool, pos_on: bool):
    if args.norm:
        sft /= 500  # Adapt marker position shift
        if isinstance(dat, dict):
            if spk_on:
                dat_spk = sig_norm_plt(dat['spk'])
                dat_pos = spk_pos_plt(dat_spk, dat['pos'], sft, (not args.inp)) if pos_on else None
            else:
                dat_spk = None
                dat_pos = spk_pos_plt(inp, dat['pos'], sft, (not args.inp)) if pos_on else None
        else:
            if spk_on:
                dat_spk = sig_norm_plt(dat)
                dat_pos = None
            elif pos_on:
                dat_spk = None
                dat_pos = spk_pos_plt(inp, dat, sft, (not args.inp))
            else:
                dat_spk = None
                dat_pos = None
    else:
        if isinstance(dat, dict):
            if spk_on:
                dat_spk = dat['spk']
                dat_pos = spk_pos_plt(dat['spk'], dat['pos'], sft, (not args.inp)) if pos_on else None
            else:
                dat_spk = None
                dat_pos = spk_pos_plt(inp, dat['pos'], sft, (not args.inp)) if pos_on else None
        else:
            if spk_on:
                dat_spk = dat
                dat_pos = None
            elif pos_on:
                dat_spk = None
                dat_pos = spk_pos_plt(inp, dat, sft, (not args.inp))
            else:
                dat_spk = None
                dat_pos = None
    return dat_spk, dat_pos


# Function for updating canvas
def update_figure():
    global i, x_pos, s_flag
    # Read and process prediction data
    data = copy.deepcopy(pred[i]) if s_flag else pklz_read(pred_flst[i])
    x = np.linspace(start=x_pos, stop=x_pos + len(data['inp']), num=len(data['inp']), endpoint=True, dtype=int)
    x_tk = np.linspace(start=min(x), stop=max(x), num=6, endpoint=True, dtype=int)
    if args.freq is not None:
        x = x / (args.freq / 1000)
        x_tk = x_tk / (args.freq / 1000)
    # Set title
    file = os.path.split(args.path)[1] if s_flag else os.path.split(pred_flst[i])[1]
    title = r"$\bf{Viewing:\ %s}$" % file.replace('_', '\\_')
    title = title + "\nSection: %%0%dd of %%0%dd" % (len(str(n)), len(str(n))) % (i + 1, n + 1) if s_flag else title
    # Arrange input data
    if args.inp:
        inp = sig_norm_plt(data['inp']) if args.norm else data['inp']
        lbl_pos_sft = 10.
        prd_pos_sft = 10. if args.sub else 25.
    else:
        inp = np.full(len(data['inp']), 0., dtype=float)
        lbl_pos_sft = 1.
        prd_pos_sft = -1.
    # Arrange label data
    if 'lbl' in data:
        spk_rf = args.spk and args.spkrf
        pos_rf = args.pos and args.posrf
    else:
        spk_rf, pos_rf = False, False
        data['lbl'] = None
    lbl_spk, lbl_pos = lbl_prd_plt(data['lbl'], inp, sft=lbl_pos_sft, spk_on=spk_rf, pos_on=pos_rf)
    # Arrange prediction data
    if 'prd' in data:
        spk_pd = args.spk and args.spkpd
        pos_pd = args.pos and args.pospd
    else:
        spk_pd, pos_pd = False, False
        data['prd'] = {'spk': None, 'pos': None}
    prd_spk, prd_pos = lbl_prd_plt(data['prd'], inp, sft=prd_pos_sft, spk_on=spk_pd, pos_on=pos_pd)
    # Plot initialization
    for ax in axes.flat:
        ax.clear()
    fig.suptitle(title)
    # Plot new data
    for ic in range(ncol):
        # Plot input data
        args.inp and axes[ax_i, ic].plot(x, inp, color=u'#ff7f0e', label="Input")
        # Plot labels
        if lbl_spk is not None:
            ls = lbl_spk[ic] if sel_flag else lbl_spk
            axes[ax_l, ic].plot(x, ls, color=u'#2ca02c', label="Spike Reference")
        if lbl_pos is not None:
            lpx = lbl_pos['x'][ic] if sel_flag else lbl_pos['x']
            lpy = lbl_pos['y'][ic] if sel_flag else lbl_pos['y']
            axes[ax_l, ic].scatter(lpx, lpy, color=u'#006400', marker='^', label="Position Reference")
        # Plot model predictions
        if prd_spk is not None:
            ps = prd_spk[ic] if sel_flag else prd_spk
            axes[ax_p, ic].plot(x, ps, color=u'#1f77b4', label="Spike Prediction")
        if prd_pos is not None:
            ppx = prd_pos['x'][ic] if sel_flag else prd_pos['x']
            ppy = prd_pos['y'][ic] if sel_flag else prd_pos['y']
            axes[ax_p, ic].scatter(ppx, ppy, color=u'#191970', marker='o', label="Position Prediction")
        # Set group annotations
        axes[0, ic].set_title(grp_str[ic]) if sel_flag else ...
        axes[-1, ic].set_xlabel("Sample Unit" if args.freq is None else "Time (ms)", size=10)
    # Set plot annotations
    for ax in axes.flat:
        ax.set_xticks(x_tk, labels=None, minor=False)
        ax.legend(loc='upper right')
    for ax in axes[:, 0]:
        ax.set_ylabel("Amplitude", size=10)
    # Set Y axis limits
    if (dn is not None) and (up is not None):
        axes[0, 0].set_ylim(dn, up)  # Y-axes are shared
    # Update figure
    fig.canvas.draw()
    fig.canvas.flush_events()


# Function for keyboard connection
def on_press(event):
    global i, n, sec, x_pos
    if event.key == 'left' or event.key == 'up':
        i -= 1
        if i < 0:
            i = n
            print("First prediction reached, loop to the last!")
        x_pos = i * sec if args.cont else 0
        update_figure()
    elif event.key == 'right' or event.key == 'down':
        i += 1
        if i > n:
            i = 0
            print("Last prediction reached, loop to the first!")
        x_pos = i * sec if args.cont else 0
        update_figure()
    elif event.key == 'escape':
        plt.close('all')


# Get plot settings
spk_flag = (args.spk and args.spkrf) or (args.spk and args.spkpd)
pos_flag = (args.pos and args.posrf) or (args.pos and args.pospd)
ref_flag = (args.spk and args.spkrf) or (args.pos and args.posrf)
prd_flag = (args.spk and args.spkpd) or (args.pos and args.pospd)
# Validate plot settings
if not (args.inp or spk_flag or pos_flag):
    raise RuntimeError("Nothing to plot! Please check your settings.")
# Initialize plot column size
ncol = 1
# Get defined y-axis limit
if args.inp or spk_flag:
    dn = args.ymin
    up = args.ymax
else:
    dn = -4
    up = 4
    args.lims = True

# Read file data in defined path
if os.path.isfile(args.path):
    raw = pklz_read(args.path)
    # Check data type
    dic_typ = False
    if 'prd' in raw:
        if isinstance(raw['prd'], dict):
            dic_typ = True
            ncol = len(raw['prd'][next(iter(raw['prd']))].shape) - 1  # Global variable
        else:
            dic_typ = False
            ncol = len(raw['prd'].shape) - 1  # Global variable
    else:
        prd_flag = False
    if 'lbl' in raw:
        if isinstance(raw['lbl'], dict):
            dic_typ = True
            ncol = len(raw['lbl'][next(iter(raw['lbl']))].shape) - 1  # Global variable
        else:
            dic_typ = False
            ncol = len(raw['lbl'].shape) - 1  # Global variable
    else:
        ref_flag = False
    # Arrange data
    if dic_typ:
        pred = [{t: raw[t][s] if t == 'inp' else {k: raw[t][k][s] for k in raw[t]} for t in raw}
                for s in range(raw['inp'].shape[0])]
    else:
        pred = [{t: raw[t][s] for t in raw} for s in range(raw['inp'].shape[0])]
    # Set global variables
    grp_str = raw['grp'] if 'grp' in raw else ["Group %02d" % d for d in range(ncol)]
    n = len(pred) - 1
    sec = pred[0]['inp'].shape[0] - args.ovlp
    s_flag = True
    # Compute global y-axis limit
    if args.lims:
        lims = np.asarray([[max(s), min(s)] for s in raw['inp']])
        # Set global variables
        dn = np.floor(lims.min(initial=None) / 10) * 10
        up = np.ceil(lims.max(initial=None) / 10) * 10
elif os.path.isdir(args.path):
    pred_flst = [os.path.join(args.path, f)
                 for f in os.listdir(args.path) if (not f.startswith('.')) and f.endswith('.sim')]
    # Check data type for column size
    raw = pklz_read(pred_flst[0])
    if 'prd' in raw:
        ncol = len(raw['prd'][next(iter(raw['prd']))].shape) if isinstance(raw['prd'], dict) else len(raw['prd'].shape)
    else:
        prd_flag = False
    if 'lbl' in raw:
        ncol = len(raw['lbl'][next(iter(raw['lbl']))].shape) if isinstance(raw['lbl'], dict) else len(raw['lbl'].shape)
    else:
        ref_flag = False
    # Set global variables
    grp_str = raw['grp'] if 'grp' in raw else ["Group %02d" % d for d in range(ncol)]
    n = len(pred_flst) - 1
    sec = raw['inp'].shape[0] - args.ovlp
    s_flag = False
else:
    # Set global variables
    s_flag = None
    grp_str = []
    # STOP
    raise RuntimeError("Invalid prediction results path!")

# Set plot axis row index
if args.sub:
    ax_i = 0 if args.inp else -1
    ax_l = ax_i + 1 if ref_flag else ax_i
    ax_p = ax_l + 1 if prd_flag else ax_l
else:
    ax_i = ax_l = ax_p = 0
# Initialize figure
i = -1  # Global variable
x_pos = 0  # Global variable
fig, axes = plt.subplots(nrows=ax_p + 1, ncols=ncol, sharex='all', sharey='all')
fig.canvas.manager.set_window_title('Prediction Results')
fig.canvas.mpl_connect('key_press_event', on_press)
fig.suptitle(r"$\bf{System\ Ready}$")
# Setup axes feature
if ncol == 1:
    axes = np.asarray([axes]).T if args.sub else np.asarray([[axes]])
    sel_flag = False  # Global variable
else:
    axes = np.asarray(axes) if args.sub else np.asarray([axes])
    sel_flag = True  # Global variable
# Plot initial panel
for c in range(ncol):
    axes[0, c].set_title(grp_str[c]) if sel_flag else ...
    if args.sub:
        if args.inp:
            axes[ax_i, c].hlines(0, 0, 100, color=u'#ff7f0e', label="Input")
            axes[ax_i, c].legend(loc='upper right')
        if ref_flag:
            axes[ax_l, c].hlines(1, 0, 100, color=u'#2ca02c', label="Spike Reference")
            axes[ax_l, c].scatter(range(0, 101, 10), [-1] * 11, color=u'#006400', marker='^', label="Position Reference")
            axes[ax_l, c].legend(loc='upper right')
        if prd_flag:
            axes[ax_p, c].hlines(1, 0, 100, color=u'#1f77b4', label="Spike Prediction")
            axes[ax_p, c].scatter(range(0, 101, 10), [-1] * 11, color=u'#191970', marker='o', label="Position Prediction")
            axes[ax_p, c].legend(loc='upper right')
    else:
        axes[0, c].hlines(2, 0, 100, color=u'#ff7f0e', label="Input")
        axes[0, c].hlines(0, 0, 100, color=u'#2ca02c', label="Spike Reference")
        axes[0, c].scatter(range(0, 101, 10), [1] * 11, color=u'#006400', marker='^', label="Position Reference")
        axes[0, c].hlines(-2, 0, 100, color=u'#1f77b4', label="Spike Prediction")
        axes[0, c].scatter(range(0, 101, 10), [-1] * 11, color=u'#191970', marker='o', label="Position Prediction")
        axes[0, c].legend(loc='upper right')
axes[0, 0].set_ylim([-3, 3])  # Y-axes are shared
# Show plot
plt.tight_layout()
plt.show()
