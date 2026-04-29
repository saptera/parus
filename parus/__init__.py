# -*- coding: utf-8 -*-

"""PARUS spike analysis package

A fully automated real-time spike analysis system. Sets the project version, registers the package on
``sys.path``, and ensures the per-user settings directory exists before any submodule is imported.
"""

import sys
import os

__package__ = 'parus'
__name__ = 'parus'
version = "1.0.0"

# Add package path to system
pkg_root = os.path.dirname(__file__)
sys.path.extend(pkg_root)
os.chdir(os.path.expanduser('~'))

# Set package settings store dir
pkg_data = os.path.join(os.path.expanduser('~'), '.parus/')
if not os.path.isdir(pkg_data):
    os.mkdir(pkg_data)
