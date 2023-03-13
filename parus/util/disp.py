# Inline display related function

import numpy as np
import plotext as ptx
import warnings

"""Function list:
plt_mdl_perf(prd, sig, lbl, size=(256, 32)): Plot current model performance with ground truth on terminal.
"""


def plt_mdl_perf(prd, sig, lbl, size=(256, 32)):
    """ Plot current model performance with ground truth on terminal.
    Args:
        prd (np.ndarray): {1D} Model prediction of [sig]
        sig (np.ndarray): {1D} Raw data input to model
        lbl (dict[str, np.ndarray, str, list[np.ndarray]]): Ground truth of [sig]
            - 'noise' (np.ndarray): {1D} Noise ground truth of [sig]
            - 'signal' (list[np.ndarray]): {1D} Grouped noise-free signal ground truth of [sig]
        size (tuple[int, int] or list[int, int] or None): Plot size, width * height (default: 256 * 32)
    """
    # Set theme
    ptx.theme('dark')
    # Plot data
    ptx.plot(prd, marker='dot', color=(30, 120, 180), label="Prediction")
    ptx.plot(sig, marker='dot', color=(255, 127, 15), label="Signal")
    ptx.plot(lbl, marker='dot', color=(40, 160, 40), label="Reference")
    # Set plot size
    if size is None:
        ptx.limit_size(True, True)
    else:
        if all(v > 0 for v in size):
            ptx.limit_size(False, False)
            ptx.plot_size(size[0], size[1])
        else:
            ptx.limit_size(True, True)
            warnings.warn("Plot size must larger than 0", RuntimeWarning, stacklevel=2)
    # Set plot text
    ptx.title("Model Performance")
    ptx.ticks_style('bold')
    ptx.xlabel('Sample Index')
    ptx.ylabel('Amplitude (mV)')
    # Display plot on terminal and clear
    ptx.show()
    ptx.clear_figure()
