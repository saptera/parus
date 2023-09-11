import numpy as np
import torch
import torch.nn as nn


class PositionalEncoding(nn.Module):
    def __init__(self, embedding_dim, dropout, max_len: int = 300):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, embedding_dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(
            0, embedding_dim, 2).float() * (-9.210340371976184 / embedding_dim))  # -9.210340371976184 = -ln(10000.0)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(1, 2)
        self.register_buffer('pe', pe)  # allows state-save

    def forward(self, x):
        x = x + x + self.pe
        return self.dropout(x)


class ContextLoader(nn.Module):
    def __init__(self, emb_dim, ant_samp):
        self.emb_dim = emb_dim
        ant = min(ant_samp, emb_dim - 1)  # Avoid index overflow
        # Get padding width
        self.pw = ((0, 0), (0, 0), (ant, emb_dim - 1 - ant))
        super().__init__()

    def forward(self, x):
        bs, nch, _ = x.shape
        x_np = x.numpy()
        x_pad = np.pad(x_np, pad_width=self.pw,
                       mode='constant', constant_values=0.0)
        x_win = np.lib.stride_tricks.sliding_window_view(
            x_pad, window_shape=(bs, nch, self.emb_dim))[0, 0, :, :, 0, :]
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
        self.context_loader = ContextLoader(
            emb_dim=context_dim, ant_samp=context_dim // 2)
        self.context_linear = nn.Linear(context_dim, 1)
        self.positional_encoding = PositionalEncoding(
            embedding_dim=context_dim, dropout=0.1, max_len=input_dim)

    def forward(self, x):
        scale = torch.abs(x).max(2, keepdim=True)[0]
        x = x / scale
        x = self.context_loader(x)
        x = self.positional_encoding(x)
        x = x.transpose(-1, -2)
        x = self.input_linear(x)
        x = self.transformer_encoder(x)
        x = self.output_linear(x)
        x = self.context_linear(x)
        x = x.transpose(-1, -2)
        x *= scale
        return x
