import h5py as h5
import torch
from torch.utils.data import Dataset
from parus.fio import sim_args_read, sim_data_read, pklz_read
import warnings


class TrainingDataset(Dataset):
    def __init__(self, data_file_path, n_samples, seq_len):

        self.__data_file = h5.File(data_file_path, "r")
        self.meta = sim_args_read(self.__data_file)
        self.grp_num = len(self.meta['grp_str'])
        # Check [n_samples] input
        if self.meta['num_sim'] < n_samples:
            warnings.warn("Requested amount exceeds available data, value clipped!", RuntimeWarning, stacklevel=2)
            self.n_samples = self.meta['num_sim']
        else:
            self.n_samples = n_samples
        # Check [seq_len] input
        if self.meta['tot_len'] == seq_len:
            self.seq_len = seq_len
        else:
            self.close()
            raise ValueError("The requested sequence length does not match the dataset sequence length!")

    def __len__(self):
        return self.n_samples

    def __getitem__(self, index):
        data = sim_data_read(self.__data_file, index)
        X = torch.from_numpy(data['sig']).view(1, self.seq_len).type(torch.FloatTensor)
        y = torch.from_numpy(data['lbl']['signal']).view(self.grp_num, self.seq_len).type(torch.FloatTensor)
        return X, y

    def close(self):
        self.__data_file.close()


class InferenceDataset(Dataset):
    def __init__(self, dataset_file_path, seq_len):
        self.sig_lst_numpy = pklz_read(dataset_file_path)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.sig_lst_numpy)

    def __getitem__(self, index):
        # Not converting in __init__ to avoid memory issues
        return torch.from_numpy(self.sig_lst_numpy[index]).type(torch.FloatTensor).view(1, self.seq_len)
