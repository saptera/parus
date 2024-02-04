# IntanTech file import functions

import os
import numpy as np

"""Function list:
# General data files
    intan_time_read(time_file, freq): Import RHD2000 [timestamp] data.
# Datatype [One File Per Signal Type] files:
    intan_typ_amp_read(amp_file, n): Import IntanTech RHD2000 "One File Per Signal Type" [amplifier] data.
    intan_typ_aux_read(aux_file, n): Import IntanTech RHD2000 "One File Per Signal Type" [auxiliary input] data.
    intan_typ_vdd_read(vdd_file, n): Import IntanTech RHD2000 "One File Per Signal Type" [supply voltage] data.
    intan_typ_adc_read(adc_file, n, irc=False): Import IntanTech RHD2000 "One File Per Signal Type" [BOARD ADC in] data.
    intan_typ_dio_read(dio_file): Import IntanTech RHD2000 "One File Per Signal Type" [BOARD digital I/O] data.
# Datatype [One File Per Channel] files:
  # Single channel files:
    intan_ch_amp_read(amp_file): Import IntanTech RHD2000 "One File Per Channel" [amplifier] data.
    intan_ch_aux_read(aux_file): Import IntanTech RHD2000 "One File Per Channel" [auxiliary input] data.
    intan_ch_vdd_read(vdd_file): Import IntanTech RHD2000 "One File Per Channel" [supply voltage] data.
    intan_ch_adc_read(adc_file, irc=False): Import IntanTech RHD2000 "One File Per Channel" [BOARD ADC input] data.
    intan_ch_dio_read(dio_file): Import IntanTech RHD2000 "One File Per Channel" [BOARD digital I/O] data.
  # Batch files:
    intan_port_amp_read(amp_path, port, n): Import IntanTech RHD2000 [amplifier] data in one recording PORT.
    intan_port_aux_read(aux_path, port, n): Import IntanTech RHD2000 [auxiliary input] data in one recording PORT.
    intan_port_vdd_read(vdd_path, port, n): Import IntanTech RHD2000 [supply voltage] data in one recording PORT.
    intan_board_adc_read(adc_path, n, irc=False): Import IntanTech RHD2000 [BOARD ADC input] data in one BOARD.
    intan_board_din_read(din_path, n): Import IntanTech RHD2000 [BOARD digital input] data in one recording BOARD.
    intan_board_dout_read(din_path, n): Import IntanTech RHD2000 [BOARD digital output] data in one recording BOARD.
"""


# General data files ------------------------------------------------------------------------------------------------- #

def intan_time_read(time_file, freq):
    """ Import IntanTech RHD2000 [timestamp] data.

    Args:
        time_file (str): IntanTech RHD2000 timestamp file
        freq (int): Sampling frequency of the recording (Hertz / Hz)

    Returns:
        np.ndarray: {1D-float} NumPy 1D array containing time data (Seconds / s)
    """
    fp = open(time_file, 'rb')
    dat = np.fromfile(fp, dtype=np.int32)  # Data type in binary file: INT32
    fp.close()
    time_data = dat / freq  # Convert sequential integers to actual time vector
    return time_data


# [One File Per Signal Type] files ----------------------------------------------------------------------------------- #

