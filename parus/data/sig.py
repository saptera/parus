# -*- coding: utf-8 -*-

"""Signal process module

Digital filters, noise generators, signal slicing/merging helpers, peak detectors, and spike-train feature
extractors used across the simulation, training, and analysis pipelines.
"""

import numpy as np
import scipy.signal as sig
import scipy.stats as stat
import warnings

__package__ = 'parus.data'
__name__ = 'parus.data.sig'

__all__ = [
    'spk_lowpass', 'spk_highpass', 'spk_bandpass', 'spk_notch',
    'noise_white', 'noise_freq_decr', 'noise_freq_incr', 'bsl_sft_lin', 'bsl_sft_sin',
    'neuron_sig_slc', 'sig_split', 'sig_merge',
    'loc_ext_1d', 'sig_peak_zsc', 'sig_peak_fwd', 'peak_extremum', 'peak_reloc_ex',
    'bin_spk_frq', 'tpt_spk_frq', 'bin_spk_isi', 'tpt_spk_isi',
    'bin_spk_cv', 'tpt_spk_cv', 'bin_spk_cv2', 'tpt_spk_cv2', 'tpt_kde_frq'
]
"""
Public function list:

- Neural signal filters:

    - spk_lowpass(x, fpass, fs)                          : Digital low-pass Butterworth filter
    - spk_highpass(x, fpass, fs)                         : Digital high-pass Butterworth filter
    - spk_bandpass(x, fpass, fstop, fs)                  : Digital band-pass Butterworth filter
    - spk_notch(x, fnotch, fs)                           : Digital notch filter

- Noise generators:

    - noise_white(size, mode, amp, seed)                 : White noise generator
    - noise_freq_decr(size, mode, amp, seed)             : Pink and brown (red) noise generator
    - noise_freq_incr(size, mode, amp, seed)             : Blue (azure) and violet (purple) noise generator
    - bsl_sft_lin(size, amp_rng)                         : Linear baseline-shift generator
    - bsl_sft_sin(size, fs, amp_rng, freq_rng)           : Sinusoid baseline-shift generator

- Neural signal operations:

    - neuron_sig_slc(rec, loc, rng)                      : Slice and pad neural signal at spike locations
    - sig_split(src, size, overlap, endpad)              : Split a signal into overlapping fixed-size parts
    - sig_merge(src, overlap, trim)                      : Merge a list of signal parts into a single trace

- Peak processing:

    - loc_ext_1d(arr, allow_plateau)                     : Detect local extrema of a 1D array
    - sig_peak_zsc(signal, lag, th, influence)           : Robust peak detection using z-scores
    - sig_peak_fwd(signal, th, neg)                      : Peak detection by forward difference and threshold
    - peak_extremum(signal, peak, th, neg, smp)          : Find the extremum point of z-score peak detections
    - peak_reloc_ex(signal, peak, th, neg, smp)          : Relocate one-hot peaks to the nearest local extremum

- Feature processing:

    - bin_spk_frq(spk, fs, t, g)                         : Average firing frequency for one-hot spikes
    - tpt_spk_frq(spk, t, g, org, end)                   : Average firing frequency for timestamp spikes
    - bin_spk_isi(spk, fs, t, g, lst)                    : Inter-spike interval (ISI) for one-hot spikes
    - tpt_spk_isi(spk, t, g, org, end, lst)              : ISI for timestamp spikes
    - bin_spk_cv(spk, fs, t, g, ddof)                    : Coefficient of variation (CV) for one-hot spikes
    - tpt_spk_cv(spk, t, g, org, end, ddof)              : CV for timestamp spikes
    - bin_spk_cv2(spk, fs, t, g)                         : 2-point coefficient of variation (CV2) for one-hot spikes
    - tpt_spk_cv2(spk, t, g, org, end)                   : 2-point coefficient of variation for timestamp spikes
    - tpt_kde_frq(spk, bw, **kwargs)                     : Estimate timestamp spike firing rate using Gaussian kernels

Private helpers:

- __bin_smp(spk, fs, t, g)                               : Time-window sampling for one-hot spikes
- __tpt_rng(spk, org, end)                               : Time-range setup for timestamp spikes
- __tpt_smp(tpt, t, g, org, end)                         : Time-window sampling for timestamp spikes
"""


# Neuronal signal filters -------------------------------------------------------------------------------------------- #

