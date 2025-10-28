# PARUS process pipeline scripts

import os

__package__ = 'parus.scripts'
__name__ = 'parus.scripts'

__all__ = ['gen_sim', 'gen_sta', 'mod_trn', 'mod_inf', 'prd_dsp']
"""
Scripts list:
  gen_sim: Generated simulated neural signal data use for model training.
  gen_sta: Visualize simulated signals generation status.
  mod_trn: Train signal separation model for spike detection.
  mod_inf: Inference raw recoding data with trained model.
  prd_dsp: Display model prediction results versus its inputs.
"""

# Get module directory
__mod_dir = os.path.dirname(os.path.abspath(__file__))

# Get scripts full path
gen_sim = os.path.join(__mod_dir, 'gensim.py').replace('\\', '/')
gen_sta = os.path.join(__mod_dir, 'gensta.py').replace('\\', '/')
mod_trn = os.path.join(__mod_dir, 'modtrn.py').replace('\\', '/')
mod_inf = os.path.join(__mod_dir, 'modinf.py').replace('\\', '/')
prd_dsp = os.path.join(__mod_dir, 'prddsp.py').replace('\\', '/')
