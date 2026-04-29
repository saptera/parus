# -*- coding: utf-8 -*-

"""MATLAB file import module

Importers for MATLAB ``*.mat`` files spanning the v5/v7 format (handled by ``scipy.io``) and the v7.3
HDF5-based format (handled by ``h5py``).
"""

import h5py as h5
import numpy as np
import scipy.io as sio

__package__ = 'parus.fio'
__name__ = 'parus.fio.matlab'
from .hdf import h5_load_dat, h5_load_ref

__all__ = ['mat_meta_read', 'mat_data_read']
"""
Public function list:

- mat_meta_read(file)        : Read MATLAB MAT file header metadata
- mat_data_read(file, rtmt)  : Read MATLAB MAT file data, optionally returning the metadata as well
"""


def mat_meta_read(file):
    """Read MATLAB MAT file header metadata.

    Parses the human-readable ASCII header that MATLAB writes at the start of every MAT file (v5, v7, and v7.3)
    to recover the file version, the originating MATLAB platform, the HDF5 flag, and the recorded creation timestamp.

    Args:
        file (str): Path to the MATLAB MAT file (``*.mat``)

    Returns:
        dict[str, float | str | bool]: MAT file header

            - version (float): MAT file version
            - platform (str): MATLAB platform string
            - hdf (bool): :data:`True` if the file uses the HDF5-based v7.3 format
            - date (str): MAT file creation timestamp as written by MATLAB (locale-dependent format)
    """
    # Read MAT file header
    header = ''  # INIT VAR
    with open(file, 'rb') as ts:
        b = ts.read(1)
        while b != b'\x00':
            try:
                header += b.decode()
            except UnicodeDecodeError:
                pass
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
    """Read the data payload of a MATLAB MAT file.

    The MAT file format is auto-detected via :func:`mat_meta_read`. v7.3 files are opened with ``h5py`` and
    walked with :func:`parus.fio.hdf.h5_load_dat`/:func:`parus.fio.hdf.h5_load_ref`; v5/v7 files are opened
    with :func:`scipy.io.loadmat` and unwrapped from the nested ``numpy.void`` structures that SciPy returns.

    Args:
        file (str): Path to the MATLAB MAT file (``*.mat``)
        rtmt (bool): When :data:`True`, also return the parsed metadata dictionary alongside the data
            (default: ``False``)

    Returns:
        dict | tuple[dict, dict]: The decoded MAT file payload as a nested dictionary; when ``rtmt`` is
            :data:`True`, a ``(data, meta)`` tuple where ``meta`` is the dictionary returned by :func:`mat_meta_read`
    """
    # Read metadata
    meta = mat_meta_read(file)

    # MATLAB v7.3 MAT-file, with HDF5 file structure
    if meta['hdf']:
        fp = h5.File(file, mode='r')

        def __check_reference(obj):
            """Recursively dereference HDF5 object references that appear in v7.3 MAT files.

            MATLAB encodes character arrays as ``uint16`` blobs and uses ``object`` arrays of HDF5 references for nested
            structures. This helper folds both back into native Python types.

            Args:
                obj: Value drawn from the v7.3 MAT structure (typically the output of
                    :func:`parus.fio.hdf.h5_load_dat`)

            Returns:
                The fully dereferenced value (string, list, dict, or :class:`numpy.ndarray` as appropriate)
            """
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
            """Flatten the nested ``numpy.void``/``object`` arrays produced by :func:`scipy.io.loadmat`.

            SciPy wraps every cell, struct, and string in additional array dimensions. This helper unwraps
            single-element wrappers and converts ``void`` records into regular dictionaries.

            Args:
                obj: Value drawn from the SciPy MAT structure

            Returns:
                The unwrapped value (string, list, dict, or :class:`numpy.ndarray` as appropriate)
            """
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
