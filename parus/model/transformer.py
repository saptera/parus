# -*- coding: utf-8 -*-

"""Transformer model module

Encoder-only Transformer model used by PARUS for spike detection, together with its positional encoding
and sparse-context input loader.
"""

import numpy as np
import torch
import torch.nn as nn
import warnings

__package__ = 'parus.model'
__name__ = 'parus.model.transformer'

__all__ = ['EncoderTransformer']
"""
Public class list:

- EncoderTransformer(input_dim, context_dim, d_model, ...) : Encoder-only Transformer for spike detection

Internal classes:

- PositionalEncoding(embedding_dim, dropout, max_len)      : Sinusoidal positional encoding for the encoder
- SparseContextLoader(emb_dim, ant_samp, n_samp, ...)      : Sparse-context patch builder for the encoder input
"""


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding used by :class:`EncoderTransformer`.

    Implements the standard ``sin``/``cos`` positional encoding with a fixed maximum length and a learnable
    dropout layer. The encoding is registered as a buffer so it survives ``state_dict`` round-trips.
    """

    def __init__(self, embedding_dim, dropout, max_len=300):
        """Build the positional encoding buffer.

        Args:
            embedding_dim (int): Length of the embedding dimension along which the sinusoids are interleaved
            dropout (float): Dropout rate applied after the positional encoding is added to the input
            max_len (int): Maximum sequence length supported by the encoding (default: ``300``)
        """
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, embedding_dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, embedding_dim, 2).float() *
                             (-9.210340371976184 / embedding_dim))  # -9.210340371976184 = -ln(10000.0)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(1, 2)
        self.register_buffer('pe', pe)  # allows state-save

    def forward(self, x):
        x = x + self.pe
        return self.dropout(x)


class SparseContextLoader(nn.Module):
    """Build per-position context patches by sampling flanking elements at variable gaps.

    For every position in the input sequence, the loader gathers ``emb_dim`` flanking samples at offsets
    determined by ``sel_meth`` and ``gap``. The resulting patches form the context fed into the Transformer encoder.
    """

    def __init__(self, emb_dim, ant_samp, n_samp, sel_meth='stp', gap=1):
        """Pre-build the flanking-sample index map and register the module.

        Args:
            emb_dim (int): Embedding context length (number of flanking samples per position)
            ant_samp (int): Number of flanking samples drawn from the anterior side of the position
            n_samp (int): Total number of samples per input sequence (used to pre-build the index map)
            sel_meth (str): Flanking-sample sampling method; one of ``{'stp', 'lin', 'geo'}`` (default: ``'stp'``)

                - ``'stp'``: constant gap ``gap``
                - ``'lin'``: linearly increasing gap up to ``gap``
                - ``'geo'``: geometrically increasing gap up to ``gap``

            gap (int | float): Constant gap (for ``'stp'``) or maximum gap (for ``'lin'``/``'geo'``) (default: ``1``)

        Warns:
            SyntaxWarning: Emitted when ``sel_meth`` is unrecognised; ``'stp'`` is used as a fallback
        """
        self.emb_dim = emb_dim
        self.ant = min(ant_samp, emb_dim - 1)  # Avoid index overflow
        # Get index positions
        # Number of space samples
        self.spc_num = max(self.ant, self.emb_dim - self.ant)
        idx = self.get_idx(sel_meth, gap)
        # Get sampling features
        self.pw = (-idx[-1].item(), idx[0].item())
        self.tgt = np.add.outer(idx, range(-idx[-1], n_samp - idx[-1]))
        # Super
        super().__init__()

    def get_idx(self, meth='stp', gap=1):
        """Return the relative flanking-sample indices for the chosen sampling method.

        Args:
            meth (str): Flanking-sample sampling method; one of ``{'stp', 'lin', 'geo'}`` (default: ``'stp'``)

                - ``'stp'``: constant gap ``gap``
                - ``'lin'``: linearly increasing gap up to ``gap``
                - ``'geo'``: geometrically increasing gap up to ``gap``

            gap (int | float): Constant gap (for ``'stp'``) or maximum gap (for ``'lin'``/``'geo'``) (default: ``1``)

        Returns:
            np.ndarray: {1D-int} Relative offsets, ordered for Transformer context loading
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
        x_pad = nn.functional.pad(x, pad=self.pw, mode='constant', value=0.0)
        x_context = x_pad[:, :, self.tgt]
        # TODO: Dimension reserved future contexts, currently removed for efficiency
        return x_context[:, 0, :, :]


class EncoderTransformer(nn.Module):
    """Encoder-only Transformer for spike detection.

    Wraps a stack of standard :class:`~torch.nn.TransformerEncoderLayer` blocks behind a sparse-context
    input loader (``SparseContextLoader``) and a sinusoidal positional encoding (``PositionalEncoding``).
    The input is amplitude-normalised before the encoder and de-normalised on the way out so the model
    handles arbitrary recording scales.
    """

    def __init__(self, input_dim, context_dim, d_model, nhead, num_layers, dim_feedforward, output_channels):
        """Build the encoder stack, context loader, positional encoding, and linear heads.

        Args:
            input_dim (int): Number of samples per input sequence
            context_dim (int): Embedding context length per position
            d_model (int): Number of expected features in the input of each encoder layer
            nhead (int): Number of attention heads in each encoder layer
            num_layers (int): Number of encoder layers
            dim_feedforward (int): Hidden dimension of the feed-forward network in each encoder layer
            output_channels (int): Number of output channels produced by the final linear head
        """
        super(EncoderTransformer, self).__init__()
        self.input_linear = nn.Linear(context_dim, d_model)
        self.transformer_encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_feedforward, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(
            self.transformer_encoder_layer, num_layers)
        # Output size is same as input size
        self.output_linear = nn.Linear(d_model, context_dim)
        self.context_loader = SparseContextLoader(
            emb_dim=context_dim, ant_samp=context_dim // 4, n_samp=input_dim, sel_meth='lin', gap=4)
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
