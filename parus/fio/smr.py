# -*- coding: utf-8 -*-

"""CED Spike2 SMR file import module

Memory-mapped reader for CED Spike2 ``*.smr`` files. Implemented with NumPy structured arrays only, with no external
SMR-specific dependency. Adapted from the `Neo <https://neuralensemble.org/>`_ package by Neural Ensemble.
"""

import numpy as np

__package__ = 'parus.fio'
__name__ = 'parus.fio.smr'

__all__ = ['smr_load', 'smr_parse_header', 'smr_read_raw', 'smr_read_chn', 'smr_conv_wfm', 'smr_conv_tsp']
"""
Public function list:

- Top-level reader:

    - smr_load(file)                          : Load every non-empty channel from a CED Spike2 SMR file

- Low-level helpers:

    - smr_parse_header(fm)                    : Parse the system, channel, and block headers of a mapped SMR file
    - smr_read_raw(fm, chn_info, blk_info)    : Read raw block data for a single channel
    - smr_read_chn(fm, header, idx)           : Read and unit-convert data for a single channel
    - smr_conv_wfm(item, scale, offset)       : Convert raw SMR waveform samples to physical units
    - smr_conv_tsp(item, fac, stack)          : Convert raw SMR timestamp ticks to seconds

Private members:

- __h_sys_dt (np.dtype)                       : System (file) header structured datatype
- __ch_type (dict[int, str])                  : Channel-kind to human-readable name mapping
- __h_chs_dt (np.dtype)                       : Channel header structured datatype
- __h_blk_dt (np.dtype)                       : Block header structured datatype
- __d_chs_dt(kind, n_extra)                   : Build the channel data structured datatype for a given kind
- __parse_struct(fm, dtype, seek)             : Parse a single structured record from the memory-mapped file
"""


# File header type definition
__h_sys_dt = np.dtype([
    ('system_id', 'i2'),
    ('copyright', 'S10'),
    ('creator', 'S8'),
    ('us_per_time', 'i2'),
    ('time_per_adc', 'i2'),
    ('filestate', 'i2'),
    ('first_data', 'i4'),
    ('channels', 'i2'),
    ('chan_size', 'i2'),
    ('extra_data', 'i2'),
    ('buffersize', 'i2'),
    ('os_format', 'i2'),
    ('max_ftime', 'i4'),
    ('dtime_base', 'f8'),
    ('datetime_detail', 'u1'),
    ('datetime_year', 'i2'),
    ('pad', 'S52'),
    ('comment1', 'S80'),
    ('comment2', 'S80'),
    ('comment3', 'S80'),
    ('comment4', 'S80'),
    ('comment5', 'S80')
])

# Channel type definition
__ch_type = {
    0: 'empty',
    1: 'Adc',
    2: 'EventFall',
    3: 'EventRise',
    4: 'EventBoth',
    5: 'Marker',
    6: 'AdcMark',
    7: 'RealMark',
    8: 'TextMark',
    9: 'RealWave'
}

# Channel header type definition
__h_chs_dt = np.dtype([
    ('del_size', 'i2'),
    ('next_del_block', 'i4'),
    ('firstblock', 'i4'),
    ('lastblock', 'i4'),
    ('blocks', 'i2'),
    ('n_extra', 'i2'),
    ('pre_trig', 'i2'),
    ('free0', 'i2'),
    ('py_sz', 'i2'),
    ('max_data', 'i2'),
    ('comment', 'S72'),
    ('max_chan_time', 'i4'),
    ('l_chan_dvd', 'i4'),
    ('phy_chan', 'i2'),
    ('title', 'S10'),
    ('ideal_rate', 'f4'),
    ('kind', 'u1'),
    ('unused1', 'i1')
])


