import os
import matplotlib.pyplot as plt
from parus.data.file_io import pklz_read

"""This SCRIPT displays model prediction data versus its inputs.
"""
""" Parameters:
    path (str): Prediction results files location.
"""

# Parameters input  -------------------------------------------------------------------------------------------------- #
path = "./pred/"
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
pred_flst = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.sim')]
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
