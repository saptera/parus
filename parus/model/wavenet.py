# -*- coding: utf-8 -*-

"""WaveNet model module

WaveNet model and its building blocks (causal/dilated convolutions, residual blocks, residual stack, and
the final dense network).
"""

import torch
import torch.nn as nn

__package__ = 'parus.model'
__name__ = 'parus.model.wavenet'

__all__ = ['WaveNet']
"""
Public class list:

- WaveNet(layer_size, stack_size, in_channels, res_channels)   : Top-level WaveNet model

Internal classes:

- DilatedCausalConv1d(channels, dilation)                      : Dilated causal 1D convolution
- CausalConv1d(in_channels, out_channels)                      : Causal 1D convolution
- ResidualBlock(res_channels, skip_channels, dilation)         : Single residual block with PixelCNN gating
- ResidualStack(layer_size, stack_size, res_channels, ...)     : Stack of residual blocks across layers and stacks
- DensNet(channels)                                            : Final dense network sitting after the residual stack
"""


class DilatedCausalConv1d(nn.Module):
    """Dilated causal 1D convolution used inside a WaveNet residual block.

    Wraps :class:`~torch.nn.Conv1d` with kernel size ``3`` and matching dilation/padding so that the output
    is causal and shares the input length.
    """

    def __init__(self, channels, dilation=1):
        """Build the dilated causal convolution.

        Args:
            channels (int): Number of channels in the input (and output)
            dilation (int): Spacing between kernel elements (default: ``1``)
        """
        super(DilatedCausalConv1d, self).__init__()
        self.conv = nn.Conv1d(channels, channels,
                              kernel_size=3, stride=1,  # Fixed for WaveNet
                              dilation=dilation,
                              padding=dilation,  # Fixed for WaveNet dilation
                              bias=True)  # Fixed for WaveNet
        self.dilation = dilation

    def init_weights_for_test(self):
        """Initialise every :class:`~torch.nn.Conv1d` weight to ``0.5`` for deterministic test runs."""
        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                m.weight.data.fill_(0.5)

    def forward(self, x):
        output = self.conv(x)[:,:,:]
        return output


class CausalConv1d(nn.Module):
    """Causal 1D convolution used as the front-end of WaveNet.

    Wraps :class:`~torch.nn.Conv1d` with kernel size ``3`` and padding ``1`` so that the output length
    matches the input length.
    """

    def __init__(self, in_channels, out_channels):
        """Build the causal convolution.

        Args:
            in_channels (int): Number of channels in the input
            out_channels (int): Number of channels in the output
        """
        super(CausalConv1d, self).__init__()
        # Padding 1 for same size/length between input and output for causal convolution
        self.conv = nn.Conv1d(in_channels, out_channels,
                              kernel_size=3, stride=1, padding=1,
                              bias=True)  # Fixed for WaveNet

    def init_weights_for_test(self):
        """Initialise every :class:`~torch.nn.Conv1d` weight to ``0.5`` for deterministic test runs."""
        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                m.weight.data.fill_(0.5)

    def forward(self, x):
        output = self.conv(x)
        # Remove last value for causal convolution
        return output


class ResidualBlock(nn.Module):
    """Single WaveNet residual block with PixelCNN gating, residual output, and skip output.

    The block applies a ``DilatedCausalConv1d``, splits the activation into ``tanh``/``sigmoid``
    branches (PixelCNN gate), then projects through two ``1x1`` convolutions for the residual and skip outputs.
    """

    def __init__(self, res_channels, skip_channels, dilation):
        """Build the dilated convolution, gating, and 1x1 projections.

        Args:
            res_channels (int): Number of residual channels for the input/residual path
            skip_channels (int): Number of skip channels for the skip path
            dilation (int): Spacing between kernel elements of the dilated convolution
        """
        super(ResidualBlock, self).__init__()
        self.dilated = DilatedCausalConv1d(res_channels, dilation=dilation)
        self.conv_res = nn.Conv1d(res_channels, res_channels, 1)
        self.conv_skip = nn.Conv1d(res_channels, skip_channels, 1)
        self.gate_tanh = nn.Tanh()
        self.gate_sigmoid = nn.Sigmoid()

    def forward(self, x, skip_size):
        output = self.dilated(x)
        # PixelCNN gate
        gated_tanh = self.gate_tanh(output)
        gated_sigmoid = self.gate_sigmoid(output)
        gated = gated_tanh * gated_sigmoid
        # Residual network
        output = self.conv_res(gated)
        input_cut = x[:, :, -output.size(2):]
        output += input_cut
        # Skip connection
        skip = self.conv_skip(gated)
        skip = skip[:, :, -skip_size:]
        return output, skip


