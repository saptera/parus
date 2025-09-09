# Inline display related function

import numpy as np
import scipy.optimize as spopt
import plotext as ptx
import matplotlib.pyplot as plt
import warnings

__all__ = ['plt_mod_cli', 'plt_mod_img', 'fit_exp_loss']
"""
Function list:
  plt_mod_cli(prd, sig, lbl, size=(256, 32)): Plot current model performance with ground truth on terminal.
  plt_mod_img(prd, sig, lbl, img=None): Plot current model performance with ground truth to image file.
  fit_exp_loss(trn_loss, vld_loss): Estimate future loss with exponential model.
"""


def plt_mod_cli(prd, sig, lbl, size=(256, 32)):
    """ Plot current model performance with ground truth on terminal.

    Args:
        prd (np.ndarray): {1D} Model prediction
        sig (np.ndarray): {1D} Raw data input to model
        lbl (np.ndarray): {1D} Noise-free signal ground truth
        size (tuple[int, int] | list[int, int] | None): Plot size, width * height (default: 256 * 32)
    """
    # Set theme
    ptx.theme('dark')
    # Plot data
    ptx.plot(sig, marker='dot', color=(255, 127, 15), label="Signal")
    ptx.plot(lbl, marker='dot', color=(40, 160, 40), label="Reference")
    ptx.plot(prd, marker='dot', color=(30, 120, 180), label="Prediction")
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
    ptx.xlabel("Sample Index")
    ptx.ylabel("Amplitude (mV)")
    # Display plot on terminal and clear
    ptx.show()
    ptx.clear_figure()


def plt_mod_img(prd, sig, lbl, img=None):
    """ Plot current model performance with ground truth to image file.

    Args:
        prd (np.ndarray): {1D} Model prediction
        sig (np.ndarray): {1D} Raw data input to model
        lbl (np.ndarray): {1D} Noise-free signal ground truth
        img (str | None): Output image file (default: None = return figure, no save)

    Returns:
        tuple[plt.Figure, plt.Axes] | tuple[None, None]: Plotted figure
    """
    # Set figure
    fig, ax = plt.subplots(1, 1, dpi=150)
    fig.set_layout_engine(layout='tight')
    ax.spines[['top', 'right']].set_visible(False)
    # Plot data
    ax.plot(sig, color='#ff7f0f', label="Signal", zorder=1)
    ax.plot(lbl, color='#28a028', label="Reference", zorder=1)
    ax.plot(prd, color='#1e78b4', label="Prediction", zorder=1)
    # Add reference lines
    ax.axhline(0, c='darkgray', lw=0.5, alpha=0.75, zorder=2)
    # Set plot text
    ax.set_title("Model Performance", fontsize=12, fontweight='bold')
    ax.set_xlabel("Sample Index", fontsize=12)
    ax.set_ylabel("Amplitude (mV)", fontsize=12)
    ax.legend(loc='upper left')
    # Output options
    if img is None:
        return fig, ax
    else:
        fig.savefig(img, format='png')
        plt.close(fig)
        return None, None


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
