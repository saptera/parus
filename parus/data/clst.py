# Spike clustering module

import numpy as np

__package__ = 'parus.data'
__name__ = 'parus.data.clst'

__all__ = [
    'cls_cosamp_blk', 'cls_cosamp_prg', 'cls_crscor_blk', 'cls_crscor_prg',
    'pos_ripple_flt', 'post_cls_chk', 'get_sig_nbr', 'find_crsch_sig', 'crsch_grp'
]
"""
Function list:
  # Signal clustering functions:
    cls_cosamp_blk(sig, pos, asp, psp, k=0.6, w=True): Clustering spikes by cosine and amplitude similarity, block mode.
    cls_cosamp_prg(sig, pos, asp, psp, k=0.6, w=True, delta=0.2): Clustering spikes cosine-amplitude, progressive mode.
    cls_crscor_blk(sig, pos, asp, psp, k=0.8): Clustering spikes by Pearson correlation coefficient, block mode.
    cls_crscor_prg(sig, pos, asp, psp, k=0.8, delta=0.2): Clustering spikes by Pearson crs-cor, progressive mode.
  # Pre/Post clustering functions:
    pos_ripple_flt(sig, pos, lim=3, neg=True): Filter out ripples from one-hot spike position array.
    post_cls_chk(avg, mode='cosamp', beta=0.5): Post-check the means of clusters from clustering function.
  # Multichannel cluster merge functions:
    get_sig_nbr(prb, lim=60): Get neighbouring channels of multichannel probe for possible same cell source.
    find_crsch_sig(cls, grp, tot, lim=0, rng=5, th=0.8): Find cross channel signal cells for multichannel probes.
    crsch_grp(res): Grouping detected cross channel cells.
Protected functions:
  _gaussian_weight(asp, psp, sigma=0.0, epsilon=2.0): Create a Gaussian weight vector centered at peak index.
  _get_wfm_smp(sig, pos, asp, psp): Get waveform samples for clustering algorithms.
"""


def _gaussian_weight(asp, psp, sigma=0.0, epsilon=2.0):
    """ Create a Gaussian weight vector centered at peak index.

    Args:
        asp (int): {>0} Anterior samples to consider
        psp (int): {>0} Posterior samples to consider
        sigma (float): {>0} Standard deviation of Gaussian in samples (default: None = 0.05 sample length)
        epsilon (float): Additional additive weight applied at peak index (default: 2.0 = double peak weight)

    Returns:
        np.ndarray: {1D-float32} Gaussian weight
    """
    num = asp + psp + 1
    sigma = sigma if sigma > 0 else num * 0.05
    dv = np.linspace(-asp / sigma, psp / sigma, num=num, endpoint=True, dtype=np.float32)  # dv = x / sigma
    wt = np.exp(-0.25 * dv ** 2) / np.sqrt(epsilon, dtype=np.float32)  # w = sqrt(Gaussian(x) / epsilon)
    wt[asp] = 1  # Normalize, peak value was emphasized with value of 2 in Gaussian
    return wt


def _get_wfm_smp(sig, pos, asp, psp):
    """ Get aligned waveform samples for clustering algorithms.

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position
        asp (int): {>0} Anterior samples to consider
        psp (int): {>0} Posterior samples to consider

    Returns:
        tuple[np.ndarray, np.ndarray]: {2D-float, 1D-int} Waveform samples and associated location
            - smp (np.ndarray): {2D-float (Num, Val)} Waveform snippets, 1D = sample number | 2D = sample value
            - loc (np.ndarray): {1D-int} Aligned sample associated location in original signal
    """
    # Check inputs
    asp = 0 if asp < 0 else asp
    psp = 0 if psp < 0 else psp
    # Set index tiles
    num = asp + psp + 1
    blk = np.arange(-asp, psp + 1, step=1, dtype=int)
    loc = np.nonzero(pos)[0]
    # Get required index
    idx = np.repeat(loc, num) + np.tile(blk, len(loc))
    idx = np.clip(idx, a_min=0, a_max=len(sig) - 1)
    # Get data
    smp = sig[idx].reshape(-1, num)
    return smp, loc


