import sys
import os

# Add package path to system
pkg_root = os.path.dirname(__file__)
sys.path.extend(pkg_root)
os.chdir(os.path.expanduser('~'))

# Set package settings store dir
pkg_data = os.path.join(os.path.expanduser('~'), '.parus/')
if not os.path.isdir(pkg_data):
    os.mkdir(pkg_data)
