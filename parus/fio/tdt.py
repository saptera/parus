# -*- coding: utf-8 -*-

"""Tucker-Davis Technologies file import module

Importers for the TDT ``*.tsq`` event header / ``*.tev`` raw voltage file pair.
"""

import copy
import numpy as np

__package__ = 'parus.fio'
__name__ = 'parus.fio.tdt'

__all__ = ['tdt_tsq_read', 'tdt_tev_read', 'tdt_chs_arng']
"""
Public function list:

- tdt_tsq_read(tsq_file)            : Import Tucker-Davis Technologies data storage event headers
- tdt_tev_read(tev_file, tsq, name) : Import Tucker-Davis Technologies data storage raw voltage traces
- tdt_chs_arng(ch_dat)              : Arrange single-channel raw data into flat signal and time arrays

Private constants:

- __tsq_dt (np.dtype)               : TDT event header structured-array datatype definition
- __long2char4 (np.vectorize)       : Element-wise long-to-4-char-string conversion for store IDs
- __tev_dt (dict[str, list])        : TDT raw voltage trace datatype definition by format ID
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
    """Import a Tucker-Davis Technologies ``*.tsq`` event header file.

    The TSQ file is a flat array of fixed-size event records. The function reads the file as a structured NumPy array,
    splits it into one column per field, and converts the four-character store IDs from their packed integer form to
    readable strings.

    Args:
        tsq_file (str): Path to the Tucker-Davis Technologies event header file (``*.tsq``)

    Returns:
        dict[str, np.ndarray]: One column per event field

            - size (int32): Length of each record
            - type (int32): Event type
            - name (str): Store ID, four-character string
            - channel (uint16): Channel number
            - sortcode (int32): Spike-sorting class
            - timestamp (int32): Event timestamps
            - fp_loc (int64): File pointer offset in the companion ``*.tev`` file (mutually exclusive with
              ``strobe``)
            - strobe (float64): Data transfer strobe value (mutually exclusive with ``fp_loc``)
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
    """Import raw voltage traces from a Tucker-Davis Technologies ``*.tev`` file.

    The TSQ event header is used to locate per-store, per-channel record offsets inside the TEV file. Epoch records
    (format ID ``>= 4``) are skipped. For each requested store ID, signals are reassembled as a 2D array with one row
    per record and one column per sample.

    Args:
        tev_file (str): Path to the Tucker-Davis Technologies raw voltage trace file (``*.tev``)
        tsq (dict[str, np.ndarray]): Event header dictionary returned by :func:`tdt_tsq_read`
        name (str | list[str] | None): Store ID(s) to read; pass :data:`None` to read every store ID present
            in ``tsq`` (default: ``None``)

    Returns:
        dict[str, dict[int, dict]]: Recording raw voltage traces

            - store_id (dict[str, dict]): All channels recorded under a given store ID
                - channel (dict[int, dict]): Per-channel content
                    - signal (np.ndarray): {2D} Raw voltage trace; rows are synchronised with ``timestamp``,
                      columns store waveform samples
                    - timestamp (np.ndarray): {1D} Timestamp of each row
                    - sortcode (np.ndarray): {1D} Sort-code class assigned by the recording system
                    - frequency (float): Sampling frequency of the trace
    """
    # Check input type
    if name is None:
        name = np.unique(tsq['name'])
    else:
        if isinstance(name, str):
            name = [name]
    # Process import
    fp = open(tev_file, 'rb')
    tev = {}  # INIT VAR
    for n in name:
        # Locate data indices
        idx = np.where(tsq['name'] == n)[0]
        info = {k: tsq[k][idx] for k in tsq}
        if info['format'][0] < 4:  # Exclude epoch data
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
    """Flatten a Tucker-Davis Technologies single-channel record into 1D signal and time arrays.

    Each row of ``ch_dat['signal']`` is a contiguous waveform anchored to the matching entry in ``ch_dat['timestamp']``.
    The function unrolls the matrix in row-major order and reconstructs a monotonically increasing timestamp vector by
    adding per-sample offsets at ``1 / frequency``.

    Args:
        ch_dat (dict[str, np.ndarray | float]): Single-channel record produced by :func:`tdt_tev_read`

    Returns:
        dict[str, np.ndarray]: Flat channel recording

            - signal (np.ndarray): {1D} Channel voltage trace
            - timestamp (np.ndarray): {1D} Per-sample timestamps aligned with ``signal``
    """
    # Flatten signal
    signal = ch_dat['signal'].flatten(order='C')
    # Flatten time
    tm_incr = np.asarray([i / ch_dat['frequency'] for i in range(ch_dat['signal'].shape[1])], dtype='float64')
    timestamp = np.add.outer(ch_dat['timestamp'], tm_incr).flatten(order='C')
    return {'signal': signal, 'timestamp': timestamp}
