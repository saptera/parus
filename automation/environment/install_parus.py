# PARUS auto-install script

import sys
import os
import shutil
import subprocess


# Check Python version
if sys.version_info < (3, 10, 0):
    sys.stderr.write("ERROR: Python 3.10 or higher is required.\n")
    sys.exit(-1)

# Upgrade [pip]
print("Upgrading [pip]")
subprocess.check_call(sys.executable + ' -m pip install --upgrade pip')
# Upgrade [setuptools]
print("\nUpgrading [setuptools]")
subprocess.check_call(sys.executable + ' -m pip install --upgrade setuptools')

# Install [NumPy]
print("\nInstalling [NumPy]")
subprocess.check_call(sys.executable + ' -m pip install "numpy>=2.0.0"')
# Install [SciPy]
print("\nInstalling [SciPy]")
subprocess.check_call(sys.executable + ' -m pip install "scipy>=1.14.0"')
# Install [h5py] for HDF5 files
print("\nInstalling [h5py]")
subprocess.check_call(sys.executable + ' -m pip install h5py')
# Install [matplotlib] for general plotting
print("\nInstalling [matplotlib]")
subprocess.check_call(sys.executable + ' -m pip install "matplotlib>=3.8.4"')
# Install [plotext] for CLI plotting
print("\nInstalling [plotext]")
subprocess.check_call(sys.executable + ' -m pip install plotext')
# Install [PySide6] for GUI
print("\nInstalling [PySide6]")
subprocess.check_call(sys.executable + ' -m pip install "PySide6>=6.8"')
# Install [PyQtGraph] for real-time plotting
print("\nInstalling [PyQtGraph]")
subprocess.check_call(sys.executable + ' -m pip install pyqtgraph')
# Install [PyTorch]
print("\nInstalling [PyTorch]")
try:
    for line in subprocess.check_output('nvcc --version').decode().split('\n'):
        if 'release' in line:
            print("CUDA version: " + line.split()[-1][1:])
            release = ''.join(line.split()[-2][:-1].split('.'))
            command = ' -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu%s' % release
            subprocess.check_call(sys.executable + command)
            break
except FileNotFoundError:
    print("CUDA not found, installing PyTorch CPU")
    command = " -m pip install torch torchvision"
    subprocess.check_call(sys.executable + command)

# Add project path
print("\nAdding [Parus] project path to library")
pth_src = os.path.join(os.path.split(__file__)[0], 'proj_path.pth')
pth_dst = os.path.join(
    sys.executable.split('Scripts')[0] if 'Scripts' in sys.executable else os.path.dirname(sys.executable),
    "Lib/site-packages/proj_path.pth")
shutil.copy2(pth_src, pth_dst)

# Finalize
print("\nPARUS installation successfully finished!")
