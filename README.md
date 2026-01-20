<div style="text-align:center">
  <img src="doc/assets/logo.svg" alt="logo" width="800">
  <h3>Fully automated real-time spike analysis system</h3>
</div><br>

![os](https://img.shields.io/badge/os-linux%2C%20win%2C%20mac-blue.svg)
[![python](https://img.shields.io/badge/python-≥3.10-aff.svg)](https://www.python.org)
[![cuda](https://img.shields.io/badge/cuda-≥12.6-pink.svg)](https://developer.nvidia.com/cuda)
![hardware](https://img.shields.io/badge/hardware-cpu%2C%20gpu-yellow.svg)
[![license](https://img.shields.io/badge/license-AGPLv3-green)](LICENSE)

## Installation

The **PARUS** system can be installed using PyPI or Automation Script

- Install via PyPI
- Install via Automation Script
  1. Navigate to `[repository_root]/automation`
  2. Locate the folder corresponding to the operating system
  3. Run the installation script: `install_parus.*`
  4. Follow the on-screen prompts to complete the installation

### System requirements

Basic software

- [Python](https://www.python.org) ≥ `3.10`
- [CUDA](https://developer.nvidia.com/cuda) ≥ `12.6`
- Python `venv` for isolation *(recommend)*

Hardware for minimum performance

- **CPU**: base speed ≥ `3.5 GHz`, cores ≥ `4`
- **Memory**: speed ≥ `2400 MHz`, capacity ≥ `16 GiB`
- **GPU**: `CUDA` compatible, VRAM ≥ `8 GiB`
- **Monitor**: resolution ≥ `1920 x 1080`, scaling = `100%` *(recommend)*
- **SSDs**

### Dependencies

- [NumPy](https://numpy.org) (≥ 2.0.0) `pip install "numpy>=2.0.0"` *(Data operation fundamentals)*
- [SciPy](https://www.scipy.org) (≥ 1.14.0) `pip install "scipy>=1.14.0"` *(Signal preprocessing and statistics)*
- [PyTorch](https://pytorch.org) (CUDA version) `pip install torch torchvision` *(Machine learning fundamentals)*
- [h5py](https://www.h5py.org/) `pip install h5py` *(HDF5 file management)*
- [Matplotlib](https://matplotlib.org) (≥ 3.8.4) `pip install "matplotlib>=3.8.4"` *(Data visualization fundamentals)*
- [plotext](https://github.com/piccolomo/plotext) `pip install plotext` *(Data visualization for model training CLI)*
- [PySide6](https://www.qt.io/qt-for-python) (≥ 6.8) `pip install "PySide6>=6.8"` *(GUI fundamentals)*
- [PyQtGraph](https://www.pyqtgraph.org) `pip install pyqtgraph` *(Data visualization for real-time GUI)*

## Package structure

### Repository structure

```
PARUS repository
├── automation                   <- Program automation scripts
│   ├── environment                  <- Execution environment building scripts
│   │   ├── install_parus.py             <- Auto-installation script
│   │   ├── proj_path.pth                <- Python [venv] project path injection
│   │   └── README.md                    <- Readme file
│   ├── Unix_like                    <- Unix-like OS exection scripts
│   │   ├── install_parus.sh             <- Installation caller script for POSIX
│   │   └── README.md                    <- Readme file
│   ├── Windows                      <- Window OS exection scripts
│   │   ├── install_parus.bat            <- Installation caller script for Windows
│   │   ├── ParusTrn.bat                 <- Model training GUI caller
│   │   ├── ParusDat.bat                 <- Data processing GUI caller
│   │   ├── ParusRT.bat                  <- Real-time GUI caller
│   │   └── README.md                    <- Readme file
│   └── README.md                    <- Readme file
├── doc                          <- Package documentation
│   ├── assets/                      <- Documentation non-text resources
│   ├── FORMAT.md                    <- Data file format documentation
│   ├── CLI.md                       <- Commandline interface documentation
│   ├── GUI.md                       <- Graphical user interface documentation
│   ├── REALTIME.md                  <- Real-time sub-system documentation
│   └── API                          <- Application interface (functions) documentation
│       └── ...                          <- Module documentation
├── parus                        <- PARUS source code (futher explained below)
├── LICENSE                      <- AGPL-3.0 license
├── README.md                    <- [THIS FILE]
├── .gitattributes               <- Git Attributes source
└── .gitignore                   <- Git Ignore source
```

### Source code structure

```
PARUS package (alphabetical order)
├── app                   <- [parus.app] Application sub-package
│   ├── afunc.py              <- Application caller functions
│   ├── pac_ma.py             <- PARUS main application SCRIPT
│   └── pac_rt.py             <- PARUS real-time application SCRIPT
├── data                  <- [parus.data] Data operation sub-package
│   ├── clst.py               <- Spike clustering module
│   ├── plot.py               <- Data plotting module
│   ├── proc.py               <- Basic data process module
│   └── sig.py                <- Signal process module
├── fio                   <- [parus.fio] File IO sub-package
│   ├── fdata.py              <- Customized data file IO module
│   ├── fmeta.py              <- Customized meta file IO module
│   ├── hdf.py                <- Hierarchical Data Format (HDF) file IO module
│   ├── intan.py              <- IntanTech file import module
│   ├── matlab.py             <- MATLAB file import module
│   └── tdt.py                <- Tucker-Davis Technologies file import module
├── gui                   <- [parus.gui] GUI sub-package
│   ├── assets/               <- GUI non-code resources
│   ├── app_main.py           <- Main application module
│   ├── elm_plot.py           <- GUI plotting module
│   ├── elm_proc.py           <- GUI process feature module
│   ├── gui_dat.py            <- Data processing GUI module
│   ├── gui_trn.py            <- Model training GUI module
│   ├── desg_*.ui             <- Qt 6 UI design files
│   └── desg_*.py             <- Compiled UI files
├── model                 <- [parus.model] Machine learning sub-package
│   ├── deset.py              <- Model data loader classes module
│   ├── eval.py               <- Model evaluation and inference module
│   ├── mio.py                <- Model operation IO module
│   ├── optim.py              <- Model training and optimization module
│   ├── post.py               <- Model inference post-process module
│   ├── transformer.py        <- Transformer model module
│   └── wavenet.py            <- WaveNet model module
├── rt                    <- [parus.rt] Real-time data processing sub-package
│   ├── assets/               <- RT-GUI non-code resources
│   ├── app_rt.py             <- Real-time application module
│   ├── hwio.py               <- Hardware IO basic function module
│   ├── intan_rhx.py          <- Intan RHX software TCP real-time data streaming module
│   ├── desg_*.ui             <- Qt 6 UI design files
│   └── desg_*.py             <- Compiled UI files
├── scripts               <- [parus.scripts] Process pipeline scripts (CLI) sub-package
│   ├── gensim.py             <- Simulated signal generation CLI
│   ├── gensta.py             <- Simulated signal statistics visualization CLI
│   ├── modinf.py             <- Model data inference CLI
│   ├── modtrn.py             <- Model training CLI
│   └── prddsp.py             <- Inference results visualization CLI
│── util                  <- [parus.util] Utility function sub-package
│   ├── base.py               <- Basic utilities function module
│   ├── cli.py                <- Commandline interface module
│   └── disp.py               <- Display helper function module
└── [EOP]
```

## Available interfaces

- [CLI](doc/CLI.md)
- [GUI](doc/GUI.md)
- [Real-time](doc/REALTIME.md)
- [API](doc/API/)

## Acknowledgements

### Pickle compatible HDF5 file

Thanks to Daan van Vugt et al. for the open-source project [h5pickle](https://github.com/DaanVanVugt/h5pickle).

To enable pickle-compatible HDF5 files for multiprocessing on platforms that use the `spawn` start method, 
we adapted code from `h5pickle` in the `fio.hdf` module.  
This ensures efficient file I/O while maintaining compatibility with `h5py`.

### Peak detection using z-score

A z-score-based peak detection function, 
inspired by a [Stack Overflow answer](https://stackoverflow.com/a/22640362/6029703) by J.P.G. van Brakel, 
is included in `data.sig` (NumPy) and `model.post` (PyTorch) modules for potential future LFP applications, 
though it is not used in the current project.
