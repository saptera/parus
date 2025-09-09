# Signal process functions

import numpy as np
from scipy import signal as sig
import scipy.stats as stat
import warnings

__all__ = [
    'spk_lowpass', 'spk_highpass', 'spk_bandpass', 'spk_notch',
    'noise_white', 'noise_freq_decr', 'noise_freq_incr', 'bsl_sft_lin', 'bsl_sft_sin',
    'neuron_sig_slc', 'sig_split', 'sig_merge',
    'loc_ext_1d', 'sig_peak_zsc', 'sig_peak_fwd', 'peak_extremum',
    'bin_spk_frq', 'tpt_spk_frq', 'bin_spk_cv2', 'tpt_spk_cv2', 'tpt_kde_frq'
]
"""
Function list:
  # Neuronal signal filters:
    spk_lowpass(x, fpass, fs): Digital lowpass Butterworth filter for neurological signals.
    spk_highpass(x, fpass, fs): Digital highpass Butterworth filter for neurological signals.
    spk_bandpass(x, fpass, fs): Digital bandpass Butterworth filter for neurological signals.
    spk_notch(x, fnotch, fs): Digital notch filter for neurological signals.
  # Noise generators:
    noise_white(size, mode=0, amp=1.0, seed=None): White noise generator.
    noise_freq_decr(size, mode=0, amp=1.0, seed=None): Pink and brown (red) noise generator.
    noise_freq_incr(size, mode=0, amp=1.0, seed=None): Blue (azure) and violet (purple) noise generator.
    bsl_sft_lin(size, amp_rng): Linear baseline shifting generator.
    bsl_sft_sin(size, fs, amp_rng, freq_rng): Sinusoid baseline shifting generator.
  # Neuronal signal operations:
    neuron_sig_slc(rec, loc, rng): Slice and pad neuronal signal to individual spikes with defined length.
    sig_split(src, size, overlap=10, endpad=0.0): Split signal into a list of parts with defined size.
    sig_merge(src, overlap=10, trim=0): Merge a list of signal parts into a signal trace.
  # Feature process functions:
    loc_ext_1d(arr, allow_plateau=True): Detect local extrema of given 1D list or array.
    sig_peak_zsc(signal, lag, threshold, influence=0.0): Robust signal peak detection using z-scores.
    sig_peak_fwd(prd, th, neg=True): Signal peak detection using forward difference.
    peak_extremum(signal, peak, threshold, positive=True, sampling=None): Find the extremum point of peak detections.
    bin_spk_frq(spk, fs, t=None, g=None): Compute average firing frequency for binary (one-hot) spikes.
    tpt_spk_frq(spk, t=None, g=None, org=0, end=None): Compute average firing frequency for timestamp spikes.
    bin_spk_cv2(spk, fs, t=None, g=None): Compute squared coefficient of variation (CV2) for binary (one-hot) spikes.
    tpt_spk_cv2(spk, t=None, g=None, org=0, end=None): Compute squared coefficient of variation for timestamp spikes.
    tpt_kde_frq(spk, bw=None, **kwargs): Estimate timestamp spike firing rate using Gaussian kernels.
"""


# Neuronal signal filters -------------------------------------------------------------------------------------------- #

