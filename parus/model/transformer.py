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
            0, embedding_dim, 2).float() * (-9.210340371976184 / embedding_dim))  # -9.210340371976184 = -ln(10000.0)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(1, 2)
        self.register_buffer('pe', pe)  # allows state-save

    def forward(self, x):
        x = x + self.pe
        return self.dropout(x)


class ContextLoader(nn.Module):
    def __init__(self, emb_dim, ant_samp, n_samp, sel_meth='stp', gap=1):
        """ Signal data context loader.

        Args:
            emb_dim (int): Embedding element length
            ant_samp (int): Anterior element length
            n_samp (int): Total number of samples per patch
            sel_meth (str): Flanking elements indices selection method (default: 'stp')
                - 'stp': Constant gap selection
                - 'lin': Linear increased gap selection
                - 'geo': Geometrical increased gap selection
            gap (int | float): Constant (for 'stp') or maximum (for 'lin' and 'geo') gap for selection
        """
        self.emb_dim = emb_dim
        self.ant = min(ant_samp, emb_dim - 1)  # Avoid index overflow
        self.samp = n_samp
        # Get index positions
        self.spc_num = max(self.ant, self.emb_dim - self.ant)  # Number of space samples
        if sel_meth == 'stp':
            idx = self.stp_idx(gap)
        elif sel_meth == 'lin':
            idx = self.lin_idx(gap)
        elif sel_meth == 'geo':
            idx = self.geo_idx(gap)
        else:
            # Fallback method
            warnings.warn("Invalid sampling method, fallback to constant step sampling.", SyntaxWarning, stacklevel=2)
            idx = self.stp_idx(gap)
        # Get sampling features
        self.pw = ((0, 0), (0, 0), (-idx[-1], idx[0]))
        self.tgt = np.add.outer(idx, range(-idx[-1], n_samp - idx[-1]))
        # Super
        super().__init__()

    def _spc2idx(func):
        """ Decorator for converting space to indices.

        Args:
            func (function): Space generation function

        Returns:
            function: Indices generation from space generation function
        """
        def inner(self, gap):
            space = func(self, gap)
            # Get accumulative distance
            distance = np.add.accumulate(space).astype(int)
            # Set origin on the posterior side
            idx = np.concatenate((distance[self.ant - 1::-1] * -1, distance[:self.emb_dim - self.ant] - distance[0]))
            return idx[::-1]  # Flip for transformer context loading order
        return inner

    @_spc2idx
    def stp_idx(self, gap=1):
        """ Return evenly spaced indices.

        Args:
            gap (int | float): Constant index distance between two adjacent selections (default: 1)

        Returns:
            np.ndarray: {1D-int} Relative index for the target position
        """
        return np.asarray([max(round(gap), 1)] * self.spc_num)  # Min distance is 1

    @_spc2idx
    def lin_idx(self, gap=3.0):
        """ Return indices spaced with a linear interval.

        Args:
            gap (int | float): Maximum index distance between two adjacent selections (default: 3.0)

        Returns:
            np.ndarray: {1D-int} Relative index for the target position
        """
        return np.linspace(1, gap, self.spc_num, endpoint=True).round(0)  # Min distance is 1

    @_spc2idx
    def geo_idx(self, gap=3.0):
        """ Return indices spaced with a geometric progression.

        Args:
            gap (int | float): Maximum index distance between two adjacent selections (default: 3.0)

        Returns:
            np.ndarray: {1D-int} Relative index for the target position
        """
        return np.geomspace(1, gap, self.spc_num, endpoint=True).round(0)  # Min distance is 1

    def forward(self, x):
        bs, ctx, _ = x.shape
        x_np = x.cpu().numpy()
        x_pad = np.pad(x_np, pad_width=self.pw, mode='constant', constant_values=0.0)
        x_context = x_pad[:, :, self.tgt]
        return torch.from_numpy(x_context[:, 0, :, :]).cuda()


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
