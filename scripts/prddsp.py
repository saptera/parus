import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from parus.fio import pklz_read


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusPrdDsp", description="Display model prediction results versus its inputs")
parser.add_argument('-v', '--version', action='version', version="Parus - Display inference results: v1.5")
parser.add_argument('path', type=str, metavar="resultPath", help="[%(type)s] Prediction results location")
parser.add_argument('-r', '--noref', dest='noref', default=True, action='store_false', help="Reference plot switch")
parser.add_argument('-n', '--norm', dest='norm', default=False, action='store_true', help="Plot normalization switch")
parser.add_argument('-c', '--cont', dest='cont', default=False, action='store_true', help="Continuous sample switch")
parser.add_argument('-o', '--ovlp', dest='ovlp', type=int, default=0, metavar="[int]", help="Sample section overlap")
parser.add_argument('-f', '--freq', dest='freq', type=float, default=None, metavar="[float]", help="Sampling frequency")
parser.add_argument('-x', '--ymax', dest='ymax', type=float, default=None, metavar="[float]", help="Plot y-axis max")
parser.add_argument('-i', '--ymin', dest='ymin', type=float, default=None, metavar="[float]", help="Plot y-axis min")
parser.add_argument('-l', '--lims', dest='lims', default=False, action='store_true', help="Plot global y-limit switch")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


# Signal normalization function
def sig_norm_plt(sig: np.ndarray):
    nrm = max(abs(np.min(sig)), abs(np.max(sig)))
    dst = sig if nrm == 0 else sig / nrm
    return dst


# Spike position acquisition function
def spk_pos_plt(spk: np.ndarray, pos: np.ndarray, sft: float):
    px = np.where(pos > 0.8)[0]
    pv = spk[px]
    py = pv + np.sign(pv) * sft
    return {'x': px, 'y': py}


# Label and prediction arrangement function
def lbl_prd_plt(dat, sft: float, nrm: bool):
    if nrm:
        if type(dat) == dict:
            dat_spk = sig_norm_plt(dat['spk'])
            dat_pos = spk_pos_plt(dat_spk, dat['pos'], sft)
        else:
            dat_spk = sig_norm_plt(dat)
            dat_pos = None
    else:
        if type(dat) == dict:
            dat_spk = dat['spk']
            dat_pos = spk_pos_plt(dat_spk, dat['pos'], sft)
        else:
            dat_spk = dat
            dat_pos = None
    return dat_spk, dat_pos


# Function for updating canvas
def update_figure():
    global i, x_pos, s_flag
    # Read and process prediction data
    data = pred[i] if s_flag else pklz_read(pred_flst[i])
    x = np.linspace(start=x_pos, stop=x_pos + len(data['inp']), num=len(data['inp']), endpoint=True, dtype=int)
    x_tk = np.linspace(start=min(x), stop=max(x), num=6, endpoint=True, dtype=int)
    if args.freq is not None:
        x = x / (args.freq / 1000)
        x_tk = x_tk / (args.freq / 1000)
    # Set title
    file = os.path.split(args.path)[1] if s_flag else os.path.split(pred_flst[i])[1]
    title = r"$\bf{Viewing: %s}$" % file.replace('_', '\\_')
    title = title + "\nSection: %%0%dd of %%0%dd" % (len(str(n)), len(str(n))) % (i + 1, n + 1) if s_flag else title
    # Arrange data
    inp = data['inp']
    lbl = data.get('lbl', None)
    prd = data['prd']
    if args.norm:
        inp = sig_norm_plt(data['inp'])
        lbl_spk, lbl_pos = (None, None) if lbl is None else lbl_prd_plt(lbl, sft=10., nrm=True)
        prd_spk, prd_pos = lbl_prd_plt(prd, sft=25., nrm=True)
    else:
        lbl_spk, lbl_pos = (None, None) if lbl is None else lbl_prd_plt(lbl, sft=10., nrm=False)
        prd_spk, prd_pos = lbl_prd_plt(prd, sft=25., nrm=False)
    # Plot initialization
    ax.clear()
    ax.set_title(title)
    # Plot input data
    ax.plot(x, inp, color=u'#ff7f0e', label="Input")
    # Plot labels
    if (lbl is not None) and args.noref:
        if lbl_pos is None:
            ax.plot(x, lbl_spk, color=u'#2ca02c', label="Reference")
        else:
            ax.plot(x, lbl_spk, color=u'#2ca02c', label="Spike Reference")
            ax.scatter(lbl_pos['x'], lbl_pos['y'], color=u'#2ca02c', marker='^', label="Position Reference")
    # Plot model predictions
    if prd_pos is None:
        ax.plot(x, prd_spk, color=u'#1f77b4', label="Prediction")
    else:
        ax.plot(x, prd_spk, color=u'#1f77b4', label="Spike Prediction")
        ax.scatter(prd_pos['x'], prd_pos['y'], color=u'#1f77b4', marker='o', label="Position Prediction")
    # Set Y axis limits
    if (dn is not None) and (up is not None):
        ax.set_ylim(dn, up)
    # Set annotations
    ax.set_xticks(x_tk, labels=None, minor=False)
    ax.set_xlabel("Sample Unit", size=10) if args.freq is None else ax.set_xlabel("Time (ms)", size=10)
    ax.set_ylabel("Amplitude", size=10)
    ax.legend(loc='upper right')
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


# Get defined y-axis limit
dn = args.ymin
up = args.ymax

# Read file data in defined path
if os.path.isfile(args.path):
    raw = pklz_read(args.path)
    pred = [{k: raw[k][s] for k in raw} for s in range(len(raw['inp']))]
    n = len(pred) - 1  # Global variable
    sec = len(pred[0]['inp']) - args.ovlp  # Global variable
    s_flag = True  # Global variable
    # Compute global y-axis limit
    if args.lims:
        lims = np.asarray([[max(s), min(s)] for s in raw['inp']])
        dn = np.floor(lims.min(initial=None) / 10) * 10  # Global variable
        up = np.ceil(lims.max(initial=None) / 10) * 10  # Global variable
elif os.path.isdir(args.path):
    pred_flst = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.sim')]
    n = len(pred_flst) - 1  # Global variable
    sec = len(pklz_read(pred_flst[0])['inp']) - args.ovlp  # Global variable
    s_flag = False  # Global variable
else:
    print("Invalid prediction results path!")
    s_flag = None  # Global variable
    exit(-1)

# Initialize figure
i = -1  # Global variable
x_pos = 0  # Global variable
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title('Prediction Results')
fig.canvas.mpl_connect('key_press_event', on_press)
ax.set_title("Ready!")
ax.hlines(1, 0, 100, color=u'#ff7f0e', label="Input")
ax.hlines(0, 0, 100, color=u'#2ca02c', label="Reference")
ax.hlines(-1, 0, 100, color=u'#1f77b4', label="Prediction")
ax.set_ylim([-2, 2])
ax.legend(loc='upper right')
# Show plot
plt.tight_layout()
plt.show()
