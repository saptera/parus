import os
import torch
from torch.utils import data
from parus.data import sim_sig_read, sim_lbl_read


class LabelledMultipleFileDataset(data.Dataset):
    # TODO: maybe we can remove seq_len as an input
    def __init__(self, sig_folder, lbl_folder, n_samples, seq_len):
        self.sig_folder = sig_folder
        print(sig_folder)
        self.lbl_folder = lbl_folder
        print(lbl_folder)
        sig_file_lst = sorted(os.listdir(sig_folder))
        lbl_file_lst = sorted(os.listdir(lbl_folder))
        print(len(sig_file_lst), len(lbl_file_lst))
        assert len(sig_file_lst) == len(lbl_file_lst), "number of sig and lbl does not match"
        assert len(sig_file_lst) >= n_samples, "not enough samples in the dataset"
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
        file_num_str = sig_filename[sig_filename.index('_')+1:sig_filename.index('.')] # e.g. sig_00202.sim -> 00202
        sig = sim_sig_read(sig_filename)
        lbl = sim_lbl_read(lbl_filename)

        # TODO: maybe we don't need the view
        X = torch.from_numpy(sig).view(1, self.seq_len)
        y = torch.from_numpy(lbl).view(1, self.seq_len)

        # TODO: maybe we don't need to convert type
        X, y = X.type(torch.FloatTensor), y.type(torch.FloatTensor)

        return X, y, file_num_str


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


class NoLabelSingleFileDataset(data.Dataset):
    def __init__(self, dataset_file_path, seq_len):
        self.sig_lst_numpy = sim_sig_read(dataset_file_path)
        #sig_lst_tensor = torch.from_numpy(sig_lst_numpy)
        #self.sig_lst_tensor = sig_lst_tensor.type(torch.FloatTensor)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.sig_lst_numpy)

    def __getitem__(self, index):
        return torch.from_numpy(self.sig_lst_numpy[index]).type(torch.FloatTensor).view(1, self.seq_len)
