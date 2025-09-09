# Data loader classes for model

import h5py as h5
import numpy as np
import torch
from torch.utils.data import Dataset
import warnings

__package__ = 'parus.model'
from ..fio import sim_args_read, sim_data_read, pklz_read

__all__ = ['TrainingDataset', 'InferenceDataset']
"""
Class list:
  TrainingDataset(file, n_sample, seq_len): Load simulated dataset for model training.
  InferenceDataset(file, seq_len, overlap=10): Load raw recording data for model inference.
"""


class TrainingDataset(Dataset):
    def __init__(self, file, n_sample, seq_len):
        """ Load simulated dataset for model training.

        Args:
            file (str): Path to simulated dataset file (HDF5 format)
            n_sample (int): Number of samples to load
            seq_len (int): Model sequence length
        """
        self.__fp = h5.File(file, 'r')
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
    def __init__(self, file, seq_len, overlap=10):
        """ Load raw recording data for model inference.

        Args:
            file (str): Path to raw recording file (PKLZ format)
            seq_len (int): Model sequence length
            overlap (int): Sample overlapping length
        """
        # Load data
        data = pklz_read(file)
        # Get features
        self.frq = data['frq']
        self.raw = data['sig'][np.newaxis, :] if data['sig'].ndim == 1 else data['sig'].copy()
        self.seq_len = seq_len
        self.overlap = overlap
        self.step = seq_len - overlap
        # Check padding length
        total = len(data['sig'])
        if total < seq_len:
            self.pad = seq_len - total
            self.n_sample = 1
        else:
            self.pad = (total - overlap - 1) // (seq_len - overlap) * (seq_len - overlap) + seq_len - total
            self.n_sample = (total - overlap - 1) // (seq_len - overlap) + 1
        # Set input array
        self.sig = np.pad(data['sig'], (0, self.pad), mode='constant', constant_values=0)

    def __len__(self):
        return self.n_sample

    def __getitem__(self, index):
        # Not converting in __init__ to avoid memory issues
        init = index * self.step
        stop = init + self.seq_len
        return torch.from_numpy(self.sig[init:stop]).type(torch.FloatTensor).view(1, self.seq_len)
