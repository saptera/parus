# WaveNet model module

import torch
import torch.nn as nn

__package__ = 'parus.model'
__name__ = 'parus.model.wavenet'

__all__ = ['WaveNet']
"""
Class list:
  DilatedCausalConv1d(channels, dilation=1): Dilated Causal Convolution for WaveNet.
  CausalConv1d(in_channels, out_channels): Causal Convolution for WaveNet.
  ResidualBlock(res_channels, skip_channels, dilation=1): Residual block.
  ResidualStack(layer_size, stack_size, res_channels, skip_channels): Stack residual blocks by layer and stack size.
  DensNet(channels): The last network of WaveNet.
  WaveNet(layer_size, stack_size, in_channels, res_channels): WaveNet model.
"""


class DilatedCausalConv1d(nn.Module):
    def __init__(self, channels, dilation=1):
        """ Dilated Causal Convolution for WaveNet.

        Args:
            channels (int): Number of channels in the input/output
            dilation (int): Spacing between kernel elements (default: 1)
        """
        super(DilatedCausalConv1d, self).__init__()
        self.conv = nn.Conv1d(channels, channels,
                              kernel_size=3, stride=1,  # Fixed for WaveNet
                              dilation=dilation,
                              padding=dilation,  # Fixed for WaveNet dilation
                              bias=True)  # Fixed for WaveNet
        self.dilation = dilation

    def init_weights_for_test(self):
        """ Weight initialization. """
        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                m.weight.data.fill_(0.5)

    def forward(self, x):
        output = self.conv(x)[:,:,:]
        return output


class CausalConv1d(nn.Module):
    def __init__(self, in_channels, out_channels):
        """ Causal Convolution for WaveNet.

        Args:
            in_channels (int): Number of channels in the input
            out_channels (int): Number of channels for the output
        """
        super(CausalConv1d, self).__init__()
        # Padding 1 for same size/length between input and output for causal convolution
        self.conv = nn.Conv1d(in_channels, out_channels,
                              kernel_size=3, stride=1, padding=1,
                              bias=True)  # Fixed for WaveNet

    def init_weights_for_test(self):
        """ Weight initialization. """
        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                m.weight.data.fill_(0.5)

    def forward(self, x):
        output = self.conv(x)
        # Remove last value for causal convolution
        return output


class ResidualBlock(nn.Module):
    def __init__(self, res_channels, skip_channels, dilation):
        """ Residual block.

        Args:
            res_channels (int): Number of residual channels for input
            skip_channels (int): Number of skip channels for output
            dilation (int): Spacing between kernel elements
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
    def __init__(self, layer_size, stack_size, res_channels, skip_channels):
        """ Stack residual blocks by layer and stack size.

        Args:
            layer_size (int): Number of layers, 10 = layer[dilation=1, dilation=2, 4, 8, 16, 32, 64, 128, 256, 512]
            stack_size (int): Number of stacks, 5 = stack[layer1, layer2, layer3, layer4, layer5]
            res_channels (int): Number of residual channels for input/output
            skip_channels (int): Number of skip channels for output
        """
        super(ResidualStack, self).__init__()
        self.layer_size = layer_size
        self.stack_size = stack_size
        self.res_blocks = self.stack_res_block(res_channels, skip_channels)

    @staticmethod
    def _residual_block(res_channels, skip_channels, dilation):
        """ Load residual block to device.

        Args:
            res_channels (int): Number of residual channels for input/output
            skip_channels (int): Number of skip channels for output
            dilation (int): Spacing between kernel elements

        Returns:
            Loaded residual block
        """
        block = ResidualBlock(res_channels, skip_channels, dilation)
        if torch.cuda.device_count() > 1:
            block = nn.DataParallel(block)
        if torch.cuda.is_available():
            block.cuda()
        return block

    def build_dilations(self):
        """ Build dilation levels with stack. """
        dilations = []
        # 5 = stack[layer1, layer2, layer3, layer4, layer5]
        for s in range(0, self.stack_size):
            # 10 = layer[dilation=1, dilation=2, 4, 8, 16, 32, 64, 128, 256, 512]
            for l in range(0, self.layer_size):
                dilations.append(2 ** l)
        return dilations

    def stack_res_block(self, res_channels, skip_channels):
        """ Prepare dilated convolution blocks by layer and stack size.

        Args:
            res_channels (int): Number of residual channels for input/output
            skip_channels (int): Number of skip channels for output

        Returns:
            Stacked residual block
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
    def __init__(self, channels):
        """ The last network of WaveNet.

        Args:
            channels (int): Number of channels for input/output
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
    def __init__(self, layer_size, stack_size, in_channels, res_channels):
        """ WaveNet model.

        Args:
            layer_size (int): Number of layers, 10 = layer[dilation=1, dilation=2, 4, 8, 16, 32, 64, 128, 256, 512]
            stack_size (int): Number of stacks, 5 = stack[layer1, layer2, layer3, layer4, layer5]
            in_channels (int): Number of channels for input
            res_channels (int): Number of channels for output
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
