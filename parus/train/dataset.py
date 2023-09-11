import os
import torch
from torch.utils import data
from parus.data import sim_sig_read, sim_lbl_read


class LabelledMultipleFileDataset(data.Dataset):
    # TODO: maybe we can remove seq_len as an input
    def __init__(self, sig_folder, lbl_folder, n_samples, seq_len):
        self.sig_folder = sig_folder
        self.lbl_folder = lbl_folder
        sig_file_lst = sorted(os.listdir(sig_folder))
        lbl_file_lst = sorted(os.listdir(lbl_folder))
        assert len(self.sig_file_lst) == len(
            self.lbl_file_lst), "number of sig and lbl does not match"
        assert len(
            self.sig_file_lst) >= n_samples, "not enough samples in the dataset"
        self.sig_file_lst = sig_file_lst[:n_samples]
        self.lbl_file_lst = lbl_file_lst[:n_samples]
        self.seq_len = seq_len

    def __len__(self):
        return len(self.sig_file_lst)

    def __getitem__(self, index):
        sig_filename = self.sig_file_lst[index]
        lbl_filename = self.lbl_file_lst[index]
        sig_filename = os.path.join(
            self.sig_folder, sig_filename)
        lbl_filename = os.path.join(
            self.lbl_folder, lbl_filename)
        sig = sim_sig_read(sig_filename)
        lbl = sim_lbl_read(lbl_filename)

        # TODO: maybe we don't need the view
        X = torch.from_numpy(sig).view(1, self.seq_len)
        y = torch.from_numpy(lbl).view(1, self.seq_len)

        # TODO: maybe we don't need to convert type
        X, y = X.type(torch.FloatTensor), y.type(torch.FloatTensor)

        return X, y


class NoLabelMultipleFileDataset(data.Dataset):
    def __init__(self, dataset_folder, seq_len):
        self.dataset_folder = dataset_folder
        self.list_name = os.listdir(dataset_folder)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.list_name)

    def __getitem__(self, index):
        sig_filename = self.list_name[index]
        sig = sim_sig_read(os.path.join(self.dataset_folder, sig_filename))
        X = torch.from_numpy(sig).view(1, self.seq_len)
        X = X.type(torch.FloatTensor)

        return X
