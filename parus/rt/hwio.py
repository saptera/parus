# Hardware IO basic function module

import queue
import numpy as np


__package__ = 'parus.rt'
__name__ = 'parus.rt.hwio'

__all__ = ['SingletonIO', 'CircularBufferFL', 'CircularBufferCR', 'MapArrayQueue',
           'read_uint8', 'read_int8', 'read_uint16', 'read_int16', 'read_uint32', 'read_int32',
           'read_uint64', 'read_int64']
"""
Class list:
  SingletonIO: Real-time hardware IO singleton metaclass.
  CircularBufferFL(size, dtype=np.float32): Circular buffer for 1D data, behave as fall-out left.
  CircularBufferCR(size, dtype=np.float32): Circular buffer for 1D data, behave as carriage return.
  MapArrayQueue(arr_len, que_len=0, dtype=np.float32, mode='fifo'): Build a queue with fixed length array items.
Function list:
  read_uint8(array, index): Reads 1 byte from byte array as unsigned 8-bit integer.
  read_int8(array, index): Reads 1 byte from byte array as signed 8-bit integer.
  read_uint16(array, index): Reads 2 byte from byte array as unsigned 16-bit integer.
  read_int16(array, index): Reads 2 byte from byte array as signed 16-bit integer.
  read_uint32(array, index): Reads 4 byte from byte array as unsigned 32-bit integer.
  read_int32(array, index): Reads 4 byte from byte array as signed 32-bit integer.
  read_uint64(array, index): Reads 8 byte from byte array as unsigned 64-bit integer.
  read_int64(array, index): Reads 8 byte from byte array as signed 64-bit integer.
"""


class SingletonIO(type):
    """ Real-time hardware IO singleton metaclass. """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonIO, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CircularBufferFL:
    def __init__(self, size, dtype=np.float32):
        """ Circular buffer for 1D data, behave as fall-out left.

        Args:
            size (int): Capacity of buffer
            dtype (np.number | str): NumPy data type for the buffer (default: 'float32')
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
        """ Return True if the buffer is empty, False otherwise. """
        return self._ptr == 0

    def full(self):
        """ Return True if the buffer is fully filled, False otherwise. """
        return self._ptr == self.size

    def put(self, data):
        """ Put new data into buffer.

        Args:
            data (np.ndarray): {1D} Data to append to the buffer
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
        """ Get current filled buffer. """
        return self.buf[:self._ptr].copy()

    def resize(self, size):
        """ Resize buffer capacity.

        Args:
            size (int): New buffer capacity
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
        """ Flush the buffer.

        Args:
            hard (bool): Hard mode will reinitialize buffer, otherwise only reset data pointer (default: False)
        """
        self._ptr = 0
        if hard:
            self.buf[:] = 0


class CircularBufferCR:
    def __init__(self, size, dtype=np.float32):
        """ Circular buffer for 1D data, behave as carriage return.

        Args:
            size (int): Capacity of buffer
            dtype (np.number | str): NumPy data type for the buffer (default: 'float32')
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
        """ Return True if the buffer is empty, False otherwise. """
        return self.__empty

    def full(self):
        """ Return True if the buffer is fully filled, False otherwise. """
        return self.__full

    def position(self, pos):
        """  Set current data pointer position.

        Args:
            pos (int): Data pointer position
        """
        pos = 0 if pos < 0 else pos if pos < self.size else self.size - 1
        self._ptr = pos

    def locate(self):
        """ Locate current data pointer. """
        return self._ptr

    def put(self, data):
        """ Put new data into buffer.

        Args:
            data (np.ndarray): {1D} Data to append to the buffer
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
        """ Get current filled buffer. """
        if self.__full:
            return self.buf.copy()
        else:
            return self.buf[:self._ptr].copy()

    def resize(self, size):
        """ Resize buffer capacity.

        Args:
            size (int): New buffer capacity
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
        """ Flush the buffer. """
        self._ptr = 0
        self.__empty = True
        self.__full = False
        self.buf[:] = 0


