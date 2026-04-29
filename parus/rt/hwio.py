# -*- coding: utf-8 -*-

"""Hardware IO basic function module

Building blocks for the PARUS real-time data path: a singleton metaclass for hardware controllers, two fixed-capacity
1D circular buffers, a fixed-array queue, and a family of low-level byte-array integer readers.
"""

import queue
import numpy as np


__package__ = 'parus.rt'
__name__ = 'parus.rt.hwio'

__all__ = ['SingletonIO', 'CircularBufferFL', 'CircularBufferCR', 'MapArrayQueue',
           'read_uint8', 'read_int8', 'read_uint16', 'read_int16', 'read_uint32', 'read_int32',
           'read_uint64', 'read_int64']
"""
Public class list:

- SingletonIO                                   : Singleton metaclass for real-time hardware IO controllers
- CircularBufferFL(size, dtype)                 : Fall-out-left circular buffer for 1D data
- CircularBufferCR(size, dtype)                 : Carriage-return circular buffer for 1D data
- MapArrayQueue(arr_len, que_len, dtype, mode)  : Queue of fixed-length 1D array items

Public function list:

- read_uint8(array, index)                      : Read 1 byte as an unsigned 8-bit integer
- read_int8(array, index)                       : Read 1 byte as a signed 8-bit integer
- read_uint16(array, index)                     : Read 2 bytes as an unsigned 16-bit integer
- read_int16(array, index)                      : Read 2 bytes as a signed 16-bit integer
- read_uint32(array, index)                     : Read 4 bytes as an unsigned 32-bit integer
- read_int32(array, index)                      : Read 4 bytes as a signed 32-bit integer
- read_uint64(array, index)                     : Read 8 bytes as an unsigned 64-bit integer
- read_int64(array, index)                      : Read 8 bytes as a signed 64-bit integer
"""


