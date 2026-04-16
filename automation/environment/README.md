## Code Execution Environment Helper Files

- `proj_path.pth`: Adds the project package to Python environment path

&emsp;&emsp;&emsp;&emsp;-> Usage: *place file in the Python package directory*  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;- Unix / Linux / macOS: `[executable_root]/lib/python[major].[minor]/site-packages/`  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;- Windows: `[executable_root]/Lib/site-packages/`  
&emsp;&emsp;&emsp;&emsp;-> `install_parus.py` *will process this operation automatically*

- `install_parus.py`: Install `parus` project dependencies and build the execution environment

&emsp;&emsp;&emsp;&emsp;-> Usage: *run command:* `python install_parus.py`

- `set_version.py`: Update `parus` project semantic version number

&emsp;&emsp;&emsp;&emsp;-> Usage: *ONLY use with project* `Makefile`
