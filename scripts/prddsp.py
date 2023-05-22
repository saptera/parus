import os
import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from parus.fio import pklz_read

mpl.use('TkAgg')  # Use TkAgg backend


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusPrdDsp", description="Display model prediction results versus its inputs")
parser.add_argument('-v', '--version', action='version', version="Parus - Display inference results: v1.5")
parser.add_argument('path', type=str, metavar="resultsFolder", help="[%(type)s] Prediction results location")
parser.add_argument('-n', '--norm', dest='norm', default=False, action='store_true', help="Plot normalization switch")
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
    title = "Viewing: SIG-%%0%dd" % len(str(n)) % i if s_flag else "Viewing: %s" % os.path.split(pred_flst[i])[1]
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
    if lbl is not None:
        ax.plot(x, lbl, color=u'#2ca02c', label="Reference")
    ax.plot(x, inp, color=u'#ff7f0e', label="Input")
    ax.plot(x, prd, color=u'#1f77b4', label="Prediction")
    ax.legend(loc='upper right')
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


# Read file data in defined path
if os.path.isfile(args.path):
    raw = pklz_read(args.path)
    pred = [{k: raw[k][s] for k in raw} for s in range(len(raw['inp']))]
    n = len(pred) - 1
    s_flag = True  # Global variable
elif os.path.isdir(args.path):
    pred_flst = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.sim')]
    n = len(pred_flst) - 1
    s_flag = False  # Global variable
else:
    print("Invalid prediction results path!")
    s_flag = None  # Global variable
    exit(-1)

# Initialize figure
i = 0  # Global variable
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
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
plt.show()
