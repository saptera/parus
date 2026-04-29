# -*- coding: utf-8 -*-

"""PARUS process pipeline scripts package

Resolves the absolute paths of the bundled CLI scripts so they can be invoked as subprocesses from the
GUI windows or from external entry points.
"""

import os

__package__ = 'parus.scripts'
__name__ = 'parus.scripts'

__all__ = ['gen_sim', 'gen_sta', 'mod_trn', 'mod_inf', 'prd_dsp']
"""
Public script paths:

- gen_sim   : Generate simulated neural signal datasets for model training
- gen_sta   : Visualise the simulated-signal generation statistics
- mod_trn   : Train a signal-separation model for spike detection
- mod_inf   : Run model inference on raw recording data
- prd_dsp   : Display model prediction results against the input signal
"""

# Get module directory
__mod_dir = os.path.dirname(os.path.abspath(__file__))

# Get scripts full path
gen_sim = os.path.join(__mod_dir, 'gensim.py').replace('\\', '/')
gen_sta = os.path.join(__mod_dir, 'gensta.py').replace('\\', '/')
mod_trn = os.path.join(__mod_dir, 'modtrn.py').replace('\\', '/')
mod_inf = os.path.join(__mod_dir, 'modinf.py').replace('\\', '/')
prd_dsp = os.path.join(__mod_dir, 'prddsp.py').replace('\\', '/')
