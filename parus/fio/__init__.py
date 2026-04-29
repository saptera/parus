# -*- coding: utf-8 -*-

"""PARUS file IO package

Readers and writers for PARUS-defined files together with import helpers for third-party recording formats.
"""

__package__ = 'parus.fio'
__name__ = 'parus.fio'

from .fmeta import *
from .fdata import *
from .hdf import *
from .matlab import *
from .intan import *
from .smr import *
from .tdt import *
