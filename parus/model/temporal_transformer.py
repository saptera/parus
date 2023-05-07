import math
import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class ContextLoader(nn.Module):
    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim
        super().__init__()

    def forward(self, x):
        batch_size, _, seq_len = x.size()
        x_context = torch.zeros(batch_size, self.embedding_dim, seq_len)
        for i in range(batch_size):
            for j in range(seq_len):
                for k in range(self.embedding_dim):
                    if j - k < 0:
                        x_context[i][k][j] = 0
                    x_context[i][k][j] = x[i][0][j-k]
        return x_context


class FeedForward(nn.Module):
    def __init__(self, embedding_dim, d_ff=64, dropout=0.1):
        super().__init__()
        self.linear_1 = nn.Linear(embedding_dim, d_ff)
        self.dropout = nn.Dropout(dropout)
        self.linear_2 = nn.Linear(d_ff, embedding_dim)

    def forward(self, x):
        x = self.dropout(F.relu(self.linear_1(x)))
        x = self.linear_2(x)
        return x


class LayerNorm(nn.Module):
    def __init__(self, embedding_dim, eps=1e-6):
        super().__init__()

        self.size = embedding_dim
        # create two learnable parameters to calibrate normalisation
        self.alpha = nn.Parameter(torch.ones(self.size))
        self.bias = nn.Parameter(torch.zeros(self.size))
        self.eps = eps

    def forward(self, x):
        norm = self.alpha * (x - x.mean(dim=-1, keepdim=True)) \
            / (x.std(dim=-1, keepdim=True) + self.eps) + self.bias
        return norm


def scaled_dot_product(q, k, v, mask=None):
    d_k = q.size()[-1]
    attn_logits = torch.matmul(q, k.transpose(-2, -1))
    attn_logits = attn_logits / math.sqrt(d_k)
    if mask is not None:
        attn_logits = attn_logits.masked_fill(mask == 0, -9e15)
    attention = F.softmax(attn_logits, dim=-1)
    values = torch.matmul(attention, v)
    return values, attention


class MultiheadAttention(nn.Module):
    def __init__(self, seq_len, embedding_dim, n_head):
        super().__init__()
        assert embedding_dim % n_head == 0, "Embedding dimension must be 0 modulo number of heads."

        self.embed_dim = embedding_dim  # 16
        self.num_heads = n_head  # 4
        self.head_dim = embedding_dim // n_head  # 4

        self.i_proj = nn.Linear(1, embedding_dim)
        self.qkv_proj = nn.Linear(embedding_dim, 3*embedding_dim)
        self.o_proj = nn.Linear(embedding_dim, 1)

        self._reset_parameters()

    def _reset_parameters(self):
        nn.init.xavier_uniform_(self.qkv_proj.weight)
        self.qkv_proj.bias.data.fill_(0)
        nn.init.xavier_uniform_(self.o_proj.weight)
        self.o_proj.bias.data.fill_(0)

    def forward(self, x, mask=None, return_attention=False):
        x = x.permute(0, 2, 1)
        x = self.i_proj(x)
        batch_size, seq_len, embed_dim = x.size()
        qkv = self.qkv_proj(x)

        qkv = qkv.reshape(batch_size, seq_len,
                          self.num_heads, 3*self.head_dim)
        qkv = qkv.permute(0, 2, 1, 3)  # [Batch, Head, SeqLen, Dims]
        q, k, v = qkv.chunk(3, dim=-1)

        # Determine value outputs
        values, attention = scaled_dot_product(q, k, v, mask=mask)
        values = values.permute(0, 2, 1, 3)  # [Batch, SeqLen, Head, Dims]
        values = values.reshape(batch_size, seq_len, embed_dim)
        o = self.o_proj(values)

        if return_attention:
            return o, attention
        else:
            return o


class PositionalEncoding(nn.Module):
    def __init__(self, embedding_dim, dropout, max_len: int = 300):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, embedding_dim)  # like 300x4
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(
            0, embedding_dim, 2).float() * (-math.log(10000.0) / embedding_dim))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1).transpose(0, 2)
        self.register_buffer('pe', pe)  # allows state-save

    def forward(self, x):
        x = x + self.pe
        return self.dropout(x)


class TransformerBlock(nn.Module):
    def __init__(self, seq_len, embedding_dim, n_head):
        super(TransformerBlock, self).__init__()
        self.norm_1 = LayerNorm(embedding_dim)
        self.norm_2 = LayerNorm(embedding_dim)
        self.multi_head = MultiheadAttention(seq_len, embedding_dim, n_head)
        self.ff = FeedForward(embedding_dim)
        self.dropout_1 = nn.Dropout(0.1)
        self.dropout_2 = nn.Dropout(0.1)

    def forward(self, x):
        x.transpose(1, 2)
        x = x + self.dropout_1(self.multi_head(x))
        x = self.norm_1(x)
        x = x + self.dropout_2(self.ff(x))
        x = self.norm_2(x)
        return x.contiguous()


def get_clones(module, N):
    return nn.ModuleList([copy.deepcopy(module) for i in range(N)])


class TemporalTransformer(nn.Module):
    def __init__(self, seq_len, embedding_dim, n_head, n_stack):
        super(TemporalTransformer, self).__init__()
        self.n_stack = n_stack
        self.context_loader = ContextLoader(embedding_dim)
        self.layer_norm = LayerNorm(embedding_dim)
        self.blocks = get_clones(TransformerBlock(
            seq_len, embedding_dim, n_head), n_stack)
        self.positional_encoding = PositionalEncoding(
            embedding_dim, 0.1, seq_len)

    def forward(self, x):
        scale = torch.abs(x).max(2, keepdim=True)[0]
        output = x / scale
        output = self.context_loader(output)
        output = self.positional_encoding(output)
        for i in range(self.n_stack):
            output = self.blocks[i](output)
        output = self.layer_norm(output)
        output *= scale
        return output.contiguous()