# Signal clustering functions ---------------------------------------------------------------------------------------- #

def cls_cosamp_blk(sig, pos, asp, psp, k=0.8, w=True, **kwargs):
    """ Clustering spikes by combining cosine and amplitude similarity, block mode.

    The similarity between 2 waveforms A and B is defined as: S = c * a ^ beta
    Where c = (A (dot) B) / (||A|| * ||B||), a = (2 * min(||A||, ||B||)) / (||A|| + ||B||)
    --------
    This function runs with BLOCK mode, considering the all waveform snippets in the whole recording together.
    This mode is more conservative and computes faster, but may perform worse in processing drifting samples.
    For progressive processing of the waveform snippets pairwise, use [cls_cosamp_prg].

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position
        asp (int): {>0} Anterior samples to consider
        psp (int): {>0} Posterior samples to consider
        k (float): {(0, 1)} Threshold for the correlation value (default: 0.8)
        w (bool): Gaussian weight flag (default: True)
        **kwargs: See below

    Keyword Args:
        beta (int | float): {>0} Weight for amplitude component (default: 0.5 = soft effect)
        sigma (float): {>0} Standard deviation of Gaussian in samples (default: 0.05 sample length)
        epsilon (float): Additional additive weight applied at peak index (default: 2.0 = double peak weight)

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]: Grouped waveforms and their means
            - res (list[np.ndarray]): {1D-int} Indices of grouped signals
            - avg (list[np.ndarray]): {1D-float} Mean of grouped signals
    """
    # Get keyword arguments
    beta = kwargs.get('beta', 0.5)
    sigma = kwargs.get('sigma', 0.0)
    epsilon = kwargs.get('epsilon', 2.0)
    # Get data
    smp, loc = _get_wfm_smp(sig, pos, asp, psp)
    # Get Gaussian weight
    wt = _gaussian_weight(asp, psp, sigma, epsilon) if w else np.ones(asp + psp + 1, dtype=np.float32)
    # Initialize process variables
    stp = np.arange(len(loc))
    res = []
    avg = []
    # COS-AMP composite accuracy
    nrm = np.linalg.norm(smp, ord=2, axis=1)  # 2nd order norm
    wnm = np.linalg.norm(smp * wt, ord=2, axis=1)  # 2nd order weighted norm
    while len(stp) > 0:
        # Compute result components
        dot = smp[stp] @ smp[stp[0]]
        mag = nrm[stp] * nrm[stp[0]]
        les = np.where(wnm[stp] < wnm[stp[0]], wnm[stp], wnm[stp[0]]) * 2
        acc = wnm[stp] + wnm[stp[0]]
        # Assign results
        var = (dot / mag) * (les / acc) ** beta
        grp = np.where(var >= k)[0]
        res.append(loc[stp[grp]])
        avg.append(np.mean(smp[stp[grp]], axis=0))
        # Remove grouped indices
        stp = np.delete(stp, grp)
    return res, avg


