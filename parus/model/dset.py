# -*- coding: utf-8 -*-

"""Model data loader classes module

PyTorch :class:`~torch.utils.data.Dataset` implementations for model training and inference, backed by
PARUS-defined HDF5 files.
"""

import numpy as np
import torch
from torch.utils.data import Dataset
import warnings

__package__ = 'parus.model'
__name__ = 'parus.model.dset'
from ..fio import H5PklFile, sim_args_read, sim_data_read

__all__ = ['TrainingDataset', 'InferenceDataset']
"""
Public class list:

- TrainingDataset(file, n_sample, seq_len)             : Load a simulated dataset for model training
- InferenceDataset(file, seq_len, overlap, to_mem)     : Load raw recording data for model inference
"""


class TrainingDataset(Dataset):
    """Load a simulated dataset for model training.

    Reads a PARUS-defined simulated signal HDF5 file via :func:`parus.fio.fdata.sim_args_read` and
    :func:`parus.fio.fdata.sim_data_read` and exposes per-sample tuples of ``(signal, label_signal, label_position)``
    shaped for direct consumption by a sequence model.

    Note:
        The underlying HDF5 file is opened in read mode and stays open for the lifetime of the dataset; call
        :meth:`close` to release the handle when done.
    """

    def __init__(self, file, n_sample, seq_len):
        """Initialise the dataset and validate the input arguments.

        Args:
            file (str): Path to the simulated dataset file (HDF5 format)
            n_sample (int): Number of samples to load; clipped to the dataset's ``num_sim`` when larger
            seq_len (int): Model sequence length; must match the dataset's ``tot_len``

        Raises:
            ValueError: If ``seq_len`` does not match the dataset's stored ``tot_len``

        Warns:
            RuntimeWarning: Emitted when ``n_sample`` exceeds the available simulated samples; the value
                is clipped to ``num_sim``
        """
        self.__fp = H5PklFile(file, 'r')
        self.meta = sim_args_read(self.__fp)
        self.grp_num = len(self.meta['grp_str'])
        # Check [n_samples] input
        if self.meta['num_sim'] < n_sample:
            warnings.warn("Requested amount exceeds available data, value clipped!", RuntimeWarning, stacklevel=2)
            self.n_sample = self.meta['num_sim']
        else:
            self.n_sample = n_sample
        # Check [seq_len] input
        if self.meta['tot_len'] == seq_len:
            self.seq_len = seq_len
        else:
            self.close()
            raise ValueError("The requested sequence length does not match the dataset sequence length!")

    def __len__(self):
        return self.n_sample

    def __getitem__(self, index):
        data = sim_data_read(self.__fp, index)
        X = torch.from_numpy(data['sig']).view(1, self.seq_len).type(torch.FloatTensor)
        y_spk = torch.from_numpy(data['lbl']['signal']).view(self.grp_num, self.seq_len).type(torch.FloatTensor)
        y_pos = torch.from_numpy(data['pos']).view(self.grp_num, self.seq_len).type(torch.FloatTensor)
        return X, y_spk, y_pos

    def close(self):
        """Close the underlying HDF5 file handle."""
        self.__fp.close()


class InferenceDataset(Dataset):
    """Load raw recording data for model inference.

    Reads a PARUS-defined raw recording HDF5 file and exposes per-sample windows of the signal trace,
    one window per channel and per sliding-window step. Windows overlap by ``overlap`` samples; the last
    window of each channel is right-padded with zeros so every window keeps length ``seq_len``.

    Note:
        The underlying HDF5 file is opened in append mode and stays open for the lifetime of the dataset
        (so post-inference helpers can write back to it); call :meth:`close` to release the handle when
        done.
    """

    def __init__(self, file, seq_len, overlap=10, to_mem=False):
        """Initialise the dataset and validate the recording layout.

        Args:
            file (str): Path to the raw recording HDF5 file
            seq_len (int): Model sequence length
            overlap (int): Sample overlap between consecutive windows (default: ``10``)
            to_mem (bool): When :data:`True`, eagerly load the entire recording into memory; trades
                memory for inference throughput (default: ``False``)

        Raises:
            ValueError: If the recording's ``raw`` dataset is not 2D (channels, samples)
        """
        # Open and validate dataset file
        self.fp = H5PklFile(file, 'r+')
        if self.fp['raw'].ndim != 2:
            self.fp.close()
            raise ValueError("Input array must be 2D (channels, samples).")
        # Load data
        self.data = self.fp['raw'][()] if to_mem else self.fp['raw']
        # Get features
        self.n_ch, self.total = self.data.shape
        self.seq_len = seq_len
        self.overlap = overlap
        self.step = seq_len - overlap
        # Check padding length
        if self.total < seq_len:
            self.pad = seq_len - self.total
            self.n_sample = 1
        else:
            self.pad = (self.total - overlap - 1) // (seq_len - overlap) * (seq_len - overlap) + seq_len - self.total
            self.n_sample = (self.total - overlap - 1) // (seq_len - overlap) + 1
        # Create a pad array for the last sample of each channel
        self.__pad_arr = np.zeros(self.pad, dtype=self.data.dtype)

    def __len__(self):
        return self.n_sample * self.n_ch

    def __getitem__(self, index):
        # Get channel and index position
        c, i = divmod(index, self.n_sample)
        init = i * self.step
        stop = init + self.seq_len
        # Get sample, pad if too short
        sample = self.data[c, init:stop]
        if stop > self.total:
            sample = np.concatenate((sample, self.__pad_arr))
        # Converting to PyTorch tensor and report progress
        return torch.from_numpy(sample).type(torch.FloatTensor).view(1, self.seq_len)

    def close(self):
        """Close the underlying HDF5 file handle."""
        self.fp.close()
