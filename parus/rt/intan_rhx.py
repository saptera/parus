# -*- coding: utf-8 -*-

"""Intan RHX software TCP real-time data streaming module

TCP-based real-time waveform streaming adapter for the IntanTech RHX recording software.
"""

import time
import socket
import warnings
import numpy as np

__package__ = 'parus.rt'
__name__ = 'parus.rt.intan_rhx'
from .hwio import SingletonIO, CircularBufferFL, CircularBufferCR, MapArrayQueue,read_uint16, read_uint32

__all__ = ['IntanRHXmTCP']
"""
Public class list:

- IntanRHXmTCP(dq, cb)        : Real-time TCP waveform streaming adapter for the Intan RHX software
"""


class IntanRHXmTCP(metaclass=SingletonIO):
    """Real-time TCP waveform streaming adapter for the IntanTech RHX recording software.

    Connects to the RHX command and waveform TCP servers, configures channel routing, and parses the
    incoming binary blocks into per-frame microvolt samples that are pushed to a downstream
    :class:`~parus.rt.hwio.MapArrayQueue` (for processing) and a
    :class:`~parus.rt.hwio.CircularBufferFL`/:class:`~parus.rt.hwio.CircularBufferCR` (for visualisation).

    The class uses :class:`~parus.rt.hwio.SingletonIO` as its metaclass so a single connection is shared
    process-wide.
    """
    frame_per_block = 128  # Hard-coded in RHX software to always handle data in blocks of 128 frames
    magic_number = 0x2ef07a08  # Intan RHX TCP magic number

    def __init__(self, dq, cb):
        """Wire the streaming adapter to the supplied data queue and visualisation buffer.

        Args:
            dq (MapArrayQueue): FIFO queue that receives the parsed waveform samples
            cb (CircularBufferFL | CircularBufferCR): Circular buffer that mirrors the same samples for visualisation
        """
        # Communication attributes
        self.sys_typ = None  # Intan controller type
        self.svr_cmd = None  # TCP command server socket
        self.buf_cmd = 1024  # Buffer size for reading TCP command socket
        self.svr_wfm = None  # TCP waveform server socket
        self.buf_wfm = 200000  # Buffer size for reading TCP waveform socket
        self.fs = 0  # Recoding sampling frequency
        self.timestep = 0  # Time step per sample, reciprocal of sampling frequency
        self.lst_chs = []  # List of channel names for data streaming
        self.blk_bts = 0  # Bytes per block
        self.running = False
        # Data operators
        self.dq = dq
        self.cb = cb
        self.__q_on = False

    def set_command_buffer_size(self, size):
        """Set the read buffer size for the TCP command socket.

        Increase this when many return commands are expected; ``1024`` bytes is sufficient for a single
        command/response pair.

        Args:
            size (int): Maximum number of bytes expected per single read
        """
        self.buf_cmd = size

    def set_waveform_buffer_size(self, size):
        """Set the read buffer size for the TCP waveform socket.

        Increase this when channels, filter bands, or acquisition time grow. TCP latency at start and stop
        of acquisition means the exact number of data blocks per read may vary.

        For one second of recording, the size ``N`` can be computed as ::

            N = (FramePerBlock * WaveformBytesPerFrame + SizeOfMagicNumber) * NumBlock

        with

            - ``FramePerBlock = 128`` (hard-coded)
            - ``WaveformBytesPerFrame = SizeOfTimestamp + SizeOfSample``
                - ``SizeOfTimestamp = 4`` (int32)
                - ``SizeOfSample = 2 * NumChannel`` (uint16)
            - ``SizeOfMagicNumber = 4`` (uint32, ``0x2ef07a08``)
            - ``NumBlock = ceil(SamplingRate / FramePerBlock)``

        Args:
            size (int): Maximum number of bytes expected per single read
        """
        self.buf_wfm = size

    def connect_to_server(self, svr_ip='localhost', cmd_port=5000, wfm_port=5001):
        """Open both TCP sockets, identify the controller, and stop the recording if it is already running.

        After a successful connection the controller type, sampling rate, and timestep are populated and
        any previously configured TCP data outputs are cleared.

        Args:
            svr_ip (str): Intan RHX software TCP server IP address (default: ``'localhost'``)
            cmd_port (int): Intan RHX software command socket port (default: ``5000``)
            wfm_port (int): Intan RHX software waveform socket port (default: ``5001``)

        Returns:
            bool: :data:`True` when both sockets connected; :data:`False` when the connection was refused

        Raises:
            ValueError: If the controller returns an unknown type string
            IOError: If the controller does not return a sampling rate
        """
        try:
            # Connect to TCP command server
            self.svr_cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.svr_cmd.connect((svr_ip, cmd_port))
            # Connect to TCP waveform server
            self.svr_wfm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.svr_wfm.connect((svr_ip, wfm_port))
        except ConnectionRefusedError:
            return False

        # Query controller type
        self.svr_cmd.sendall(b'get type')
        cmd_retval = str(self.svr_cmd.recv(self.buf_cmd), 'utf-8')
        if cmd_retval == "Return: Type ControllerRecordUSB2":
            self.sys_typ = 'rec2'
        elif cmd_retval == "Return: Type ControllerRecordUSB3":
            self.sys_typ = 'rec3'
        elif cmd_retval == "Return: Type ControllerStimRecord":
            self.sys_typ = 'stir'
        else:
            raise ValueError("Invalid controller type!")

        # Query runmode from RHX software
        self.svr_cmd.sendall(b'get runmode')
        cmd_retval = str(self.svr_cmd.recv(self.buf_cmd), 'utf-8')
        # Stop running controller
        if cmd_retval != "Return: RunMode Stop":
            self.svr_cmd.sendall(b'set runmode stop')
            time.sleep(0.1)  # Wait controller

        # Query sampling rate from RHX software
        self.svr_cmd.sendall(b'get sampleratehertz')
        cmd_retval = str(self.svr_cmd.recv(self.buf_cmd), 'utf-8')
        # Look for sampling rate string
        if cmd_retval.find("Return: SampleRateHertz ") == -1:
            raise IOError("Unable to get sampling rate from server!")
        # Calculate timestep
        self.fs = float(cmd_retval[24:])  # 24 = len("Return: SampleRateHertz ")
        self.timestep = 1/ self.fs

        # Clear TCP data output to ensure no TCP channels are enabled
        self.svr_cmd.sendall(b'execute clearalldataoutputs')
        time.sleep(0.1)  # Wait controller
        return True

    def config_channel(self, port, ch, sub=None, enable=True):
        """Enable or disable a single controller channel for TCP data streaming.

        The accepted ports depend on the controller variant; using a port that is not supported by the
        connected controller emits a :class:`RuntimeWarning` and the call is ignored.

        Args:
            port (str): Port name; one of ``{'a'-'d', 'e'-'h' (1024-channel only), 'analog-in', 'analog-out',
                'digital-in', 'digital-out'}``
            ch (int): Channel number on the port
            sub (str | None): Sub-channel name for amplifier ports; one of ``{'aux', 'vdd'}``; pass
                :data:`None` for the main amplifier channel (default: ``None``)
            enable (bool): When :data:`True`, enable the channel; when :data:`False`, disable it (default: ``True``)

        Returns:
            str | None: Configured channel name on success; :data:`None` when the requested combination is
                rejected (with a warning)

        Warns:
            RuntimeWarning: Emitted when ``port``/``sub`` combinations are invalid for the connected controller
        """
        # Arrange name
        port = port.strip().lower()
        if port in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            if sub is None:
                name = '%s-%03d' % (port, ch)
            else:
                sub = sub.strip().lower()
                # Check sub-channel name
                if sub not in ['aux', 'vdd']:
                    warnings.warn("Invalid amplifier sub-channel [%s], valid names ['aux', 'vdd']" % sub.upper(),
                                  RuntimeWarning, stacklevel=2)
                    return
                # Check controller compatibility
                if self.sys_typ == 'stir':
                    warnings.warn("Amplifier %s sub-channels cannot be directly controlled through TCP "
                                  "with Stimulation/Recording Controller" % sub.upper(), RuntimeWarning, stacklevel=2)
                    return
                name = '%s-%s%d' % (port, sub, ch)
        elif port == 'analog-in':
            name = 'analog-in-%02d' % ch if self.sys_typ == 'rec2' else 'analog-in-%d' % ch
        elif port == 'analog-out':
            if self.sys_typ == 'stir':
                name = 'analog-out-%d' % ch
            else:
                warnings.warn("Analog output channels cannot be directly controlled through TCP "
                              "with USB Interface Board or Recording Controller", RuntimeWarning, stacklevel=2)
                return
        elif port in ['digital-in', 'digital-out']:
            name = '%s-%02d' % (port, ch) if self.sys_typ == 'rec2' else '%s-%d' % (port, ch)
        else:
            warnings.warn("Invalid port [%s], valid names ['a'-'d', 'e'-'h'(1024CH), 'analog-in', 'analog-out', "
                          "'digital-in', 'digital-out']" % port.upper(), RuntimeWarning, stacklevel=2)
            return
        # Configure channel
        if enable:
            if name not in self.lst_chs:
                self.lst_chs.append(name)
                self.svr_cmd.sendall(bytes('set %s.tcpdataoutputenabled true' % name, 'utf-8'))
                time.sleep(0.1)  # Wait controller
        else:
            if name in self.lst_chs:
                self.lst_chs.remove(name)
                self.svr_cmd.sendall(bytes('set %s.tcpdataoutputenabled false' % name, 'utf-8'))
                time.sleep(0.1)  # Wait controller
        return name

    def write_data_queue(self, enable=True):
        """Toggle whether incoming samples are pushed to the data queue (the visualisation buffer is always written).

        Args:
            enable (bool): When :data:`True`, enable writes to ``self.dq``; when :data:`False`, only the
                visualisation buffer is updated (default: ``True``)
        """
        self.__q_on = enable

    def run(self):
        """Compute the per-block byte size and start the controller's recording run mode."""
        waveform_bytes_per_frame = 4 + 2 * len(self.lst_chs)
        self.blk_bts = self.frame_per_block * waveform_bytes_per_frame + 4
        self.svr_cmd.sendall(b'set runmode run')
        self.running = True

    def read(self):
        """Read one batch from the waveform socket, parse it into samples, and push them downstream.

        Each block starts with the ``0x2ef07a08`` magic number followed by ``frame_per_block`` frames; each
        frame consists of an INT32 timestamp (ignored) and a UINT16 sample that is converted to microvolts
        with the Intan factor ``0.195`` and zero-offset ``32768``.

        Raises:
            ValueError: If the received payload is not an integer multiple of ``blk_bts`` or any block's
                magic number is wrong (indicating data corruption)
        """
        raw = self.svr_wfm.recv(self.buf_wfm)
        blk_cnt, blk_rem = divmod(len(raw), self.blk_bts)
        if blk_rem != 0:
            raise ValueError("Arrived data is not an integer multiple of the expected data size per block.")
        # Parsing data block
        pos = 0  # Current byte position
        for _ in range(blk_cnt):
            # Verify Intan RHX TCP Magic Number
            magic_number, pos = read_uint32(raw, pos)
            if magic_number != 0x2ef07a08:
                raise ValueError('Incorrect magic number, raw data corrupted!')
            # Parsing data frame
            smp = np.zeros(128, dtype=np.float32)  # Initialize data
            for i in range(self.frame_per_block):
                # Ignore timestamp
                pos += 4  # INT32 data type
                # Get waveform sample
                raw_sp, pos = read_uint16(raw, pos)
                smp[i] = 0.195 * (raw_sp - 32768)  # Convert to microvolts
            # Assign to outputs
            if self.__q_on:
                self.dq.put(smp)
            self.cb.put(smp)

    def stop(self):
        """Stop the controller's run mode and clear all configured TCP data outputs."""
        self.svr_cmd.sendall(b'set runmode stop')
        time.sleep(0.1)  # Wait controller
        self.svr_cmd.sendall(b'execute clearalldataoutputs')
        time.sleep(0.1)  # Wait controller
        self.running = False

    def disconnect_server(self):
        """Stop streaming (if running) and close both TCP sockets."""
        # Stop running session
        if self.running:
            self.stop()
        # Disconnect
        self.svr_cmd.shutdown(socket.SHUT_RDWR)
        self.svr_wfm.shutdown(socket.SHUT_RDWR)
        time.sleep(0.1)
        self.svr_cmd.close()
        self.svr_wfm.close()
        time.sleep(0.1)
