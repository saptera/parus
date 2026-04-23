<div style="text-align:center;">
  <img src="doc/assets/banner.png" alt="banner" width="800">
  <p style="font-size:200%;"><b>Fully automated real-time spike analysis system</b></p>
</div><br>

![os](https://img.shields.io/badge/os-linux%2C%20win%2C%20mac-blue.svg)
[![python](https://img.shields.io/badge/python-≥3.10-aff.svg)](https://www.python.org)
[![cuda](https://img.shields.io/badge/cuda-≥12.6-pink.svg)](https://developer.nvidia.com/cuda)
![hardware](https://img.shields.io/badge/hardware-cpu%2C%20gpu-yellow.svg)
[![license](https://img.shields.io/badge/license-AGPLv3-green)](LICENSE)

## Installation

**PARUS** is designed as a modular, cross-platform system supporting Unix, Linux, Windows, and macOS environments. 
Refer to the [system requirements](#system-requirements) and [installation methods](#installation-methods) 
for prerequisites and deployment procedures.

### System Requirements

Basic software

- [Python](https://www.python.org) ≥ `3.10`
- [CUDA](https://developer.nvidia.com/cuda) ≥ `12.6`
- Python `venv` for isolation *(recommend)*

Hardware for optimum performance

- **CPU**: base speed ≥ `3.5 GHz`, cores ≥ `4`
- **Memory**: speed ≥ `2400 MHz`, capacity ≥ `16 GiB`
- **GPU**: `CUDA` compatible, VRAM ≥ `8 GiB`
- **Monitor**: resolution ≥ `1920 x 1080`, scaling = `100%` *(recommended for small screen with high-resolution)*
- **SSDs** *(recommended for large file and real-time subsystem)*

### Installation Methods

The **PARUS** system can be installed using **PyPI**, **form source** or with **automation script**.

- Install via PyPI ***(stable release)***

  ```bash
  pip install parus-major
  ```

  > **Note:** `pip` cannot detect your local [CUDA](https://developer.nvidia.com/cuda) runtime, 
  > so the CPU-only build of [PyTorch](https://pytorch.org/get-started/locally/) is pulled in by default. 
  > For GPU acceleration, install a CUDA-matched ``torch`` wheel ***before*** running the command above, 
  > or reinstall afterwards.

- Install from source

  ```bash
  git clone https://github.com/saptera/parus.git
  cd parus
  pip install -e .
  ```

  > **Note:** For the same issue of `pip` addressed above, consider to pre-install or reinstall optimum build of 
  > [PyTorch](https://pytorch.org/get-started/locally/) for this option.

- Install with automation scripts ***(recommended for end users)***

  1. Download the source as a ZIP from (*Code* → *Download ZIP*) and extract it
  2. Navigate to `[repository_root]/automation`
  3. Locate the folder corresponding to the operating system
  4. Run the installation script: `install_parus.*`
  5. Follow the on-screen prompts to complete the installation

  > **Note:** Install a matching [CUDA](https://developer.nvidia.com/cuda) runtime ***before*** running the script. 
  > So the script can detect CUDA version and install optimum [PyTorch](https://pytorch.org/get-started/locally/) build.

### Dependencies

- [NumPy](https://numpy.org) (≥ 2.0.0) `pip install "numpy>=2.0.0"` *(Data operation fundamentals)*
- [SciPy](https://www.scipy.org) (≥ 1.14.0) `pip install "scipy>=1.14.0"` *(Signal preprocessing and statistics)*
- [PyTorch](https://pytorch.org) (CUDA version) `pip install torch torchvision` *(Machine learning fundamentals)*
- [h5py](https://www.h5py.org/) `pip install h5py` *(HDF5 file management)*
- [Matplotlib](https://matplotlib.org) (≥ 3.8.4) `pip install "matplotlib>=3.8.4"` *(Data visualization fundamentals)*
- [plotext](https://github.com/piccolomo/plotext) `pip install plotext` *(Data visualization for model training CLI)*
- [PySide6](https://www.qt.io/qt-for-python) (≥ 6.8) `pip install "PySide6>=6.8"` *(GUI fundamentals)*
- [PyQtGraph](https://www.pyqtgraph.org) `pip install pyqtgraph` *(Data visualization for real-time GUI)*

## Data Formats

Refer to [FORMAT](doc/FORMAT.md) for detailed documentation of all file formats used or defined in the PARUS system.

Refer to [CONVERSION](doc/CONVERSION.md) for detailed walkthrough of adapting raw data for the PARUS system.

## Available Interfaces

- [Application Programming Interface (API)](doc/API)
- [Command Line Interface (CLI)](doc/CLI.md)
- [Graphical User Interface (GUI)](doc/GUI.md)
- [Real-time Data Processing System (RT)](doc/REALTIME.md)

## Package Structure

### Repository Structure

```
PARUS repository
├── parus                        <- PARUS source code (futher explained in the next section)
├── automation                   <- Program automation scripts
│   ├── environment                  <- Execution environment building scripts
│   │   ├── install_parus.py             <- Auto-installation script
│   │   ├── proj_path.pth                <- Python [venv] project path injection
│   │   ├── set_version.py               <- Project version setting script
│   │   └── README.md                    <- Readme file
│   ├── POSIX                        <- POSIX OS (Unix/Linux/macOS) execution scripts
│   │   ├── install_parus.sh             <- Installation caller script for POSIX
│   │   ├── parus_trn.sh                 <- Model training GUI caller
│   │   ├── parus_dat.sh                 <- Data processing GUI caller
│   │   ├── parus_rt.sh                  <- Real-time GUI caller
│   │   └── README.md                    <- Readme file
│   ├── Windows                      <- Window OS execution scripts
│   │   ├── install_parus.bat            <- Installation caller script for Windows
│   │   ├── ParusTrn.bat                 <- Model training GUI caller
│   │   ├── ParusDat.bat                 <- Data processing GUI caller
│   │   ├── ParusRT.bat                  <- Real-time GUI caller
│   │   └── README.md                    <- Readme file
│   └── README.md                    <- Readme file
├── doc                          <- Package documentation
│   ├── assets/                      <- Documentation non-text resources
│   ├── FORMAT.md                    <- Data file format documentation
│   ├── CONVERSION.md                <- Data file conversion guides
│   ├── API                          <- Application programming interface documentation
│   │   ├── source                       <- Sphinx documentation source directory
│   │   │   ├── _static/                     <- Documentation HTML static components
│   │   │   ├── conf.py                      <- Sphinx build configuration file
│   │   │   └── index.rst                    <- API documentation homepage source file
│   │   ├── api.zip                      <- API HTML documentation bulid
│   │   ├── Makefile                     <- API documentation build makefile
│   │   └── README.md                    <- Readme file
│   ├── CLI.md                       <- Commandline interface documentation
│   ├── GUI.md                       <- Graphical user interface documentation
│   └── REALTIME.md                  <- Real-time sub-system documentation
├── pyproject.toml               <- Project build definitions
├── Makefile                     <- Project build makefile
├── LICENSE                      <- AGPL-3.0 license
├── README.md                    <- [THIS FILE] Main documentation
├── .gitattributes               <- Git Attributes source
└── .gitignore                   <- Git Ignore source
```

### Source Code Structure

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
│   ├── smr.py                <- CED Spike2 SMR file import module
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
│   ├── disp.py               <- Display helper function module
│   └── helper.py             <- User data IO and conversion helper function module
└── [EOP]
```

## Acknowledgements

### Pickle Compatible HDF5 File

Thanks to Daan van Vugt et al. for the open-source project [h5pickle](https://github.com/DaanVanVugt/h5pickle).

To enable pickle compatible HDF5 files for Python `multiprocessing` on platforms that use the `spawn` start method, 
we adapted code from `h5pickle` in the `fio.hdf` module.  
This ensures efficient file I/O while maintaining compatibility with `h5py`.

### CED Spike2 SMR File

Thanks to Neural Ensemble for the open-source package [Neo](https://neuralensemble.org/).

The SMR file import function is based on concepts from the Neo package 
and has been substantially adapted to enable implementation using pure NumPy and native I/O functionality.

### Peak Detection Using Z-score

Z-score based peak detection functions, inspired by a 
[Stack Overflow answer](https://stackoverflow.com/a/22640362/6029703) by J.P.G. van Brakel, 
are included in `data.sig` (NumPy based) and `model.post` (PyTorch based) modules for potential future LFP applications, 
though it is not used in the current project.