class SingletonIO(type):
    """Singleton metaclass for real-time hardware IO controllers.

    Ensures that any class using this metaclass returns the same instance for repeated constructor calls,
    so a hardware controller is only opened once per process.
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonIO, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CircularBufferFL:
    """Fall-out-left circular buffer for 1D data.

    Behaves as a finite-capacity write-anywhere buffer: every new sample is appended at the right end and,
    once the buffer is full, older samples on the left are dropped to make room. Useful for short-history
    recording where only the most recent ``size`` samples matter.
    """

    def __init__(self, size, dtype=np.float32):
        """Initialise the buffer to the given capacity and dtype.

        Args:
            size (int): Buffer capacity in samples (must be positive)
            dtype (np.number | str): NumPy data type for the underlying array (default: ``np.float32``)

        Raises:
            ValueError: If ``size`` is not a positive integer
        """
        # Set inputs
        self.size = int(size)
        if self.size <= 0:
            raise ValueError("Size must be a positive integer!")
        self.dtype = dtype
        # Initialize buffer
        self.buf = np.zeros(self.size, dtype=self.dtype)
        self._ptr = 0  # Buffer position pointer

    def __len__(self):
        return self.size

    def __getitem__(self, item):
        return self.buf[item]

    def __setitem__(self, key, value):
        self.buf[key] = value
        return

    def empty(self):
        """Return :data:`True` when no samples have been written into the buffer yet."""
        return self._ptr == 0

    def full(self):
        """Return :data:`True` when the buffer has been fully filled."""
        return self._ptr == self.size

    def put(self, data):
        """Append ``data`` to the buffer; older samples on the left are discarded when the buffer is full.

        Args:
            data (np.ndarray): {1D} Samples to append
        """
        num = data.size
        if num < self.size:
            avl = self.size - self._ptr
            if num > avl:
                pos = num - avl
                self.buf[:-num] = self.buf[pos:self._ptr]  # Shift
                self.buf[-num:] = data  # Assign
                self._ptr = self.size
            else:
                pos = self._ptr + num
                self.buf[self._ptr:pos] = data
                self._ptr = pos
        else:
            self.buf = data[-self.size:]
            self._ptr = self.size

    def get(self):
        """Return a copy of the currently filled portion of the buffer."""
        return self.buf[:self._ptr].copy()

    def resize(self, size):
        """Resize the buffer to a new capacity, preserving as many existing samples as possible.

        Args:
            size (int): New buffer capacity (must be positive)

        Raises:
            ValueError: If ``size`` is not a positive integer
        """
        # Check inputs
        size = int(size)
        if size <= 0:
            raise ValueError("Size must be a positive integer!")
        # Set new size
        if size < self.size:
            self.buf = self.buf[-size:]
            self.size = size
            self._ptr = min(self._ptr, size)
        elif size > self.size:
            dat = self.buf
            self.buf = np.zeros(size, dtype=self.dtype)
            self.buf[:self.size] = dat
            self.size = size
        else:
            pass  # Equal size, nothing to change

    def flush(self, hard=False):
        """Reset the buffer write pointer (and optionally zero out the underlying memory).

        Args:
            hard (bool): When :data:`True`, also zero out the underlying array; when :data:`False`, only
                the write pointer is reset (default: ``False``)
        """
        self._ptr = 0
        if hard:
            self.buf[:] = 0


class CircularBufferCR:
    """Carriage-return circular buffer for 1D data.

    Behaves as a fixed-capacity ring buffer: when the write pointer reaches the end of the buffer, it wraps
    back to the start and overwrites the oldest samples. The visible content always covers the most recent
    ``size`` samples; reads return them in the order they were written.
    """

    def __init__(self, size, dtype=np.float32):
        """Initialise the ring buffer to the given capacity and dtype.

        Args:
            size (int): Buffer capacity in samples (must be positive)
            dtype (np.number | str): NumPy data type for the underlying array (default: ``np.float32``)

        Raises:
            ValueError: If ``size`` is not a positive integer
        """
        # Set inputs
        self.size = int(size)
        if self.size <= 0:
            raise ValueError("Size must be a positive integer!")
        self.dtype = dtype
        # Initialize buffer
        self.buf = np.zeros(self.size, dtype=self.dtype)
        self._ptr = 0  # Buffer position pointer
        # Initialize control variables
        self.__empty = True
        self.__full = False

    def __len__(self):
        return self.size

    def __getitem__(self, item):
        return self.buf[item]

    def __setitem__(self, key, value):
        self.buf[key] = value
        return

    def empty(self):
        """Return :data:`True` when no samples have been written into the buffer yet."""
        return self.__empty

    def full(self):
        """Return :data:`True` once the buffer has been fully filled at least once."""
        return self.__full

    def position(self, pos):
        """Move the write pointer to ``pos`` (clamped to ``[0, size - 1]``).

        Args:
            pos (int): New write-pointer position
        """
        pos = 0 if pos < 0 else pos if pos < self.size else self.size - 1
        self._ptr = pos

    def locate(self):
        """Return the current write-pointer position."""
        return self._ptr

    def put(self, data):
        """Append ``data`` to the ring buffer, wrapping the write pointer when it reaches the end.

        Args:
            data (np.ndarray): {1D} Samples to append
        """
        num = data.size
        # Update status
        if self.__empty and num > 0:
            self.__empty = False
        # Set values
        if num < self.size:
            avl = self.size - self._ptr
            if num > avl:
                pos = num - avl
                self.buf[self._ptr:] = data[:avl]
                self.buf[:pos] = data[avl:]
                self.__full = True  # Update status
            else:
                pos = self._ptr + num
                self.buf[self._ptr:pos] = data
            self._ptr = pos
        else:
            self.buf = data[-self.size:]
            self._ptr = self.size
            self.__full = True  # Update status

    def get(self):
        """Return a copy of the buffer in chronological order (full buffer when full, otherwise the prefix)."""
        if self.__full:
            return self.buf.copy()
        else:
            return self.buf[:self._ptr].copy()

    def resize(self, size):
        """Resize the buffer to a new capacity, preserving as many existing samples as possible.

        Args:
            size (int): New buffer capacity (must be positive)

        Raises:
            ValueError: If ``size`` is not a positive integer
        """
        # Check inputs
        size = int(size)
        if size <= 0:
            raise ValueError("Size must be a positive integer!")
        # Set new size
        if size < self._ptr:
            self.buf = self.buf[:size]
            self._ptr = 0
            self.size = size
            self.__full = True
        elif size < self.size:
            if self.__full:
                pos = size - self._ptr
                self.buf[self._ptr:size] = self.buf[-pos:]
            self.buf = self.buf[:size]
            self.size = size
        elif size > self.size:
            buf = np.zeros(size, dtype=self.dtype)
            if self.__full:
                pos = self.size - self._ptr
                buf[:pos] = self.buf[self._ptr:]
                buf[pos:self.size] = self.buf[:self._ptr]
            else:
                buf[:self._ptr] = self.buf[:self._ptr]
            self.buf = buf
            self.size = size
            self.__full = False
        else:
            pass  # Equal size, nothing to change

    def flush(self):
        """Zero the buffer, reset the write pointer, and clear the empty/full flags."""
        self._ptr = 0
        self.__empty = True
        self.__full = False
        self.buf[:] = 0


class MapArrayQueue:
    """Queue of fixed-length 1D array items.

    Wraps a standard :class:`queue.Queue` (or :class:`queue.LifoQueue`) but accumulates incoming samples in
    an internal receiver array and only enqueues the receiver once it is filled to ``arr_len``. This lets
    streaming hardware deliver irregularly sized chunks while downstream consumers see uniform-length items.
    """

    def __init__(self, arr_len, que_len=0, dtype=np.float32, mode='fifo'):
        """Initialise the receiver array and the underlying queue.

        Args:
            arr_len (int): Length of every array item enqueued (must be positive)
            que_len (int): Maximum queue depth; ``0`` means unbounded (default: ``0``)
            dtype (np.number | str): NumPy data type for the receiver array (default: ``np.float32``)
            mode (str): Queue mode; one of ``{'fifo', 'lifo'}`` (default: ``'fifo'``)

        Raises:
            ValueError: If ``arr_len`` is not a positive integer or ``mode`` is not one of ``{'fifo', 'lifo'}``
        """
        # Set array
        self._alen = int(arr_len)
        if self._alen <= 0:
            raise ValueError("Array size must be a positive integer!")
        self.dtype = dtype
        self.__recv = np.zeros(self._alen, self.dtype)  # Receiver array
        self.__ptr = 0  # Current receiver array position pointer
        # Set queue
        self._qlen = int(que_len)
        self.mode = mode.strip().lower()
        if self.mode == 'fifo':
            self.__q = queue.Queue(maxsize=self._qlen)
        elif self.mode == 'lifo':
            self.__q = queue.LifoQueue(maxsize=self._qlen)
        else:
            raise ValueError("Only support FIFO and LIFO mode, got [%s] instead!" % self.mode)

    def __len__(self):
        return self._alen

    def qsize(self):
        """Return the approximate number of items currently in the queue."""
        return self.__q.qsize()

    def empty(self):
        """Return :data:`True` when the queue is empty."""
        return self.__q.empty()

    def full(self):
        """Return :data:`True` when the queue is full."""
        return self.__q.full()

    def put(self, data, block=True, timeout=None):
        """Append ``data`` to the receiver array, enqueuing fixed-length chunks as the array fills.

        Args:
            data (np.ndarray): {1D} Samples to append; may be of any length
            block (bool): When :data:`True`, block until a free slot is available (default: ``True``)
            timeout (int | float | None): Timeout in seconds when blocking; pass :data:`None` to wait
                indefinitely (default: ``None``)
        """
        rem = data.size  # Remaining elements size
        pos = 0  # Input data current position
        # Check if previous receiver array is empty
        if self.__ptr != 0:
            avl = self._alen - self.__ptr  # Available space
            if rem > avl:
                # Put data
                self.__recv[self.__ptr:] = data[:avl]
                self.__q.put(self.__recv.copy(), block=block, timeout=timeout)
                # Shift position
                self.__ptr = 0
                rem -= avl
                pos = avl
            elif rem == avl:
                # Put data
                self.__recv[self.__ptr:] = data
                self.__q.put(self.__recv.copy(), block=block, timeout=timeout)
                # Shift position
                self.__ptr = 0
                return  # End process
            else:
                end = self.__ptr + rem
                self.__recv[self.__ptr:end] = data
                self.__ptr = end
                return  # End process, no put into queue
        # Loop putting data
        while rem >= self._alen:
            # Put data
            end = pos + self._alen
            self.__q.put(data[pos:end], block=block, timeout=timeout)
            # Shift position
            pos = end
            rem -= self._alen
        # Deal with remainders
        if rem != 0:
            self.__recv[:rem] = data[pos:]
            self.__ptr = rem

    def put_nowait(self, data):
        """Equivalent to :meth:`put` with ``block=False``."""
        self.put(data, block=False)

    def get(self, block=True, timeout=None):
        """Remove and return the next array item from the queue.

        Args:
            block (bool): When :data:`True`, block until an item is available (default: ``True``)
            timeout (int | float | None): Timeout in seconds when blocking; pass :data:`None` to wait
                indefinitely (default: ``None``)

        Returns:
            np.ndarray: {1D} Array item of length ``arr_len``
        """
        return self.__q.get(block=block, timeout=timeout)

    def get_nowait(self):
        """Equivalent to :meth:`get` with ``block=False``."""
        return self.__q.get_nowait()

    def remainder(self, pad=None):
        """Return the partially filled receiver array that has not yet been enqueued.

        Args:
            pad (int | float | None): When given, pad the trailing slots with this value so the returned
                array has length ``arr_len``; when :data:`None`, return only the filled prefix (default: ``None``)

        Returns:
            np.ndarray | None: {1D} The remaining (optionally padded) array; :data:`None` when the receiver is empty
        """
        if self.__ptr == 0:
            return None
        elif pad is None:
            return self.__recv[:self.__ptr]
        else:
            self.__recv[self.__ptr:] = 0
            return self.__recv.copy()

    def task_done(self):
        """Indicate that a previously enqueued task has been fully processed."""
        self.__q.task_done()

    def join(self):
        """Block until every queued item has been retrieved and marked as done."""
        self.__q.join()

    def clear(self):
        """Drop every queued item without processing them."""
        self.__q.queue.clear()


def read_uint8(array, index):
    """Read 1 byte from a byte array as an unsigned 8-bit integer.

    Args:
        array (bytes): Source byte array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Decoded integer value and the index of the next byte
    """
    nxt = index + 1
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=False)
    return var, nxt


def read_int8(array, index):
    """Read 1 byte from a byte array as a signed 8-bit integer.

    Args:
        array (bytes): Source byte array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Decoded integer value and the index of the next byte
    """
    nxt = index + 1
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=True)
    return var, nxt


def read_uint16(array, index):
    """Read 2 bytes from a byte array as an unsigned 16-bit integer (little-endian).

    Args:
        array (bytes): Source byte array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Decoded integer value and the index of the next byte
    """
    nxt = index + 2
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=False)
    return var, nxt


def read_int16(array, index):
    """Read 2 bytes from a byte array as a signed 16-bit integer (little-endian).

    Args:
        array (bytes): Source byte array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Decoded integer value and the index of the next byte
    """
    nxt = index + 2
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=True)
    return var, nxt


def read_uint32(array, index):
    """Read 4 bytes from a byte array as an unsigned 32-bit integer (little-endian).

    Args:
        array (bytes): Source byte array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Decoded integer value and the index of the next byte
    """
    nxt = index + 4
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=False)
    return var, nxt


def read_int32(array, index):
    """Read 4 bytes from a byte array as a signed 32-bit integer (little-endian).

    Args:
        array (bytes): Source byte array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Decoded integer value and the index of the next byte
    """
    nxt = index + 4
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=True)
    return var, nxt


def read_uint64(array, index):
    """Read 8 bytes from a byte array as an unsigned 64-bit integer (little-endian).

    Args:
        array (bytes): Source byte array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Decoded integer value and the index of the next byte
    """
    nxt = index + 8
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=False)
    return var, nxt


def read_int64(array, index):
    """Read 8 bytes from a byte array as a signed 64-bit integer (little-endian).

    Args:
        array (bytes): Source byte array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Decoded integer value and the index of the next byte
    """
    nxt = index + 8
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=True)
    return var, nxt
