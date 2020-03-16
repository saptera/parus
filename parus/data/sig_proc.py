import numpy as np
from scipy import signal as sig

"""Function list:
# Neuronal signal filters:
    spk_lowpass(x, fpass, fs): Digital lowpass Butterworth filter for neurological signals.
    spk_highpass(x, fpass, fs): Digital highpass Butterworth filter for neurological signals.
    spk_bandpass(x, fpass, fs): Digital bandpass Butterworth filter for neurological signals.
    spk_notch(x, fnotch, fs): Digital notch filter for neurological signals.
# Noise generators:
    noise_white(size, mode=0, amp=1.0, seed=None): White noise generator.
    noise_freq_decr(size, mode=0, amp=1.0, seed=None): Pink and brown(red) noise generator.
    noise_freq_incr(size, mode=0, amp=1.0, seed=None): Blue(Azure) and violet(purple) noise generator.
"""


# Neuronal signal filters -------------------------------------------------------------------------------------------- #

def spk_lowpass(x, fpass, fs):
    """Digital lowpass Butterworth filter for neurological signals.

    Automatic design a digital lowpass Butterworth filter for neurological signals with input frequency
    and perform forward-backward digital filtering using cascaded second-order sections.
    --------
    The Butterworth filter has maximally flat frequency response in the passband.
    --------
    This function applies a linear digital filter twice, once forward and once backwards.
    The combined filter has zero phase and a filter order twice that of the original.

    Args:
        x (np.ndarray): The array of data to be filtered.
        fpass (float): Passband edge frequency (Hz).
        fs (float): The sampling frequency of the digital system (Hz).

    Returns:
        np.ndarray: The filtered output with the same shape as x.
    """
    ws = fpass * 1.1
    ordr, wn = sig.buttord(fpass, ws, 2, 50, False, fs)
    sos = sig.butter(ordr, wn, 'lowpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_highpass(x, fpass, fs):
    """Digital highpass Butterworth filter for neurological signals.

    Automatic design a digital highpass Butterworth filter for neurological signals with input frequency
    and perform forward-backward digital filtering using cascaded second-order sections.
    --------
    The Butterworth filter has maximally flat frequency response in the passband.
    --------
    This function applies a linear digital filter twice, once forward and once backwards.
    The combined filter has zero phase and a filter order twice that of the original.

    Args:
        x (np.ndarray): The array of data to be filtered.
        fpass (float): Passband edge frequency (Hz).
        fs (float): The sampling frequency of the digital system (Hz).

    Returns:
        np.ndarray: The filtered output with the same shape as x.
    """
    ws = fpass * 0.9
    ordr, wn = sig.buttord(fpass, ws, 2, 50, False, fs)
    sos = sig.butter(ordr, wn, 'highpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_bandpass(x, fpass, fstop, fs):
    """Digital bandpass Butterworth filter for neurological signals.

    Automatic design a digital bandpass Butterworth filter for neurological signals with input frequency
    and perform forward-backward digital filtering using cascaded second-order sections.
    --------
    The Butterworth filter has maximally flat frequency response in the passband.
    --------
    This function applies a linear digital filter twice, once forward and once backwards.
    The combined filter has zero phase and a filter order twice that of the original.

    Args:
        x (np.ndarray): The array of data to be filtered.
        fpass (float): Passband edge frequency (Hz).
        fstop (float): Stopband edge frequency (Hz).
        fs (float): The sampling frequency of the digital system (Hz).

    Returns:
        np.ndarray: The filtered output with the same shape as x.
    """
    wp = [fpass, fstop]
    ws = [fpass * 0.9, fstop * 1.1]
    ordr, wn = sig.buttord(wp, ws, 5, 40, False, fs)
    sos = sig.butter(ordr, wn, 'bandpass', False, 'sos', fs)
    y = sig.sosfiltfilt(sos, x)
    return y


def spk_notch(x, fnotch, fs):
    """Digital notch filter for neurological signals.

    Automatic design a digital notch filter for neurological signals with input frequency
    and perform forward-backward digital filtering.
    --------
    A notch filter is a band-stop filter with a narrow bandwidth (high quality factor).
    It rejects a narrow frequency band and leaves the rest of the spectrum little changed.
    --------
    This function applies a linear digital filter twice, once forward and once backwards.
    The combined filter has zero phase and a filter order twice that of the original.

    Args:
        x (np.ndarray): The array of data to be filtered.
        fnotch (float): Frequency to remove from a signal (Hz).
        fs (float): The sampling frequency of the digital system (Hz).

    Returns:
        np.ndarray: The filtered output with the same shape as x.
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
        size (int): Number of samples to be generated.
        mode (int): {0 or 1} White noise random distribution type. (default: 0 = UNIFORM)
                --  0 = UNIFORM distribution
                --  1 = GAUSSIAN distribution
        amp (float): Amplitude of noise (default: 1.0 = [-0.5 0.5))
        seed (int or None): Random seed used to initialize the pseudo-random number generator.

    Returns:
        np.ndarray: {1D} Generated white noise.
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
    """ Pink and brown(red) noise generator.

    Pink noise's power density decreases 3 dB per octave
    with increasing frequency (density proportional to 1/f) finite frequency range.
    The frequency spectrum of pink noise is linear in logarithmic scale;
    it has equal power in bands that are proportionally wide.
    --------
    Brown noise's power density decreases 6 dB per octave
    with increasing frequency (density proportional to 1/f^2) finite frequency range.

    Args:
        size (int): Number of samples to be generated.
        mode (int): {0 or 1} White noise random distribution type. (default: 0 = PINK)
                --  0 = PINK noise generation
                --  1 = BROWN(RED) noise generation
        amp (float): Amplitude of noise (default: 1.0 = [-0.5 0.5))
        seed (int or None): Random seed used to initialize the pseudo-random number generator.

    Returns:
        np.ndarray: {1D} Generated noise.
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
    """ Blue(Azure) and violet(purple) noise generator.

    Blue noise's power density increases 3 dB per octave,
    with increasing frequency (density proportional to f) over a finite frequency range.
    --------
    Violet noise's power density increases 6 dB per octave,
    with increasing frequency (density proportional to f^2) over a finite frequency range.

    Args:
        size (int): Number of samples to be generated.
        mode (int): {0 or 1} White noise random distribution type. (default: 0 = BLUE)
                --  0 = BLUE(AZURE) noise generation
                --  1 = VIOLET(PURPLE) noise generation
        amp (float): Amplitude of noise (default: 1.0 = [-0.5 0.5))
        seed (int or None): Random seed used to initialize the pseudo-random number generator.

    Returns:
        np.ndarray: {1D} Generated noise.
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
