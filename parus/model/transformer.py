import numpy as np
import torch
import torch.nn as nn
import warnings


class PositionalEncoding(nn.Module):
    def __init__(self, embedding_dim, dropout, max_len: int = 300):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, embedding_dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(
            # -9.210340371976184 = -ln(10000.0)
            0, embedding_dim, 2).float() * (-9.210340371976184 / embedding_dim))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(1, 2)
        self.register_buffer('pe', pe)  # allows state-save

    def forward(self, x):
        x = x + self.pe
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
        x_np = x.detach().cpu().numpy()
        x_pad = np.pad(x_np, pad_width=self.pw,
                       mode='constant', constant_values=0.0)
        x_win = np.lib.stride_tricks.sliding_window_view(
            x_pad, window_shape=(bs, nch, self.emb_dim))[0, 0, :, :, 0, :]
        x_trs = np.transpose(x_win, axes=(1, 2, 0))
        x_context = np.flip(x_trs, axis=1).copy()
        return torch.from_numpy(x_context).cuda()


class SparseContextLoader(nn.Module):
    def __init__(self, emb_dim, ant_samp, n_samp, sel_meth='stp', gap=1):
        """ Signal data context loader.

        Args:
            emb_dim (int): Embedding element length
            ant_samp (int): Anterior element length
            n_samp (int): Total number of samples per patch
            sel_meth (str): Flanking elements indices sampling method (default: 'stp')
                - 'stp': Constant gap sampling
                - 'lin': Linear increased gap sampling
                - 'geo': Geometrical increased gap sampling
            gap (int | float): Constant (for 'stp') or maximum (for 'lin' and 'geo') gap for sampling (default: 1)
        """
        self.emb_dim = emb_dim
        self.ant = min(ant_samp, emb_dim - 1)  # Avoid index overflow
        # Get index positions
        # Number of space samples
        self.spc_num = max(self.ant, self.emb_dim - self.ant)
        idx = self.get_idx(sel_meth, gap)
        # Get sampling features
        self.pw = ((0, 0), (0, 0), (-idx[-1], idx[0]))
        self.tgt = np.add.outer(idx, range(-idx[-1], n_samp - idx[-1]))
        # Super
        super().__init__()

    def get_idx(self, meth='stp', gap=1):
        """ Return selected indices based on chosen method.

        Args:
            meth (str): Flanking elements indices sampling method (default: 'stp')
                - 'stp': Constant gap sampling
                - 'lin': Linear increased gap sampling
                - 'geo': Geometrical increased gap sampling
            gap (int | float): Constant (for 'stp') or maximum (for 'lin' and 'geo') gap for sampling (default: 1)

        Returns:
            np.ndarray: {1D-int} Relative index for the target position
        """
        # Get space based on method, minimum distance is forced to 1
        if meth == 'stp':
            space = np.asarray([max(round(gap), 1)] * self.spc_num)
        elif meth == 'lin':
            space = np.linspace(1, gap, self.spc_num, endpoint=True).round(0)
        elif meth == 'geo':
            space = np.geomspace(1, gap, self.spc_num, endpoint=True).round(0)
        else:
            # Fallback method
            warnings.warn(
                "Invalid sampling method, fallback to constant gap sampling.", SyntaxWarning, stacklevel=2)
            space = np.asarray([max(round(gap), 1)] * self.spc_num)
        # Get accumulative distance
        distance = np.add.accumulate(space).astype(int)
        # Set origin on the posterior side
        idx = np.concatenate(
            (distance[self.ant - 1::-1] * -1, distance[:self.emb_dim - self.ant] - distance[0]))
        return idx[::-1]  # Flip for transformer context loading order

    def forward(self, x):
        bs, ctx, _ = x.shape
        x_np = x.cpu().numpy()
        x_pad = np.pad(x_np, pad_width=self.pw,
                       mode='constant', constant_values=0.0)
        x_context = x_pad[:, :, self.tgt]
        # TODO: Dimension reserved future contexts, currently removed for efficiency
        return torch.from_numpy(x_context[:, 0, :, :]).cuda()


class EncoderTransformer(nn.Module):
    def __init__(self, input_dim, context_dim, d_model, nhead, num_layers, dim_feedforward, output_channels):
        super(EncoderTransformer, self).__init__()
        self.input_linear = nn.Linear(context_dim, d_model)
        self.transformer_encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_feedforward, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(
            self.transformer_encoder_layer, num_layers)
        # Output size is same as input size
        self.output_linear = nn.Linear(d_model, context_dim)
        # self.context_loader = ContextLoader(
        #     emb_dim=context_dim, ant_samp=context_dim // 2)
        self.context_loader = SparseContextLoader(
            emb_dim=context_dim, ant_samp=context_dim // 2, n_samp=input_dim, sel_meth='geo', gap=5
        )
        self.extra_linear1 = nn.Linear(context_dim, 2*context_dim)
        self.extra_linear2 = nn.Linear(2*context_dim, context_dim)
        self.context_linear = nn.Linear(context_dim, output_channels)
        self.positional_encoding = PositionalEncoding(
            embedding_dim=context_dim, dropout=0.1, max_len=input_dim)
        self.relu = nn.ReLU()

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
