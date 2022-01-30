import os
import argparse
import matplotlib.pyplot as plt
from parus.data.file_io import pklz_read


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="DMIR", description="Display model prediction results versus its inputs")
parser.add_argument('-v', '--version', action='version', version="Display inference results: v1.0")
parser.add_argument('path', type=str, metavar="resultsFolder", help="[%(type)s] Prediction results files location")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


# Function for updating canvas
def update_figure():
    # Read and process prediction data
    data = pklz_read(pred_flst[i])
    x = list(range(len(data['lbl'])))
    inp = data['inp'] / -data['inp'].min()
    prd = data['prd'] / -data['prd'].min()
    # Plotting
    ax.clear()
    ax.set_title("Viewing: %s" % os.path.split(pred_flst[i])[1])
    ax.plot(x, inp, color='orange', label="Input")
    ax.plot(x, prd, color='green', label="Prediction")
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
ax.hlines(1, 0, 100, color='orange', label="Input")
ax.hlines(-1, 0, 100, color='green', label="Prediction")
ax.set_ylim([-2, 2])
ax.legend(loc='upper right')
plt.show()
