import os
import torch
import numpy as np
import h5py
from torch.utils import data
from parus.data import sim_sig_read
from parus.fio import sim_data_read


class LabelledSingleFileDataset(data.Dataset):
    def __init__(self, data_file_path, n_samples, seq_len):
        self.n_samples = n_samples
        self.data_file_path = data_file_path
        self.seq_len = seq_len

    def __len__(self):
        return self.n_samples

    def __getitem__(self, index):
        with h5py.File(self.data_file_path, "r") as file:
            data = sim_data_read(file, index)
            
        sig = data['sig']
        lbl = np.sum(data['lbl']['signal'], axis=0) # using only simple spike
        
        X = torch.from_numpy(sig).view(1, self.seq_len).type(torch.FloatTensor)
        y = torch.from_numpy(lbl).view(1, self.seq_len).type(torch.FloatTensor)

        return X, y
    

class NoLabelSingleFileDataset(data.Dataset):
    def __init__(self, dataset_file_path, seq_len):
        self.sig_lst_numpy = sim_sig_read(dataset_file_path)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.sig_lst_numpy)

    def __getitem__(self, index):
        # not converting in __init__ to avoid memory issues
        return torch.from_numpy(self.sig_lst_numpy[index]).type(torch.FloatTensor).view(1, self.seq_len)