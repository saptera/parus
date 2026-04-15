# PARUS Command Line Interface (CLI)

This document describes the command-line tools available in the PARUS pipeline 
for simulated neural signal generation, model training, evaluation, and inference.

CLI scripts are located at `parus/scripts/`

All scripts support following flags:

| Option            | Description                                |
|-------------------|--------------------------------------------|
| `-h`, `--help`    | Show help message and exit                 |
| `-v`, `--version` | Displays the current version of the script |

### Table of contents

- [Simulated Dataset Generation `ParusGenSim`](#1-parusgensim---simulated-dataset-generation)
- [Dataset Statistics Visualization `ParusGenStat`](#2-parusgenstat---dataset-statistics-visualization)
- [Model Training `ParusModTrn`](#3-parusmodtrn---model-training)
- [Prediction Visualization `ParusPrdDsp`](#4-parusprddsp---prediction-visualization)
- [Model Inference `ParusModInf`](#5-parusdatinf---model-inference)

---

## 1. `ParusGenSim` - Simulated Dataset Generation

Generate simulated neural signal datasets for model training.

### Usage

- Unix / Linux / macOS

  ```bash
  python3 gensim.py signalFolder noiseFolder outputFolder sampleNumber [options]
  ```

- Windows

  ```bat
  py gensim.py signalFolder noiseFolder outputFolder sampleNumber [options]
  ```

### Description

Generates simulated neural signal data. *Intended for model training purposes only.*

### Positional Arguments

| Argument       | Type | Description                                         |
|----------------|------|-----------------------------------------------------|
| `signalFolder` | str  | Directory containing archived signal data (`*.arc`) |
| `noiseFolder`  | str  | Directory containing noise data (`*.noi`)           |
| `outputFolder` | str  | Output directory for simulated data (`*.sim`)       |
| `sampleNumber` | int  | Number of samples to generate                       |

### Generation Properties

| Option              | Type       | Default    | Description                                 |
|---------------------|------------|------------|---------------------------------------------|
| `-l`, `--length`    | int        | 300        | Total signal length                         |
| `-f`, `--freq`      | int/float  | 20000      | Sampling frequency (Hz)                     |
| `-ig`, `--mingap`   | int        | 20         | Minimum gap between signal events           |
| `-xg`, `--maxgap`   | int        | 80         | Maximum gap between signal events           |
| `-gp`, `--group`    | {typ, spk} | (disabled) | Grouping method (cell type or spike type)   |
| `-gr`, `--grpratio` | list       | (equal)    | Group occurrence ratios                     |
| `-no`, `--noionly`  | float      | 0.0        | Ratio of noise-only samples (0 ≤ value < 1) |

### Data Randomization

| Option            | Type        | Default      | Description                                   |
|-------------------|-------------|--------------|-----------------------------------------------|
| `-sf`, `--sigfac` | float float | (no scaling) | Signal amplitude scaling range [`low` `high`] |
| `-nf`, `--noifac` | float float | (no scaling) | Noise scaling range [`low` `high`]            |

### Baseline Augmentation

| Option               | Type        | Default | Description                                 |
|----------------------|-------------|---------|---------------------------------------------|
| `-bs`, `--baseshift` | list        | None    | Methods: `cst`, `lin`, `sin`, `nos`         |
| `-bp`, `--basecomp`  | list        | (equal) | Composition ratio of baseline methods       |
| `-ba`, `--baseamps`  | float float | None    | Amplitude range [`low` `high`]              |
| `-bf`, `--basefreq`  | float float | None    | Frequency range [`low` `high`] (`sin` only) |

### Extra Settings

| Option             | Type | Default   | Description                          |
|--------------------|------|-----------|--------------------------------------|
| `-eg`, `--example` | int  | None      | Number of additional example samples |
| `-tp`, `--settyp`  | str  | (general) | Dataset usage type label             |

---

## 2. `ParusGenStat` - Dataset Statistics Visualization

Visualize statistics of generated datasets.

### Usage

- Unix / Linux / macOS

  ```bash
  python3 gensta.py reportFile
  ```

- Windows

  ```bat
  py gensta.py reportFile
  ```

### Arguments

| Argument      | Type | Description                    |
|---------------|------|--------------------------------|
| `reportFile`  | str  | Path to generation report file |

---

## 3. `ParusModTrn` - Model Training

Train a neural signal separation model.

### Usage

- Unix / Linux / macOS

  ```bash
  python3 modtrn.py art_dir dat_dir [options]
  ```

- Windows

  ```bat
  py modtrn.py art_dir dat_dir [options]
  ```

### Description

Train a spike detection model using generated datasets.

### Positional Arguments

| Argument  | Type | Description                      |
|-----------|------|----------------------------------|
| `art_dir` | str  | Path to store training artifacts |
| `dat_dir` | str  | Path to training dataset         |

### Dataset Parameters

| Option             | Type | Default | Description                   |
|--------------------|------|---------|-------------------------------|
| `-dtn`, `--smptrn` | int  | 500000  | Training samples              |
| `-dvl`, `--smpvld` | int  | 1000    | Validation samples            |
| `-dts`, `--smptst` | int  | 1000    | Testing samples               |
| `-dwk`, `--numwkr` | int  | 1       | Number of data loader workers |

### Model Configuration

| Option             | Type | Default | Description               |
|--------------------|------|---------|---------------------------|
| `-mid`, `--modstr` | str  | 'parus' | Model name                |
| `-mls`, `--lenseq` | int  | 300     | Sequence length           |
| `-mdc`, `--dimctx` | int  | 32      | Context dimension         |
| `-mdm`, `--dimmod` | int  | 256     | Model input dimension     |
| `-mnh`, `--nummhd` | int  | 16      | Number of attention heads |
| `-mnl`, `--numlyr` | int  | 6       | Number of encoder layers  |
| `-mdf`, `--dimffd` | int  | 256     | Feedforward dimension     |

### Training Settings

| Option             | Type           | Default | Description             |
|--------------------|----------------|---------|-------------------------|
| `-tep`, `--numeps` | int            | 10      | Number of epochs        |
| `-tbs`, `--szsbat` | int            | 64      | Batch size              |
| `-tev`, `--stpevl` | int            | 1000    | Steps per evaluation    |
| `-tlr`, `--lrbase` | float          | 1.0     | Base learning rate      |
| `-tlf`, `--lrfact` | float          | 1.0     | Learning rate factor    |
| `-tlw`, `--lrwarm` | int            | 7000    | Warmup steps            |
| `-tpc`, `--prmclp` | float          | 0.5     | Gradient clipping value |
| `-tls`, `--lossfn` | {l1, mse, bce} | 'l1'    | Loss function           |

### Additional Options

| Option             | Type                     | Default | Description                              |
|--------------------|--------------------------|---------|------------------------------------------|
| `-pth`, `--pkdths` | float                    | -50.0   | Post-inference spike detection threshold |
| `-t`, `--hint`     | {text, disp, save, none} | text    | Validation results output mode           |
| `-d`, `--debug`    | flag                     | False   | Enter debug mode                         |

---

## 4. `ParusPrdDsp` - Prediction Visualization

Display model predictions versus input signals.

### Usage

- Unix / Linux / macOS

  ```bash
  python3 prddsp.py resultPath [options]
  ```

- Windows

  ```bat
  py prddsp.py resultPath [options]
  ```

### Arguments

| Argument     | Type | Description                |
|--------------|------|----------------------------|
| `resultPath` | str  | Path to prediction results |

### Plot Controls

| Option           | Type | Default     | Description              |
|------------------|------|-------------|--------------------------|
| `-i`, `--inp`    | flag | True (show) | Hide input plot          |
| `-s`, `--spk`    | flag | True (show) | Hide all spike plots     |
| `-sr`, `--spkrf` | flag | True (show) | Hide spike reference     |
| `-sp`, `--spkpd` | flag | True (show) | Hide spike prediction    |
| `-p`, `--pos`    | flag | True (show) | Hide all position plots  |
| `-pr`, `--posrf` | flag | True (show) | Hide position reference  |
| `-pp`, `--pospd` | flag | True (show) | Hide position prediction |

### Data Settings

| Option         | Type  | Default | Description                |
|----------------|-------|---------|----------------------------|
| `-n`, `--norm` | flag  | False   | Enable normalization       |
| `-c`, `--cont` | flag  | False   | Enable continuous sampling |
| `-o`, `--ovlp` | int   | (no)    | Overlap size               |
| `-f`, `--freq` | float | (auto)  | Sampling frequency         |

### Axis Settings

| Option          | Type  | Default | Description          |
|-----------------|-------|---------|----------------------|
| `-yx`, `--ymax` | float | (auto)  | Max Y-axis           |
| `-yi`, `--ymin` | float | (auto)  | Min Y-axis           |
| `-lm`, `--lims` | flag  | False   | Global Y-axis limits |
| `-sb`, `--sub`  | flag  | False   | Enable subplot mode  |

---

## 5. `ParusDatInf` - Model Inference

Run inference using a trained model.

### Usage

- Unix / Linux / macOS

  ```bash
  python3 modinf.py ckpt [paths] [options]
  ```

- Windows

  ```bat
  py modinf.py ckpt [paths] [options]
  ```

### Description

Apply a trained model to raw signal data.

### Positional Arguments

| Argument | Type | Description                      |
|----------|------|----------------------------------|
| `ckpt`   | str  | Path to trained model checkpoint |

### Data Input

| Option         | Type | Default | Description          |
|----------------|------|---------|----------------------|
| `-f`, `--file` | list | None    | Input files (`*.h5`) |
| `-d`, `--dirs` | list | None    | Input directories    |

### Processing Options

| Option              | Type      | Default | Description                  |
|---------------------|-----------|---------|------------------------------|
| `-lp`, `--overlap`  | int       | 10      | Sample overlap size          |
| `-tm`, `--memory`   | flag      | False   | Load entire file into memory |
| `-bs,` `--batch`    | int       | 2048    | Batch size                   |
| `-cp`, `--compress` | int (0–9) | 4       | Output compression level     |
