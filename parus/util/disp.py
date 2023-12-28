# Inline display related function

import numpy as np
import scipy.optimize as spopt
import plotext as ptx
import warnings

"""Function list:
plt_mdl_perf(prd, sig, lbl, size=(256, 32)): Plot current model performance with ground truth on terminal.
fit_exp_loss(trn_loss, vld_loss): Estimate future loss with exponential model.
"""


def plt_mdl_perf(prd, sig, lbl, size=(256, 32)):
    """ Plot current model performance with ground truth on terminal.

    Args:
        prd (np.ndarray): {1D} Model prediction of [sig]
        sig (np.ndarray): {1D} Raw data input to model
        lbl (dict[str, np.ndarray, str, list[np.ndarray]]): Ground truth of [sig]
            - 'noise' (np.ndarray): {1D} Noise ground truth of [sig]
            - 'signal' (list[np.ndarray]): {1D} Grouped noise-free signal ground truth of [sig]
        size (tuple[int, int] | list[int, int] | None): Plot size, width * height (default: 256 * 32)
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


def fit_exp_loss(trn_loss, vld_loss):
    """ Estimate future loss with exponential model.

    Args:
        trn_loss (list[int | float] | np.ndarray): Current list of training loss
        vld_loss (list[int | float] | np.ndarray): Current list of validation loss
    """

    def fit_exp(x, y):
        """ Exponential model fitting function """
        # Model fitting
        expdef = lambda prm, n: prm[0] * np.exp(prm[1] * n) + prm[2]
        sumsqr = lambda prm: np.sum(np.square(expdef(prm, x) - y))
        model = spopt.fmin(func=sumsqr, x0=(1.0, 1.0, 0.0), xtol=0.00001, ftol=0.00001, disp=False)
        # Fit evaluation
        varres = np.sum(np.square(expdef(model, x) - y)) / (len(x) - 3)  # Number of parameters = 3
        vartot = np.sum(np.square(y - np.mean(y))) / (len(x) - 1)
        rsqt = 1 - varres / vartot
        return model, rsqt

    def loss_esti(loss, typ):
        """ Future loss estimation function """
        src_x = np.asarray(range(1, len(loss) + 1), dtype=float)
        src_y = np.asarray(loss, dtype=float)
        est_p, est_r = fit_exp(src_x, src_y)
        est_x = np.linspace(start=len(src_x) + 1, stop=len(src_x) + 10, num=10, dtype=float)
        est_y = est_p[0] * np.exp(est_p[1] * est_x) + est_p[2]
        est_str = " ".join('%.2f' % i for i in est_y)
        print("Estimated future [%s] loss @ Adj-Rsqr=%.4f:" % (typ, est_r), est_str)

    # Process estimation
    if len(trn_loss) < 4:
        print("Insufficient data points to estimation future [TRAIN] loss")
    else:
        loss_esti(trn_loss, "TRAIN")
    if len(vld_loss) < 4:
        print("Insufficient data points to estimation future [VALID] loss")
    else:
        loss_esti(vld_loss, "VALID")
