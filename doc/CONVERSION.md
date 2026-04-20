# PARUS Data Conversion Guide

Detailed data file format specifications are available in [FORMAT.md](FORMAT.md).  
This guide provides a step-by-step overview of how to convert or adapt user data 
into standard PARUS input/output files.

### Table of Contents

- [Import Raw Traces for Data Processing](#import-raw-traces-for-data-processing)
  - [1. Load Raw Data](#1-load-raw-data)
  - [2. Validate and Prepare Raw Data](#2-validate-and-prepare-raw-data)
  - [3. Create a PARUS-Compatible HDF5 Data File](#3-create-a-parus-compatible-hdf5-data-file)
- [Prepare Curated Data for Model Training](#prepare-curated-data-for-model-training)
  - [1. Create Data Groups for Signal Position Labels](#1-create-data-groups-for-signal-position-labels)
  - [2. Insert Spike Position Data](#2-insert-spike-position-data)
  - [3. Create Archived Signal](#3-create-archived-signal)
  - [4. Create Simulated Datasets](#4-create-simulated-datasets)

---

## Import Raw Traces for Data Processing

### 1. Load Raw Data

The PARUS package provides multiple functions for reading raw data.  
These functions are designed to be low-level, lightweight, and minimally dependent, 
while remaining consistent with Pythonic conventions.

#### Supported Formats

The following data formats are currently supported:

- [Hierarchical Data Format 5](https://www.hdfgroup.org/solutions/hdf5/) (HDF5): `parus.fio.hdf`
- [Intan Technologies](https://intantech.com/) RHD formats: `parus.fio.intan`
- [MATLAB](https://www.mathworks.com/products/matlab.html) data (all versions): `parus.fio.matlab`
- [CED Spike2](https://ced.co.uk/products/spike2) file (SMR and legacy formats): `parus.fio.smr`
- [Tucker-Davis Technologies](https://www.tdt.com/) (TDT) data buckets: `parus.fio.tdt`

Custom data import functions can also be used. As long as the output is a NumPy array, it can be processed by PARUS.

### 2. Validate and Prepare Raw Data

To initialize processing in PARUS, only two inputs are required:

1. **Sampling frequency**: `NumPy float32` - `scalar`
2. **Raw data trace**: `NumPy float32` - `2D array`, shape: `(n_channels, n_samples)`

#### Data Validation

PARUS provides utility functions to validate and automatically correct input data:

```python
from parus.util import check_sampling_frequency, check_raw_data

raw, frq = user_defined_data_reading_function(file)

frq = check_sampling_frequency(frq)
raw = check_raw_data(raw)
```

These functions:

- Convert inputs to `float32` when necessary
- Issue warnings for non-optimal data types
- Raise a `ValueError` if automatic correction fails

#### Raw Data Shape Validation

The `check_raw_data` function also validates array dimensions:

- **1D input** -> automatically expanded to 2D
- **More than 2 dimensions** -> raises `ValueError`
- **Channels dimension larger than samples** -> warning issued (possible transpose needed)

### 3. Create a PARUS-Compatible HDF5 Data File

After validation, use the helper function below to create a properly formatted file for further processing:

```python
from parus.util import create_raw_data_file

fp = create_raw_data_file(file, raw, frq, force=False)  # Set force=True to overwrite existing files
```

- The function returns an ***open file pointer (`fp`)*** with `r+` mode
- If no further operations are required, make sure to close it:

```python
fp.close()
```

---

## Prepare Curated Data for Model Training

The initial steps for this process are the same as [import raw traces](#import-raw-traces-for-data-processing).

- If the sample data is intended for **noise archive creation**, proceed to [STEP 3](#3-create-archived-signal).
- If the sample data is intended for **signal archive creation**, manual labeling is required before proceeding.

### 1. Create Data Groups for Signal Position Labels

The HDF5 data structure for organizing spike position labels is defined as follows:

```
HDF5 (Hierarchical Data Format 5)
└── pos                       <- Sorted spike timestamps
    ├── [spk_typ_01]              <- Subgroup of spike type 01
    │   ├── [ch_idx_00]               <- Recording channel 00
    │   │   ├── [cell_id_00]              <- Detected cell 00
    │   │   ├── [cell_id_01]              <- Detected cell 01
    │   │   └── ...                       <- Other detected cells
    │   ├── [ch_idx_01]               <- Recording channel 01
    │   │   └── ...                       <- Detected cells in channel 01
    │   └── ...                       <- Other recoding channels
    ├── [spk_typ_02]              <- Subgroup of spike type 02
    │   └── ...                       <- Recording channels and cells in spike type 02
    └── ...                       <- Subgroup of other spike types

```

A helper function is provided to create the required data groups:

```python
from parus.util import add_position_groups

add_position_groups(fp, spike_types, force=False)  # Set force=True to overwrite existing groups
```

- `fp`: HDF5 file pointer
- `spike_types`: List of spike type identifiers (`str`)
- `force`: Set to `True` to overwrite existing groups

### 2. Insert Spike Position Data

Spike position data must be stored as a `NumPy int8` - `1D array` in one-hot format.

If your data is in timestamp format, you can convert it using the provided helper function:

```python
from parus.util import timestamp_to_onehot

loc = timestamp_to_onehot(tmp, frq, raw.shape[1])
```

* `tmp`: Spike timestamps
* `frq`: Sampling frequency
* `raw.shape[1]`: Total number of samples

Once converted, the data can be inserted into the HDF5 file:

```python
fp['spike_name']['channel_number'].create_dataset(
    name='cell_name',
    data=loc,
    compression='gzip',
    compression_opts=9
)
```

- Compression (`compression='gzip', compression_opts=9`) is optional but recommended for large datasets.
- HDF5 keys must be strings. Ensure channel indices in `int` are converted to `str` before use.

> **Tip:** To convert one-hot encoded labels back to timestamps:
> 
> ```python
> from parus.util import onehot_to_timestamp
> 
> tmp = onehot_to_timestamp(loc, frq)
> ```

### 3. Create Archived Signal

Refer to the [GUI - Create Archived Signal](GUI.md#1-create-archive-signal) section for detailed instructions.

### 4. Create Simulated Datasets

Refer to the [GUI - Dataset Generation](GUI.md#2-dataset-generation) section for detailed instructions.