def cls_cosamp_prg(sig, pos, asp, psp, k=0.6, w=True, delta=0.2, **kwargs):
    """ Clustering spikes by combining cosine and amplitude similarity, progressive mode.

    The similarity between 2 waveforms A and B is defined as: S = c * a ^ beta
    Where c = (A (dot) B) / (||A|| * ||B||), a = (2 * min(||A||, ||B||)) / (||A|| + ||B||)
    --------
    This function runs with PROGRESSIVE mode, considering the waveform snippets step-by-step.
    This mode is more sensitive and not broadcasting, but may processing drifting samples better.
    For block processing of the waveform snippets, use [cls_cosamp_blk].

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position
        asp (int): {>0} Anterior samples to consider
        psp (int): {>0} Posterior samples to consider
        k (float): {(0, 1)} Threshold for the correlation value (default: 0.8)
        w (bool): Gaussian weight flag (default: True)
        delta (float | None): {[0, 1]} Weight for new samples
        **kwargs: See below

    Keyword Args:
        beta (int | float): {>0} Weight for amplitude component (default: 0.5 = soft effect)
        sigma (float): {>0} Standard deviation of Gaussian in samples (default: 0.05 sample length)
        epsilon (float): Additional additive weight applied at peak index (default: 2.0 = double peak weight)

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]: Grouped waveforms and their means
            - res (list[np.ndarray]): {1D-int} Indices of grouped signals
            - avg (list[np.ndarray]): {1D-float} Mean of grouped signals
    """
    # Get keyword arguments
    beta = kwargs.get('beta', 0.5)
    sigma = kwargs.get('sigma', 0.0)
    epsilon = kwargs.get('epsilon', 2.0)
    # Get data
    smp, loc = _get_wfm_smp(sig, pos, asp, psp)
    # Get Gaussian weight
    wt = _gaussian_weight(asp, psp, sigma, epsilon) if w else np.ones(asp + psp + 1, dtype=np.float32)
    # Initialize clustering history variables
    hst = smp[np.newaxis, 0]
    res = [np.array([loc[0]])]
    avg = [smp[0]]
    # Progressive COS-AMP composite accuracy
    nrm = np.linalg.norm(hst, ord=2, axis=1)
    wnm = np.linalg.norm(hst * wt, ord=2, axis=1)
    for i, s in zip(loc[1:], smp[1:]):
        nc = np.linalg.norm(s, ord=2)
        # Compute results
        dot = hst @ s
        mag = nrm * nc
        les = np.where(wnm < nc, wnm, nc) * 2
        acc = wnm + nc
        var =  (dot / mag) * (les / acc) ** beta
        # Check and assign results
        grp = np.argmax(var)
        if var[grp] < k:
            hst = np.vstack((hst, s))  # Add new history group
            res.append(np.array([i]))  # Add new result group
            avg.append(s)  # Add new average group
        else:
            res[grp] = np.append(res[grp], i)
            # Sum for all signal
            avg[grp] = avg[grp] + s
            # Update signal means
            if delta is None:
                hst[grp] = avg[grp] / len(res[grp])  # No weighting
            else:
                hst[grp] = hst[grp] * (1 - delta) + s * delta  # Weighted average for signal drifting
        # Update history norm
        nrm = np.linalg.norm(hst, ord=2, axis=1)
        wnm = np.linalg.norm(hst * wt, ord=2, axis=1)
    return res, [avg[_] / len(res[_]) for _ in range(len(res))]


def cls_crscor_blk(sig, pos, asp, psp, k=0.8):
    """ Clustering spikes by Pearson correlation coefficient, block mode.

    The similarity between 2 waveforms A and B is defined as:
    S = ((A - mean(A)) (dot) (B - mean(B))) / sqrt(sum((A - mean(A)) ^ 2) * sum((B - mean(B)) ^ 2))
    --------
    This function runs with BLOCK mode, considering the all waveform snippets in the whole recording together.
    This mode is more conservative and computes faster, but may perform worse in processing drifting samples.
    For progressive processing of the waveform snippets pairwise, use [cls_crscor_prg].

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position
        asp (int): {>0} Anterior samples to consider
        psp (int): {>0} Posterior samples to consider
        k (float): {(0, 1)} Threshold for the correlation value (default: 0.8)

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]: Grouped waveforms and their means
            - res (list[np.ndarray]): {1D-int} Indices of grouped signals
            - avg (list[np.ndarray]): {1D-float} Mean of grouped signals
    """
    # Get data
    smp, loc = _get_wfm_smp(sig, pos, asp, psp)
    # Initialize process variables
    stp = np.arange(len(loc))
    res = []
    avg = []
    # Pearson's R
    sft = (smp.T - np.mean(smp, axis=1)).T  # Sample mean shift
    sqs = np.sum(sft ** 2, axis=1)  # Sum of squares of mean shift
    while len(stp) > 0:
        # Get numerator and denominator for Pearson-R
        nmr = sft[stp] @ sft[stp[0]]
        dnm = np.sqrt(sqs[stp] * sqs[stp[0]])
        # Assign results
        var = nmr / dnm
        grp = np.where(var >= k)[0]
        res.append(loc[stp[grp]])
        avg.append(np.mean(smp[stp[grp]], axis=0))
        # Remove grouped indices
        stp = np.delete(stp, grp)
    return res, avg