def spk_lowpass(x, fpass, fs):
    """Apply a digital low-pass Butterworth filter to a neural signal.

    Designs a Butterworth filter from the input passband edge using :func:`scipy.signal.buttord` and applies
    it as a forward-backward filter in cascaded second-order-section form via :func:`scipy.signal.sosfiltfilt`.
    The resulting filter has zero phase and an effective order twice that of the underlying design.

    Args:
        x (np.ndarray): Input signal to filter
        fpass (float): Passband edge frequency in Hz
        fs (float): Sampling frequency of the input signal in Hz

    Returns:
        np.ndarray: Filtered signal with the same shape as ``x``
    """
    ws = fpass * 1.1
    ordr, wn = sig.buttord(fpass, ws, 2, 50, False, fs)
    sos = sig.butter(ordr, wn, 'lowpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_highpass(x, fpass, fs):
    """Apply a digital high-pass Butterworth filter to a neural signal.

    Designs a Butterworth filter from the input passband edge using :func:`scipy.signal.buttord` and applies
    it as a forward-backward filter in cascaded second-order-section form via :func:`scipy.signal.sosfiltfilt`.
    The resulting filter has zero phase and an effective order twice that of the underlying design.

    Args:
        x (np.ndarray): Input signal to filter
        fpass (float): Passband edge frequency in Hz
        fs (float): Sampling frequency of the input signal in Hz

    Returns:
        np.ndarray: Filtered signal with the same shape as ``x``
    """
    ws = fpass * 0.9
    ordr, wn = sig.buttord(fpass, ws, 2, 50, False, fs)
    sos = sig.butter(ordr, wn, 'highpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_bandpass(x, fpass, fstop, fs):
    """Apply a digital band-pass Butterworth filter to a neural signal.

    Designs a Butterworth filter from the input passband and stopband edges using :func:`scipy.signal.buttord`
    and applies it as a forward-backward filter in cascaded second-order-section form via
    :func:`scipy.signal.sosfiltfilt`. The resulting filter has zero phase and an effective order twice that
    of the underlying design.

    Args:
        x (np.ndarray): Input signal to filter
        fpass (float): Lower passband edge frequency in Hz
        fstop (float): Upper passband edge frequency in Hz
        fs (float): Sampling frequency of the input signal in Hz

    Returns:
        np.ndarray: Filtered signal with the same shape as ``x``
    """
    wp = [fpass, fstop]
    ws = [fpass * 0.9, fstop * 1.1]
    ordr, wn = sig.buttord(wp, ws, 5, 40, False, fs)
    sos = sig.butter(ordr, wn, 'bandpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_notch(x, fnotch, fs):
    """Apply a digital notch filter (narrow band-stop) to a neural signal.

    Designs a single-frequency notch filter via :func:`scipy.signal.iirnotch` and applies it as a
    forward-backward filter via :func:`scipy.signal.filtfilt`. The resulting filter has zero phase and an
    effective order twice that of the underlying design.

    Args:
        x (np.ndarray): Input signal to filter
        fnotch (float): Frequency to remove from the signal in Hz
        fs (float): Sampling frequency of the input signal in Hz

    Returns:
        np.ndarray: Filtered signal with the same shape as ``x``
    """
    q = fnotch / 2
    b, a = sig.iirnotch(fnotch, q, fs)
    y = sig.filtfilt(b, a, x)
    return y


# Noise generators --------------------------------------------------------------------------------------------------- #

def noise_white(size, mode=0, amp=1.0, seed=None):
    """Generate a white-noise signal.

    White noise has a flat power spectrum: equal power in any frequency band of a given bandwidth. The output
    is centred at zero with peak-to-peak amplitude ``amp``.

    Args:
        size (int): Number of samples to generate
        mode (int): Distribution selector (default: ``0``)

            - ``0``: uniform distribution
            - ``1``: Gaussian distribution

        amp (float): Peak-to-peak amplitude of the noise; the output spans ``[-amp/2, amp/2)`` (default: ``1.0``)
        seed (int | None): Random seed for the pseudo-random number generator (default: ``None``)

    Returns:
        np.ndarray | None: {1D-scalar} Generated white noise; :data:`None` when ``mode`` is invalid
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
    """Generate pink (1/f) or brown (1/f^2) noise.

    Pink noise's power density decreases at 3 dB per octave (density proportional to ``1/f``); brown noise's
    decreases at 6 dB per octave (density proportional to ``1/f^2``). Both spectra are produced over a finite
    frequency range by spectral shaping of a complex Gaussian draw.

    Args:
        size (int): Number of samples to generate
        mode (int): Noise colour selector (default: ``0``)

            - ``0``: pink noise generation
            - ``1``: brown (red) noise generation

        amp (float): Peak-to-peak amplitude of the noise; the output spans ``[-amp/2, amp/2)`` (default: ``1.0``)
        seed (int | None): Random seed for the pseudo-random number generator (default: ``None``)

    Returns:
        np.ndarray | None: {1D-scalar} Generated noise; :data:`None` when ``mode`` is invalid
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
    """Generate blue (f) or violet (f^2) noise.

    Blue noise's power density increases at 3 dB per octave (density proportional to ``f``); violet noise's
    increases at 6 dB per octave (density proportional to ``f^2``). Both spectra are produced over a finite
    frequency range by spectral shaping of a complex Gaussian draw.

    Args:
        size (int): Number of samples to generate
        mode (int): Noise colour selector (default: ``0``)

            - ``0``: blue (azure) noise generation
            - ``1``: violet (purple) noise generation

        amp (float): Peak-to-peak amplitude of the noise; the output spans ``[-amp/2, amp/2)`` (default: ``1.0``)
        seed (int | None): Random seed for the pseudo-random number generator (default: ``None``)

    Returns:
        np.ndarray | None: {1D-scalar} Generated noise; :data:`None` when ``mode`` is invalid
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
    """Generate a linear baseline-shift signal.

    Two endpoint amplitudes are drawn uniformly from ``amp_rng`` and the result is the linear interpolation
    between them, sampled at ``size`` evenly spaced points.

    Args:
        size (int): Number of samples to generate
        amp_rng (tuple[int | float, int | float]): Inclusive range from which the two endpoint amplitudes are drawn

    Returns:
        np.ndarray: {1D-scalar} Generated baseline-shift signal of length ``size``
    """
    # Compute random values for periodic signal
    amp_a, amp_p = np.random.uniform(amp_rng[0], amp_rng[1], 2)
    # Compute randomized signal
    sft = np.linspace(amp_a, amp_p, size)
    return sft


def bsl_sft_sin(size, fs, amp_rng, freq_rng):
    """Generate a sinusoidal baseline-shift signal.

    Amplitude, frequency, and phase are drawn uniformly within the supplied ranges, and the resulting
    sinusoid is sampled at ``size`` evenly spaced points at sampling rate ``fs``.

    Args:
        size (int): Number of samples to generate
        fs (int | float): Sampling frequency of the digital system in Hz
        amp_rng (tuple[int | float, int | float]): Inclusive range from which the amplitude is drawn
        freq_rng (tuple[int | float, int | float]): Inclusive range from which the sinusoid frequency is drawn (Hz)

    Returns:
        np.ndarray: {1D-scalar} Generated baseline-shift signal of length ``size``
    """
    # Compute random values for periodic signal
    amp = np.random.uniform(amp_rng[0], amp_rng[1])
    freq = np.random.uniform(freq_rng[0], freq_rng[1]) / fs * 2 * np.pi
    phase = np.random.uniform(0., 2 * np.pi)
    # Compute randomized signal
    x = np.arange(0, size, 1) * freq + phase
    sft = amp * np.sin(x)
    return sft


# Neural signal operations ------------------------------------------------------------------------------------------- #

def neuron_sig_slc(rec, loc, rng):
    """Slice and pad a neural signal into individual spike snippets of variable lengths.

    For each spike location, the snippet spans ``[loc - rng_anterior, loc + rng_posterior]`` with per-spike
    ranges. Snippets that overlap their neighbours are split at the local minimum of ``|rec|`` between the
    overlapping pair, with padding on the trimmed side so that every snippet keeps its requested length.
    Out-of-bounds anterior/posterior segments are padded with the signal's edge value.

    Args:
        rec (np.ndarray): {1D-scalar} Recorded neural signal
        loc (list[int]): Spike peak indices into ``rec``
        rng (list[tuple[int, int]]): Per-spike anterior/posterior lengths in samples, aligned with ``loc``

    Returns:
        list[np.ndarray] | None: {1D-scalar, n*rng} Per-spike snippets; :data:`None` when ``loc`` is empty
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
    """Split a signal into overlapping fixed-size parts.

    Consecutive parts share ``overlap`` samples; the last part is right-padded with ``endpad`` so that every
    part has length ``size``.

    Args:
        src (np.ndarray | list[int | float]): {1D-scalar} Input signal
        size (int): Sample size of each part
        overlap (int): Overlap between two consecutive parts in samples (default: ``10``)
        endpad (int | float): Padding value used to extend the last part to ``size`` (default: ``0.0``)

    Returns:
        list[np.ndarray]: {1D-scalar, n*size} Split parts of the signal
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
    """Merge a list of signal parts into a single signal trace.

    The averaging is performed over the ``overlap`` samples that two consecutive parts share. ``trim``
    samples are removed from the end of the merged signal, which is useful for reversing the right-padding
    introduced by :func:`sig_split`.

    Args:
        src (list[np.ndarray | list[int | float]] | np.ndarray): {1D(n * size) | 2D(n, size)} Input list of signal parts
        overlap (int): Overlap between two consecutive parts in samples (default: ``10``)
        trim (int): Number of samples to remove at the end of the merged signal (default: ``0``)

    Returns:
        np.ndarray: {1D-scalar} Merged signal trace
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


# Peak process functions --------------------------------------------------------------------------------------------- #

def loc_ext_1d(arr, allow_plateau=True):
    """Detect local extrema in a 1D array.

    A point is a local maximum (resp. minimum) when it is strictly greater (resp. less) than both of its
    neighbours. With ``allow_plateau``, consecutive equal-value runs are first compressed before the
    comparison so the first index of each plateau is detected.

    Args:
        arr (list[int | float] | np.ndarray): Input array
        allow_plateau (bool): When :data:`True`, the first index of each constant plateau is detected as an
            extremum (default: ``True``)

    Returns:
        dict[str, np.ndarray]: Detected local extrema

            - max (np.ndarray): Indices of local maxima
            - min (np.ndarray): Indices of local minima
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


def sig_peak_zsc(signal, lag, th, influence=0.0):
    """Detect signal peaks using a robust z-score criterion.

    Maintains a moving mean and standard deviation over a window of length ``lag``. A sample whose
    deviation from the moving mean exceeds ``th`` standard deviations is flagged as a positive (``+1``) or
    negative (``-1``) peak. The flagged sample is then mixed back into the moving window with weight
    ``influence`` to control how much detected peaks adapt the threshold.

    Inspired by `J.P.G. van Brakel <https://stackoverflow.com/a/22640362/6029703>`_.

    Args:
        signal (list[int | float] | np.ndarray): {1D-Scalar} Input signal array
        lag (int): Sliding window length; larger lags assume more stationary data
        th (int | float): Threshold in standard deviations above which a sample is classified as a peak
        influence (float): Influence of detected peaks on the threshold in ``[0, 1]``; ``0`` assumes
            stationary signal, ``1`` treats peaks like normal data points (default: ``0.0``)

    Returns:
        np.ndarray: {1D-int} Per-sample peak flags (``1`` positive peak, ``-1`` negative peak, ``0`` no peak)
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
        if abs(s - avg) > th * std:
            peak[i] = 1 if s > avg else -1
            filt[i + lag] = influence * s + (1 - influence) * filt[i + lag - 1]
        # Update sliding window sums
        lin_sum = lin_sum + filt[i + lag] - filt[i]
        sqr_sum = sqr_sum + (filt[i + lag] + filt[i]) * (filt[i + lag] - filt[i])
    return peak


def sig_peak_fwd(signal, th, neg=True):
    """Detect signal peaks by combining a forward-difference sign change with a fixed threshold.

    A peak is reported where the forward difference changes sign (i.e. the signal levels off) and the signal
    value exceeds ``th`` (or falls below ``th`` when ``neg`` is :data:`True`).

    Args:
        signal (list[int | float] | np.ndarray): {1D-Scalar} Input signal
        th (int | float): Peak detection threshold
        neg (bool): When :data:`True`, look for samples below ``th``; when :data:`False`, above ``th``

    Returns:
        np.ndarray: {1D-int} Per-sample peak flags (``1`` peak, ``0`` no peak)
    """
    diff = np.sign(np.ediff1d(signal, to_end=signal[-1:]))
    diff[1:] = diff[:-1] + diff[1:]
    det = np.where((signal < th) & (diff == 0), 1, 0) if neg else np.where((signal > th) & (diff == 0), 1, 0)
    return det.astype(np.int8)


def peak_extremum(signal, peak, th, neg=True, smp=None):
    """Find the extremum point of consecutive peak detections from :func:`sig_peak_zsc`.

    Consecutive same-sign peaks (``+1`` or ``-1``) are grouped, and within each group the index of the
    extremum is kept when its absolute value passes ``th``. Optionally, a fixed-size window of flanking
    samples around each extremum is also returned.

    Args:
        signal (list[int | float] | np.ndarray): {1D-Scalar} Input signal
        peak (list[int] | np.ndarray): {1D-int} Per-sample peak flags from :func:`sig_peak_zsc`
        th (int | float): Lower bound on ``|signal[extremum]|`` for the extremum to be retained
        neg (bool): When :data:`True`, retain negative peaks (``-1``); otherwise retain positive peaks
            (default: ``True``)
        smp (int | None): Number of flanking samples to include on each side of the extremum; pass
            :data:`None` to skip sampling (default: ``None``)

    Returns:
        tuple[np.ndarray, np.ndarray | None]: Extremum indices and optional flanking samples

            - pos (np.ndarray): {1D-int} Per-group extremum indices in ``signal``
            - smp (np.ndarray | None): {2D-float} Flanking-sample windows (``None`` when ``smp`` is
              :data:`None` on input)
    """
    val = -1 if neg else 1
    th = abs(th)
    # Detect extremum position
    det = np.where(peak == val)[0]
    grp = np.split(det, np.where(np.diff(det) != 1)[0] + 1)
    pos = [i[np.argmax(signal[i])] for i in grp if np.max(signal[i]) * val > th]
    # Sampling signal and return
    if smp is None:
        return np.array(pos, dtype=int), None
    else:
        rng = [range(i - smp, i + smp + 1) for i in pos]
        rng = np.clip(rng, a_min=0, a_max=len(signal) - 1)
        smp = signal[rng]
        return np.array(pos, dtype=int), smp


def peak_reloc_ex(signal, peak, th=None, neg=True, smp=10):
    """Relocate one-hot peak indices to the nearest local extremum within a sample window.

    For each non-zero entry in ``peak``, the function searches a ``2 * smp + 1`` window in ``signal`` for the
    local minimum (when ``neg`` is :data:`True`) or maximum and replaces the original index with the found
    extremum. An optional threshold ``th`` further filters out shallow extrema.

    Args:
        signal (list[int | float] | np.ndarray): {1D-Scalar} Input signal
        peak (list[int] | np.ndarray): {1D-int} One-hot peak indices to relocate
        th (int | float | None): Bound on the relocated extremum value; pass :data:`None` to disable
            filtering (default: ``None``)
        neg (bool): When :data:`True`, search for local minima; when :data:`False`, local maxima (default: ``True``)
        smp (int): One-sided search range in samples (default: ``10``)

    Returns:
        np.ndarray: {1D-int8} Relocated one-hot peak indices (same shape as ``signal``)
    """
    # Get search range
    det = np.nonzero(peak)[0]
    rng = np.clip([range(i - smp, i + smp + 1) for i in det], a_min=0, a_max=len(signal) - 1)
    # Detect local extrema
    idx = np.argmin(signal[rng], axis=1) if neg else np.argmax(signal[rng], axis=1)
    pos = rng[np.arange(len(det)), idx]
    if th is not None:
        pos = np.array([p for p in pos if signal[p] < th]) if neg else np.array([p for p in pos if signal[p] > th])
    # Cast to output type
    res = np.zeros_like(signal, dtype=np.int8)
    res[pos] = 1
    return res


# Feature process functions ------------------------------------------------------------------------------------------ #

def __bin_smp(spk, fs, t, g=None):
    """Build per-window index lists from a one-hot spike vector.

    Slides a window of length ``t * fs`` across ``spk`` with step ``g * fs`` (or ``t * fs`` when ``g`` is
    :data:`None`) and returns the spike indices found within each window.

    Args:
        spk (list[int | float] | np.ndarray): {1D} One-hot spike event data
        fs (int | float): Data sampling frequency in Hz
        t (int | float): Time window in seconds
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)

    Returns:
        list[np.ndarray]: Per-window spike indices (one array per sliding step)
    """
    win = round(fs * t, ndigits=None)
    stp = win if g is None else round(fs * g, ndigits=None)
    smp = np.lib.stride_tricks.sliding_window_view(spk, win)[::stp]
    pos = [np.nonzero(smp[i])[0] for i in range(smp.shape[0])]
    return pos


def __tpt_rng(spk, org=0, end=None):
    """Sort a timestamp spike array and clip it to ``[org, end)``.

    Args:
        spk (list[int | float] | np.ndarray): {1D} Timestamp spike event data
        org (int | float | None): Start of the time range; pass :data:`None` to use the first value of ``spk``
            (default: ``0``)
        end (int | float | None): End of the time range; pass :data:`None` to use the last value of ``spk``
            (default: ``None``)

    Returns:
        tuple[np.ndarray, int | float, int | float]: Sorted spikes within ``[org, end)`` and the resolved time range

    Raises:
        ValueError: If ``end <= org`` after resolving the defaults
    """
    # Sort timestamps for valid results
    tpt = np.sort(spk, kind='stable')
    # Get time range
    org = tpt[0].item() if org is None else org
    end = tpt[-1].item() if end is None else end
    if end <= org:
        raise ValueError("Timestamp origin must be LESS than end.")
    # Limit timestamps between [org, end)
    idx = np.where((tpt >= org) & (tpt < end))[0]
    return tpt[idx], org, end


def __tpt_smp(tpt, t, g, org, end):
    """Build per-window timestamp lists from a sorted timestamp spike array.

    Slides a window of length ``t`` across ``[org, end)`` with step ``g`` (or ``t`` when ``g`` is
    :data:`None`) and returns the timestamps found within each window.

    Args:
        tpt (np.ndarray): {1D-SORTED} Sorted timestamp spike event data
        t (int | float): Time window in seconds
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t``
        org (int | float): Start of the time range
        end (int | float): End of the time range

    Returns:
        list[np.ndarray]: Per-window timestamps (one array per sliding step)
    """
    stp = t if g is None else g
    wini = np.arange(org, end, stp)
    wstp = wini + t
    wstp[-1] = wstp[-1] + 0.0001  # Make sure the last timestamp is included
    pos = [tpt[np.where((tpt >= wini[i]) & (tpt < wstp[i]))[0]] for i in range(len(wini))]
    return pos


def bin_spk_frq(spk, fs, t=None, g=None):
    """Compute the average firing frequency of a one-hot spike train.

    When ``t`` is :data:`None`, a single global firing frequency is returned; otherwise the function returns
    one frequency per sliding window of length ``t``.

    Args:
        spk (list[int | float] | np.ndarray): {1D} One-hot spike event data
        fs (int | float): Data sampling frequency in Hz
        t (int | float | None): Time window in seconds; pass :data:`None` to compute over the whole trace
            (default: ``None``)
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)

    Returns:
        float | list[float]: Firing frequency in Hz; a single float when ``t`` is :data:`None`, otherwise one
            value per sliding window
    """
    if t is None:
        pos = np.nonzero(spk)[0]
        return pos.size / len(spk) * fs
    else:
        pos = __bin_smp(spk, fs, t, g)
        return [p.size / t for p in pos]


def tpt_spk_frq(spk, t=None, g=None, org=0, end=None):
    """Compute the average firing frequency of a timestamp spike train.

    When ``t`` is :data:`None`, a single global firing frequency is returned over ``[org, end)``; otherwise
    the function returns one frequency per sliding window of length ``t``.

    Args:
        spk (list[int | float] | np.ndarray): {1D} Timestamp spike event data
        t (int | float | None): Time window in seconds; pass :data:`None` to compute over the whole trace
            (default: ``None``)
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)
        org (int | float | None): Start of the time range; pass :data:`None` to use the first value of ``spk``
            (default: ``0``)
        end (int | float | None): End of the time range; pass :data:`None` to use the last value of ``spk``
            (default: ``None``)

    Returns:
        float | list[float]: Firing frequency in Hz; a single float when ``t`` is :data:`None`, otherwise one
            value per sliding window
    """
    # Sort timestamps and get time range
    tpt, org, end = __tpt_rng(spk, org, end)
    # Compute frequency
    if t is None:
        return tpt.size / (end - org)
    else:
        pos = __tpt_smp(tpt, t, g, org, end)
        return [p.size / t for p in pos]


def bin_spk_isi(spk, fs, t=None, g=None, lst=False):
    """Compute the inter-spike interval (ISI) of a one-hot spike train.

    When ``t`` is :data:`None`, a single global ISI is returned (mean of the per-pair ISIs, or the full list
    when ``lst`` is :data:`True`). Otherwise, the function returns the mean ISI per sliding window.

    Args:
        spk (list[int | float] | np.ndarray): {1D} One-hot spike event data
        fs (int | float): Data sampling frequency in Hz
        t (int | float | None): Time window in seconds; pass :data:`None` to compute over the whole trace
            (default: ``None``)
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)
        lst (bool): When :data:`True` and ``t`` is :data:`None`, return every ISI rather than the mean
            (default: ``False``)

    Returns:
        float | list[float]: ISI in seconds; layout depends on ``t`` and ``lst``

    Warns:
        RuntimeWarning: Emitted when there are fewer than two spikes; the function then returns ``NaN``
    """
    pos = np.nonzero(spk)[0]
    if pos.size < 2:
        warnings.warn("Not enough spikes detected to compute ISI, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    else:
        if t is None:
            gap = np.ediff1d(pos) / fs
            res = gap.tolist() if lst else np.mean(gap).item()
        else:
            # Sampling
            pos = __bin_smp(spk, fs, t, g)
            # Check and compute
            res = []  # INIT VAR
            for p in pos:
                if p.size < 2:
                    res.append(float('nan'))
                else:
                    gap = np.ediff1d(p) / fs
                    res.append(np.mean(gap).item())
        return res


def tpt_spk_isi(spk, t=None, g=None, org=0, end=None, lst=False):
    """Compute the inter-spike interval (ISI) of a timestamp spike train.

    When ``t`` is :data:`None`, a single global ISI is returned (mean of the per-pair ISIs, or the full list
    when ``lst`` is :data:`True`). Otherwise, the function returns the mean ISI per sliding window.

    Args:
        spk (list[int | float] | np.ndarray): {1D} Timestamp spike event data
        t (int | float | None): Time window in seconds; pass :data:`None` to compute over the whole trace
            (default: ``None``)
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)
        org (int | float | None): Start of the time range; pass :data:`None` to use the first value of ``spk``
            (default: ``0``)
        end (int | float | None): End of the time range; pass :data:`None` to use the last value of ``spk``
            (default: ``None``)
        lst (bool): When :data:`True` and ``t`` is :data:`None`, return every ISI rather than the mean
            (default: ``False``)

    Returns:
        float | list[float]: ISI in seconds; layout depends on ``t`` and ``lst``

    Warns:
        RuntimeWarning: Emitted when there are fewer than two spikes; the function then returns ``NaN``
    """
    if len(spk) < 2:
        warnings.warn("Not enough spikes detected to compute ISI, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    # Sort timestamps and get time range
    tpt, org, end = __tpt_rng(spk, org, end)
    # Compute ISI
    if t is None:
        gap = np.ediff1d(tpt)
        res = gap.tolist() if lst else np.mean(gap).item()
    else:
        # Compute sample locations
        pos = __tpt_smp(tpt, t, g, org, end)
        # ISI with samples
        res = []  # INIT VAR
        for p in pos:
            if p.size < 2:
                res.append(float('nan'))
            else:
                gap = np.ediff1d(p)
                res.append(np.mean(gap).item())
    return res


def bin_spk_cv(spk, fs, t=None, g=None, ddof=0):
    """Compute the coefficient of variation (CV) of inter-spike intervals for a one-hot spike train.

    The CV is ``std(ISI, ddof=ddof) / mean(ISI)``. When ``t`` is :data:`None`, a single global CV is returned;
    otherwise the function returns one CV per sliding window.

    Args:
        spk (list[int | float] | np.ndarray): {1D} One-hot spike event data
        fs (int | float): Data sampling frequency in Hz
        t (int | float | None): Time window in seconds; pass :data:`None` to compute over the whole trace
            (default: ``None``)
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)
        ddof (int | float): Delta degrees of freedom for the standard deviation (default: ``0``)

    Returns:
        float | list[float]: CV; a single float when ``t`` is :data:`None`, otherwise one value per sliding window

    Warns:
        RuntimeWarning: Emitted when there are not enough spikes for the CV; the function then returns ``NaN``
    """
    pos = np.nonzero(spk)[0]
    lim = max(ddof - 1, 2)
    if pos.size < lim:
        warnings.warn("Not enough spikes detected to compute CV, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    else:
        if t is None:
            gap = np.ediff1d(pos) / fs
            return np.std(gap, ddof=ddof).item() / np.mean(gap).item()
        else:
            # Sampling
            pos = __bin_smp(spk, fs, t, g)
            # Check and compute
            res = []  # INIT VAR
            for p in pos:
                if p.size < lim:
                    res.append(float('nan'))
                else:
                    gap = np.ediff1d(p) / fs
                    res.append(np.std(gap, ddof=ddof).item() / np.mean(gap).item())
            return res


def tpt_spk_cv(spk, t=None, g=None, org=0, end=None, ddof=0):
    """Compute the coefficient of variation (CV) of inter-spike intervals for a timestamp spike train.

    The CV is ``std(ISI, ddof=ddof) / mean(ISI)``. When ``t`` is :data:`None`, a single global CV is returned;
    otherwise the function returns one CV per sliding window.

    Args:
        spk (list[int | float] | np.ndarray): {1D} Timestamp spike event data
        t (int | float | None): Time window in seconds; pass :data:`None` to compute over the whole trace
            (default: ``None``)
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)
        org (int | float | None): Start of the time range; pass :data:`None` to use the first value of ``spk``
            (default: ``0``)
        end (int | float | None): End of the time range; pass :data:`None` to use the last value of ``spk``
            (default: ``None``)
        ddof (int | float): Delta degrees of freedom for the standard deviation (default: ``0``)

    Returns:
        float | list[float]: CV; a single float when ``t`` is :data:`None`, otherwise one value per sliding window

    Warns:
        RuntimeWarning: Emitted when there are not enough spikes for the CV; the function then returns ``NaN``
    """
    lim = max(ddof - 1, 2)
    if len(spk) < lim:
        warnings.warn("Not enough spikes detected to compute CV, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    # Sort timestamps and get time range
    tpt, org, end = __tpt_rng(spk, org, end)
    # Compute CV
    if t is None:
        gap = np.ediff1d(tpt)
        return np.std(gap, ddof=ddof).item() / np.mean(gap).item()
    else:
        # Compute sample locations
        pos = __tpt_smp(tpt, t, g, org, end)
        # CV with samples
        res = []  # INIT VAR
        for p in pos:
            if p.size < lim:
                res.append(float('nan'))
            else:
                gap = np.ediff1d(p)
                res.append(np.std(gap, ddof=ddof).item() / np.mean(gap).item())
        return res


def bin_spk_cv2(spk, fs, t=None, g=None):
    """Compute the 2-point coefficient of variation (CV2) of a one-hot spike train.

    The CV2 is ``2 * mean(|ISI[i+1] - ISI[i]| / (ISI[i] + ISI[i+1]))``. When ``t`` is :data:`None`, a single
    global CV2 is returned; otherwise the function returns one CV2 per sliding window.

    Args:
        spk (list[int | float] | np.ndarray): {1D} One-hot spike event data
        fs (int | float): Data sampling frequency in Hz
        t (int | float | None): Time window in seconds; pass :data:`None` to compute over the whole trace
            (default: ``None``)
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)

    Returns:
        float | list[float]: CV2; a single float when ``t`` is :data:`None`, otherwise one value per sliding window

    Warns:
        RuntimeWarning: Emitted when there are fewer than three spikes; the function then returns ``NaN``
    """
    pos = np.nonzero(spk)[0]
    if pos.size < 3:
        warnings.warn("Not enough spikes detected to compute CV2, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    else:
        if t is None:
            gap = np.ediff1d(pos) / fs
            return 2 * np.mean(np.absolute(np.ediff1d(gap)) / (gap[:-1] + gap[1:])).item()
        else:
            # Sampling
            pos = __bin_smp(spk, fs, t, g)
            # Check and compute
            res = []  # INIT VAR
            for p in pos:
                if p.size < 3:
                    res.append(float('nan'))
                else:
                    gap = np.ediff1d(p) / fs
                    res.append(2 * np.mean(np.absolute(np.ediff1d(gap)) / (gap[:-1] + gap[1:])).item())
            return res


def tpt_spk_cv2(spk, t=None, g=None, org=0, end=None):
    """Compute the 2-point coefficient of variation (CV2) of a timestamp spike train.

    The CV2 is ``2 * mean(|ISI[i+1] - ISI[i]| / (ISI[i] + ISI[i+1]))``. When ``t`` is :data:`None`, a single
    global CV2 is returned; otherwise the function returns one CV2 per sliding window.

    Args:
        spk (list[int | float] | np.ndarray): {1D} Timestamp spike event data
        t (int | float | None): Time window in seconds; pass :data:`None` to compute over the whole trace
            (default: ``None``)
        g (int | float | None): Sampling step in seconds; pass :data:`None` to use ``t`` (default: ``None``)
        org (int | float | None): Start of the time range; pass :data:`None` to use the first value of ``spk``
            (default: ``0``)
        end (int | float | None): End of the time range; pass :data:`None` to use the last value of ``spk``
            (default: ``None``)

    Returns:
        float | list[float]: CV2; a single float when ``t`` is :data:`None`, otherwise one value per sliding window

    Warns:
        RuntimeWarning: Emitted when there are fewer than three spikes; the function then returns ``NaN``
    """
    if len(spk) < 3:
        warnings.warn("Not enough spikes detected to compute CV2, NaN returned.", RuntimeWarning, stacklevel=2)
        return float('nan')
    # Sort timestamps and get time range
    tpt, org, end = __tpt_rng(spk, org, end)
    # Compute CV2
    if t is None:
        gap = np.ediff1d(tpt)
        return 2 * np.mean(np.absolute(np.ediff1d(gap)) / (gap[:-1] + gap[1:])).item()
    else:
        # Compute sample locations
        pos = __tpt_smp(tpt, t, g, org, end)
        # CV2 with samples
        res = []  # INIT VAR
        for p in pos:
            if p.size < 3:
                res.append(float('nan'))
            else:
                gap = np.ediff1d(p)
                res.append(2 * np.mean(np.absolute(np.ediff1d(gap)) / (gap[:-1] + gap[1:])).item())
        return res


def tpt_kde_frq(spk, bw=None, **kwargs):
    """Estimate the firing rate of a timestamp spike train using a Gaussian kernel-density estimate.

    Wraps :class:`scipy.stats.gaussian_kde`; the bandwidth is selected via ``bw`` and the estimate is
    evaluated at either an explicit sample grid (``smp``) or at ``num`` points evenly spaced over ``[org, end]``.

    Args:
        spk (list[int | float] | np.ndarray): {1D} Timestamp spike event data
        bw (int | float | str | Callable | None): Bandwidth selection rule (default: ``None``)

            - int | float: used directly as the bandwidth factor
            - ``'scott'``: auto-compute Scott's factor
            - ``'silverman'``: auto-compute Silverman's factor
            - callable: receives a :class:`scipy.stats.gaussian_kde` instance and returns a scalar
            - :data:`None`: use Scott's factor

        **kwargs: See below

    Keyword Args:
        smp (list[int | float] | np.ndarray): {1D} Explicit evaluation grid; when provided, ``org``, ``end``
            and ``num`` are ignored
        org (int | float | None): Start of the evaluation grid; defaults to the first value of ``spk``
        end (int | float | None): End of the evaluation grid; defaults to the last value of ``spk``
        num (int): Number of evaluation points (default: ``1000``)

    Returns:
        np.ndarray: Estimated firing-rate values at every grid point
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
