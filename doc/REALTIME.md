# PARUS Real-Time System

PARUS real-time system is a dedicated GUI developed for signal, process and status monitoring.

The data stream was duplicated at the **Open Ephys** controller and transmitted via TCP 
to the real-time processing system utilising a CUDA compatible GPU.

![Real-Time system Window](assets/gui_rts.png)

User can start the PARUS real-time application using one of the following methods, depending on the installation type.

### 1. Installation via PyPI

If PARUS was installed using PyPI, launch the training application with the following Python code:

```python
from parus.app import ParusRT

ParusRT()
```

### 2. Installation via Automation Scripts

#### a. Using a Desktop Shortcut

If user selected the option to create a desktop shortcut during installation:

- Double-click the `PARUS Real-Time` icon on the desktop to launch the application.

#### b. Without a Desktop Shortcut

If no desktop shortcut was created, use the appropriate script for the operating system:

- **Unix / Linux / macOS**  
  Navigate to the `automation/POSIX/` directory and run:

  ```bash
  parus_rt.sh
  ```

- **Windows**  
  Navigate to the `automation/Windows/` directory and run (double click):

  ```bat
  ParusRT.bat
  ```

## Main GUI components

- `Acquisition Control Panel` (left top)  
  Configures the transmission control protocol (TCP) connection to the recording system.
- `Processing Control Panel` (left bottom)  
  Sets model and sorter processing options.
- `Raw Signal Plot` (top plot)  
  Displays raw data streamed from the recording system.
- `Sorted Spikes Plot` (bottom plot)  
  Shows the processed signals with automatically labelled cells.
- `Status Bar`  
  Continuously reports recording speed, processing speed, and system latency.

## Controls

- Amplitude Settings
  - `Min Amplitude`
  - `Max Amplitude`
  - `Auto Amplitude` / `Set Amplitude`
- Time Range Setting  
  Click `Set Time` button to update time range, this will also resize the `buffer` and `ring` sizes.
