import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from parus.fio import pklz_read


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusPrdDsp", description="Display model prediction results versus its inputs")
parser.add_argument('-v', '--version', action='version', version="Parus - Display inference results: v1.5")
parser.add_argument('path', type=str, metavar="resultPath", help="[%(type)s] Prediction results location")
parser.add_argument('-f', '--noref', dest='noref', default=True, action='store_false', help="Reference plot switch")
parser.add_argument('-n', '--norm', dest='norm', default=False, action='store_true', help="Plot normalization switch")
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


# Function for updating canvas
def update_figure():
    # Read and process prediction data
    data = pred[i] if s_flag else pklz_read(pred_flst[i])
    x = list(range(len(data['inp'])))
    # Set title
    file = os.path.split(args.path)[1] if s_flag else os.path.split(pred_flst[i])[1]
    title = r"$\bf{Viewing: %s}$" % file.replace('_', '\\_')
    title = title + "\nSection: %%0%dd of %%0%dd" % (len(str(n)), len(str(n))) % (i + 1, n + 1) if s_flag else title
    # Arrange data
    if args.norm:
        lbl = sig_norm_plt(data['lbl']) if 'lbl' in data else None
        inp = sig_norm_plt(data['inp'])
        prd = sig_norm_plt(data['prd'])
    else:
        lbl = data.get('lbl', None)
        inp = data['inp']
        prd = data['prd']
    # Plotting
    ax.clear()
    ax.set_title(title)
    if (lbl is not None) and args.noref:
        ax.plot(x, lbl, color=u'#2ca02c', label="Reference")
    ax.plot(x, inp, color=u'#ff7f0e', label="Input")
    ax.plot(x, prd, color=u'#1f77b4', label="Prediction")
    ax.legend(loc='upper right')
    if (dn is not None) and (up is not None):
        ax.set_ylim(dn, up)
    # Update figure
    fig.canvas.draw()
    fig.canvas.flush_events()


# Function for keyboard connection
def on_press(event):
    global i
    if event.key == 'left' or event.key == 'up':
        i -= 1
        if i < 0:
            i = n
            print("First prediction reached, loop to the last!")
        update_figure()
    elif event.key == 'right' or event.key == 'down':
        i += 1
        if i > n:
            i = 0
            print("Last prediction reached, loop to the first!")
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
    n = len(pred) - 1
    s_flag = True  # Global variable
    # Compute global y-axis limit
    if args.lims:
        lims = np.asarray([[max(s), min(s)] for s in raw['inp']])
        dn = np.floor(lims.min(initial=None) / 10) * 10  # Global variable
        up = np.ceil(lims.max(initial=None) / 10) * 10  # Global variable
elif os.path.isdir(args.path):
    pred_flst = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.sim')]
    n = len(pred_flst) - 1
    s_flag = False  # Global variable
else:
    print("Invalid prediction results path!")
    s_flag = None  # Global variable
    exit(-1)

# Initialize figure
i = -1  # Global variable
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title('Prediction Results')
fig.canvas.mpl_connect('key_press_event', on_press)
ax.set_title("Ready!")
ax.hlines(0, 0, 100, color=u'#2ca02c', label="Reference")
ax.hlines(1, 0, 100, color=u'#ff7f0e', label="Input")
ax.hlines(-1, 0, 100, color=u'#1f77b4', label="Prediction")
ax.set_ylim([-2, 2])
ax.legend(loc='upper right')
# Show plot
plt.tight_layout()
plt.show()
