# Spike clustering functions

import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth

"""Function list:
cls_pk_val(sig, pos, bw=None): Clustering spikes with peak height only.
"""


def cls_pk_val(sig, pos, bw=None):
    """ Clustering spikes with peak height only.

    Args:
        sig (np.ndarray[int | float]): Input signal
        pos (np.ndarray[int]): One-hot spike position
        bw (int | float | None): Bandwidth used in the flat kernel (default: None = estimate from data)

    Returns:
        dict[int, list[int]]: Clustered spikes indices
    """
    # Get peak value
    idx = np.argwhere(pos == 1).flatten()
    pk = sig[idx].reshape(-1, 1)
    # Assess bandwidth
    if (bw is None) or (bw <= 0):
        bw = estimate_bandwidth(pk, quantile=0.5)
        bw = 0.01 if bw <= 0 else bw  # Check the estimation
    # Fit values
    ms = MeanShift(bandwidth=bw, bin_seeding=True)
    ms.fit(pk)
    # Arrange data
    lbl = ms.labels_
    res = {}  # INIT VAR
    for l in np.unique(lbl):
        res[l.item()] = idx[lbl == l].tolist()
    return res