def spk_lowpass(x, fpass, fs):
    """ Digital lowpass Butterworth filter for neurological signals.

    Automatic design a digital lowpass Butterworth filter for neurological signals with input frequency
    and perform forward-backward digital filtering using cascaded second-order sections.
    --------
    The Butterworth filter has maximally flat frequency response in the passband.
    --------
    This function applies a linear digital filter twice, once forward and once backwards.
    The combined filter has zero phase and a filter order twice that of the original.

    Args:
        x (np.ndarray): The array of data to be filtered
        fpass (float): Passband edge frequency (Hz)
        fs (float): The sampling frequency of the digital system (Hz)

    Returns:
        np.ndarray: The filtered output with the same shape as x
    """
    ws = fpass * 1.1
    ordr, wn = sig.buttord(fpass, ws, 2, 50, False, fs)
    sos = sig.butter(ordr, wn, 'lowpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_highpass(x, fpass, fs):
    """ Digital highpass Butterworth filter for neurological signals.

    Automatic design a digital highpass Butterworth filter for neurological signals with input frequency
    and perform forward-backward digital filtering using cascaded second-order sections.
    --------
    The Butterworth filter has maximally flat frequency response in the passband.
    --------
    This function applies a linear digital filter twice, once forward and once backwards.
    The combined filter has zero phase and a filter order twice that of the original.

    Args:
        x (np.ndarray): The array of data to be filtered
        fpass (float): Passband edge frequency (Hz)
        fs (float): The sampling frequency of the digital system (Hz)

    Returns:
        np.ndarray: The filtered output with the same shape as x
    """
    ws = fpass * 0.9
    ordr, wn = sig.buttord(fpass, ws, 2, 50, False, fs)
    sos = sig.butter(ordr, wn, 'highpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_bandpass(x, fpass, fstop, fs):
    """ Digital bandpass Butterworth filter for neurological signals.

    Automatic design a digital bandpass Butterworth filter for neurological signals with input frequency
    and perform forward-backward digital filtering using cascaded second-order sections.
    --------
    The Butterworth filter has maximally flat frequency response in the passband.
    --------
    This function applies a linear digital filter twice, once forward and once backwards.
    The combined filter has zero phase and a filter order twice that of the original.

    Args:
        x (np.ndarray): The array of data to be filtered
        fpass (float): Passband edge frequency (Hz)
        fstop (float): Stopband edge frequency (Hz)
        fs (float): The sampling frequency of the digital system (Hz)

    Returns:
        np.ndarray: The filtered output with the same shape as x
    """
    wp = [fpass, fstop]
    ws = [fpass * 0.9, fstop * 1.1]
    ordr, wn = sig.buttord(wp, ws, 5, 40, False, fs)
    sos = sig.butter(ordr, wn, 'bandpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_notch(x, fnotch, fs):
    """ Digital notch filter for neurological signals.

    Automatic design a digital notch filter for neurological signals with input frequency
    and perform forward-backward digital filtering.
    --------
    A notch filter is a band-stop filter with a narrow bandwidth (high quality factor).
    It rejects a narrow frequency band and leaves the rest of the spectrum little changed.
    --------
    This function applies a linear digital filter twice, once forward and once backwards.
    The combined filter has zero phase and a filter order twice that of the original.

    Args:
        x (np.ndarray): The array of data to be filtered
        fnotch (float): Frequency to remove from a signal (Hz)
        fs (float): The sampling frequency of the digital system (Hz)

    Returns:
        np.ndarray: The filtered output with the same shape as x
    """
    q = fnotch / 2
    b, a = sig.iirnotch(fnotch, q, fs)
    y = sig.filtfilt(b, a, x)
    return y


# Noise generators --------------------------------------------------------------------------------------------------- #

def noise_white(size, mode=0, amp=1.0, seed=None):
    """ White noise generator.

    White noise is a signal, with a flat frequency spectrum when plotted as a linear function of frequency.
    The signal has equal power in any band of a given bandwidth (power spectral density).

    Args:
        size (int): Number of samples to be generated
        mode (int): {0 | 1} White noise random distribution type. (default: 0 = UNIFORM)
            - 0 = UNIFORM distribution
            - 1 = GAUSSIAN distribution
        amp (float): Amplitude of noise (default: 1.0 -> [-0.5 0.5))
        seed (int | None): Random seed used to initialize the pseudo-random number generator

    Returns:
        np.ndarray: {1D-scalar} Generated white noise
    """
    # Set random status
    ran = np.random.RandomState(seed)
    # Generate noise signal
    if mode == 0:
        noise = ran.rand(size)
    elif mode == 1:
        noise = ran.randn(size)
    else:
        print("Mode error: mode should be either 0 or 1, got %d instead" % mode)
        return None
    # Normalize output
    noise = noise * amp - amp / 2
    return noise


def noise_freq_decr(size, mode=0, amp=1.0, seed=None):
    """ Pink and brown (red) noise generator.

    Pink noise's power density decreases 3 dB per octave
    with increasing frequency (density proportional to 1/f) finite frequency range.
    The frequency spectrum of pink noise is linear in logarithmic scale;
    it has equal power in bands that are proportionally wide.
    --------
    Brown noise's power density decreases 6 dB per octave
    with increasing frequency (density proportional to 1/f^2) finite frequency range.

    Args:
        size (int): Number of samples to be generated
        mode (int): {0 | 1} White noise random distribution type (default: 0 = PINK)
            - 0 = PINK noise generation
            - 1 = BROWN (RED) noise generation
        amp (float): Amplitude of noise (default: 1.0 -> [-0.5 0.5))
        seed (int | None): Random seed used to initialize the pseudo-random number generator

    Returns:
        np.ndarray: {1D-scalar} Generated noise
    """
    # Set random status
    ran = np.random.RandomState(seed)
    # Generate noise signal
    f = ran.randn(int(np.ceil(size / 2)) + 1) + 1j * ran.randn(int(np.ceil(size / 2)) + 1)
    if mode == 0:
        s = np.sqrt(np.arange(len(f)) + 1)    # Filter, avoid ZeroDivisionError by [+1]
    elif mode == 1:
        s = np.arange(len(f)) + 1    # Filter, avoid ZeroDivisionError by [+1]
    else:
        print("Mode error: mode should be either 0 or 1, got %d instead" % mode)
        return None
    noise = (np.fft.irfft(f / s)).real
    noise = noise[:-1] if size % 2 else noise
    # Calculate transform parameters
    amp *= ran.rand() * 0.1 + 0.9    # Get a random amplitude
    cet = ran.rand() * 0.1    # Get a random center
    rate = amp / (noise.max() - noise.min())
    const = (amp * noise.min()) / (noise.max() - noise.min()) + (amp / 2 - cet)
    # Normalize output
    noise = noise * rate - const
    return noise


def noise_freq_incr(size, mode=0, amp=1.0, seed=None):
    """ Blue (azure) and violet (purple) noise generator.

    Blue noise's power density increases 3 dB per octave,
    with increasing frequency (density proportional to f) over a finite frequency range.
    --------
    Violet noise's power density increases 6 dB per octave,
    with increasing frequency (density proportional to f^2) over a finite frequency range.

    Args:
        size (int): Number of samples to be generated
        mode (int): {0 | 1} White noise random distribution type (default: 0 = BLUE)
            - 0 = BLUE (AZURE) noise generation
            - 1 = VIOLET (PURPLE) noise generation
        amp (float): Amplitude of noise (default: 1.0 -> [-0.5 0.5))
        seed (int | None): Random seed used to initialize the pseudo-random number generator

    Returns:
        np.ndarray: {1D-scalar} Generated noise
    """
    # Set random status
    ran = np.random.RandomState(seed)
    # Generate noise signal
    f = ran.randn(int(np.ceil(size / 2)) + 1) + 1j * ran.randn(int(np.ceil(size / 2)) + 1)
    if mode == 0:
        s = np.sqrt(np.arange(len(f)))    # Filter, avoid ZeroDivisionError by [+1]
    elif mode == 1:
        s = np.arange(len(f))    # Filter, avoid ZeroDivisionError by [+1]
    else:
        print("Mode error: mode should be either 0 or 1, got %d instead" % mode)
        return None
    noise = (np.fft.irfft(f * s)).real
    noise = noise[:-1] if size % 2 else noise
    # Calculate transform parameters
    amp *= ran.rand() * 0.1 + 0.9    # Get a random amplitude
    cet = ran.rand() * 0.1    # Get a random center
    rate = amp / (noise.max() - noise.min())
    const = (amp * noise.min()) / (noise.max() - noise.min()) + (amp / 2 - cet)
    # Normalize output
    noise = noise * rate - const
    return noise


def bsl_sft_lin(size, amp_rng):
    """ Linear baseline shifting generator.

    Args:
        size (int): Number of samples to be generated
        amp_rng (tuple[int | float, int | float]): Randomize range of baseline shift amplitude

    Returns:
        np.ndarray: {1D-scalar} Generated baseline shift
    """
    # Compute random values for periodic signal
    amp_a, amp_p = np.random.uniform(amp_rng[0], amp_rng[1], 2)
    # Compute randomized signal
    sft = np.linspace(amp_a, amp_p, size)
    return sft


def bsl_sft_sin(size, fs, amp_rng, freq_rng):
    """ Sinusoid baseline shifting generator.

    Args:
        size (int): Number of samples to be generated
        fs (int | float): The sampling frequency of the digital system (Hz)
        amp_rng (tuple[int | float, int | float]): Randomize range of baseline shift amplitude
        freq_rng (tuple[int | float, int | float]): Randomize range of baseline shift frequency (Hz)

    Returns:
        np.ndarray: {1D-scalar} Generated baseline shift
    """
    # Compute random values for periodic signal
    amp = np.random.uniform(amp_rng[0], amp_rng[1])
    freq = np.random.uniform(freq_rng[0], freq_rng[1]) / fs * 2 * np.pi
    phase = np.random.uniform(0., 2 * np.pi)
    # Compute randomized signal
    x = np.arange(0, size, 1) * freq + phase
    sft = amp * np.sin(x)
    return sft


# Neuronal signal operations ----------------------------------------------------------------------------------------- #

def neuron_sig_slc(rec, loc, rng):
    """ Slice and pad neuronal signal to individual spikes with defined length.

    Args:
        rec (np.ndarray): {1D-scalar} Recorded neuronal signal
        loc (list[int]): Detected spike peak locations, stored as index of iterable [rec]
        rng (list[tuple[int, int]]): Length of data points for each [loc], in order (anterior, posterior)

    Returns:
        list[np.ndarray]: {1D-scalar, n*rng} Sliced signals
    """
    # Extract and convert data from inputs
    tot_spk = len(loc)
    if tot_spk == 0:
        return None
    else:
        srt_idx = np.argsort(loc)
        sig_abs = np.abs(rec)
    # INIT VAR; spike list, list of NumPy 1D-array must be adopted as spikes may not have the same length
    spk_lst = []

    # Get slicing parameters for the first spike
    curr_loc_a = loc[srt_idx[0]] - rng[srt_idx[0]][0]  # _a = anterior, same for all variables ends with [_a] below
    curr_loc_p = loc[srt_idx[0]] + rng[srt_idx[0]][1]  # _p = posterior, same for all variables ends with [_p] below
    next_loc_a = loc[srt_idx[1]] - rng[srt_idx[1]][0]
    # Check anterior padding
    if curr_loc_a < 0:
        curr_pad_a = np.full(abs(curr_loc_a), rec[0])
        curr_loc_a = 0
    else:
        curr_pad_a = []
    # Check posterior padding
    if curr_loc_p > next_loc_a:
        slc_a = max(loc[srt_idx[0]], next_loc_a)
        slc_p = min(curr_loc_p, loc[srt_idx[1]])
        slc_idx = slc_a + np.argmin(sig_abs[slc_a:slc_p])
        curr_pad_p = np.full(curr_loc_p - slc_idx, rec[slc_idx])
        curr_loc_p = slc_idx
        # Get anterior padding values for next spike
        next_pad_a = np.full(slc_idx - next_loc_a, rec[slc_idx])
        next_loc_a = slc_idx
    else:
        curr_pad_p = []
        next_pad_a = []
    # Store spike
    spk_lst.append(np.concatenate((curr_pad_a, rec[curr_loc_a:curr_loc_p], curr_pad_p)))

    # Get slicing parameters for intermediate spikes
    if tot_spk == 1:
        return spk_lst
    elif tot_spk > 2:
        for i in range(1, len(srt_idx) - 1):
            # Transfer anterior padding info from last iteration
            curr_loc_a = next_loc_a
            curr_pad_a = next_pad_a
            # Check posterior padding for current iteration
            curr_loc_p = loc[srt_idx[i]] + rng[srt_idx[i]][1]
            next_loc_a = loc[srt_idx[i + 1]] - rng[srt_idx[i + 1]][0]
            if curr_loc_p > next_loc_a:
                slc_a = max(loc[srt_idx[i]], next_loc_a)
                slc_p = min(curr_loc_p, loc[srt_idx[i + 1]])
                slc_idx = slc_a + np.argmin(sig_abs[slc_a:slc_p])
                curr_pad_p = np.full(curr_loc_p - slc_idx, rec[slc_idx])
                curr_loc_p = slc_idx
                # Get anterior padding values for next spike
                next_pad_a = np.full(slc_idx - next_loc_a, rec[slc_idx])
                next_loc_a = slc_idx
            else:
                curr_pad_p = []
                next_pad_a = []
            # Store spike
            spk_lst.append(np.concatenate((curr_pad_a, rec[curr_loc_a:curr_loc_p], curr_pad_p)))

    # Get slicing parameters for the last spike
    curr_loc_p = loc[srt_idx[-1]] + rng[srt_idx[-1]][1]
    if curr_loc_p >= len(rec):
        curr_pad_p = np.full(curr_loc_p - len(rec) + 1, rec[-1])
        curr_loc_p = len(rec) - 1
    else:
        curr_pad_p = []
    # Store spike, direct use anterior padding info from last iteration as no next check required
    spk_lst.append(np.concatenate((next_pad_a, rec[next_loc_a:curr_loc_p], curr_pad_p)))
    return spk_lst


def sig_split(src, size, overlap=10, endpad=0.0):
    """ Split signal into a list of parts with defined size.

    Args:
        src (np.ndarray | list[int | float]): {1D-scalar} Input signal
        size (int): Sample size of each signal part
        overlap (int): Overlapping sample size between 2 consecutive parts (default: 10)
        endpad (int | float): Padding value of the last part to the target size (default: 0)

    Returns:
        list[np.ndarray]: {1D-scalar, n*size} Output list of split signal
    """
    if not isinstance(src, np.ndarray):
        src = np.asarray(src)
    tot = len(src)
    dst = []  # INIT VAR
    pad = []  # INIT VAR
    for c, i in enumerate(range(0, tot, size - overlap)):
        ep = i + size
        # Check if pad needed
        if ep > tot:
            pad.append(c)
        # Slice data
        dst.append(src[i:ep])
    # Check the end padding
    for c in pad:
        dst[c] = np.append(dst[c], np.full(size - len(dst[c]), endpad, dtype=dst[c].dtype))
    return dst


def sig_merge(src, overlap=10, trim=0):
    """ Merge a list of signal parts into a signal trace.

    Args:
        src (list[np.ndarray | list[int | float]] | np.ndarray): {1D(n * size) | 2D(n, size)} Input list of split signal
        overlap (int): Overlapping sample size between 2 consecutive parts (default: 10)
        trim (int): Samples to remove at the end of merged signal

    Returns:
        np.ndarray: {1D-scalar} Output merged signal
    """
    # Get sizes
    size = len(src[0])
    lead = size - overlap
    tot_len = len(src) * (size - overlap) + overlap
    # Initialize arrays
    dst = np.zeros(tot_len, dtype=type(src[0][0]))
    # Process merge
    if overlap > 0:
        crs = src[0][:overlap]
        # Process merge
        pos = [n * (size - overlap) for n in range(len(src))]
        for i, p in enumerate(pos):
            dst[p:p+overlap] = np.add(src[i][:overlap], crs) / 2
            dst[p+overlap:p+lead] = src[i][overlap:-overlap]
            crs = src[i][-overlap:]
        # Process ending and return
        dst[-overlap:] = crs
    else:
        dst = np.asarray(src).flatten(order='C')
    return dst[:tot_len-trim]


# Feature process functions ------------------------------------------------------------------------------------------ #

def loc_ext_1d(arr, allow_plateau=True):
    """ Detect local extrema of given 1D list or array.

    Args:
        arr (list[int | float] | np.ndarray): Input array
        allow_plateau (bool): Allow to detect first index of extrema with plateau (default: True)

    Returns:
        dict[str, np.ndarray]: Detected local extrema
            - max (np.ndarray): Local maxima
            - min (np.ndarray): Local minima
    """
    if allow_plateau:
        dif = np.ediff1d(arr, to_begin=1)  # Padding 1 to the beginning, forcing keep first value
        idx = np.nonzero(dif)[0]  # Mask consecutive repeat values, allowing plateau
        cmp = arr[idx]
    else:
        idx = np.arange(len(arr))
        cmp = arr
    # Check local maximum (peaks) and minimum (dips)
    mx = np.pad((cmp[1:-1] > cmp[0:-2]) * (cmp[1:-1] > cmp[2:]), pad_width=1, mode='edge')
    mi = np.pad((cmp[1:-1] < cmp[0:-2]) * (cmp[1:-1] < cmp[2:]), pad_width=1, mode='edge')
    return {'max': idx[mx], 'min': idx[mi]}


def sig_peak_zsc(signal, lag, threshold, influence=0.0):
    """ Robust signal peak detection using z-scores.
        Inspired from J.P.G. van Brakel [https://stackoverflow.com/a/22640362/6029703]

    Args:
        signal (list[int | float] | np.ndarray): Input signal
        lag (int): The length of data will be smoothed, larger lags should be included for more stationary data
        threshold (int | float): Threshold of standard deviations from the moving mean above to classify as peak
        influence (float): {0 ~ 1} The influence of signals on the algorithm's detection threshold (default: 0.0)
            - 0: Signals have no influence on the threshold, implicitly assume signal is stationary
            - 1: Signals have full influence of normal data points

    Returns:
        np.ndarray: {1D-int} Detected peak indices. 1 = positive peak, -1 = negative peak, 0 = no peak
    """
    # Initialize operational series
    peak = np.zeros_like(signal, dtype=int)
    filt = np.concatenate((signal[:lag][::-1], signal))
    # Compute sliding window initial values
    win_fac = 1 / lag
    lin_sum = np.sum(filt[:lag], axis=None)
    sqr_sum = np.sum(np.square(filt[:lag]), axis=None)

    for i, s in enumerate(signal):
        # Update filter
        avg = lin_sum * win_fac
        std = np.sqrt(abs(sqr_sum * win_fac - avg * avg))  # abs() to avoid negative lavue caused by precision loss
        # Peak detection with influence
        if abs(s - avg) > threshold * std:
            peak[i] = 1 if s > avg else -1
            filt[i + lag] = influence * s + (1 - influence) * filt[i + lag - 1]
        # Update sliding window sums
        lin_sum = lin_sum + filt[i + lag] - filt[i]
        sqr_sum = sqr_sum + (filt[i + lag] + filt[i]) * (filt[i + lag] - filt[i])
    return peak


def sig_peak_fwd(prd, th, neg=True):
    """ Signal peak detection using forward difference.

    Args:
        prd (list[int | float] | np.ndarray): {1D-Scalar} Input prediction results
        th (int | float): Peak detection threshold
        neg (bool): Negative peak flag -- True = peak less than threshold, False = peak greater than threshold

    Returns:
        np.ndarray: {int} Detected peak indices -- 1 = peak, 0 = no peak
    """
    diff = np.sign(np.ediff1d(prd, to_end=prd[-1:]))
    diff[1:] = diff[:-1] + diff[1:]
    det = np.where((prd < th) & (diff == 0), 1, 0) if neg else np.where((prd > th) & (diff == 0), 1, 0)
    return det.astype(np.int8)


def peak_extremum(signal, peak, threshold, positive=True, sampling=None):
    """ Find the extremum point of peak detections.

    Args:
        signal (list[int | float] | np.ndarray): Input signal
        peak (list[int] | np.ndarray): {1D-int} Detected peak (1 = positive peak, -1 = negative peak, 0 = no peak)
        threshold (int | float): Limit for the extremum value
        positive (bool): Flag to define the peak direction (default: True)
        sampling (int | None): Number of flanking samples to extract around the extremum (default: None = No sampling)

    Returns:
        tuple[np.ndarray, np.ndarray | None]: {1D-int} Peak extremum indices; {2D-float | None} Signal samples
    """
    val = 1 if positive else -1
    th = abs(threshold)
    # Detect extremum position
    det = np.where(peak == val)[0]
    grp = np.split(det, np.where(np.diff(det) != 1)[0] + 1)
    pos = [i[np.argmax(signal[i])] for i in grp if np.max(signal[i]) * val > th]
    # Sampling signal and return
    if sampling is None:
        return np.array(pos, dtype=int), None
    else:
        rng = [range(i - sampling, i + sampling + 1) for i in pos]
        rng = np.clip(rng, a_min=0, a_max=len(signal) - 1)
        smp = signal[rng]
        return np.array(pos, dtype=int), smp


def bin_spk_frq(spk, fs, t=None, g=None):
    """ Compute average firing frequency for binary (one-hot) spikes.

    Args:
        spk (list[int | float] or np.ndarray): {1D} One-hot spike event data
        fs (int | float): Data sampling frequency (Hz)
        t (int | float | None): Time window to compute feature (default: None = compute whole trace)
        g (int | float | None): Time sampling step to compute feature (default: None = the same as [t])

    Returns:
        float | list[float]: Average firing frequency (Hz) of spike data
    """
    if len(spk) < 2:
        warnings.warn("Size too small to compute frequency, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    else:
        if t is None:
            pos = np.where(spk > 0)[0]
            return len(pos) / len(spk) * fs
        else:
            win = round(fs * t, ndigits=None)
            stp = win if g is None else round(fs * g, ndigits=None)
            smp = np.lib.stride_tricks.sliding_window_view(spk, win)[::stp]
            return (np.sum(smp, axis=-1) / t).tolist()


def tpt_spk_frq(spk, t=None, g=None, org=0, end=None):
    """ Compute average firing frequency for timestamp spikes.

    Args:
        spk (list[int | float] or np.ndarray): {1D} Spike event data by timestamp
        t (int | float | None): Time window to compute feature (default: None = compute whole trace)
        g (int | float | None): Time sampling step to compute feature (default: None = the same as [t])
        org (int | float | None): Beginning of timestamps, set None to use first value of [spk] (default: 0)
        end (int | float | None): The end time of timestamps (default: None = use last value of [spk])

    Returns:
        float | list[float]: Average firing frequency (Hz) of spike data
    """
    if len(spk) < 2:
        warnings.warn("Size too small to compute frequency, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    # Sort timestamps for valid results
    tpt = np.sort(spk, kind='stable')
    # Get time range
    org = tpt[0].item() if org is None else org
    end = tpt[-1].item() if end is None else end
    if end <= org:
        warnings.warn("Timestamp origin must be GREATER than end, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    # Compute frequency
    if t is None:
        return tpt.size / (end - org)
    else:
        stp = t if g is None else g
        wini = np.arange(org, end, stp)
        wstp = wini + t
        wstp[-1] = wstp[-1] + 0.0001  # Make sure the last timestamp is included
        cnt = [(np.where((tpt >=wini[i]) & (tpt < wstp[i]))[0]).size for i in range(len(wini))]
        return np.divide(cnt, t).tolist()


def bin_spk_cv2(spk, fs, t=None, g=None):
    """ Compute squared coefficient of variation (CV2) for binary (one-hot) spikes.

    Args:
        spk (list[int | float] | np.ndarray): {1D} One-hot spike event data
        fs (int | float): Data sampling frequency (Hz)
        t (int | float | None): Time window to compute (default: None = compute whole trace)
        g (int | float | None): Time sampling step to compute feature (default: None = the same as [t])

    Returns:
        float | list[float]: Squared coefficient of variation (CV2) of spike data
    """
    pos = np.nonzero(spk)[0]
    if len(pos) < 3:
        warnings.warn("Not enough spikes detected to compute CV2, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    else:
        if t is None:
            gap = np.ediff1d(pos) / fs
            return 2 * np.mean(np.absolute(np.ediff1d(gap)) / (gap[:-1] + gap[1:])).item()
        else:
            # Sampling
            win = round(fs * t, ndigits=None)
            stp = win if g is None else round(fs * g, ndigits=None)
            smp = np.lib.stride_tricks.sliding_window_view(spk, win)[::stp]
            pos = [np.nonzero(smp[i])[0] for i in range(smp.shape[0])]
            # Check and compute
            res = []  # INIT VAR
            for p in pos:
                if len(p) < 3:
                    res.append(float('nan'))
                else:
                    gap = np.ediff1d(p) / fs
                    res.append(2 * np.mean(np.absolute(np.ediff1d(gap)) / (gap[:-1] + gap[1:])).item())
            return res


def tpt_spk_cv2(spk, t=None, g=None, org=0, end=None):
    """ Compute squared coefficient of variation (CV2) for timestamp spikes.

    Args:
        spk (list[int | float] or np.ndarray): {1D} Spike event data by timestamp
        t (int | float | None): Time window to compute feature (default: None = compute whole trace)
        g (int | float | None): Time sampling step to compute feature (default: None = the same as [t])
        org (int | float | None): Beginning of timestamps, set None to use first value of [spk] (default: 0)
        end (int | float | None): End of timestamps, set None to use last value of [spk] (default: None)

    Returns:
        float | list[float]: Squared coefficient of variation (CV2) of spike data
    """
    if len(spk) < 3:
        warnings.warn("Not enough spikes detected to compute CV2, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    # Sort timestamps for valid results
    tpt = np.sort(spk, kind='stable')
    # Compute CV2
    if t is None:
        gap = np.ediff1d(tpt)
        return 2 * np.mean(np.absolute(np.ediff1d(gap)) / (gap[:-1] + gap[1:])).item()
    else:
        # Get time range
        org = tpt[0].item() if org is None else org
        end = tpt[-1].item() if end is None else end
        if end <= org:
            warnings.warn("Timestamp origin must be GREATER than end, NaN returned.", RuntimeWarning, stacklevel=2)
            return float('nan')
        # Compute sample windows
        stp = t if g is None else g
        wini = np.arange(org, end, stp)
        wstp = wini + t
        wstp[-1] = wstp[-1] + 0.0001  # Make sure the last timestamp is included
        # CV2 with samples
        pos = [tpt[np.where((tpt >=wini[i]) & (tpt < wstp[i]))[0]] for i in range(len(wini))]
        res = []  # INIT VAR
        for p in pos:
            if len(p) < 3:
                res.append(float('nan'))
            else:
                gap = np.ediff1d(p)
                res.append(2 * np.mean(np.absolute(np.ediff1d(gap)) / (gap[:-1] + gap[1:])).item())
        return res


def tpt_kde_frq(spk, bw=None, **kwargs):
    """ Estimate timestamp spike firing rate using Gaussian kernels.

    Args:
        spk (list[int | float] or np.ndarray): {1D} Spike event data by timestamp
        bw (int | float | str | function | None): The method used to calculate the estimator bandwidth (default: None)
            - (int | float): Value will be used directly as bandwidth factor
            - {'scott'}: Auto compute Scott's factor
            - {'silverman'}: Auto compute Silverman's factor
            - (function): Callable take a gaussian_kde instance as only parameter and return a scalar
            - {None}: Using 'scott'

   Keyword Args:
       smp (list[int | float] or np.ndarray): {1D} Resample data by timestamp, ignore [org] [end] [num] if defined
       org (int | float | None): Beginning of timestamps, use first value of [spk] if undefined
       end (int | float | None): End of timestamps, use last value of [spk] if undefined
       num (int): Number of samples to compute, 1000 if undefined

    Returns:
        np.ndarray: Firing rate estimations
    """
    tpt = np.sort(spk, kind='stable')
    # Get sampling range
    smp = kwargs.get('smp', None)
    if smp is None:
        org = kwargs.get('org', tpt[0])
        end = kwargs.get('end', tpt[-1])
        num = kwargs.get('num', 1000)
        smp = np.linspace(org, end, num)
    # Compute Gaussian kernel-density estimate
    kde = stat.gaussian_kde(tpt, bw_method=bw, weights=None)
    est = kde(smp) * tpt.size
    return est
