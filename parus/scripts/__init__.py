# PARUS process pipeline scripts

import os

__all__ = ['gen_sim', 'gen_sta', 'prd_dsp']
"""
Scripts list:
  gen_sim: Generated simulated neural signal data use for model training.
  gen_sta: Visualize simulated signals generation status.
  prd_dsp: Display model prediction results versus its inputs.
"""

# Get module directory
__mod_dir = os.path.dirname(os.path.abspath(__file__))

# Get scripts full path
gen_sim = os.path.join(__mod_dir, 'gensim.py').replace('\\', '/')
gen_sta = os.path.join(__mod_dir, 'gensta.py').replace('\\', '/')
prd_dsp = os.path.join(__mod_dir, 'prddsp.py').replace('\\', '/')
