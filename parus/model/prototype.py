import math
import torch
import torch.nn as nn
import torch.nn.functional as F


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class LSTM(nn.Module):

    def __init__(self, ninp=1, nhid=256, nlayers=1, dropout=0.5):
        super(Transformer, self).__init__()
        self.lstm = nn.LSTM(ninp, nhid, nlayers, dropout=dropout)
        self.drop = nn.Dropout(dropout)

    def forward(self, input, hidden):
        output, hidden = self.lstm(input, hidden)
        output = self.drop(output)
        decoded = self.decoder(output)
        return decoded, hidden

    def init_hidden(self, batch_size):
        weight = next(self.parameters())
        return (weight.new_zeros(self.nlayers, batch_size, self.nhid),
                weight.new_zeros(self.nlayers, batch_size, self.nhid))