# Channel data type definition
def __d_chs_dt(kind, n_extra=0):
    """Build the structured NumPy datatype that describes the per-record layout of an SMR channel.

    The SMR format encodes ADC waveforms, event timestamps, marker codes, and label text using a small set of channel
    kinds. This helper returns the matching structured ``dtype`` so the channel's binary records can be parsed in-place.

    Args:
        kind (int): SMR channel kind code (1-9; ``0`` and unrecognised values fall back to a void placeholder)
        n_extra (int): Number of extra bytes per record (used by ``AdcMark``, ``RealMark`` and ``TextMark``
            channels) (default: ``0``)

    Returns:
        np.dtype: Structured datatype describing one record of the channel
    """
    # Adc: Raw half precision signal
    if kind == 1:
        dt = [('waveform', 'i2')]
    # Event types
    elif kind in [2, 3, 4]:
        dt = [('tick', 'i4')]
    # Marker
    elif kind == 5:
        dt = [('tick', 'i4'), ('marker', 'i4')]
    # AdcMark: Marker half precision waveform
    elif kind == 6:
        dt = [('tick', 'i4'), ('marker', 'i4'), ('waveform', 'i2', n_extra // 2)]
    # RealMark: Marker single precision waveform
    elif kind == 7:
        dt = [('tick', 'i4'), ('marker', 'i4'), ('waveform', 'f4', n_extra // 4)]
    # TextMark
    elif kind == 8:
        dt = [('tick', 'i4'), ('marker', 'i4'), ('label', 'S%d' % n_extra)]
    # RealWave: Raw half precision waveform
    elif kind == 9:
        dt = [('waveform', 'f4')]
    # Empty and fallback types
    else:
        dt = [('empty', 'V')]  # Void type as a placeholder
    return np.dtype(dt)


# Block header type definition
__h_blk_dt = np.dtype([
    ('pred_block', 'i4'),
    ('succ_block', 'i4'),
    ('start_time', 'i4'),
    ('end_time', 'i4'),
    ('channel_num', 'i2'),
    ('items', 'i2')
])


def __parse_struct(fm, dtype, seek=0):
    """Parse a single structured record from the memory-mapped SMR file.

    String fields are decoded as ISO-8859-1, NUL-padding is stripped, and the leading byte is interpreted as a
    Pascal-style length prefix.

    Args:
        fm (np.memmap): Memory-mapped view of the SMR file
        dtype (np.dtype): Structured datatype describing the record to parse
        seek (int): Byte offset of the record within ``fm`` (default: ``0``)

    Returns:
        dict: Field-name to decoded-value mapping
    """
    last = seek + dtype.itemsize
    h = fm[seek:last].view(dtype)
    info = {}  # INIT VAR
    for k in dtype.names:
        v = h[k][0]
        if dtype[k].kind == 'S':
            v = v.decode('iso-8859-1').lstrip('\x00')  # Decode and remove NULL
            if len(v) > 0:
                n = ord(v[0]) + 1
                v = v[1:n]
        info[k] = v
    return info


# Low level reading functions ---------------------------------------------------------------------------------------- #

def smr_parse_header(fm):
    """Parse the system, channel, and block headers of a memory-mapped SMR file.

    The system header is parsed first; legacy systems with ``system_id < 6`` are normalised by patching the missing
    time-base and datetime fields. Each channel header then contributes its kind-specific extension (scale/offset for
    waveform channels, edge-state for ``EventBoth``, etc.) and finally every block header on the channel chain is
    walked.

    Args:
        fm (np.memmap): Memory-mapped view of the SMR file

    Returns:
        dict: Three sub-dictionaries

            - system (dict): File-level header fields, including ``time_factor`` (seconds per tick)
            - channel (dict[int, dict]): Per-channel header keyed by channel index
            - block (dict[int, list[dict]]): Per-channel list of block headers, each carrying its file offset
    """
    # Parse SMR file header
    sys_info = __parse_struct(fm, __h_sys_dt, seek=0)
    if sys_info['system_id'] < 6:
        sys_info['dtime_base'] = 1e-6
        sys_info['datetime_detail'] = 0
        sys_info['datetime_year'] = 0
    sys_info['time_factor'] = np.float32(sys_info['us_per_time'] * sys_info['dtime_base'])
    diskblock = 512 if sys_info['system_id'] == 9 else 1

    # Parse channel headers
    chs_info = {}  # INIT VAR
    for cid in range(sys_info['channels']):
        pos = 512 + 140 * cid
        chi = __parse_struct(fm, __h_chs_dt, seek=pos)
        pos += __h_chs_dt.itemsize
        # Channel type specific parsing
        if chi['kind'] in [1, 6]:
            dt = np.dtype([('scale', 'f4'), ('offset', 'f4'), ('unit', 'S6')])
            chi.update(__parse_struct(fm, dt, seek=pos))
            pos += dt.itemsize
            dt = np.dtype([('divide', 'i2')]) if sys_info['system_id'] < 6 else np.dtype([('interleave', 'i2')])
            chi.update(__parse_struct(fm, dt, seek=pos))
        elif chi['kind'] in [7, 9]:
            dt = np.dtype([('min', 'f4'), ('max', 'f4'), ('unit', 'S6')])
            chi.update(__parse_struct(fm, dt, seek=pos))
            pos += dt.itemsize
            dt = np.dtype([('divide', 'i2')]) if sys_info['system_id'] < 6 else np.dtype([('interleave', 'i2')])
            chi.update(__parse_struct(fm, dt, seek=pos))
        elif chi['kind'] == 4:
            dt = np.dtype([('init_low', 'u1'), ('next_low', 'u1')])
            chi.update(__parse_struct(fm, dt, seek=pos))
        chi['type'] = __ch_type[chi['kind']]
        # Store header
        chs_info[cid] = chi

    # Parse block headers
    blk_info = {}  # INIT VAR
    for cid in chs_info:
        blk = []  # INIT VAR
        pos = chs_info[cid]['firstblock'] * diskblock
        for b in range(chs_info[cid]['blocks']):
            bki = __parse_struct(fm, __h_blk_dt, seek=pos)
            bki['offset'] = pos + 20  # Header [__h_blk_dt] size = 20
            blk.append(bki)
            pos = bki['succ_block'] * diskblock
        # Store header
        blk_info[cid] = blk

    # Return header info and file mapping
    return {'system': sys_info, 'channel': chs_info, 'block':blk_info}


def smr_conv_wfm(item, scale=1, offset=0):
    """Convert raw SMR waveform samples to physical units.

    The conversion follows the SMR specification ``physical = raw * scale / 6553.6 + offset``, where ``6553.6`` is the
    ratio between the 16-bit ADC range (``65536``) and the SMR full-scale input range (``10`` V).

    Args:
        item (list[np.ndarray]): Per-block raw waveform arrays, in the order returned by :func:`smr_read_raw`
        scale (float): Channel scale factor from the channel header (default: ``1``)
        offset (float): Channel offset from the channel header (default: ``0``)

    Returns:
        np.ndarray: {1D-float32} Concatenated waveform in the channel's physical unit, or an empty array
            when ``item`` is empty
    """
    if item:
        item = np.hstack(item) * scale / 6553.6 + offset  # 6553.6 = [ADC range 65536] / [Input range 10(V)]
    else:
        item = np.asarray([])
    return item.astype(np.float32)


def smr_conv_tsp(item, fac, stack=False):
    """Convert raw SMR timestamp ticks to seconds.

    The SMR file stores timestamps as integer ticks of the system time base. Multiplying by the recording
    ``time_factor`` (returned by :func:`smr_parse_header`) yields seconds.

    Args:
        item (list[np.ndarray]): Per-block raw timestamp arrays
        fac (float): Recording time-base factor (seconds per tick)
        stack (bool): When :data:`True` concatenate ``item`` along the last axis; when :data:`False`
            squeeze a leading axis of size one (default: ``False``)

    Returns:
        np.ndarray: {1D-float32} Timestamps in seconds, or an empty array when ``item`` is empty
    """
    if item:
        item = np.hstack(item) if stack else np.squeeze(item, axis=0)
        item = item * fac
    else:
        item = np.asarray([])
    return item.astype(np.float32)


def smr_read_raw(fm, chn_info, blk_info):
    """Read the raw block-level data of a single SMR channel.

    Walks the block header list, slices each block out of the memory-mapped file using the channel's structured
    datatype, and concatenates the per-field results into lists. For waveform-bearing channels a matching list of
    per-block ``time`` arrays is also produced (linearly spaced between the block's ``start_time`` and ``end_time``).

    Args:
        fm (np.memmap): Memory-mapped view of the SMR file
        chn_info (dict): Channel header (entry of ``smr_parse_header(...)['channel']``)
        blk_info (list[dict]): Block headers for the channel (entry of ``smr_parse_header(...)['block']``)

    Returns:
        dict[str, list[np.ndarray]]: Per-field, per-block raw arrays. The set of keys depends on the
            channel kind (``waveform``, ``tick``, ``marker``, ``label``, ...); waveform-bearing channels
            also have a ``time`` key
    """
    # Get data info
    dt = __d_chs_dt(chn_info['kind'], chn_info['n_extra'])
    data = {k: [] for k in dt.names}  # INIT VAR
    if 'waveform' in data:
        wfm = True
        data['time'] = []  # Insert time array
    else:
        wfm = False
    # Read raw data
    for blk in blk_info:
        # Arrange data
        ii = blk['offset']
        it = blk['items'] * dt.itemsize + ii
        raw = fm[ii:it].view(dt)
        for k in dt.names:
            data[k].append(np.asarray(raw[k]))
        if wfm:
            # Compute time constants
            time = np.linspace(blk['start_time'], blk['end_time'], blk['items'], endpoint=True, dtype=np.float32)
            data['time'].append(time.copy())
    # Squeeze and return
    return data


def smr_read_chn(fm, header, idx):
    """Read and unit-convert the data of a single SMR channel.

    Combines :func:`smr_read_raw` with :func:`smr_conv_wfm` and :func:`smr_conv_tsp` so the returned arrays are in
    physical units (volts for waveforms, seconds for timestamps).

    Args:
        fm (np.memmap): Memory-mapped view of the SMR file
        header (dict): Output of :func:`smr_parse_header`
        idx (int): Channel index to read

    Returns:
        dict[str, np.ndarray]: Field-name to converted-array mapping for the channel
    """
    chi = header['channel'][idx]
    bki = header['block'][idx]
    data = smr_read_raw(fm, chi, bki)
    for k in data:
        if k == 'waveform':
            data[k] = smr_conv_wfm(data[k], scale=chi['scale'], offset=chi['offset'])
        elif k == 'time':
            data[k] = smr_conv_tsp(data[k], fac=header['system']['time_factor'], stack=True)
        elif k in ['tick', 'marker']:
            data[k] = smr_conv_tsp(data[k], fac=header['system']['time_factor'], stack=False)
    return data


# Reading function --------------------------------------------------------------------------------------------------- #

def smr_load(file):
    """Load every non-empty channel from a CED Spike2 SMR file.

    The file is memory-mapped read-only, headers are parsed with :func:`smr_parse_header`, and each non-empty channel
    is read with :func:`smr_read_chn`. Channels are keyed by their textual ``title`` from the channel header rather
    than by index.

    Args:
        file (str): Path to the CED Spike2 SMR file (``*.smr``)

    Returns:
        dict[str, dict[str, np.ndarray]]: Mapping from channel title to the converted channel data returned
            by :func:`smr_read_chn`
    """
    # Map file
    fm = np.memmap(file, dtype='u1', offset=0, mode='r')
    # Parse header
    header = smr_parse_header(fm)
    # Load data
    data = {}  # INIT VAR
    for c in header['channel']:
        if header['channel'][c]['kind'] != 0:
            data[header['channel'][c]['title']] = smr_read_chn(fm, header, c)
    # Close file and return
    fm._mmap.close()
    del fm
    return data
