import os
import torch
from torch.utils import data
from parus.data import sim_sig_read, sim_lbl_read

class SimulatedNoiseDataset(data.Dataset):
    def __init__(self, dataset_folder, list_id, seq_len):
        self.dataset_folder = dataset_folder
        self.list_id = list_id
        self.seq_len = seq_len
    def __len__(self):
        return len(self.list_id)

    def __getitem__(self, index):
        id = self.list_id[index]
        sig_filename = os.path.join(self.dataset_folder, "sig", "sig_" + id + ".sim")
        lbl_filename = os.path.join(self.dataset_folder, "lbl", "lbl_" + id + ".sim")
        sig = sim_sig_read(sig_filename)
        lbl = sim_lbl_read(lbl_filename)

        X = torch.from_numpy(sig).view(1, self.seq_len)
        y = torch.from_numpy(lbl).view(1, self.seq_len)

        X, y = X.type(torch.FloatTensor), y.type(torch.FloatTensor)

        return X, y

class HumanDataset(data.Dataset):
    def __init__(self, dataset_folder, seq_len):
        self.dataset_folder = dataset_folder
        self.list_name = os.listdir(dataset_folder)
        self.seq_len = seq_len
    def __len__(self):
        return len(self.list_name)

    def __getitem__(self, index):
        sig_filename = self.list_name[index]
        sig = sim_sig_read(self.dataset_folder + "/" + sig_filename)
        X = torch.from_numpy(sig).view(1, self.seq_len)
        X = X.type(torch.FloatTensor)

        return X

def get_datagen(id_list, data_folder, seq_len, params):
    dataset = SimulatedNoiseDataset(data_folder, id_list, seq_len)
    datagen = data.DataLoader(dataset, **params)
    #for inp, lbl in datagen:
    #    print(inp.max())
    #    print(lbl.max())
    return datagen

def get_train_datagen(data_folder, seq_len, params):
    return get_datagen([str(num).zfill(5) for num in range(1000000)], data_folder, seq_len, params)

def get_val_datagen(data_folder, seq_len, params):
    return get_datagen([str(num).zfill(5) for num in range(10000)], data_folder, seq_len, params)
    
def get_test_datagen(data_folder, seq_len, params):
    return get_datagen([str(num).zfill(5) for num in range(5000)], data_folder, seq_len, params)
