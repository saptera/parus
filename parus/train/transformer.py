import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Dataset
from parus.train.datagen import get_train_datagen, get_val_datagen, get_test_datagen
from parus.data import sim_sig_read, sim_lbl_read


class SimulatedNoiseDataset(Dataset):
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


class PositionalEncoding(nn.Module):
    def __init__(self, embedding_dim, dropout, max_len: int = 300):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, embedding_dim)  # [300, context]
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(
            0, embedding_dim, 2).float() * (-9.210340371976184 / embedding_dim))  # -9.210340371976184 = -ln(10000.0)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(1,2)
        self.register_buffer('pe', pe)  # allows state-save

    def forward(self, x):
        #print("x.shape: ", x.shape) # [batch, context, 300]
        #print("pe.shape: ", self.pe.shape) [1, context, 300]
        x = x + x + self.pe # [1, context, 300] + [batch, context, 300] = [batch, context, 300] because of broadcasting
        return self.dropout(x)


class ContextLoader(nn.Module):
    def __init__(self, emb_dim, ant_samp):
        self.emb_dim = emb_dim
        ant = min(ant_samp, emb_dim - 1)  # Avoid index overflow
        self.pw = ((0, 0), (0, 0), (ant, emb_dim - 1 - ant))  # Get padding width
        super().__init__()

    def forward(self, x):
        bs, nch, _ = x.shape
        x_np = x.numpy()  # Convert to NumPy array for efficiency
        x_pad = np.pad(x_np, pad_width=self.pw, mode='constant', constant_values=0.0)
        x_win = np.lib.stride_tricks.sliding_window_view(x_pad, window_shape=(bs, nch, self.emb_dim))[0, 0, :, :, 0, :]
        x_trs = np.transpose(x_win, axes=(1, 2, 0))
        x_context = np.flip(x_trs, axis=1).copy()
        return torch.from_numpy(x_context)


class EncoderTransformer(nn.Module):
    def __init__(self, input_dim, context_dim, d_model, nhead, num_layers, dim_feedforward):
        super(EncoderTransformer, self).__init__()
        self.input_linear = nn.Linear(context_dim, d_model)
        self.transformer_encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_feedforward, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(
            self.transformer_encoder_layer, num_layers)
        # Output size is same as input size
        self.output_linear = nn.Linear(d_model, context_dim)
        self.context_loader = ContextLoader(emb_dim=context_dim, ant_samp=context_dim // 2)
        self.context_linear = nn.Linear(context_dim, 1)
        self.positional_encoding = PositionalEncoding(embedding_dim=context_dim, dropout=0.1, max_len=input_dim)
    def forward(self, x):
        #print(x.shape) #[batch,1,300]
        x = self.context_loader(x)
        #print(x.shape) #[batch, context, 300]
        x = self.positional_encoding(x)
        #print(x.shape)  #[batch, context, 300]
        x = x.transpose(-1,-2)
        #print(x.shape) #[batch, 300, context]
        x = self.input_linear(x)
        #print(x.shape) #[batch, 300, 64]
        x = self.transformer_encoder(x)
        #print(x.shape) # [batch, 300, 64]
        x = self.output_linear(x)
        #print(x.shape) # [batch, 300, context]
        #x = x.transpose(-2, -1) #swap context dimension to the last dimension, because linear operator on the last dimension
        # print(x.shape) # [batch, 300, context]
        x = self.context_linear(x)
        #print(x.shape) # [batch, 300, 1]
        x = x.transpose(-1, -2) #swap back context dimension
        #print(x.shape) # [batch,1,300]
        #print("end of transformer")
        return x


# Initialize model
model = EncoderTransformer(input_dim=300, context_dim=16, d_model=64, nhead=8, num_layers=6, dim_feedforward=128)
model.train()  # set the model to training mode

# Define loss function and optimizer
criterion = nn.L1Loss(reduction='mean')
optimizer = optim.Adam(model.parameters(), lr=0.0001)

# Generate random training data
sequence_length = 300
epochs = 100
batch_size = 32
data_folder_path = "/home/proj_wavemoto/dataset/generated_data/v5_ss_1m"
train_data_hparams = {'batch_size': 32,
                      'shuffle': True,
                      'num_workers': 10}
dataset = SimulatedNoiseDataset(os.path.join(data_folder_path,"trn"), [str(num).zfill(5) for num in range(1000)], sequence_length)
datagen = DataLoader(dataset, **train_data_hparams)

for epoch in range(epochs):
    total_loss = 0
    for input_data, target_data in datagen:
        # Reset the gradients
        optimizer.zero_grad()

        # Forward pass
        output = model(input_data)

        # Compute the loss
        loss = criterion(output, target_data)

        # Backward pass
        loss.backward()

        # Update the weights
        optimizer.step()

        total_loss += loss.item()

    # Print average loss for this epoch
    avg_loss = total_loss / len(datagen)
    print(f'Epoch {epoch+1}, Avg Loss: {avg_loss}')