def cls_crscor_prg(sig, pos, asp, psp, k=0.9, delta=0.2):
    """ Clustering spikes by Pearson correlation coefficient, progressive mode.

    The similarity between 2 waveforms A and B is defined as:
    S = ((A - mean(A)) (dot) (B - mean(B))) / sqrt(sum((A - mean(A)) ^ 2) * sum((B - mean(B)) ^ 2))
    --------
    This function runs with PROGRESSIVE mode, considering the waveform snippets step-by-step.
    This mode is more sensitive and not broadcasting, but may processing drifting samples better.
    For block processing of the waveform snippets, use [cls_crscor_blk].

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position
        asp (int): {>0} Anterior samples to consider
        psp (int): {>0} Posterior samples to consider
        k (float): {(0, 1)} Threshold for the correlation value (default: 0.8)
        delta (float | None): {[0, 1]} Weight for new samples

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]: Grouped waveforms and their means
            - res (list[np.ndarray]): {1D-int} Indices of grouped signals
            - avg (list[np.ndarray]): {1D-float} Mean of grouped signals
    """
    # Get data
    smp, loc = _get_wfm_smp(sig, pos, asp, psp)
    # Initialize clustering history variables
    hst = smp[np.newaxis, 0]
    res = [np.array([loc[0]])]
    avg = [smp[0]]
    # Progressive Pearson's R
    sft = (smp.T - np.mean(smp, axis=1)).T  # Sample mean shift
    sqs = np.sum(sft ** 2, axis=1)  # Sum of squares of mean shift
    hsf = (hst.T - np.mean(hst, axis=1)).T  # Averaged history mean shift
    hss = np.sum(hsf ** 2, axis=1)  # History sum of squares of mean shift
    for i, s, f, q in zip(loc[1:], smp[1:], sft[1:], sqs[1:]):
        # Compute results
        nmr = hsf @ f
        dnm = np.sqrt(hss * q)
        var = nmr / dnm
        # Check and assign results
        grp = np.argmax(var)
        if var[grp] < k:
            hst = np.vstack((hst, s))  # Add new history group
            res.append(np.array([i]))  # Add new result group
            avg.append(s)  # Add new average group
        else:
            res[grp] = np.append(res[grp], i)
            # Sum for all signal
            avg[grp] = avg[grp] + s
            # Update signal means
            if delta is None:
                hst[grp] = avg[grp] / len(res[grp])  # No weighting
            else:
                hst[grp] = hst[grp] * (1 - delta) + s * delta  # Weighted average for signal drifting
        # Update history variables
        hsf = (hst.T - np.mean(hst, axis=1)).T
        hss = np.sum(hsf ** 2, axis=1)
    return res, [avg[_] / len(res[_]) for _ in range(len(res))]


# Pre/Post clustering functions -------------------------------------------------------------------------------------- #

def pos_ripple_flt(sig, pos, lim=3, neg=True):
    """ Filter out ripples from one-hot spike position array.

    Args:
        sig (np.ndarray): {1D-Scalar} Input signal
        pos (np.ndarray): {1D-int} One-hot spike position
        lim (int): Minimum index difference required (default: 3)
        neg (bool): Search direction (default: True = negative peak)

    Returns:
        np.ndarray: {1D-int} Filtered one-hot spike position
    """
    # Find consecutive indices from position
    pos = pos.copy()  # Avoid overwrite
    loc = np.nonzero(pos)[0]
    chk = [i for i in np.split(loc, np.where(np.ediff1d(loc) > lim)[0] + 1) if i.size > 1]
    # Filtering
    for i in chk:
        # Find actual location
        val = i[np.argmin(sig[i])] if neg else i[np.argmax(sig[i])]
        # Set position data
        pos[i] = 0
        pos[val] = 1
    return pos


