# User helper function module

import os
import numpy as np
import h5py as h5
import warnings

__package__ = 'parus.util'
__name__ = 'parus.util.helper'

__all__ = ['check_sampling_frequency', 'check_raw_data', 'create_raw_data_file', 'add_position_groups',
           'timestamp_to_onehot', 'onehot_to_timestamp']
"""
Function list:
  check_sampling_frequency(fs): Check and auto-convert the data format of sampling frequency.
  check_raw_data(raw): Check and auto-convert the data format of raw recordings.
  create_raw_data_file(file, raw, fs, force=False): Create a compatible HDF5 file with given raw data.
  add_position_groups(fp, spk=None, force=False): Add empty spike position groups to the data file.
  timestamp_to_onehot(tp, fs, num): Covert spike timestamp array to one-hot spike label.
  onehot_to_timestamp(oh, fs): Covert one-hot spike label to spike timestamp array.
"""


def check_sampling_frequency(fs):
    """ Check and auto-convert the data format of sampling frequency.

    Args:
        fs: Sampling frequency

    Returns:
        np.float32: Validated sampling frequency
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
    """ Check and auto-convert the data format of raw recordings.

    Args:
        raw: Raw recording data

    Returns:
        np.ndarray: Validated raw data
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
    """ Create a compatible HDF5 file with given raw data.

    - An opened file pointer will be returned, please close with `fp.close()` if no further usage

    Args:
        file (str): File name
        raw (np.ndarray): Raw recording data
        fs (int | float | np.dtypes.Float32DType): Sampling frequency
        force (bool): Overwrite existing file (default: False)

    Returns:
        h5.File: HDF5 file pointer ('a' mode)
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
    """ Add empty spike position groups to the data file.

    Args:
        fp (h5.File): HDF5 file pointer
        spk (list[str] | None): Spike waveform type name list (default: None = infer from file)
        force (bool): Overwrite existing position group (default: False)

    Returns:
        h5.file: Forwarded file pointer
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
    """ Covert spike timestamp array to one-hot spike label.

    Args:
        tp (np.ndarray): {1D} Timestamp spike position label
        fs (int | float | np.dtypes.Float32DType): Sampling frequency
        num (int): Total length of raw recording

    Returns:
        np.ndarray: {1D-int8} One-hot spike position label
    """
    pos = np.zeros(num, dtype=np.int8)
    loc = np.round(tp * fs, decimals=0).astype(int)
    pos[loc] = 1
    return pos


def onehot_to_timestamp(oh, fs):
    """ Covert one-hot spike label to spike timestamp array.

    Args:
        oh (np.ndarray): {1D-int8} Timestamp spike position label
        fs (int | float | np.dtypes.Float32DType): Sampling frequency

    Returns:
        np.ndarray: {1D-float32} Spike timestamp position
    """
    idx = np.nonzero(oh)[0]
    ts = idx.astype(np.float32) / fs
    return ts
