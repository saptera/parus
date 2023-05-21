# Tucker-Davis Technologies file IO functions

import copy
import numpy as np

"""Function list:
    tdt_tsq_read(tsq_file): Import Tucker-Davis Technologies data storage event headers.
    tdt_tev_read(tev_file, tsq, name=None): Import Tucker-Davis Technologies data storage raw voltage traces.
    tdt_chs_arng(ch_dat): Arrange Tucker-Davis Technologies single channel raw data into 2 arrays of signal and time.
# Private variables:
    __tsq_dt {np.dtype}: TDT event header structured array datatype definition.
    __long2char4 {np.vectorize}: TDT event header store ID long to string conversion elementwise function.
    __tev_dt {dict[str, list[int or str]]}: TDT raw voltage traces datatype definition.
"""


# TDT event header structured array datatype definition
__tsq_dt = np.dtype(
    {'names': ('size', 'type', 'name', 'channel', 'sortcode', 'timestamp', 'fp_loc', 'strobe', 'format', 'frequency'),
     'formats': ('int32', 'int32', 'uint32', 'uint16', 'uint16', 'float64', 'int64', 'float64', 'int32', 'float32'),
     'offsets': (0, 4, 8, 12, 14, 16, 24, 24, 32, 36)}, align=True)

# TDT event header store ID long to string conversion elementwise function
__long2char4 = np.vectorize(lambda x: ''.join(chr(x >> (i << 3) & 0xFF) for i in range(4)) if x > 9999 else '%04d' % x)

# TDT raw voltage traces datatype definition
__tev_dt = {'count': [1, 1, 2, 4], 'dtype': ['float32', 'int32', 'int16', 'int8']}


def tdt_tsq_read(tsq_file):
    """ Import Tucker-Davis Technologies data storage event headers.

    Args:
        tsq_file (str): Tucker-Davis Technologies event header file (*.tsq)

    Returns:
        dict[str, np.ndarray]: Recording event headers
            - size (int32): The length of this record
            - type (int32): Event type
            - name (str): Store ID, 4 characters string
            - channel (uint16): Channel number
            - sortcode (int32): Type for spike-sorting
            - timestamp (int32): Data timestamps
            File storage position, only ONE valid at a time:
                - fp_loc (int64): File pointer location in TEV where A/D samples reside
                - strobe (float64): Data transfer strobe control
            - format (int32): Data format ID
            - frequency (float32): Sampling frequency
    """
    # Read data
    raw = np.fromfile(tsq_file, dtype=__tsq_dt)
    tsq = {key: raw[key] for key in raw.dtype.names}
    # Type cast ['name'] key from [uint32] to [str] of 4 characters
    tsq['name'] = __long2char4(tsq['name'])
    return tsq


def tdt_tev_read(tev_file, tsq, name=None):
    """ Import Tucker-Davis Technologies data storage raw voltage traces.

    Args:
        tev_file (str): Tucker-Davis Technologies raw voltage trace file (*.tev)
        tsq (dict[str, np.ndarray]): Tucker-Davis Technologies data storage event header info
        name (str or list[str] or None): Store ID(s) to read, set None to read all (default: None)

    Returns:
        dict[str, dict[int, dict]]: Recording raw voltage traces
            - store_id (dict[str, dict]): All channel data with defined store ID
                - channel (dict[int, dict]): Single channel data with defined store ID
                    - signal (np.ndarray): {2D} Raw voltage trace, row synced with [timestamp], col stored waveform
                    - timestamp (np.ndarray): {1D} Timestamp of key positions
                    - sortcode (np.ndarray): {1D} Raw trace sorting info
                    - frequency (float): Sampling frequency of the trace
    """
    # Check input type
    if name is None:
        name = np.unique(tsq['name'])
    else:
        if type(name) == str:
            name = [name]
    # Process import
    fp = open(tev_file, 'rb')
    tev = {n: {} for n in name}  # INIT VAR
    for n in name:
        # Locate data indices
        idx = np.where(tsq['name'] == n)[0]
        info = {k: tsq[k][idx] for k in tsq}
        # Get data basic info
        chs = np.unique(info['channel'])
        pos = [np.where(info['channel'] == c)[0] for c in chs]
        dts = [__tev_dt['dtype'][info['format'][p][0]] for p in pos]
        fsc = [info['frequency'][p][0].item() for p in pos]
        # Get data timing info
        tms = [info['timestamp'][p] for p in pos]
        stc = [info['sortcode'][p] for p in pos]
        # Get data positions in file
        loc = [info['fp_loc'][p] for p in pos]
        smp = (info['size'] - 10) * [__tev_dt['count'][i] for i in info['format']]
        smp = [smp[p] for p in pos]
        # Set data structure
        data = {c: {'signal': np.zeros((len(smp[i]), max(smp[i])), dtype=dts[i]),
                    'timestamp': tms[i], 'sortcode': stc[i], 'frequency': fsc[i]} for i, c in enumerate(chs)}
        # Read data
        for i, c in enumerate(chs):
            for p in range(len(pos[i])):
                fp.seek(loc[i][p], 0)
                data[c]['signal'][p] = np.fromfile(fp, dtype=dts[i], count=smp[i][p])
        tev[n] = copy.deepcopy(data)
    fp.close()
    return tev


def tdt_chs_arng(ch_dat):
    """ Arrange Tucker-Davis Technologies single channel raw data into 2 arrays of signal and time.

    Args:
        ch_dat (dict[str, np.ndarray or float]): Tucker-Davis Technologies single channel raw data

    Returns:
        dict[str, np.ndarray]: Arranged channel recording
            - signal (np.ndarray): {1D} Channel voltage trace
            - timestamp (np.ndarray): {1D} Channel timestamps
    """
    # Flatten signal
    signal = ch_dat['signal'].flatten(order='C')
    # Flatten time
    tm_incr = np.asarray([i / ch_dat['frequency'] for i in range(ch_dat['signal'].shape[1])], dtype='float64')
    timestamp = np.add.outer(ch_dat['timestamp'], tm_incr).flatten(order='C')
    return {'signal': signal, 'timestamp': timestamp}