def post_cls_chk(avg, mode='cosamp', beta=0.5):
    """ Post-check the means of clusters from clustering function.

    Args:
        avg (list[np.ndarray]): Mean of clustered waveforms, returned from clustering functions
        mode (str): {'cossim', 'ampsim', 'cosamp', 'crscor'} Check mode
        beta (int | float): {>0} Weight for amplitude component, oly valid with [cosamp] (default: 0.5 = soft effect)

    Returns:
        np.ndarray: {2D-float32} Similarity matrix
    """
    res = np.zeros((len(avg), len(avg)), dtype=np.float32)
    avg = np.asarray(avg)  # Cast type
    if mode == 'cossim':
        nrm = np.linalg.norm(avg, ord=2, axis=1)  # 2nd order norm
        for i in range(len(avg) - 1):
            dot = avg[i + 1:] @ avg[i]
            mag = nrm[i + 1:] * nrm[i]
            # Assign results
            res[i, i] = 1.0
            res[i, i + 1:] = res[i + 1:, i] = dot / mag
    elif mode == 'ampsim':
        nrm = np.linalg.norm(avg, ord=2, axis=1)  # 2nd order norm
        for i in range(len(avg) - 1):
            les = np.where(nrm[i + 1:] < nrm[i], nrm[i + 1:], nrm[i]) * 2
            acc = nrm[i + 1:] + nrm[i]
            # Assign results
            res[i, i] = 1.0
            res[i, i + 1:] = res[i + 1:, i] = les / acc
    elif mode == 'cosamp':
        nrm = np.linalg.norm(avg, ord=2, axis=1)  # 2nd order norm
        for i in range(len(avg) - 1):
            dot = avg[i + 1:] @ avg[i]
            mag = nrm[i + 1:] * nrm[i]
            les = np.where(nrm[i + 1:] < nrm[i], nrm[i + 1:], nrm[i]) * 2
            acc = nrm[i + 1:] + nrm[i]
            # Assign results
            res[i, i] = 1.0
            res[i, i + 1:] = res[i + 1:, i] = (dot / mag) * (les / acc) ** beta
    elif mode == 'crscor':
        sft = (avg.T - np.mean(avg, axis=1)).T  # Sample mean shift
        sqs = np.sum(sft ** 2, axis=1)  # Sum of squares of mean shift
        for i in range(len(avg) - 1):
            nmr = sft[i + 1:] @ sft[i]
            dnm = np.sqrt(sqs[i + 1:] * sqs[i])
            # Assign results
            res[i, i] = 1.0
            res[i, i + 1:] = res[i + 1:, i] = nmr / dnm
    else:
        raise ValueError("Invalid similarity check mode, allowed mode: ['cossim', 'ampsim', 'cosamp', 'crscor'].")
    return res


# Multichannel cluster merge functions ------------------------------------------------------------------------------- #

def get_sig_nbr(prb, lim=60):
    """ Get neighbouring channels of multichannel probe for possible same cell source.

    Args:
        prb (dict): Multichannel probe geometry data
        lim (int | float): Signal distance limit (μm, inclusive) for neighbouring channel (default: 60μm)

    Returns:
        dict[int, list[int]]: Probe channel neighbours
    """
    # Extract data from probe dictionary
    tot = len(prb['site'])
    c = np.zeros(tot, dtype=int)
    x = np.zeros(tot, dtype=int)
    y = np.zeros(tot, dtype=int)
    for i, s in enumerate(prb['site']):
        c[i] = s['id']
        x[i], y[i] = s['geo']
    # Compute distance
    xx = np.subtract.outer(x, x)
    yy = np.subtract.outer(y, y)
    dist = np.sqrt(xx ** 2 + yy ** 2)
    # Arrange result
    org, tgt = np.where(dist <= lim)
    return {c[i].item(): c[tgt[org == i]].tolist() for i in range(len(prb['site']))}


