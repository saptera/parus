import torch
import torch.nn as nn
from torch.utils import data
import numpy as np
from parus.data.data_proc import sim_sig_read, sim_lbl_read, nsd_write
from parus.train.wavenet import WaveNet

TRAIN_DATA_PATH = "/home/proj_wavemoto/dataset/noise_separation/sim100000_min20_max80_len300/"
TEST_DATA_PATH = "/home/proj_wavemoto/dataset/noise_separation/sim100000_min20_max80_len300/"

TEST_PRED_PATH = "/home/proj_wavemoto/log/pred/noise_cnn/"
MODEL_FILE_PATH = "/home/proj_wavemoto/log/models/noise_cnn.pt"

SEQ_LEN = 300
DROPOUT = 0.1

EPOCH = 20
LR = 0.001
LR_DECAY = 0.95
CLIP = 0.5
TRAIN_PARAMS = {'batch_size': 30,
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

        X = torch.from_numpy(sig).view(SEQ_LEN, 1)
        y = torch.from_numpy(lbl).view(SEQ_LEN, 1)

        X, y = X.type(torch.FloatTensor), y.type(torch.FloatTensor)

        return X, y


def get_data_generator(data_folder, id_list, params):
    dataset = SimulatedNoiseDataset(data_folder, id_list)
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
            output = torch.transpose(output, 1, 2)
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
                    out = torch.transpose(out, 1, 2)
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


def inference(model, test_id_list, test_params):
    test_gen = get_data_generator(TEST_DATA_PATH, test_id_list, test_params)

    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda:0" if use_cuda else "cpu")

    # prediction and saving
    with torch.no_grad():
        counter = 0
        for inputs, labels in test_gen:
            inputs = inputs.to(device)
            outputs = model(inputs)

            pred = outputs.squeeze().cpu().numpy()
            labels = labels.squeeze().cpu().numpy()

            filename = TEST_PRED_PATH + "pred_" + str(counter).zfill(5) + ".sim"
            nsd_write(filename, {"sig": pred, "lbl": labels})
            counter += 1


def main():
    train_id_list = [str(num).zfill(5) for num in range(50000)]
    val_id_list = [str(num).zfill(5) for num in range(50000, 75000)]
    test_id_list = [str(num).zfill(5) for num in range(75000, 100000)]

    model = WaveNet(layer_size=7, stack_size=1, in_channels=1, res_channels=5)
    criterion = nn.L1Loss(reduction='mean')
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1.0, gamma=LR_DECAY)

    train(model, criterion, optimizer, scheduler, train_id_list, val_id_list, TRAIN_PARAMS)
    inference(model, test_id_list, TEST_PARAMS)


if __name__ == '__main__':
    main()
