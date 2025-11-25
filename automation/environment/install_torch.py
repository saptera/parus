# PyTorch auto-install script

import sys
import subprocess

try:
    for line in subprocess.check_output('nvcc --version').decode().split('\n'):
        if 'release' in line:
            print("CUDA version: " + line.split()[-1][1:])
            release = ''.join(line.split()[-2][:-1].split('.'))
            command = " -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu%s" % release
            subprocess.check_call(sys.executable + command)
            break
except FileNotFoundError:
    print("CUDA not found, installing PyTorch CPU")
    command = " -m pip install torch torchvision"
    subprocess.check_call(sys.executable + command)
