import math
import numpy as np
import torch
from torch.utils import data
import torch.nn as nn
import torch.nn.functional as F

from parus.data.data_proc import nsd_read


class Dataset(data.Dataset):
    def __init__(self, dataset_folder, list_ID):
        self.dataset_folder = dataset_folder
        self.list_ID = list_ID

    def __len__(self):
        return len(self.list_ID)

    def __getitem__(self, index):
        ID = self.list_ID[index]
        data_dict = nsd_read(self.dataset_folder + "sig_" + ID + ".nsd")

        print(ID)
        # Load data and get label
        X = torch.from_numpy(data_dict["sig"]).view(150, 1)
        y = torch.from_numpy(data_dict["lbl"]).view(150, 1)
        X, y = X.type(torch.FloatTensor), y.type(torch.FloatTensor)

        return X, y


class LSTM(nn.Module):
    def __init__(self, n_input=1, n_hidden=256, n_layers=1, dropout=0.5):
        super(LSTM, self).__init__()
        self.lstm = nn.LSTM(n_input, n_hidden, n_layers, dropout=dropout)
        self.n_layers = n_layers
        self.n_hidden = n_hidden

    def forward(self, input, hidden):
        output, hidden = self.lstm(input, hidden)
        return output, hidden

    def init_hidden(self, batch_size):
        weight = next(self.parameters())
        return (weight.new_zeros(self.n_layers, 150, self.n_hidden),
                weight.new_zeros(self.n_layers, 150, self.n_hidden))


# CUDA for PyTorch
use_cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if use_cuda else "cpu")

# Parameters
params = {'batch_size': 2,
          'shuffle': True,
          'num_workers': 1}
epochs = 10
data_folder = "sig_samp/"

# Generators
train_ID = [str(num).zfill(5) for num in range(4000)]
train_set = Dataset(data_folder, train_ID)
train_gen = data.DataLoader(train_set, **params)

vld_ID = [str(num).zfill(5) for num in range(4000, 5000)]
vld_set = Dataset(data_folder, vld_ID)
vld_gen = data.DataLoader(vld_set, **params)


model = LSTM(1, 256, 2, 0.5)
model.to(device)
criterion = nn.L1Loss(reduction='sum')
lr = 1.0
optimizer = torch.optim.Adam(model.parameters(), lr=lr)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1.0, gamma=0.95)

epochs = 2
counter = 0
print_every = 1000
clip = 5
valid_loss_min = np.Inf

model.train()
for i in range(epochs):
    h = model.init_hidden(params["batch_size"])

    for inputs, labels in train_gen:
        print(inputs.size(), inputs.type())
        counter += 1
        h = tuple([e.data.float() for e in h])
        print(h[0].type())
        inputs, labels = inputs.to(device), labels.to(device)
        model.zero_grad()

        output, h = model(inputs, h)
        loss = criterion(output.squeeze(), labels.float())
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), clip)
        optimizer.step()

        if counter % print_every == 0:
            val_h = model.init_hidden(params["batch_size"])
            val_losses = []
            model.eval()
            for inp, lab in vld_gen:
                val_h = tuple([each.data for each in val_h])
                inp, lab = inp.to(device), lab.to(device)
                out, val_h = model(inp, val_h)
                val_loss = criterion(out.squeeze(), lab.float())
                val_losses.append(val_loss.item())

            model.train()
            print("Epoch: {}/{}...".format(i + 1, epochs),
                  "Step: {}...".format(counter),
                  "Loss: {:.6f}...".format(loss.item()),
                  "Val Loss: {:.6f}".format(np.mean(val_losses)))
            if np.mean(val_losses) <= valid_loss_min:
                torch.save(model.state_dict(), './state_dict.pt')
                print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(valid_loss_min,
                                                                                                np.mean(val_losses)))
                valid_loss_min = np.mean(val_losses)




# # Loop over epochs
# model.train()
# for epoch in range(epochs):
#     hidden = model.init_hidden(params["batch_size"])
#     # Training
#     for local_batch, local_labels in train_gen:
#         # Transfer to GPU
#         local_batch, local_labels = local_batch.to(device), local_labels.to(device)
#
#         # Model computations
#         output, hidden = model(local_batch, hidden)
#         loss = criterion(output.squeeze(), local_labels.float())
#         loss.backward()
#         optimizer.step()
#
#
#     # Validation
#     with torch.set_grad_enabled(False):
#         for local_batch, local_labels in vld_gen:
#             hidden = model.init_hidden(params["batch_size"])
#             # Transfer to GPU
#             local_batch, local_labels = local_batch.to(device), local_labels.to(device)
#
#             # Model computations
#             [...]