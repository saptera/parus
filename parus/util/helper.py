# -*- coding: utf-8 -*-

"""User data helper function module

Helpers for validating, converting, and structuring user-supplied data and labels.
"""

import os
import numpy as np
import h5py as h5
import warnings

__package__ = 'parus.util'
__name__ = 'parus.util.helper'

__all__ = ['check_sampling_frequency', 'check_raw_data', 'create_raw_data_file', 'add_position_groups',
           'timestamp_to_onehot', 'onehot_to_timestamp']
"""
Public function list:

- check_sampling_frequency(fs)               : Validate the data type of sampling frequency and convert when needed
- check_raw_data(raw)                        : Validate the type and shape of raw recording, converting when needed
- create_raw_data_file(file, raw, fs, force) : Create a PARUS-compatible HDF5 file with the given raw recording
- add_position_groups(fp, spk, force)        : Add empty per-channel spike position groups to an open data file
- timestamp_to_onehot(tp, fs, num)           : Convert a spike timestamp array to a one-hot label vector
- onehot_to_timestamp(oh, fs)                : Convert a one-hot spike label vector to a timestamp array
"""


def check_sampling_frequency(fs):
    """Validate the data type of sampling frequency and convert it when necessary.

    The PARUS pipeline expects sampling frequencies stored as ``numpy.float32``. Inputs of any other numeric
    type are auto-converted with a runtime warning.

    Args:
        fs (int | float | np.ndarray | np.float32): Sampling frequency value to validate

    Returns:
        np.float32: Validated or auto-converted sampling frequency

    Raises:
        ValueError: If ``fs`` cannot be converted to ``numpy.float32``
    """
    if isinstance(fs, np.ndarray) and isinstance(fs.dtype, np.dtypes.Float32DType):
        print("Sampling frequency data type is valid")
        return fs
    else:
        try:
            fs = np.float32(fs)
            warnings.warn("Sampling frequency data type is not optimal\n"
                          "    -> Auto-converted to [numpy.float32]", Warning, stacklevel=2)
            return fs
        except ValueError:
            raise ValueError("Invalid sampling frequency data type\n    -> Please verify the input")


def check_raw_data(raw):
    """Validate the type and shape of raw recording, converting and reshaping when necessary.

    Raw recordings are expected as ``numpy.float32`` arrays of shape ``(n_channels, n_samples)``. A 1D array is
    auto-expanded to a single-channel 2D array. A 2D array with ``n_channels > n_samples`` is accepted but triggers a
    warning, since the dimensions are likely transposed.

    Args:
        raw (np.ndarray): Raw recording data to validate; any array-like accepted by :func:`numpy.asarray`
            also works and is converted internally

    Returns:
        np.ndarray: {2D-float32} Validated raw recording with shape ``(n_channels, n_samples)``

    Raises:
        ValueError: If ``raw`` cannot be converted to ``numpy.float32`` or has more than two dimensions
    """
    # Check data type
    if isinstance(raw, np.ndarray):
        if isinstance(raw.dtype, np.dtypes.Float32DType):
            print("Raw data type is optimal")
        else:
            try:
                raw = raw.astype(np.float32)
                warnings.warn("Raw data type is not optimal\n"
                              "    -> Auto-converted to [numpy.float32]", Warning, stacklevel=2)
            except ValueError:
                raise ValueError("Unable to convert raw data to the required type\n    -> Please verify the input")
    else:
        try:
            raw = np.asarray(raw, dtype=np.float32)
            warnings.warn("Raw data type is not optimal\n"
                          "    -> Auto-converted to [numpy.float32]", Warning, stacklevel=2)
        except ValueError:
            raise ValueError("Unable to convert raw data to the required type\n    -> Please verify the input")

    # Check data shape
    if len(raw.shape) == 1:
        raw = raw[np.newaxis, :]
        warnings.warn("Raw data has a single dimension; expected shape: (n_channels, n_samples)\n"
                      "    -> Channel dimension has been expanded", Warning, stacklevel=2)
    elif len(raw.shape) == 2:
        if raw.shape[0] > raw.shape[1]:
            warnings.warn("Number of channels exceeds number of samples; expected shape: (n_channels, n_samples)\n"
                          "    -> Please verify that dimensions are not reversed", Warning, stacklevel=2)
        else:
            print("Raw data shape is valid")
    else:
        raise ValueError("Invalid raw data shape; expected shape: (n_channels, n_samples)")

    return raw


