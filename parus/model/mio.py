# -*- coding: utf-8 -*-

"""Model operation IO module

Hyperparameter, dataset, checkpoint, and training-log IO helpers for the model training pipeline.
"""

import os
import time
import json
import torch
from torch.utils import data
from typing import TextIO

__package__ = 'parus.model'
__name__ = 'parus.model.mio'
from .dset import TrainingDataset

__all__ = [
    'save_hparams', 'load_hparams', 'load_all_datasets', 'save_model', 'load_model',
    'write_train_log', 'write_train_history'
]
"""
Public function list:

- save_hparams(hparams_file, hparams)                          : Save hyperparameters to a JSON file
- load_hparams(hparams_file, debug)                            : Load hyperparameters from a JSON file (or defaults)
- load_all_datasets(dataset_dir, seq_len, batch_size, ...)     : Build training/validation/testing data loaders
- save_model(save_dir, model, optimizer, epoch, description)   : Save a model checkpoint with optimizer state
- load_model(ckpt_path, model, remap)                          : Load model weights from a checkpoint
- write_train_log(fp, ep, stp, lr, tls, vls, t, tot_ep, ...)   : Append a record to the training log file
- write_train_history(fp, ep, stp, lr, tls, vls, t)            : Append a record to the JSON training history

Protected constants:

- _default_hparams (dict)                                      : Default hyperparameters for model operations
- _debug_hparams (dict)                                        : Hyperparameter overrides used in debug mode
"""


# Default hyperparameters for model operation
_default_hparams = {
    'data': {
        'n_trn_samples': 500000,
        'n_vld_samples': 1000,
        'n_tst_samples': 1000,
        'n_worker': 1,
        'dataset_name': None,  # Update when dataset is defined
        'spike_groups': [],  # Update when dataset is defined
        'sampling_frequency': 0.0  # Update when dataset is defined
    },
    'model': {
        'model_name': 'parus',
        'sequence_length': 300,
        'd_context': 32,
        'd_model': 256,
        'n_head': 16,
        'n_layers': 6,
        'd_feedforward': 256,
        'output_channels': 1  # Update when dataset is defined, equal to the length of ['data']['spike_groups']
    },
    'train': {
        'start_epoch': 1,  # DO NOT CHANGE for normal use, NOT INCLUDED in scripts/GUIs
        'total_epoch': 10,
        'batch_size': 64,
        'steps_per_eval': 1000,
        'base_learning_rate': 1.0,
        'learning_rate_factor': 1.0,
        'learning_rate_warmup': 7000,
        'model_param_clip': 0.5,
        'loss_function': 'l1'
    }
}

# Debug hyperparameters for model test run
_debug_hparams = {
    'data': {
        'n_trn_samples': 6400,
        'n_vld_samples': 500,
        'n_tst_samples': 500
    },
    'train': {
        'total_epoch': 2,
        'steps_per_eval': 50
    }
}


def save_hparams(hparams_file, hparams=None):
    """Save model hyperparameters to a JSON file.

    Starts from the built-in defaults in ``_default_hparams`` and overlays any keys present in ``hparams``
    before writing. The resulting file is suitable for round-tripping through :func:`load_hparams`.

    Args:
        hparams_file (str): Output hyperparameter file path
        hparams (dict | None): Per-section hyperparameter overrides; pass :data:`None` to write the defaults
            unchanged (default: ``None``)

    Returns:
        bool: Always :data:`True` on successful write
    """
    # Load default hyperparameters
    hp = _default_hparams.copy()
    # Update hyperparameters
    if isinstance(hparams, dict):
        [hp[k].update(hparams[k]) for k in hparams]
    # Write file
    with open(hparams_file, 'w') as fp:
        json.dump(hp, fp, indent=2)
    return True


