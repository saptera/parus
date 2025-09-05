# MATLAB file import functions

import h5py as h5
import numpy as np
import scipy.io as sio

__package__ = 'parus.fio'
from .hdf import h5_load_dat, h5_load_ref

__all__ = ['mat_meta_read', 'mat_data_read']
"""
Function list:
  mat_meta_read(file): Read MATLAB MAT file header metadata.
  mat_data_read(file, meta): Read MATLAB MAT file data.
"""


def mat_meta_read(file):
    """ Read MATLAB MAT file header metadata.

    Args:
        file (str): MATLAB MAT file path

    Returns:
        dict[str, float | str | bool | str]: MAT file header
            - version (float): MAT file version
            - platform (str): MATLAB platform
            - hdf (bool): MAT file HDF standard flag
            - date (str): MAT file creation time (locale format)
    """
    # Read MAT file header
    header = ''  # INIT VAR
    with open(file, 'rb') as ts:
        b = ts.read(1)
        while b != b'\x00':
            header += b.decode()
            b = ts.read(1)
    header = header.strip()  # Remove blanks

    # Parse header data
    meta = {}  # INIT VAR
    part = header.split(', ')
    meta['version'] = float(part[0].split(' ')[1])  # MAT file version
    meta['platform'] = part[1].split(': ')[-1]  # MATLAB platform
    meta['hdf'] = 'HDF' in header  # Check if the MAT file use HDF format
    ds = part[2].split(' HDF')[0] if meta['hdf'] else part[2]  # Get creation data string
    meta['date'] = ds.split(': ')[-1]
    return meta


def mat_data_read(file, rtmt=False):
    """ Read MATLAB MAT file data.

    Args:
        file (str): MATLAB MAT file path
        rtmt (bool): Return metadata with the data (default: False = return data only)

    Returns:
        Loaded data
    """
    # Read metadata
    meta = mat_meta_read(file)

    # MATLAB v7.3 MAT-file, with HDF5 file structure
    if meta['hdf']:
        fp = h5.File(file, mode='r')

        def __check_reference(obj):
            """ HDF5-MAT recursive reading helper function. """
            if isinstance(obj, np.ndarray):
                if obj.dtype == 'uint16':
                    return bytes(obj).decode('utf-16')
                elif obj.dtype == 'object':
                    rtv = []  # INIT VAR
                    for i in obj.flatten():
                        src = h5_load_ref(i, fp)
                        rtv.append(__check_reference(src))
                    return rtv
                else:
                    return obj
            elif isinstance(obj, dict):
                rtv = {}  # INIT VAR
                for n in obj:
                    rtv[n] = __check_reference(obj[n])
                return rtv
            else:
                return obj

        # Read data
        data = {}  # INIT VAR
        keys = [k for k in fp.keys() if not (k.startswith('#') and k.endswith('#'))]  # Get valid keys
        for k in keys:
            raw = h5_load_dat(fp[k])
            data[k] = __check_reference(raw)
        fp.close()

    # MATLAB v5 and v7 MAT-file
    else:
        raw = sio.loadmat(file)
        ddk = [k for k in raw.keys() if k.startswith('__') and k.endswith('__')]
        [raw.pop(k) for k in ddk]  # Remove dunder keys

        def __unpack_named(obj):
            """ SciPy-MAT output rearrange function. """
            if isinstance(obj, np.ndarray):
                if obj.dtype.type == np.void:
                    rtv = {}  # INIT VAR
                    for n in obj.dtype.names:
                        rtv[n] = __unpack_named(obj[n].flatten().tolist())
                    return rtv
                elif obj.dtype.type == np.str_:
                    return str(obj[0])
                else:
                    return obj
            elif isinstance(obj, list):
                if len(obj) == 1:
                    return __unpack_named(obj[0])
                else:
                    rtv = []  # INIT VAR
                    for i in obj:
                        rtv.append(__unpack_named(i))
                    return rtv
            else:
                return obj

        data = {}  # INIT VAR
        for k in raw:
            data[k] = __unpack_named(raw[k])

    # Return loaded data
    if rtmt:
        return data, meta
    else:
        return data