def create_raw_data_file(file, raw, fs, force=False):
    """Create a PARUS-compatible HDF5 file with the given raw recording and sampling frequency.

    The output file contains a top-level ``frq`` dataset (``numpy.float32`` scalar) and a gzip-compressed ``raw``
    dataset of shape ``(n_channels, n_samples)``.

    Args:
        file (str): Output HDF5 file path
        raw (np.ndarray): {2D-float32} Raw recording data with shape ``(n_channels, n_samples)``
        fs (int | float | np.float32): Sampling frequency
        force (bool): When :data:`False` and ``file`` already exists, the existing file is opened in ``r+``
            mode instead of being overwritten (default: ``False``)

    Returns:
        h5.File: Pointer to the newly created or pre-existing HDF5 file (``'r+'`` mode when reusing,
            ``'w'`` mode when fresh)

    Note:
        The returned file pointer remains open. Close it with :meth:`h5py.File.close` once no further
        operations on the file are required.
    """
    # Check file availability
    if os.path.isfile(file) and (not force):
        warnings.warn("Target file already exists in the file; return target file pointer\n"
                      "    -> Set `force=True` to overwrite existing data", Warning, stacklevel=2)
        return h5.File(file, 'r+')
    # Create new file
    fp = h5.File(file, 'w')
    fp.create_dataset(name='frq', data=np.float32(fs))
    fp.create_dataset(name='raw', data=raw, compression='gzip', compression_opts=9)
    return fp


def add_position_groups(fp, spk=None, force=False):
    """Add empty per-channel spike position groups to an open PARUS data file.

    The created hierarchy is ``pos/<waveform_name>/<channel_index>/`` for every waveform name in ``spk`` and
    every channel implied by ``raw.shape[0]``. Existing position groups are preserved unless ``force`` is set.

    Args:
        fp (h5.File): Pointer to an open PARUS HDF5 data file
        spk (list[str] | None): Spike waveform type names; pass :data:`None` to infer from the existing
            ``spk`` group in ``fp`` (default: ``None``)
        force (bool): When :data:`True`, an existing ``pos`` group is deleted before recreation
            (default: ``False``)

    Returns:
        h5.File: The same file pointer ``fp`` (returned for chaining convenience)

    Raises:
        ValueError: If ``raw`` is missing from ``fp`` (channel count cannot be determined) or if ``spk`` is
            :data:`None` and no ``spk`` group exists in ``fp``

    Note:
        ``fp`` is modified in place; the returned reference points to the same object and the file is left
        open for the caller to continue using or to close.
    """
    # Check channel number
    if 'raw' in fp:
        ch  = fp['raw'].shape[0]
    else:
        raise ValueError("Raw data is not present in the file; channel count cannot be validated")
    # Check spike waveform names
    if spk is None:
        if 'spk' in fp:
            spk = list(fp['spk'].keys())
        else:
            raise ValueError("Spike waveform data is not available in the file; spike labels cannot be defined")
    # Check existence of position data
    if 'pos' in fp:
        if force:
            del fp['pos']
        else:
            warnings.warn("Spike position data already exists in the file; no changes were made\n"
                          "    -> Set `force=True` to overwrite existing data", Warning, stacklevel=2)
            return fp

    # Build spike position group
    grp = fp.create_group('pos')
    for s in spk:
        gs = grp.create_group(s)
        for c in range(ch):
            gs.create_group(str(c))
    print("Spike position data structure has been successfully created; access using `fp[spk][ch]`")
    return fp


def timestamp_to_onehot(tp, fs, num):
    """Convert a spike timestamp array to a one-hot label vector.

    Each timestamp is rounded to the nearest sample index (using ``fs``) and marked with ``1`` in the output.

    Args:
        tp (np.ndarray): {1D} Spike timestamps in seconds
        fs (int | float | np.float32): Sampling frequency in Hz
        num (int): Total length of the target one-hot vector (typically ``n_samples`` of the recording)

    Returns:
        np.ndarray: {1D-int8} One-hot spike position label of length ``num``
    """
    pos = np.zeros(num, dtype=np.int8)
    loc = np.round(tp * fs, decimals=0).astype(int)
    pos[loc] = 1
    return pos


def onehot_to_timestamp(oh, fs):
    """Convert a one-hot spike label vector to a timestamp array.

    Args:
        oh (np.ndarray): {1D-int8} One-hot spike position label
        fs (int | float | np.float32): Sampling frequency in Hz

    Returns:
        np.ndarray: {1D-float32} Spike timestamps in seconds
    """
    idx = np.nonzero(oh)[0]
    ts = idx.astype(np.float32) / fs
    return ts