class ResidualStack(nn.Module):
    """Stack of WaveNet residual blocks across layers and stacks.

    The dilation of the ``i``-th block in a layer is ``2 ** i``; ``stack_size`` such layers are stacked back to back.
    For example, ``layer_size=10`` and ``stack_size=5`` yields five layers of dilations ``[1, 2, 4, ..., 512]``.
    """

    def __init__(self, layer_size, stack_size, res_channels, skip_channels):
        """Build every residual block defined by the dilation schedule.

        Args:
            layer_size (int): Number of blocks per layer (e.g. ``10`` → dilations ``1, 2, 4, ..., 512``)
            stack_size (int): Number of layers in the stack
            res_channels (int): Number of residual channels for input/output
            skip_channels (int): Number of skip channels for output
        """
        super(ResidualStack, self).__init__()
        self.layer_size = layer_size
        self.stack_size = stack_size
        self.res_blocks = self.stack_res_block(res_channels, skip_channels)

    @staticmethod
    def _residual_block(res_channels, skip_channels, dilation):
        """Build a residual block and place it on CUDA (with :class:`~torch.nn.DataParallel` when available).

        Args:
            res_channels (int): Number of residual channels for input/output
            skip_channels (int): Number of skip channels for output
            dilation (int): Spacing between kernel elements

        Returns:
            ResidualBlock | nn.DataParallel: The constructed residual block, optionally data-parallelised
                across multiple GPUs and moved to CUDA when one is available
        """
        block = ResidualBlock(res_channels, skip_channels, dilation)
        if torch.cuda.device_count() > 1:
            block = nn.DataParallel(block)
        if torch.cuda.is_available():
            block.cuda()
        return block

    def build_dilations(self):
        """Return the dilation schedule for the full stack.

        Returns:
            list[int]: Dilation values for every block in the stack, in stack-then-layer order
        """
        dilations = []
        # 5 = stack[layer1, layer2, layer3, layer4, layer5]
        for s in range(0, self.stack_size):
            # 10 = layer[dilation=1, dilation=2, 4, 8, 16, 32, 64, 128, 256, 512]
            for l in range(0, self.layer_size):
                dilations.append(2 ** l)
        return dilations

    def stack_res_block(self, res_channels, skip_channels):
        """Build every residual block defined by the stack's dilation schedule.

        Args:
            res_channels (int): Number of residual channels for input/output
            skip_channels (int): Number of skip channels for output

        Returns:
            list[ResidualBlock | nn.DataParallel]: One residual block per dilation entry from
                :meth:`build_dilations`, in the same order
        """
        res_blocks = []
        dilations = self.build_dilations()
        for dilation in dilations:
            block = self._residual_block(res_channels, skip_channels, dilation)
            res_blocks.append(block)
        return res_blocks

    def forward(self, x, skip_size):
        output = x
        skip_connections = []
        for res_block in self.res_blocks:
            # output is the next input
            output, skip = res_block(output, skip_size)
            skip_connections.append(skip)
        return torch.stack(skip_connections)


class DensNet(nn.Module):
    """Final dense network sitting after the WaveNet residual stack."""

    def __init__(self, channels):
        """Build the dense network.

        Args:
            channels (int): Number of channels for the intermediate convolutions
        """
        super(DensNet, self).__init__()
        self.conv1 = nn.Conv1d(1, channels, 1)
        self.conv2 = nn.Conv1d(channels, channels, 1)
        self.relu = nn.ReLU()
        self.linear = nn.Linear(300,300)

    def forward(self, x):
        output = self.linear(x)
        output = self.conv1(output)
        output = self.linear(output)
        output = self.conv2(output)
        return output


class WaveNet(nn.Module):
    """WaveNet model for spike-detection prediction.

    Composes a ``CausalConv1d`` front-end, a ``ResidualStack``, and a ``DensNet`` head. Inputs are amplitude-normalised
    before the front-end and de-normalised on the way out so the model handles arbitrary recording scales.
    """

    def __init__(self, layer_size, stack_size, in_channels, res_channels):
        """Build the front-end, residual stack, and dense head.

        Args:
            layer_size (int): Number of blocks per residual layer (e.g. ``10`` → dilations ``1, 2, 4, ..., 512``)
            stack_size (int): Number of layers in the residual stack
            in_channels (int): Number of channels in the input
            res_channels (int): Number of residual channels passed through the residual stack
        """
        super(WaveNet, self).__init__()
        self.causal = CausalConv1d(in_channels, res_channels)
        self.res_stack = ResidualStack(layer_size, stack_size, res_channels, in_channels)
        self.densnet = DensNet(1)

    def forward(self, x):
        scale = torch.abs(x).max(2, keepdim=True)[0]
        output = x / scale
        output = self.causal(output)
        skip_connections = self.res_stack(output, 300)
        output = torch.sum(skip_connections, dim=0)
        output = self.densnet(output)
        output *= scale
        return output.contiguous()
