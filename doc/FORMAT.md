# PARUS Data File Formats

Custom data file formats have been defined in PARUS system.  
All formats were designed to support cross-platform and cross programming language accessibility.  
For clarity and ease of implementation, the details of each file format are described below.

### Table of contents

- [Data processing and exchange format](#data-processing-and-exchange-format)
  - [Dataset key `frq`](#dataset-key-frq)
  - [Dataset key `raw`](#dataset-key-raw)
  - [Group key `spk`](#group-key-spk)
  - [Group key `pos`](#group-key-pos)
- [PARUS optimized file formats](#parus-optimized-file-formats)
  - [Compressed pickled data (PKLZ) file](#compressed-pickled-data-pklz-file)
  - [Compressed JSON with Secure Hash embedded (CJSH) file](#compressed-json-with-secure-hash-embedded-cjsh-file)
- [Archived signal file formats](#archived-signal-file-formats)
  - [Archived spike waveform (`*.arc`) file](#archived-spike-waveform-arc-file)
  - [Archived background waveform (`*.noi`) file](#archived-background-waveform-noi-file)
- [Simulated training dataset formats](#simulated-training-dataset-formats)
  - [Training dataset (`*.sim`) file](#training-dataset-sim-file)
  - [Generation statistics (`*.cjh`) file](#generation-statistics-cjh-file)
- [Trained model formats](#trained-model-formats)
  - [Hyperparameter (`hparams.json`) file](#hyperparameter-hparamsjson-file)
  - [Training history (`history.json`) file](#training-history-historyjson-file)
  - [Training log (`train.log`) file](#training-log-trainlog-file)
  - [Test results (`*.pklz`) file](#test-results-pklz-file)
- [Probe geometry (`*.prb`) file](#probe-geometry-prb-file)

---

## Data processing and exchange format

The standard data file format used by PARUS system is HDF5 (Hierarchical Data Format 5) with 4 keys reserved,
which are `frq`, `raw`, `spk`, and `pos`.  
The recognizable extensions are `*.hdf`, `*.h5`, `*.hdf5`, `*.he5`

Structure summary of standard data format:

```
HDF5 (Hierarchical Data Format 5)
├── frq                       <- Sampling frequency
├── raw                       <- Raw recording traces
├── spk                       <- Isolated spike traces
│   ├── [spk_typ_01]              <- Isolated spike trace type 01
│   ├── [spk_typ_02]              <- Isolated spike trace type 02
│   └── ...                       <- Other isolated spike trace types
├── pos                       <- Sorted spike timestamps
│   ├── [spk_typ_01]              <- Subgroup of spike type 01
│   │   ├── [ch_idx_00]               <- Recording channel 00
│   │   │   ├── [cell_id_00]              <- Detected cell 00
│   │   │   ├── [cell_id_01]              <- Detected cell 01
│   │   │   └── ...                       <- Other detected cells
│   │   ├── [ch_idx_01]               <- Recording channel 01
│   │   │   └── ...                       <- Detected cells in channel 01
│   │   └── ...                       <- Other recoding channels
│   ├── [spk_typ_02]              <- Subgroup of spike type 02
│   │   └── ...                       <- Recording channels and cells in spike type 02
│   └── ...                       <- Subgroup of other spike types
├── [user_keys]               <- All other group/dataset keys are reserved for user
└── EOF                       <- End of file
```

Details of each group/dataset are as follows.

### Dataset key `frq`

Stores a single `float32` value representing the sampling rate.

### Dataset key `raw`

Stores raw recording traces as a 2D `float32` matrix in C-order, where:
- Rows (first dimension) correspond to channels
- Columns (second dimension) correspond to samples

**Note:** For single-channel recordings, the channel dimension (first dimension) must still be preserved.

### Group key `spk`

Stores isolated spike waveforms as 2D `float32` matrices in C-order.

This group may contain multiple datasets, depending on the model output configuration.  
Each dataset is named according to the spike type (_e.g._, `ss`, `cs`).
And the dimension of the datasets is identical to `raw` dataset.

### Group key `pos`

Stores sorted spike timestamps as 1D `int8` arrays in C-order.

This group may contain multiple subgroups, each named identically to a dataset in the `spk` group.

Each spike-type subgroup contains multiple channel subgroups, where:
- Channel indices are stored as string keys
- Each channel subgroup contains multiple datasets named by cell identifier

Each dataset is a 1D `int8` array of binary values (`0` or `1`), where `1` indicates the occurrence of a spike event.

---

## PARUS optimized file formats

Two customized file type have been defined for optimized data storage and exchange in PARUS system.

### Compressed pickled data (PKLZ) file

The PKLZ file format consists of Python objects serialized using `pickle` and then compressed with `zlib`.

This file format provides reduced file size for data storage within Python applications.

Files can be read using the `pklz_read` API and written using the `pklz_write` API from the `parus.fio` module.  
Recognized file extensions are `.pklz` and `.pkz`.

### Compressed JSON with Secure Hash embedded (CJSH) file

The CJSH file format is a structured container for JSON data.
1. The data is serialized using `json` and compressed with `zlib`.
2. SHA-256 checksum of the compressed data is generated using `hashlib`.
3. The compressed data is stored under the `arc` key, and the checksum is stored under the `cks` key.
4. The resulting structure is serialized again with `json` and compressed with `zlib` using compression level `0`.

This file format provides secure data storage with checksum validation.
The use of `JSON` and `ZLIB` enables data exchange across multiple programming languages.

Files can be read using the `cjsh_read` API and written using the `cjsh_write` API from the `parus.fio` module.  
Recognized file extensions are `.cjsh` and `.cjh`.

---

## Archived signal file formats

All archived neural signal files are store with `CJSH` format defined above.

### Archived spike waveform (`*.arc`) file

The data structure of archived spike waveform is defined as follows:

> - data (`dict`): signal data structure
>   - sig (`list[float]`): neural signal data
>   - pos (`int`): index of spike location in `sig`
>   - rng (`list[int, int]` | `null`): 2 indices to define refined signal range
>   - freq (`int` | `float`): recording frequency of `sig`
> - meta (`dict`): metadata structure of the signal
>   - organism (`dict`): organism for the signal recording
>     - gn (`str`): generic name
>     - se (`str`): specific epithet
>     - st (`str`): strain identifier
>     - mod (`str` | `null`): genetic modification, `None` (JSON `null`) for wildtype
>     - note (`Any`): extra notes
>   - region (`list`): recoding region(s) of the signal
>   - neuron (`dict`): neural cell information
>     - typ (`str`): cell type
>     - spk (`str`): spike type - `ss` for simple spike, `cs` for complex spike or `fp` for field potential
>     - note (`Any`): extra notes
>   - system (`dict`): recording system information
>     - typ (`str`): system type - `d` for digital or `a` for analog
>     - mfr (`str`): system manufacture
>     - pn (`str`): manufacture part number or model
>     - sn (`str`): manufacture serial number or batch number
>     - soc (`int` | `float` | `str`): Socket in system for recording
>     - note (`Any`): extra notes
>   - probe (`dict`): recording probe information
>     - typ (`str`): probe type - `si` for silicon, `w` for tungsten, `gls` for glass pipette etc.
>     - mfr (`str`): probe manufacture
>     - pn (`str`): manufacture part number or model
>     - sn (`str`): manufacture serial number or batch number
>     - chn (`int` | `float`): recording site channel number
>     - note (`Any`): extra notes
>   - datetime (`str[datetime.ISO-format]`): recording date and time information

Files can be created with PARUS `Model Training` -> `Create Archive Signal` GUI.  
Files can be read using the `arc_read` API and written using the `arc_write` API from the `parus.fio` module.  
Data can be plotted using `arc_plot` API from the `parus.fio` module.

### Archived background waveform (`*.noi`) file

The data structure of archived background waveform is defined as follows:

> - data (`dict`): neural recording noise data structure
>   - noi (`list[float]`): neural recording noise data
>   - freq (`int` | `float`): recording frequency of `noi`
> - meta (`dict`): metadata structure of the noise
>   - organism (`dict`): organism for the signal recording
>     - gn (`str`): generic name
>     - se (`str`): specific epithet
>     - st (`str`): strain identifier
>     - mod (`str` | `null`): genetic modification, `None` (JSON `null`) for wildtype
>     - note (`Any`): extra notes
>   - region (`list`): recoding region(s) of the signal
>   - feature (`dict`): recorded features in the noise signal
>     - typ (`list[str]`): existing noise - `fp` for field potential, `ele` for elec-sti, `opto` for opto-sti etc.
>     - note (`Any`): extra notes
>   - system (`dict`): recording system information
>     - typ (`str`): system type - `d` for digital or `a` for analog
>     - mfr (`str`): system manufacture
>     - pn (`str`): manufacture part number or model
>     - sn (`str`): manufacture serial number or batch number
>     - soc (`int` | `float` | `str`): Socket in system for recording
>     - note (`Any`): extra notes
>   - probe (`dict`): recording probe information
>     - typ (`str`): probe type - `si` for silicon, `w` for tungsten, `gls` for glass pipette etc.
>     - mfr (`str`): probe manufacture
>     - pn (`str`): manufacture part number or model
>     - sn (`str`): manufacture serial number or batch number
>     - chn (`int` | `float`): recording site channel number
>     - note (`Any`): extra notes
>   - datetime (`str[datetime.ISO-format]`): recording date and time information

Files can be created with PARUS `Model Training` GUI.  
Files can be read using the `noi_read` API and written using the `noi_write` API from the `parus.fio` module.

---

## Simulated training dataset formats

The training set can be generated with PARUS CLI `parus.scripts.gensim` or GUI `Model Training` -> `Dataset Generation`.

**NOTE:** These data files should not be directly modified by user.

### Training dataset (`*.sim`) file

The SIM file format is a structured container for HDF5 data.

The structure is as follows:

```
HDF5 (Hierarchical Data Format 5)
├── args                <- Input arguments for dataset generation
├── sims                <- Simulated signals
│   ├── [samp_idx_0]        <- Sample index '0'
│   │   ├── sig                 <- Sample waveform
│   │   ├── lbl                 <- Label waveform
│   │   │   ├── signal              <- Pure spike waveform
│   │   │   └── noise               <- Pure background waveform
│   │   └── pos                 <- Spike position binary array
│   └── ...                 <- Other sample indices
├── exeg                <- Extra signals for special validation purpose
│   ├── [samp_idx_0]        <- Sample index '0', structure is identical to [sims]
│   └── ...                 <- Other sample indices
└── EOF                 <- End of file
```

All waveforms stored as a 1D `float32` array.  
Position is a 1D `int8` array of binary values (`0` or `1`), where `1` indicates the occurrence of a spike event.

### Generation statistics (`*.cjh`) file

This file contains statistical information associated with generated training dataset.

This file is store with CJSH format defined above.  
The statistic results can be plotted with PARUS CLI `parus.scripts.gensta` or
GUI `Model Training` -> `Dataset Generation` -> `View Statistics`.

---

## Trained model formats

Multiple files will be created during model training.

```
Model artifacts folder
├── optimum.ckpt        <- Model weights with best validation set performace
├── final.ckpt          <- Model weights after training finalized
├── hparams.json        <- Hyperparameters used for training
├── history.json        <- Training history
├── train.log           <- Training event log
├── tst_opt.pklz        <- Test results of [optimum.ckpt] weights
├── tst_fin.pklz        <- Test results of [final.ckpt] weights
└── vld_ep*_stp*.png    <- [optional] Saved model validation results during training
```

### Model weights (`*.ckpt`) file

Model weights are store as dictionary with following keys:
- epoch (`int`): Current training epoch number
- description (`str` | `None`): Description of the model
- model_state_dict (`dict`): Model weights
- optimizer_state_dict (`dict`): Optimizer weights

The data is serialized using `save` API from `PyTorch`.  
Data can be read using the `load_model` API and written using the `save_model` API from the `parus.model` module.

### Hyperparameter (`hparams.json`) file

This file is store as standard JSON format with indent of `2`.

The data contains following keys:

> - data (`dict`):
>   - n_trn_samples (`int`): Number of training samples
>   - n_vld_samples (`int`): Number of validation samples
>   - n_tst_samples (`int`): Number of testing samples
>   - n_worker (`int`): Number of parallel processes for data loading
>   - dataset_name (`str`): Name of the dataset
>   - spike_groups (`list[str]`): List of spike types
>   - sampling_frequency (`int` |  `float`): Sampling rate of the samples
> - model (`dict`):
>   - model_name (`str`): Name of the model
>   - sequence_length (`int`): Frame size (number of data points) in each sample
>   - d_context (`int`): Embedding sparse context element length
>   - d_model (`int`): Number of expected features in the input
>   - n_head (`int`): Number of heads in the multi-head-attention models
>   - n_layers (`int`): Number of sub-encoder-layers in the encoder
>   - d_feedforward (`int`): Dimension of the feedforward network model
>   - output_channels (`int`): Number of output features (length of `spike_groups`)
> - train (`dict`):
>   - start_epoch (`int`): Initial epoch number, usually unchanged as `1`
>   - total_epoch (`int`): Total number of epoches
>   - batch_size (`int`): Data batch size
>   - steps_per_eval (`int`): Number of steps for each validation
>   - base_learning_rate (`float`): Base learning rate
>   - learning_rate_factor (`float`): Learning rate factor
>   - learning_rate_warmup (`int`): Number of warm-up steps
>   - model_param_clip (`float`): Weight clip to avoid overflow
>   - loss_function (`str`): Loss function name

### Training history (`history.json`) file

This file is store as standard JSON format.

The data is a list of dictionary, each contains following keys:

> - epoch (`int`): Epoch number
> - step (`int`): Step number
> - learning_rate (`float`): Learning rate
> - loss_training (`float`): Model training loss
> - loss_validation (`float`): Model validation loss
> - time (`float`): Time used for current step

### Training log (`train.log`) file

This file contains similar information as `history.json`, but with human-readable format.  
This file can be opened with any text editor.

### Test results (`*.pklz`) file

All model test results files are store with `PKLZ` format defined above.

The model test results can be visualized with PARUS CLI `parus.scripts.prddsp` or
GUI `Model Training` -> `Model Training` -> `View Testing Results`.

---

## Probe geometry (`*.prb`) file

The PRB file format is a structured container for JSON data.

The data contains following keys:

> - info (`dict`):
>   - mfr (`str`): Probe manufacturer
>   - typ (`str`): Name of the probe
>   - pn (`str` | `null`): Probe part number
>   - sn (`str` | `null`): Probe serial number
>   - sty (`str`): {'left' | 'right' | 'edge' | 'centre'} Channel alignment (plotting only)
>   - note (`Any`): Notes
> - site (`list`):
>   - _=[element]=_ (`dict`): Recording site information
>     - id (`int`): Channel index
>     - shk (`int`): Channel shank index
>     - col (`int`): Channel column index with shank
>     - geo (`tuple[float, float]`): Channel position (X, Y)
>     - pad (`tuple[float, float]`): Channel physical size in μm

Files can be read using any `json` module.  
Linear probe data (e.g. from JRClust) can be converted with using `conv_lin_prb` API from the `parus.data` module.

Probe can be visualized using `plot_prb` API from the `parus.data` module.  
Probe can be visualized with PARUS `Data Processing` -> `Spike Sorting` -> `View` at the probe section.
