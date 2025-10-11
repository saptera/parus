# Model data loader classes module

import numpy as np
import torch
from torch.utils.data import Dataset
import warnings

__package__ = 'parus.model'
__name__ = 'parus.model.dset'
from ..fio import H5PklFile, sim_args_read, sim_data_read

__all__ = ['TrainingDataset', 'InferenceDataset']
"""
Class list:
  TrainingDataset(file, n_sample, seq_len): Load simulated dataset for model training.
  InferenceDataset(file, seq_len, overlap=10, to_mem=False, prt_idt=8): Load raw recording data for model inference.
"""


class TrainingDataset(Dataset):
    def __init__(self, file, n_sample, seq_len):
        """ Load simulated dataset for model training.

        Args:
            file (str): Path to simulated dataset file (HDF5 format)
            n_sample (int): Number of samples to load
            seq_len (int): Model sequence length
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
        """ Close dataset HDF5 file. """
        self.__fp.close()


class InferenceDataset(Dataset):
    def __init__(self, file, seq_len, overlap=10, to_mem=False, prt_idt=8):
        """ Load raw recording data for model inference.

        Args:
            file (str): Path to raw recording file (HDF5 format)
            seq_len (int): Model sequence length
            overlap (int): Sample overlapping length
            to_mem (bool): Load all data into memory, accelerate speed at the risk of memory overflow (default: False)
            prt_idt (int): Progress print indents
        """
        # Open and validate dataset file
        self.fp = H5PklFile(file, 'r+')
        if self.fp['raw'].ndim != 2:
            self.fp.close()
            raise ValueError("Input array must be 2D (channels, samples).")
        # Load data
        self.__read_only = True  # File R/W flag
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
        """ Close dataset HDF5 file. """
        self.fp.close()