class MapArrayQueue:
    def __init__(self, arr_len, que_len=0, dtype=np.float32, mode='fifo'):
        """ Queue with fixed length 1D array items.

        Args:
            arr_len (int): Length of each array element
            que_len (int): Size of queue (default: 0 = infinitive)
            dtype (np.number | str): NumPy data type for the buffer (default: 'float32')
            mode (str): {'fifo' | 'lifo'} Queue mode (default: 'fifo')
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
        """ Return the approximate size of the queue. """
        return self.__q.qsize()

    def empty(self):
        """ Return True if the queue is empty, False otherwise. """
        return self.__q.empty()

    def full(self):
        """ Return True if the queue is full, False otherwise. """
        return self.__q.full()

    def put(self, data, block=True, timeout=None):
        """ Put item into the queue, with fixed sized array filled.

        Args:
            data (np.ndarray): {1D} Data to put to the queue
            block (bool): Block if necessary until a free slot is available (default: True)
            timeout (int | float): Timeout in seconds (default: None = no timeout)
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
        """ Equivalent to put(item, block=False). """
        self.put(data, block=False)

    def get(self, block=True, timeout=None):
        """ Remove and return an item from the queue.

        Args:
            block (bool): Block if necessary until an item is available (default: True)
            timeout (int | float): Timeout in seconds (default: None = no timeout)

        Returns:
            np.ndarray: {1D} Array item
        """
        return self.__q.get(block=block, timeout=timeout)

    def get_nowait(self):
        """ Equivalent to get(False). """
        return self.__q.get_nowait()

    def remainder(self, pad=None):
        """  Get the remaining data which is not met the size to be put into the queue.

        Args:
            pad (int | float | None): Padding value to make the remainder to the length (default: None = no padding)

        Returns:
            np.ndarray | None: {1D} Remaining data, None if empty
        """
        if self.__ptr == 0:
            return None
        elif pad is None:
            return self.__recv[:self.__ptr]
        else:
            self.__recv[self.__ptr:] = 0
            return self.__recv.copy()

    def task_done(self):
        """ Indicate that a formerly enqueued task is complete. """
        self.__q.task_done()

    def join(self):
        """ Blocks until all items in the queue have been gotten and processed. """
        self.__q.join()

    def clear(self):
        """ Clear all queued items. """
        self.__q.queue.clear()


def read_uint8(array, index):
    """ Reads 1 byte from byte array as unsigned 8-bit integer.

    Args:
        array (bytes): Data bytes array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Integer value and next index
    """
    nxt = index + 1
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=False)
    return var, nxt


def read_int8(array, index):
    """ Reads 1 byte from byte array as signed 8-bit integer.

    Args:
        array (bytes): Data bytes array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Integer value and next index
    """
    nxt = index + 1
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=True)
    return var, nxt


def read_uint16(array, index):
    """ Reads 2 bytes from byte array as unsigned 16-bit integer.

    Args:
        array (bytes): Data bytes array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Integer value and next index
    """
    nxt = index + 2
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=False)
    return var, nxt


def read_int16(array, index):
    """ Reads 2 bytes from byte array as signed 16-bit integer.

    Args:
        array (bytes): Data bytes array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Integer value and next index
    """
    nxt = index + 2
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=True)
    return var, nxt


def read_uint32(array, index):
    """ Reads 4 bytes from byte array as unsigned 32-bit integer.

    Args:
        array (bytes): Data bytes array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Integer value and next index
    """
    nxt = index + 4
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=False)
    return var, nxt


def read_int32(array, index):
    """ Reads 4 bytes from byte array as signed 32-bit integer.

    Args:
        array (bytes): Data bytes array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Integer value and next index
    """
    nxt = index + 4
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=True)
    return var, nxt


def read_uint64(array, index):
    """ Reads 8 bytes from byte array as unsigned 64-bit integer.

    Args:
        array (bytes): Data bytes array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Integer value and next index
    """
    nxt = index + 8
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=False)
    return var, nxt


def read_int64(array, index):
    """ Reads 8 bytes from byte array as signed 64-bit integer.

    Args:
        array (bytes): Data bytes array
        index (int): Starting index of the integer

    Returns:
        tuple[int, int]: Integer value and next index
    """
    nxt = index + 8
    var_bts = array[index:nxt]
    var = int.from_bytes(var_bts, byteorder='little', signed=True)
    return var, nxt
