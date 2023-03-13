# IntanTech file IO functions

import os
import numpy as np

"""Function list:
# For single file:
    intan_time_read(time_file, freq):  Import IntanTech RHD2000 "One File Per Channel" formatted [timestamp] data.
    intan_amp_read(amp_file):  Import IntanTech RHD2000 "One File Per Channel" formatted [amplifier] data.
    intan_aux_read(aux_file):  Import IntanTech RHD2000 "One File Per Channel" formatted [auxiliary input] data.
    intan_vdd_read(vdd_file):  Import IntanTech RHD2000 "One File Per Channel" formatted [supply voltage] data.
    intan_adc_read(adc_file):  Import IntanTech RHD2000 "One File Per Channel" formatted [BOARD ADC input] data.
    intan_dio_read(dio_file):  Import IntanTech RHD2000 "One File Per Channel" formatted [BOARD digital I/O] data.
# For file batch:
    intan_port_amp_read(amp_path, port, n):  Import IntanTech RHD2000 [amplifier] data in one recording PORT.
    intan_port_aux_read(aux_path, port, n):  Import IntanTech RHD2000 [auxiliary input] data in one recording PORT.
    intan_port_vdd_read(vdd_path, port, n):  Import IntanTech RHD2000 [supply voltage] data in one recording PORT.
    intan_board_adc_read(adc_path, n):  Import IntanTech RHD2000 [BOARD ADC input] data in one recording BOARD.
    intan_board_din_read(din_path, n):  Import IntanTech RHD2000 [BOARD digital input] data in one recording BOARD.
    intan_board_dout_read(din_path, n):  Import IntanTech RHD2000 [BOARD digital output] data in one recording BOARD.
"""


# For single file ---------------------------------------------------------------------------------------------------- #

def intan_time_read(time_file, freq):
    """ Import IntanTech RHD2000 "One File Per Channel" formatted [timestamp] data.

    Args:
        time_file (str): IntanTech RHD2000 "One File Per Channel" formatted time file.
        freq (int): Sampling frequency of the recording (Hertz / Hz).

    Returns:
        np.ndarray: {1D} NumPy 1D array containing time data (Seconds / s).
    """
    f = open(time_file, 'rb')    # Read in as binary file
    dat = np.fromfile(f, dtype=np.int32)    # Data type in binary file: INT32
    f.close()
    time_data = dat / freq    # Convert sequential integers to actual time vector
    return time_data


def intan_amp_read(amp_file):
    """ Import IntanTech RHD2000 "One File Per Channel" formatted [amplifier] data.

    Args:
        amp_file (str): IntanTech RHD2000 "One File Per Channel" formatted amplifier file.

    Returns:
        np.ndarray: {1D} NumPy 1D array containing amplifier data (microVolts / mV).
    """
    f = open(amp_file, 'rb')    # Read in as binary file
    dat = np.fromfile(f, dtype=np.int16)    # Data type in binary file: INT16
    f.close()
    amp_data = np.round((dat * 0.195), 3)    # Conversion factor to mV: 0.195, round to avoid FLOAT artifact
    return amp_data


def intan_aux_read(aux_file):
    """ Import IntanTech RHD2000 "One File Per Channel" formatted [auxiliary input] data.

    Args:
        aux_file (str): IntanTech RHD2000 "One File Per Channel" formatted auxiliary input file.

    Returns:
        np.ndarray: {1D} NumPy 1D array containing auxiliary input data (Volts / V).
    """
    f = open(aux_file, 'rb')    # Read in as binary file
    dat = np.fromfile(f, dtype=np.uint16)    # Data type in binary file: UINT16
    f.close()
    aux_data = np.round((dat * 0.0000374), 7)    # Conversion factor to V: 0.0000374, round to avoid FLOAT artifact
    return aux_data


def intan_vdd_read(vdd_file):
    """ Import IntanTech RHD2000 "One File Per Channel" formatted [supply voltage] data.

    Args:
        vdd_file (str): IntanTech RHD2000 "One File Per Channel" formatted supply voltage file.

    Returns:
        np.ndarray: {1D} NumPy 1D array containing supply voltage data (Volts / V).
    """
    f = open(vdd_file, 'rb')    # Read in as binary file
    dat = np.fromfile(f, dtype=np.uint16)    # Data type in binary file: UINT16
    f.close()
    vdd_data = np.round((dat * 0.0000748), 7)    # Conversion factor to V: 0.0000748, round to avoid FLOAT artifact
    return vdd_data


def intan_adc_read(adc_file):
    """ Import IntanTech RHD2000 "One File Per Channel" formatted [BOARD ADC input] data.

    Args:
        adc_file (str): IntanTech RHD2000 "One File Per Channel" formatted ADC input file.

    Returns:
        np.ndarray: {1D} NumPy 1D array containing ADC input data (Volts / V).
    """
    f = open(adc_file, 'rb')    # Read in as binary file
    dat = np.fromfile(f, dtype=np.uint16)    # Data type in binary file: UINT16
    f.close()
    adc_data = np.round((dat * 0.000050354), 9)    # Conversion factor to V: 0.000050354, round to avoid FLOAT artifact
    return adc_data


