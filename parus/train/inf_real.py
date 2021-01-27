import torch
import torch.nn as nn
from torch.utils import data
import numpy as np
from parus.data.data_proc import sim_sig_read, sim_lbl_read, nsd_write
from parus.data.intan_func import intan_amp_read

from parus.train.wavenet import WaveNet

REAL_DATA_PATH = "/home/proj_wavemoto/dataset/complex_spike/real_data/"

PRED_PATH = "/home/proj_wavemoto/log/pred/real_data_pred/"
MODEL_FILE_PATH = "/home/proj_wavemoto/log/models/complex_real.pt"

SEQ_LEN = 300
NUM_CHANNEL = 64

TRAIN_PARAMS = {'batch_size': 25,
                'shuffle': True,
                'num_workers': 20}
TEST_PARAMS = {'batch_size': 1,
               'shuffle': False,
               'num_workers': 1}


def import_intan_amp(amp_file, length=300, overlap=50):
    """ Import IntanTech RHD2000 amplifier data for model inference.

    Args:
        amp_file (str): IntanTech RHD2000 "One File Per Channel" formatted amplifier file.
        length (int): Length of cut sample from amplifier data.
        overlap (int): Overlap length between 2 cut sample.

    Returns:
        np.ndarray: {2D} Imported IntanTech RHD2000 amplifier data for model inference.
    """
    # Import data
    data = intan_amp_read(amp_file)
    # Get range
    idx_start = np.arange(start=0, stop=len(data), step=length - overlap, dtype=np.uint32)
    idx_stop = np.add(idx_start, length)
    # Padding data
    pad_len = idx_stop[-1] - len(data)
    if pad_len >= 0:
        data = np.append(data, np.full(pad_len, data[-1]))
    # Rearrange data into a 2D-array
    dst = np.empty((len(idx_start), length), dtype=data.dtype)
    for i in range(len(idx_start)):
        dst[i] = data[idx_start[i]:idx_stop[i]]
    return dst


class RealDataset(data.Dataset):
    def __init__(self, file_path):
        self.arr_2d = import_intan_amp(file_path)

    def __len__(self):
        return len(self.arr_2d)

    def __getitem__(self, index):
        sig = self.arr_2d[index]
        X = torch.from_numpy(sig).view(1, SEQ_LEN).type(torch.FloatTensor)

        return X


def get_data_generator(file_path, params):
    dataset = RealDataset(file_path)
    datagen = data.DataLoader(dataset, **params)
    return datagen


def inference(model, file_name, test_params):
    file_path = REAL_DATA_PATH + file_name + ".dat"
    test_gen = get_data_generator(file_path, test_params)

    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda:0" if use_cuda else "cpu")

    # prediction and saving
    with torch.no_grad():
        counter = 0
        for inputs in test_gen:
            inputs = inputs.to(device)
            outputs = model(inputs)

            pred = outputs.squeeze().cpu().numpy()
            inputs = inputs.squeeze().cpu().numpy()

            filename = PRED_PATH + "pred_" + file_name + "_" + str(counter).zfill(5) + ".sim"
            nsd_write(filename, {"sig": pred, "lbl": inputs})
            counter += 1


def main():
    filenames = ["amp-A-" + str(num).zfill(3) for num in range(64)]
    model = WaveNet(layer_size=7, stack_size=3, in_channels=1, res_channels=64)
    model.load_state_dict(torch.load(MODEL_FILE_PATH))
    for name in filenames:
        inference(model, name, TEST_PARAMS)


if __name__ == '__main__':
    main()