def intan_typ_amp_read(amp_file, n):
    """ Import IntanTech RHD2000 "One File Per Signal Type" [amplifier] data.

    Args:
        amp_file (str): IntanTech RHD2000 "One File Per Signal Type" formatted amplifier file
        n (int): Number of channels at defined file

    Returns:
        list[np.ndarray]: {1D-float, n} List of NumPy 1D array containing amplifier data (microVolts / mV)
    """
    fp = open(amp_file, 'rb')
    dat = np.fromfile(fp, dtype=np.int16)  # Data type in binary file: INT16
    fp.close()
    mat = np.reshape(dat, (n, dat.size // n), order='F')  # Reshape matrix with column-major order
    del dat
    amp_data = [np.round((s * 0.195), 3).astype('float32') for s in mat]  # Conversion factor to mV: 0.195
    return amp_data


def intan_typ_aux_read(aux_file, n):
    """ Import IntanTech RHD2000 "One File Per Signal Type" [auxiliary input] data.

    Args:
        aux_file (str): IntanTech RHD2000 "One File Per Signal Type" formatted auxiliary input file
        n (int): Number of channels at defined file

    Returns:
        list[np.ndarray]: {1D-float, n} List of NumPy 1D array containing auxiliary input data (Volts / V)
    """
    fp = open(aux_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    mat = np.reshape(dat, (n, dat.size // n), order='F')  # Reshape matrix with column-major order
    aux_data = [np.round((s * 0.0000374), 7) for s in mat]  # Conversion factor to V: 0.0000374
    return aux_data


def intan_typ_vdd_read(vdd_file, n):
    """ Import IntanTech RHD2000 "One File Per Signal Type" [supply voltage] data.

    Args:
        vdd_file (str): IntanTech RHD2000 "One File Per Signal Type" formatted supply voltage file
        n (int): Number of channels at defined file

    Returns:
        list[np.ndarray]: {1D-float, n} List of NumPy 1D array containing supply voltage data (Volts / V)
    """
    fp = open(vdd_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    mat = np.reshape(dat, (n, dat.size // n), order='F')  # Reshape matrix with column-major order
    vdd_data = [np.round((s * 0.0000748), 7) for s in mat]  # Conversion factor to V: 0.0000748
    return vdd_data


def intan_typ_adc_read(adc_file, n, irc=False):
    """ Import IntanTech RHD2000 "One File Per Signal Type" [BOARD ADC input] data.

    Args:
        adc_file (str): IntanTech RHD2000 "One File Per Signal Type" formatted ADC input file
        n (int): Number of channels at defined file
        irc (bool): Set to True if the data file was generated by an Intan Recording Controller (default: False)

    Returns:
        list[np.ndarray]: {1D-float, n} List of NumPy 1D array containing ADC input data (Volts / V)
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
    """ Import IntanTech RHD2000 "One File Per Signal Type" [BOARD digital I/O] data.

    Args:
        dio_file (str): IntanTech RHD2000 "One File Per Signal Type" formatted supply digital I/O file

    Returns:
        list[np.ndarray]: {1D-int[0|1], 16} List of NumPy 1D array containing digital I/O data (0 | 1)
    """
    fp = open(dio_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    dio_data = [np.clip(np.bitwise_and(dat, 2 ** s), a_min=0, a_max=1) for s in range(16)]  # 16 channels in total
    return dio_data


# [One File Per Channel] Single channel files ------------------------------------------------------------------------ #

def intan_ch_amp_read(amp_file):
    """ Import IntanTech RHD2000 "One File Per Channel" [amplifier] data.

    Args:
        amp_file (str): IntanTech RHD2000 "One File Per Channel" formatted amplifier file

    Returns:
        np.ndarray: {1D-float} NumPy 1D array containing amplifier data (microVolts / mV)
    """
    fp = open(amp_file, 'rb')
    dat = np.fromfile(fp, dtype=np.int16)  # Data type in binary file: INT16
    fp.close()
    amp_data = np.round((dat * 0.195), 3).astype('float32')  # Conversion factor to mV: 0.195, round to avoid artifact
    return amp_data


def intan_ch_aux_read(aux_file):
    """ Import IntanTech RHD2000 "One File Per Channel" [auxiliary input] data.

    Args:
        aux_file (str): IntanTech RHD2000 "One File Per Channel" formatted auxiliary input file

    Returns:
        np.ndarray: {1D-float} NumPy 1D array containing auxiliary input data (Volts / V)
    """
    fp = open(aux_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    aux_data = np.round((dat * 0.0000374), 7)  # Conversion factor to V: 0.0000374, round to avoid artifact
    return aux_data


def intan_ch_vdd_read(vdd_file):
    """ Import IntanTech RHD2000 "One File Per Channel" [supply voltage] data.

    Args:
        vdd_file (str): IntanTech RHD2000 "One File Per Channel" formatted supply voltage file

    Returns:
        np.ndarray: {1D-float} NumPy 1D array containing supply voltage data (Volts / V)
    """
    fp = open(vdd_file, 'rb')
    dat = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    vdd_data = np.round((dat * 0.0000748), 7)  # Conversion factor to V: 0.0000748, round to avoid artifact
    return vdd_data


def intan_ch_adc_read(adc_file, irc=False):
    """ Import IntanTech RHD2000 "One File Per Channel" [BOARD ADC input] data.

    Args:
        adc_file (str): IntanTech RHD2000 "One File Per Channel" formatted ADC input file
        irc (bool): Set to True if the data file was generated by an Intan Recording Controller (default: False)

    Returns:
        np.ndarray: {1D-float} NumPy 1D array containing ADC input data (Volts / V)
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
    """ Import IntanTech RHD2000 "One File Per Channel" [BOARD digital I/O] data.

    Args:
        dio_file (str): IntanTech RHD2000 "One File Per Channel" formatted digital I/O file

    Returns:
        np.ndarray: {1D-int[0|1]} NumPy 1D array containing digital I/O data (0 | 1)
    """
    fp = open(dio_file, 'rb')
    dio_data = np.fromfile(fp, dtype=np.uint16)  # Data type in binary file: UINT16
    fp.close()
    return dio_data


# [One File Per Channel] Batch files --------------------------------------------------------------------------------- #

def intan_port_amp_read(amp_path, port, n):
    """ Import IntanTech RHD2000 [amplifier] data in one recording PORT.

    Args:
        amp_path (str): IntanTech RHD2000 "One File Per Channel" formatted amplifier files stored path
        port (str): IntanTech RHD2000 recording amplifier port name
        n (int): Number of channels at defined port

    Returns:
        list[np.ndarray]: {1D-float, n} List of NumPy 1D array containing amplifier data (microVolts / mV)
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
    """ Import IntanTech RHD2000 [auxiliary input] data in one recording PORT.

    Args:
        aux_path (str): IntanTech RHD2000 "One File Per Channel" formatted auxiliary input files stored path
        port (str): IntanTech RHD2000 recording auxiliary input port name
        n (int): Number of channels at defined port

    Returns:
        list[np.ndarray]: {1D-float, n} List of NumPy 1D array containing auxiliary input data (Volts / V)
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
    """ Import IntanTech RHD2000 [supply voltage] data in one recording PORT.

    Args:
        vdd_path (str): IntanTech RHD2000 "One File Per Channel" formatted supply voltage files stored path
        port (str): IntanTech RHD2000 recording supply voltage port name
        n (int): Number of channels at defined port

    Returns:
        list[np.ndarray]: {1D-float, n} List of NumPy 1D array containing supply voltage data (Volts / V)
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
    """ Import IntanTech RHD2000 [BOARD ADC input] data in one recording BOARD.

    Args:
        adc_path (str): IntanTech RHD2000 "One File Per Channel" formatted ADC input files stored path
        n (int): Number of ADC input channels at defined board
        irc (bool): Set to True if the data file was generated by an Intan Recording Controller (default: False)

    Returns:
        list[np.ndarray]: {1D-float, n} List of NumPy 1D array containing ADC input data (Volts / V)
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
    """ Import IntanTech RHD2000 [BOARD digital input] data in one recording BOARD.

    Args:
        din_path (str): IntanTech RHD2000 "One File Per Channel" formatted digital input files stored path
        n (int): Number of digital input channels at defined board

    Returns:
        list[np.ndarray]: {1D-int[0|1], n} List of NumPy 1D array containing digital input data (0| 1)
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
    """ Import IntanTech RHD2000 [BOARD digital input] data in one recording BOARD.

    Args:
        dout_path (str): IntanTech RHD2000 "One File Per Channel" formatted digital output files stored path
        n (int): Number of digital input channels at defined board

    Returns:
        list[np.ndarray]: {1D-int[0|1], n} List of NumPy 1D array containing digital output data (0 | 1)
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