def intan_dio_read(dio_file):
    """ Import IntanTech RHD2000 "One File Per Channel" formatted [BOARD digital I/O] data.

    Args:
        dio_file (str): IntanTech RHD2000 "One File Per Channel" formatted digital I/O file.

    Returns:
        np.ndarray: {1D} NumPy 1D array containing digital I/O data (0 | 1).
    """
    f = open(dio_file, 'rb')    # Read in as binary file
    dio_data = np.fromfile(f, dtype=np.uint16)    # Data type in binary file: UINT16
    f.close()
    return dio_data


# For file batch ----------------------------------------------------------------------------------------------------- #

def intan_port_amp_read(amp_path, port, n):
    """ Import IntanTech RHD2000 [amplifier] data in one recording PORT.

    Args:
        amp_path (str): IntanTech RHD2000 "One File Per Channel" formatted amplifier files stored path.
        port (str): IntanTech RHD2000 recording amplifier port name.
        n (int): Number of channels at defined port

    Returns:
        list[np.ndarray]: {[1D]} List of NumPy 1D array containing amplifier data (microVolts / mV).
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
            temp = intan_amp_read(os.path.join(amp_path, name))
            port_amp_data.append(temp)
            j += 1
        else:
            port_amp_data.append(np.array([]))
            print('Amplifier data of [PORT.%s - CH.%03d] is missing!' % (port.capitalize(), i))
    return port_amp_data


def intan_port_aux_read(aux_path, port, n):
    """ Import IntanTech RHD2000 [auxiliary input] data in one recording PORT.

    Args:
        aux_path (str): IntanTech RHD2000 "One File Per Channel" formatted auxiliary input files stored path.
        port (str): IntanTech RHD2000 recording auxiliary input port name.
        n (int): Number of channels at defined port

    Returns:
        list[np.ndarray]: {[1D]} List of NumPy 1D array containing auxiliary input data (Volts / V).
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
            temp = intan_aux_read(os.path.join(aux_path, name))
            port_aux_data.append(temp)
            j += 1
        else:
            port_aux_data.append(np.array([]))
            print('Auxiliary input data of [PORT.%s - AUX.%d] is missing!' % (port.capitalize(), i))
    return port_aux_data


def intan_port_vdd_read(vdd_path, port, n):
    """ Import IntanTech RHD2000 [supply voltage] data in one recording PORT.

    Args:
        vdd_path (str): IntanTech RHD2000 "One File Per Channel" formatted supply voltage files stored path.
        port (str): IntanTech RHD2000 recording supply voltage port name.
        n (int): Number of channels at defined port

    Returns:
        list[np.ndarray]: {[1D]} List of NumPy 1D array containing supply voltage data (Volts / V).
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
            temp = intan_vdd_read(os.path.join(vdd_path, name))
            port_vdd_data.append(temp)
            j += 1
        else:
            port_vdd_data.append(np.array([]))
            print('Auxiliary input data of [PORT.%s - VDD.%d] is missing!' % (port.capitalize(), i))
    return port_vdd_data


def intan_board_adc_read(adc_path, n):
    """ Import IntanTech RHD2000 [BOARD ADC input] data in one recording BOARD.

    Args:
        adc_path (str): IntanTech RHD2000 "One File Per Channel" formatted ADC input files stored path.
        n (int): Number of ADC input channels at defined board

    Returns:
        list[np.ndarray]: {[1D]} List of NumPy 1D array containing ADC input data (Volts / V).
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
            temp = intan_adc_read(os.path.join(adc_path, name))
            board_adc_data.append(temp)
            j += 1
        else:
            board_adc_data.append(np.array([]))
            print('Board ADC input data [%02d] is missing!' % i)
    return board_adc_data


def intan_board_din_read(din_path, n):
    """ Import IntanTech RHD2000 [BOARD digital input] data in one recording BOARD.

    Args:
        din_path (str): IntanTech RHD2000 "One File Per Channel" formatted digital input files stored path.
        n (int): Number of digital input channels at defined board

    Returns:
        list[np.ndarray]: {[1D]} List of NumPy 1D array containing digital input data (Volts / V).
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
            temp = intan_dio_read(os.path.join(din_path, name))
            board_din_data.append(temp)
            j += 1
        else:
            board_din_data.append(np.array([]))
            print('Board digital input data [%02d] is missing!' % i)
    return board_din_data


def intan_board_dout_read(dout_path, n):
    """ Import IntanTech RHD2000 [BOARD digital input] data in one recording BOARD.

    Args:
        dout_path (str): IntanTech RHD2000 "One File Per Channel" formatted digital output files stored path.
        n (int): Number of digital input channels at defined board

    Returns:
        list[np.ndarray]: {[1D]} List of NumPy 1D array containing digital output data (Volts / V).
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
            temp = intan_dio_read(os.path.join(dout_path, name))
            board_dout_data.append(temp)
            j += 1
        else:
            board_dout_data.append(np.array([]))
            print('Board digital output data [%02d] is missing!' % i)
    return board_dout_data