def load_hparams(hparams_file=None, debug=False):
    """Load model hyperparameters from a JSON file, falling back to the defaults.

    Starts from ``_default_hparams``, overlays the user-supplied JSON when available, and finally overlays
    ``_debug_hparams`` when ``debug`` is :data:`True`.

    Args:
        hparams_file (str | None): Input hyperparameter file path; pass :data:`None` (or any non-existent
            path) to use the built-in defaults (default: ``None``)
        debug (bool): When :data:`True`, overlay the debug-mode hyperparameter overrides on top of the
            loaded values (default: ``False``)

    Returns:
        dict: Resolved hyperparameter dictionary with the same nested structure as ``_default_hparams``
    """
    # Load default hyperparameters
    hp = _default_hparams.copy()
    # Update hyperparameters if file exist
    if (hparams_file is not None) and os.path.isfile(hparams_file):
        with open(hparams_file, 'r') as fp:
            hparams = json.load(fp)
        [hp[k].update(hparams[k]) for k in hparams]
    # Debug mode
    if debug:
        print("Set hyperparameters for debugging mode")
        [hp[k].update(_debug_hparams[k]) for k in _debug_hparams]
    return hp


def load_all_datasets(dataset_dir, seq_len, batch_size, data_hparams):
    """Build training/validation/testing :class:`~torch.utils.data.DataLoader` instances from a folder.

    Walks ``dataset_dir`` for files starting with ``trn``, ``vld``, ``tst`` (extension ``.sim``), wraps each
    with a :class:`~parus.model.dset.TrainingDataset`, and returns the matching DataLoaders. The training
    and validation loaders shuffle on every epoch; the testing loader does not.

    Args:
        dataset_dir (str): Folder containing the training/validation/testing dataset files
        seq_len (int): Model sequence length
        batch_size (int): Loader batch size
        data_hparams (dict[str, int]): Dataset hyperparameters

            - n_trn_samples (int): Training set sample count
            - n_vld_samples (int): Validation set sample count
            - n_tst_samples (int): Testing set sample count
            - n_worker (int): Number of multiprocessing workers per loader

    Returns:
        tuple[data.DataLoader, data.DataLoader, data.DataLoader]: Loaders in (training, validation, testing) order

    Raises:
        FileNotFoundError: If any of the three dataset files (``trn*.sim``, ``vld*.sim``, ``tst*.sim``) is
            missing under ``dataset_dir``
    """
    # Unpack dataset hyperparameters
    num_smp = {'trn': data_hparams['n_trn_samples'],
               'vld': data_hparams['n_vld_samples'],
               'tst': data_hparams['n_tst_samples']}
    num_wkr = data_hparams['n_worker']
    # Locate all datasets
    dls = {}  # INIT VAR
    for mode in ['trn', 'vld', 'tst']:
        for f in os.listdir(dataset_dir):
            if f.startswith(mode) and f.endswith('.sim'):
                # Get dataset
                dataset = TrainingDataset(os.path.join(dataset_dir, f), num_smp[mode], seq_len)
                # Create data loader
                shuffle = mode in ['trn', 'vld']
                datagen = data.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_wkr)
                # Assign and exit search loop
                dls[mode] = datagen
                break
        else:
            mtp = {'trn': "TRAINING", 'vld': "VALIDATION", 'tst': "TESTING"}[mode]
            raise FileNotFoundError("Cannot locate %s set at defined path!" % mtp)
    # Unpack and return for variable assignment
    return dls['trn'], dls['vld'], dls['tst']


def save_model(save_dir, model, optimizer, epoch, description=None):
    """Save a model checkpoint with the matching optimizer state.

    The checkpoint dictionary stores ``epoch``, ``description``, ``model_state_dict``, and
    ``optimizer_state_dict``. The output filename is ``"{description}.ckpt"`` when ``description`` is a
    non-empty string and ``"epoch_{epoch:03d}.ckpt"`` otherwise.

    Args:
        save_dir (str): Output directory for the checkpoint file
        model (torch.nn.Module): Model whose ``state_dict`` is captured
        optimizer (torch.optim.Optimizer): Optimizer whose ``state_dict`` is captured
        epoch (int): Current epoch number
        description (str | None): Custom checkpoint description; pass :data:`None` (or an empty string) to
            use the epoch-based default name (default: ``None``)
    """
    # Validate description
    if description:  # Check for both None and EmptyStr
        file = "%s.ckpt" % description
        desc = description
    else:
        file = "epoch_%03d.ckpt" % epoch
        desc = 'epoch_record'
    # Get current model and optimizer data
    ckpt = {
        'epoch': epoch,
        'description': desc,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict()
    }
    # Serialize with PyTorch
    ckpt_path = os.path.join(save_dir, file)
    torch.save(ckpt, ckpt_path)


