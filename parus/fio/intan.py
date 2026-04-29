# -*- coding: utf-8 -*-

"""IntanTech file import module

Importers for the IntanTech RHD2000 raw binary recording formats: ``One File Per Signal Type`` (one file holding
interleaved samples for every channel) and ``One File Per Channel`` (one file per recording channel).
Per-channel readers are also wrapped by per-port and per-board batch helpers.
"""

import os
import numpy as np

__package__ = 'parus.fio'
__name__ = 'parus.fio.intan'

__all__ = [
    'intan_time_read',
    'intan_typ_amp_read', 'intan_typ_aux_read', 'intan_typ_vdd_read', 'intan_typ_adc_read', 'intan_typ_dio_read',
    'intan_ch_amp_read', 'intan_ch_aux_read', 'intan_ch_vdd_read', 'intan_ch_adc_read', 'intan_ch_dio_read',
    'intan_port_amp_read', 'intan_port_aux_read', 'intan_port_vdd_read',
    'intan_board_adc_read', 'intan_board_din_read', 'intan_board_dout_read'
]
"""
Public function list:

- General data files:

    - intan_time_read(time_file, freq)        : Import RHD2000 timestamp data

- One-file-per-signal-type files:

    - intan_typ_amp_read(amp_file, n)         : Import "One File Per Signal Type" amplifier data
    - intan_typ_aux_read(aux_file, n)         : Import "One File Per Signal Type" auxiliary input data
    - intan_typ_vdd_read(vdd_file, n)         : Import "One File Per Signal Type" supply voltage data
    - intan_typ_adc_read(adc_file, n, irc)    : Import "One File Per Signal Type" board ADC input data
    - intan_typ_dio_read(dio_file)            : Import "One File Per Signal Type" board digital I/O data

- One-file-per-channel files (single channel):

    - intan_ch_amp_read(amp_file)             : Import "One File Per Channel" amplifier data
    - intan_ch_aux_read(aux_file)             : Import "One File Per Channel" auxiliary input data
    - intan_ch_vdd_read(vdd_file)             : Import "One File Per Channel" supply voltage data
    - intan_ch_adc_read(adc_file, irc)        : Import "One File Per Channel" board ADC input data
    - intan_ch_dio_read(dio_file)             : Import "One File Per Channel" board digital I/O data

- One-file-per-channel files (batch):

    - intan_port_amp_read(amp_path, port, n)  : Batch import of amplifier data for one recording port
    - intan_port_aux_read(aux_path, port, n)  : Batch import of auxiliary input data for one recording port
    - intan_port_vdd_read(vdd_path, port, n)  : Batch import of supply voltage data for one recording port
    - intan_board_adc_read(adc_path, n, irc)  : Batch import of board ADC input data for one recording board
    - intan_board_din_read(din_path, n)       : Batch import of board digital input data for one recording board
    - intan_board_dout_read(dout_path, n)     : Batch import of board digital output data for one recording board
"""


# General data files ------------------------------------------------------------------------------------------------- #

def intan_time_read(time_file, freq):
    """Import the timestamp data of an IntanTech RHD2000 recording.

    The timestamp file stores monotonically increasing INT32 sample indices. Dividing by the sampling frequency
    converts them to physical time in seconds.

    Args:
        time_file (str): Path to the IntanTech RHD2000 timestamp file
        freq (int): Sampling frequency of the recording (Hz)

    Returns:
        np.ndarray: {1D-float} Time vector in seconds
    """
    fp = open(time_file, 'rb')
    dat = np.fromfile(fp, dtype=np.int32)  # Data type in binary file: INT32
    fp.close()
    time_data = dat / freq  # Convert sequential integers to actual time vector
    return time_data


# [One File Per Signal Type] files ----------------------------------------------------------------------------------- #