def find_crsch_sig(cls, grp, tot, lim=0, rng=5, th=0.8):
    """ Find cross channel signal cells for multichannel probes.

    Args:
        cls (dict[int, list[np.ndarray]]): Multichannel spike cluster
        grp (dict[int, list[int]]): Probe channel neighbours
        tot (int): Total length of the source signal
        lim (int): Minimum number of spikes for cluster
        rng (int): Allowed range for checking overlapping (default: 5)
        th (float): {[0, 1]} Threshold rate of overlapping (default: 0.8)

    Returns:
        list[dict[str, dict[str, int] | dict[str, int]]]: Main cell and sub cell information
    """
    res = []  # INIT VAR
    # Get search indices range
    num = 2 * rng + 1
    blk = np.arange(-rng, rng + 1, step=1, dtype=int)
    # Process scan
    for g in grp:
        chs = [c for c in grp[g] if c != g]
        # Exclude empty channels
        if (len(cls[g]) == 0) or (sum([len(cls[c]) for c in chs]) == 0):
            continue
        # Get cells in main channel
        for i, ref in enumerate(cls[g]):
            # Get indices
            idx = np.repeat(ref, num) + np.tile(blk, len(ref))
            idx = np.clip(idx, a_min=0, a_max=tot - 1).reshape(-1, num, order='C')
            # Search in neighbouring channels
            for c in chs:
                # Exclude empty channel
                if len(cls[c]) == 0:
                    continue
                for j, tgt in enumerate(cls[c]):
                    # Limit minimum cluster size
                    if len(tgt) < lim:
                        continue
                    # Find match clusters
                    loc = np.zeros(tot, dtype=np.int8)
                    loc[tgt] = 1
                    match = np.sum(np.sum(loc[idx], axis=1) == 1)
                    # Compute synchronized rate
                    score = match / len(tgt)
                    if score > th:
                        res.append({'main': {'ch': g, 'id': i}, 'sub': {'ch': c, 'id': j}})
    return res


def crsch_grp(res):
    """ Grouping detected cross channel cells.

    Args:
        res (list[dict[str, dict[str, int] | dict[str, int]]]): Main cell and sub cell information

    Returns:
        list[tuple(int, int)]: Signal group list as (channel, index) pair
    """
    if not res:
        return [], []
    # Initialize variables
    pm = (res[0]['main']['ch'], res[0]['main']['id'])
    ps = (res[0]['sub']['ch'], res[0]['sub']['id'])
    grp = [[pm, ps]]
    reg = [{pm[0]: [1, 0], ps[0]: [1, 1]}]
    cnt = [[0, 0]]
    # Find grouping pairs
    for p in res[1:]:
        pm = (p['main']['ch'], p['main']['id'])
        ps = (p['sub']['ch'], p['sub']['id'])
        for i, g in enumerate(grp):
            ck_gm = pm in g
            ck_gs = ps in g
            if ck_gm or ck_gs:
                pt = ps if ck_gm else pm
                g.append(pt)
                # Count for group in the same channel
                if pt[0] in reg[i]:
                    reg[i][pt[0]] = [reg[i][pt[0]][0] + 1, reg[i][pt[0]][1]]
                    cnt[i].append(reg[i][pt[0]][0])
                else:
                    reg[i][pt[0]] = [1, len(g) - 1]
                    cnt[i].append(0)
                break
        else:
            grp.append([pm, ps])
            reg.append({pm[0]: [1, 0], ps[0]: [1, 1]})
            cnt.append([0, 0])
    # Final fittings for counting
    for i, r in enumerate(reg):
        for k in r:
            if r[k][0] > 1:
                cnt[i][r[k][1]] = 1
    return grp, cnt