def load_model(ckpt_path, model, remap=None):
    """Load model weights from a checkpoint file in place and return the model.

    Reads the checkpoint with ``weights_only=True`` for safety and applies ``model_state_dict`` to the
    supplied model.

    Args:
        ckpt_path (str): Path to the model checkpoint file
        model (torch.nn.Module): Model instance to load the weights into
        remap (str | dict[str, str] | torch.device | None): Storage-location remap argument forwarded to
            :func:`torch.load`; pass :data:`None` to keep the saved device assignments (default: ``None``)

    Returns:
        torch.nn.Module: The same ``model`` instance, returned for chaining convenience
    """
    ckpt = torch.load(ckpt_path, map_location=remap, weights_only=True)
    model.load_state_dict(ckpt['model_state_dict'])
    return model


def write_train_log(fp, ep, stp, lr, tls, vls, t, tot_ep, curr_loss=float('inf')):
    """Append a single training-step record to a model training log file.

    Writes one timestamped status line for the step and, when validation loss improved over ``curr_loss``,
    a second line announcing the model save. The file pointer is flushed after each call so the log stays
    up-to-date during long runs.

    Args:
        fp (TextIO): Log file pointer opened in a writable mode
        ep (int): Epoch number
        stp (int): Step number within the epoch
        lr (float): Current learning rate
        tls (float): Training loss for this step
        vls (float): Validation loss for this step
        t (float): Wall-clock time used for this step in seconds
        tot_ep (int): Total number of epochs for the run
        curr_loss (float): Best validation loss seen so far (default: ``float('inf')``)
    """
    # Get event time
    t_str = time.strftime("[%Y-%m-%d %H:%M:%S] ")
    # Record model status
    stat = "Epoch: %d/%d - Step: %d - Learning Rate: %.4e - Trn Loss: %.6f - Val Loss: %.6f - Time: %.4f" % (
        ep, tot_ep, stp, lr, tls, vls, t)
    fp.write(t_str + stat + '\n')
    print(stat)
    # Record model save event
    if vls < curr_loss:
        improve = "    -> Validation loss decreased (%.6f --> %.6f)!  Saving model..." % (curr_loss, vls)
        fp.write(t_str + improve + '\n')
        print(improve)
    fp.flush()  # Update immediately


def write_train_history(fp, ep, stp, lr, tls, vls, t):
    """Append a single training-step record to a JSON training history file.

    The file is treated as an append-friendly JSON array on disk: the trailing ``]`` is replaced with the
    new entry and a fresh closing ``]`` so that the file remains valid JSON after every call. The first
    call to an empty file writes the opening ``[``.

    Args:
        fp (TextIO): {``'r+'``, ``'w+'``, ``'a+'``} History file pointer opened in a read+write text mode
        ep (int): Epoch number
        stp (int): Step number within the epoch
        lr (float): Current learning rate
        tls (float): Training loss for this step
        vls (float): Validation loss for this step
        t (float): Wall-clock time used for this step in seconds
    """
    rec = {'epoch': ep, 'step': stp, 'learning_rate': lr, 'loss_training': tls, 'loss_validation': vls, 'time': t}
    jstr = '    ' + str(rec).replace("'", '"') + '\n]\n'
    # Initialize seek position
    fp.seek(0, os.SEEK_END)
    pos = fp.tell()
    # Seek end ']' mark
    while pos > 0 and fp.read(1) != '}':
        pos -= 1
        fp.seek(pos, os.SEEK_SET)
    # Write new data
    if pos == 0:
        fp.write('[\n')
    else:
        fp.seek(pos, os.SEEK_SET)
        fp.truncate()
        fp.write('},\n')
    fp.write(jstr)
    fp.flush()  # Update immediately
