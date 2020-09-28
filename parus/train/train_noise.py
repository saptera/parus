import torch
import torch.nn as nn
from torch.utils import data
import numpy as np
from parus.data.data_proc import sim_sig_read, sim_lbl_read

TRAIN_DATA_PATH = "/home/proj_wavemoto/dataset/noise_separation/sim10000_min20_max80_len300"
TEST_DATA_PATH = "/home/proj_wavemoto/dataset/noise_separation/sim10000_min20_max80_len300"
SEQ_LEN = 300


class SimulatedNoiseDataset(data.Dataset):
    def __init__(self, dataset_folder, list_id):
        self.dataset_folder = dataset_folder
        self.list_id = list_id

    def __len__(self):
        return len(self.list_id)

    def __getitem__(self, index):
        id = self.list_id[index]
        sig_filename = self.dataset_folder + "/sig/" + "sig_" + id + ".sim"
        lbl_filename = self.dataset_folder + "/lbl/" + "lbl_" + id + ".sim"
        sig = sim_sig_read(sig_filename)
        lbl = sim_lbl_read(lbl_filename)
        # Load data and get label
        # print("sig shape without view: ", torch.from_numpy(sig).shape)
        # print("lbl shape without view: ", torch.from_numpy(lbl).shape)
        X = torch.from_numpy(sig).view(SEQ_LEN, 1)
        y = torch.from_numpy(lbl).view(SEQ_LEN, 1)
        # print("sig shape with view: ", X.shape)
        # print("lbl shape with view: ", y.shape)
        X, y = X.type(torch.FloatTensor), y.type(torch.FloatTensor)

        return X, y


def main():
    train_id_list = [str(num).zfill(5) for num in range(10000)]
    train_data = SimulatedNoiseDataset(TRAIN_DATA_PATH, train_id_list)
    print(train_data[0])



if __name__ == '__main__':
    main()
