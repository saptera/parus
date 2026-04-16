# CED Spike2 SMR file import module
# Modified from NEO package (https://neuralensemble.org/) for pure and native file operation

import numpy as np

__package__ = 'parus.fio'
__name__ = 'parus.fio.smr'

__all__ = ['smr_load', 'smr_parse_header', 'smr_read_raw', 'smr_read_chn', 'smr_conv_wfm', 'smr_conv_tsp']
"""
Function list:
  # Low level reading functions:
    smr_parse_header(fm): Parse CED Spike 2 SMR file header information.
    smr_conv_wfm(item, scale=1, offset=0): Convert raw SMR waveform data to the physical unit.
    smr_conv_tsp(item, fac, stack=False): Convert raw SMR timestamp data to the physical seconds.
    smr_read_raw(fm, chn_info, blk_info): Read raw data from SMR channel.
  # Reading function:
    smr_load(file): Load data from CED Spike2 SMR file.
  # Private functions:
    __d_chs_dt(kind, n_extra=0): Get channel data type definition.
    __parse_struct(fm, dtype, seek=0): Parse data with defined structure.
Private constants:
  __h_sys_dt {np.dtype}: File header type definition.
  __ch_type {dict}: Channel type definition.
  __h_chs_dt {np.dtype}: Channel header type definition.
  __h_blk_dt {np.dtype}: Block header type definition.
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
    """ Get channel data type definition.

    Args:
        kind (int): Channel type
        n_extra (int): Extra data type definition (default: 0)

    Returns:
        np.dtype: Channel data type definitions
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
    """ Parse data with defined structure.

    Args:
        fm (np.memmap): CED Spike2 SMR file memory mapping
        dtype (np.dtype): NumPy data type definition
        seek (int): File memory mapping offset

    Returns:
        dict: Parsed data
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
    """ Parse CED Spike 2 SMR file header information.

    Args:
        fm (np.memmap): SMR file memory mapping

    Returns:
        dict: SMR header information
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
    """ Convert raw SMR waveform data to the physical unit.

    Args:
        item (list[np.ndarray]): Raw waveform data from SMR file
        scale (float): Channel scaling factor
        offset (float): Channel offset value

    Returns:
        np.ndarray: {1D-float32} Converted waveform data
    """
    if item:
        item = np.hstack(item) * scale / 6553.6 + offset  # 6553.6 = [ADC range 65536] / [Input range 10(V)]
    else:
        item = np.asarray([])
    return item.astype(np.float32)


def smr_conv_tsp(item, fac, stack=False):
    """ Convert raw SMR timestamp data to the physical seconds.

    Args:
        item (list[np.ndarray]): Raw waveform data from SMR file
        fac (float): Recording file time base factor
        stack (bool): Stack timestamp control flag

    Returns:
        np.ndarray: {1D-float32} Converted timestamp data
    """
    if item:
        item = np.hstack(item) if stack else np.squeeze(item, axis=0)
        item = item * fac
    else:
        item = np.asarray([])
    return item.astype(np.float32)


def smr_read_raw(fm, chn_info, blk_info):
    """ Read raw data from SMR channel.

    Args:
        fm (np.memmap): SMR file memory mapping
        chn_info (dict): Channel header
        blk_info (dict): Channel block header

    Returns:
        dict[list[np.ndarray]]: Raw data from file
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
    """ Read and convert data from SMR channel.

    Args:
        fm (np.memmap): SMR file memory mapping
        header (dict): SMR file header information
        idx (int): Channel index

    Returns:
        dict[np.ndarray]: Raw data from file
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
    """ Load data from CED Spike2 SMR file.

    Args:
        file (str): CED Spike2 SMR file path (`*.smr`)

    Returns:
        dict: Loaded data
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
