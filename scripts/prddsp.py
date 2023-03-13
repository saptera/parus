import os
import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
from parus.fio import pklz_read

mpl.use('TkAgg')  # Use TkAgg backend


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusPrdDsp", description="Display model prediction results versus its inputs")
parser.add_argument('-v', '--version', action='version', version="Parus - Display inference results: v1.5")
parser.add_argument('path', type=str, metavar="resultsFolder", help="[%(type)s] Prediction results files location")
parser.add_argument('-n', '--norm', dest='norm', default=False, action='store_true', help="Plot normalization switch")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


# Function for updating canvas
def update_figure():
    # Read and process prediction data
    data = pklz_read(pred_flst[i])
    x = list(range(len(data['lbl'])))
    if args.norm:
        lbl_nrm = max(abs(data['lbl'].min()), abs(data['lbl'].max()))
        lbl = data['lbl'] if lbl_nrm == 0 else data['lbl'] / lbl_nrm
        inp_nrm = max(abs(data['inp'].min()), abs(data['inp'].max()))
        inp = data['inp'] if inp_nrm == 0 else data['inp'] / inp_nrm
        prd_nrm = max(abs(data['prd'].min()), abs(data['prd'].max()))
        prd = data['prd'] if prd_nrm == 0 else data['prd'] / prd_nrm
    else:
        lbl = data['lbl']
        inp = data['inp']
        prd = data['prd']
    # Plotting
    ax.clear()
    ax.set_title("Viewing: %s" % os.path.split(pred_flst[i])[1])
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


# Read file list in defined path
pred_flst = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.sim')]
n = len(pred_flst) - 1
i = 0  # Global variable

# Initialize figure
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
