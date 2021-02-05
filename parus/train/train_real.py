import torch
import torch.nn as nn
from torch.utils import data
import numpy as np
from parus.data.data_proc import sim_sig_read, sim_lbl_read, nsd_write
from parus.data.intan_func import intan_amp_read
from parus.train.wavenet import WaveNet

TRAIN_DATA_PATH = "/home/proj_wavemoto/dataset/complex_spike/complex100000_min20_max80_len300/"
TEST_DATA_PATH = "/home/proj_wavemoto/dataset/complex_spike/real_data/"

TEST_PRED_PATH = "/home/proj_wavemoto/log/pred/complex_real_inf/"
MODEL_FILE_PATH = "/home/proj_wavemoto/log/models/complex_inf.pt"

SEQ_LEN = 300
DROPOUT = 0.4

EPOCH = 30
LR = 0.001
LR_DECAY = 0.95
CLIP = 0.5
TRAIN_PARAMS = {'batch_size': 25,
                'shuffle': True,
                'num_workers': 20}
TEST_PARAMS = {'batch_size': 1,
               'shuffle': False,
               'num_workers': 1}


class SimulatedNoiseDataset(data.Dataset):
    def __init__(self, dataset_folder, list_id):
        self.dataset_folder = dataset_folder
        self.list_id = list_id

    def __len__(self):
        return len(self.list_id)

    def __getitem__(self, index):
        id = self.list_id[index]
        sig_filename = self.dataset_folder + "sig/" + "sig_" + id + ".sim"
        lbl_filename = self.dataset_folder + "lbl/" + "lbl_" + id + ".sim"
        sig = sim_sig_read(sig_filename)
        lbl = sim_lbl_read(lbl_filename)

        X = torch.from_numpy(sig).view(1, SEQ_LEN)
        y = torch.from_numpy(lbl).view(1, SEQ_LEN)

        X, y = X.type(torch.FloatTensor), y.type(torch.FloatTensor)

        return X, y

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

def get_data_generator(data_folder, id_list, params):
    dataset = SimulatedNoiseDataset(data_folder, id_list)
    datagen = data.DataLoader(dataset, **params)
    return datagen


def get_test_data_generator(file_path, params):
    dataset = RealDataset(file_path)
    datagen = data.DataLoader(dataset, **params)
    return datagen


def train(model, criterion, optimizer, scheduler, train_id_list, val_id_list, train_params):
    train_gen = get_data_generator(TRAIN_DATA_PATH, train_id_list, train_params)
    val_gen = get_data_generator(TRAIN_DATA_PATH, val_id_list, train_params)

    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda:0" if use_cuda else "cpu")
    model.to(device)

    # training loop
    counter = 0
    valid_loss_min = np.Inf
    print_every = 500
    model.train()
    for i in range(EPOCH):
        for inputs, labels in train_gen:
            counter += 1
            inputs, labels = inputs.to(device), labels.to(device)
            model.zero_grad()
            output = model(inputs)
            loss = criterion(output, labels.float())
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), CLIP)
            optimizer.step()

            if counter % print_every == 0:
                val_losses = []
                model.eval()
                for inp, lab in val_gen:
                    inp, lab = inp.to(device), lab.to(device)
                    out = model(inp)
                    val_loss = criterion(out, lab.float())
                    val_losses.append(val_loss.item())

                model.train()
                print("Epoch: {}/{}...".format(i + 1, EPOCH),
                      "Step: {}...".format(counter),
                      "Loss: {:.6f}...".format(loss.item()),
                      "Val Loss: {:.6f}".format(np.mean(val_losses)))
                if np.mean(val_losses) <= valid_loss_min:
                    torch.save(model.state_dict(), MODEL_FILE_PATH)
                    print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(valid_loss_min,
                                                                                                    np.mean(val_losses)))
                    valid_loss_min = np.mean(val_losses)

        scheduler.step()


def inference(model, file_name, test_params):
    file_path = TEST_DATA_PATH + file_name + ".dat"
    test_gen = get_test_data_generator(file_path, test_params)

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

            filename = TEST_PRED_PATH + "pred_" + file_name + "_" + str(counter).zfill(5) + ".sim"
            nsd_write(filename, {"sig": pred, "lbl": inputs})
            print(filename)
            counter += 1


def main():
    train_id_list = [str(num).zfill(5) for num in range(50000)]
    val_id_list = [str(num).zfill(5) for num in range(50000, 75000)]

    model = WaveNet(layer_size=7, stack_size=3, in_channels=1, res_channels=64)
    criterion = nn.L1Loss(reduction='mean')
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1.0, gamma=LR_DECAY)

    train(model, criterion, optimizer, scheduler, train_id_list, val_id_list, TRAIN_PARAMS)
    inference(model, "amp-A-001", TEST_PARAMS)


if __name__ == '__main__':
    main()