def intan_typ_amp_read(amp_file, n):
    """Import amplifier data from an IntanTech RHD2000 ``One File Per Signal Type`` recording.

    Samples are stored as INT16 in column-major order with one row per channel. The conversion factor to microvolts
    is ``0.195`` and the result is rounded to three decimals to suppress quantisation artefacts.

    Args:
        amp_file (str): Path to the ``One File Per Signal Type`` amplifier file
        n (int): Number of channels stored in ``amp_file``

    Returns:
        list[np.ndarray]: {1D-float, n} Per-channel amplifier traces in microvolts (μV)
    """
    fp = open(amp_file, 'rb')
    dat = np.fromfile(fp, dtype=np.int16)  # Data type in binary file: INT16
    fp.close()
    mat = np.reshape(dat, (n, dat.size // n), order='F')  # Reshape matrix with column-major order
    del dat
    amp_data = [np.round((s * 0.195), 3).astype('float32') for s in mat]  # Conversion factor to μV: 0.195
    return amp_data


def intan_typ_aux_read(aux_file, n):
    """Import auxiliary input data from an IntanTech RHD2000 ``One File Per Signal Type`` recording.

    Samples are stored as UINT16 in column-major order with one row per channel. The conversion factor to volts is
    ``0.0000374`` and the result is rounded to seven decimals.

    Args:
        aux_file (str): Path to the ``One File Per Signal Type`` auxiliary input file
        n (int): Number of channels stored in ``aux_file``

    Returns:
        list[np.ndarray]: {1D-float, n} Per-channel auxiliary input traces in volts (V)
    """
    fp = open(aux_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    mat = np.reshape(dat, (n, dat.size // n), order='F')  # Reshape matrix with column-major order
    aux_data = [np.round((s * 0.0000374), 7) for s in mat]  # Conversion factor to V: 0.0000374
    return aux_data


def intan_typ_vdd_read(vdd_file, n):
    """Import supply voltage data from an IntanTech RHD2000 ``One File Per Signal Type`` recording.

    Samples are stored as UINT16 in column-major order with one row per channel. The conversion factor to volts is
    ``0.0000748`` and the result is rounded to seven decimals.

    Args:
        vdd_file (str): Path to the ``One File Per Signal Type`` supply voltage file
        n (int): Number of channels stored in ``vdd_file``

    Returns:
        list[np.ndarray]: {1D-float, n} Per-channel supply voltage traces in volts (V)
    """
    fp = open(vdd_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    mat = np.reshape(dat, (n, dat.size // n), order='F')  # Reshape matrix with column-major order
    vdd_data = [np.round((s * 0.0000748), 7) for s in mat]  # Conversion factor to V: 0.0000748
    return vdd_data


def intan_typ_adc_read(adc_file, n, irc=False):
    """Import board ADC input data from an IntanTech RHD2000 ``One File Per Signal Type`` recording.

    Samples are stored as UINT16 in column-major order with one row per channel. The Intan Recording Controller and
    the standard RHD2000 evaluation board use different conversion factors and offsets, so the right scaling is
    selected via ``irc``.

    Args:
        adc_file (str): Path to the ``One File Per Signal Type`` ADC input file
        n (int): Number of channels stored in ``adc_file``
        irc (bool): Set to :data:`True` when the file was produced by an Intan Recording Controller; the
            conversion factor becomes ``(sample - 32768) * 0.0003125`` instead of ``sample * 0.000050354``
            (default: ``False``)

    Returns:
        list[np.ndarray]: {1D-float, n} Per-channel ADC input traces in volts (V)
    """
    fp = open(adc_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    mat = np.reshape(dat, (n, dat.size // n), order='F')  # Reshape matrix with column-major order
    if irc:
        adc_data = [np.round((s - 32768) * 0.0003125, 7) for s in mat]  # Conversion factor to V: 0.0003125, with offset
    else:
        adc_data = [np.round((s * 0.000050354), 9) for s in mat]  # Conversion factor to V: 0.000050354
    return adc_data


def intan_typ_dio_read(dio_file):
    """Import board digital I/O data from an IntanTech RHD2000 ``One File Per Signal Type`` recording.

    The 16 digital lines are bit-packed into UINT16 samples. The function unpacks them into one binary trace per line.

    Args:
        dio_file (str): Path to the ``One File Per Signal Type`` digital I/O file

    Returns:
        list[np.ndarray]: {1D-int[0|1], 16} Per-line digital I/O traces (0 or 1)
    """
    fp = open(dio_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    dio_data = [np.clip(np.bitwise_and(dat, 2 ** s), a_min=0, a_max=1) for s in range(16)]  # 16 channels in total
    return dio_data


# [One File Per Channel] Single channel files ------------------------------------------------------------------------ #

def intan_ch_amp_read(amp_file):
    """Import amplifier data from an IntanTech RHD2000 ``One File Per Channel`` recording.

    Samples are stored as INT16. The conversion factor to microvolts is ``0.195`` and the result is rounded to three
    decimals to suppress quantisation artefacts.

    Args:
        amp_file (str): Path to the ``One File Per Channel`` amplifier file

    Returns:
        np.ndarray: {1D-float} Amplifier trace in microvolts (μV)
    """
    fp = open(amp_file, 'rb')
    dat = np.fromfile(fp, dtype=np.int16)  # Data type in binary file: INT16
    fp.close()
    amp_data = np.round((dat * 0.195), 3).astype('float32')  # Conversion factor to μV: 0.195, round to avoid artifact
    return amp_data


def intan_ch_aux_read(aux_file):
    """Import auxiliary input data from an IntanTech RHD2000 ``One File Per Channel`` recording.

    Samples are stored as UINT16. The conversion factor to volts is ``0.0000374`` and the result is rounded to seven
    decimals.

    Args:
        aux_file (str): Path to the ``One File Per Channel`` auxiliary input file

    Returns:
        np.ndarray: {1D-float} Auxiliary input trace in volts (V)
    """
    fp = open(aux_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    aux_data = np.round((dat * 0.0000374), 7)  # Conversion factor to V: 0.0000374, round to avoid artifact
    return aux_data


def intan_ch_vdd_read(vdd_file):
    """Import supply voltage data from an IntanTech RHD2000 ``One File Per Channel`` recording.

    Samples are stored as UINT16. The conversion factor to volts is ``0.0000748`` and the result is rounded to seven
    decimals.

    Args:
        vdd_file (str): Path to the ``One File Per Channel`` supply voltage file

    Returns:
        np.ndarray: {1D-float} Supply voltage trace in volts (V)
    """
    fp = open(vdd_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    vdd_data = np.round((dat * 0.0000748), 7)  # Conversion factor to V: 0.0000748, round to avoid artifact
    return vdd_data


def intan_ch_adc_read(adc_file, irc=False):
    """Import board ADC input data from an IntanTech RHD2000 ``One File Per Channel`` recording.

    Samples are stored as UINT16. The Intan Recording Controller and the standard RHD2000 evaluation board use
    different conversion factors and offsets, so the right scaling is selected via ``irc``.

    Args:
        adc_file (str): Path to the ``One File Per Channel`` ADC input file
        irc (bool): Set to :data:`True` when the file was produced by an Intan Recording Controller; the
            conversion factor becomes ``(sample - 32768) * 0.0003125`` instead of ``sample * 0.000050354``
            (default: ``False``)

    Returns:
        np.ndarray: {1D-float} ADC input trace in volts (V)
    """
    fp = open(adc_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    if irc:
        adc_data = np.round((dat - 32768) * 0.0003125, 7)  # Conversion factor to V: 0.0003125, with offset of 32768
    else:
        adc_data = np.round((dat * 0.000050354), 9)  # Conversion factor to V: 0.000050354, round to avoid artifact
    return adc_data


def intan_ch_dio_read(dio_file):
    """Import board digital I/O data from an IntanTech RHD2000 ``One File Per Channel`` recording.

    Samples are read raw as UINT16 since each ``One File Per Channel`` digital file already stores a single line.

    Args:
        dio_file (str): Path to the ``One File Per Channel`` digital I/O file

    Returns:
        np.ndarray: {1D-int[0|1]} Digital I/O trace (0 or 1)
    """
    fp = open(dio_file, 'rb')
    dio_data = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    return dio_data


# [One File Per Channel] Batch files --------------------------------------------------------------------------------- #

def intan_port_amp_read(amp_path, port, n):
    """Batch import amplifier data for every channel on a single IntanTech RHD2000 recording port.

    Iterates over the expected per-channel filenames (``amp-<Port>-NNN.dat``). Channels with no matching file are
    returned as empty arrays, and a warning is printed for each missing file.

    Args:
        amp_path (str): Directory holding the ``One File Per Channel`` amplifier files
        port (str): Port name appearing in the filename (case-insensitive; capitalised internally)
        n (int): Number of channels expected on the port

    Returns:
        list[np.ndarray]: {1D-float, n} Per-channel amplifier traces in microvolts (μV); missing channels
            are returned as empty arrays
    """
    # Get all existing files
    prefix = 'amp-' + port.capitalize()
    files = [f for f in os.listdir(amp_path) if f.startswith(prefix) and f.endswith('.dat')]
    # Initialize variables
    j = 0
    port_amp_data = []
    # Get all channel data
    for i in range(n):
        name = prefix + ('-%03d.dat' % i)
        if name == files[j]:
            temp = intan_ch_amp_read(os.path.join(amp_path, name))
            port_amp_data.append(temp)
            j += 1
        else:
            port_amp_data.append(np.array([]))
            print('Amplifier data of [PORT.%s - CH.%03d] is missing!' % (port.capitalize(), i))
    return port_amp_data


def intan_port_aux_read(aux_path, port, n):
    """Batch import auxiliary input data for every channel on a single IntanTech RHD2000 recording port.

    Iterates over the expected per-channel filenames (``aux-<Port>-AUXn.dat``). Channels with no matching file are
    returned as empty arrays, and a warning is printed for each missing file.

    Args:
        aux_path (str): Directory holding the ``One File Per Channel`` auxiliary input files
        port (str): Port name appearing in the filename (case-insensitive; capitalised internally)
        n (int): Number of auxiliary channels expected on the port

    Returns:
        list[np.ndarray]: {1D-float, n} Per-channel auxiliary input traces in volts (V); missing channels
            are returned as empty arrays
    """
    # Get all existing files
    prefix = 'aux-' + port.capitalize()
    files = [f for f in os.listdir(aux_path) if f.startswith(prefix) and f.endswith('.dat')]
    # Initialize variables
    j = 0
    port_aux_data = []
    # Get all channel data
    for i in range(n):
        name = prefix + ('-AUX%d.dat' % i)
        if name == files[j]:
            temp = intan_ch_aux_read(os.path.join(aux_path, name))
            port_aux_data.append(temp)
            j += 1
        else:
            port_aux_data.append(np.array([]))
            print('Auxiliary input data of [PORT.%s - AUX.%d] is missing!' % (port.capitalize(), i))
    return port_aux_data


def intan_port_vdd_read(vdd_path, port, n):
    """Batch import supply voltage data for every channel on a single IntanTech RHD2000 recording port.

    Iterates over the expected per-channel filenames (``vdd-<Port>-VDDn.dat``). Channels with no matching file are
    returned as empty arrays, and a warning is printed for each missing file.

    Args:
        vdd_path (str): Directory holding the ``One File Per Channel`` supply voltage files
        port (str): Port name appearing in the filename (case-insensitive; capitalised internally)
        n (int): Number of supply voltage channels expected on the port

    Returns:
        list[np.ndarray]: {1D-float, n} Per-channel supply voltage traces in volts (V); missing channels
            are returned as empty arrays
    """
    # Get all existing files
    prefix = 'vdd-' + port.capitalize()
    files = [f for f in os.listdir(vdd_path) if f.startswith(prefix) and f.endswith('.dat')]
    # Initialize variables
    j = 0
    port_vdd_data = []
    # Get all channel data
    for i in range(n):
        name = prefix + ('-VDD%d.dat' % i)
        if name == files[j]:
            temp = intan_ch_vdd_read(os.path.join(vdd_path, name))
            port_vdd_data.append(temp)
            j += 1
        else:
            port_vdd_data.append(np.array([]))
            print('Auxiliary input data of [PORT.%s - VDD.%d] is missing!' % (port.capitalize(), i))
    return port_vdd_data


def intan_board_adc_read(adc_path, n, irc=False):
    """Batch import board ADC input data for every channel on a single IntanTech RHD2000 recording board.

    Iterates over the expected per-channel filenames (``board-ADC-NN.dat``). Channels with no matching file are
    returned as empty arrays, and a warning is printed for each missing file.

    Args:
        adc_path (str): Directory holding the ``One File Per Channel`` ADC input files
        n (int): Number of board ADC channels expected
        irc (bool): Set to :data:`True` when the files were produced by an Intan Recording Controller; the
            conversion factor becomes ``(sample - 32768) * 0.0003125`` instead of ``sample * 0.000050354``
            (default: ``False``)

    Returns:
        list[np.ndarray]: {1D-float, n} Per-channel ADC input traces in volts (V); missing channels are
            returned as empty arrays
    """
    # Get all existing files
    files = [f for f in os.listdir(adc_path) if f.startswith('board-ADC-') and f.endswith('.dat')]
    # Initialize variables
    j = 0
    board_adc_data = []
    # Get all channel data
    for i in range(n):
        name = 'board-ADC-%02d.dat' % i
        if name == files[j]:
            temp = intan_ch_adc_read(os.path.join(adc_path, name), irc)
            board_adc_data.append(temp)
            j += 1
        else:
            board_adc_data.append(np.array([]))
            print('Board ADC input data [%02d] is missing!' % i)
    return board_adc_data


def intan_board_din_read(din_path, n):
    """Batch import board digital input data for every channel on a single IntanTech RHD2000 recording board.

    Iterates over the expected per-channel filenames (``board-DIN-NN.dat``). Channels with no matching file are
    returned as empty arrays, and a warning is printed for each missing file.

    Args:
        din_path (str): Directory holding the ``One File Per Channel`` digital input files
        n (int): Number of board digital input channels expected

    Returns:
        list[np.ndarray]: {1D-int[0|1], n} Per-channel digital input traces (0 or 1); missing channels are
            returned as empty arrays
    """
    # Get all existing files
    files = [f for f in os.listdir(din_path) if f.startswith('board-DIN-') and f.endswith('.dat')]
    # Initialize variables
    j = 0
    board_din_data = []
    # Get all channel data
    for i in range(n):
        name = 'board-DIN-%02d.dat' % i
        if name == files[j]:
            temp = intan_ch_dio_read(os.path.join(din_path, name))
            board_din_data.append(temp)
            j += 1
        else:
            board_din_data.append(np.array([]))
            print('Board digital input data [%02d] is missing!' % i)
    return board_din_data


def intan_board_dout_read(dout_path, n):
    """Batch import board digital output data for every channel on a single IntanTech RHD2000 recording board.

    Iterates over the expected per-channel filenames (``board-DOUT-NN.dat``). Channels with no matching file are
    returned as empty arrays, and a warning is printed for each missing file.

    Args:
        dout_path (str): Directory holding the ``One File Per Channel`` digital output files
        n (int): Number of board digital output channels expected

    Returns:
        list[np.ndarray]: {1D-int[0|1], n} Per-channel digital output traces (0 or 1); missing channels are
            returned as empty arrays
    """
    # Get all existing files
    files = [f for f in os.listdir(dout_path) if f.startswith('board-DOUT-') and f.endswith('.dat')]
    # Initialize variables
    j = 0
    board_dout_data = []
    # Get all channel data
    for i in range(n):
        name = 'board-DOUT-%02d.dat' % i
        if name == files[j]:
            temp = intan_ch_dio_read(os.path.join(dout_path, name))
            board_dout_data.append(temp)
            j += 1
        else:
            board_dout_data.append(np.array([]))
            print('Board digital output data [%02d] is missing!' % i)
    return board_dout_data
