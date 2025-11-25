## Code Execution Environment Helper Files

- `proj_path.pth`: Adds the project package to Python virtual environment `venv` path

&emsp;&emsp;&emsp;&emsp;-> Usage: place file in `[proj_root]/venv/Lib/site-packages/`

- `install_torch.py`: Detects the available compute platform (CPU | CUDA) and installs the corresponding PyTorch build

&emsp;&emsp;&emsp;&emsp;-> Usage: run command: `python install_torch.py`
