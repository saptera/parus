# Model operation IO functions

import os
import time
import json
import torch
from torch.utils import data
from typing import TextIO

__package__ = 'parus.model'
from .dset import TrainingDataset

__all__ = [
    'save_hparams', 'load_hparams', 'load_all_datasets', 'save_model', 'load_model',
    'write_train_log', 'write_train_history'
]
"""
Function list:
  save_hparams(hparams_file, hparams=None): Save hyperparameters to a JSON file.
  load_hparams(hparams_file=None, debug=False): Load model hyperparameters JSON file, use default if file unavailable.
  load_all_datasets(dataset_dir, seq_len, batch_size, data_hparams): Get all dataset loaders from defined folder.
  save_model(save_dir, model, optimizer, epoch, description=None): Save current model with optimizer info.
  load_model(ckpt_path, model): Load model checkpoint from file.
  write_train_log(fp, ep, stp, lr, tls, vls, t, tot_ep, curr_loss=float('inf')): Write model training log file.
  write_train_history(fp, ep, stp, lr, tls, vls, t): Write model training history file in JSON format.
Protected constants:
  _default_hparams {dict}: Default hyperparameters for model operation.
  _debug_hparams {dict}: Debug hyperparameters for model test run.
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
        'n_trn_samples': 5000,
        'n_vld_samples': 500,
        'n_tst_samples': 500
    },
    'train': {
        'total_epoch': 1,
        'steps_per_eval': 80
    }
}


def save_hparams(hparams_file, hparams=None):
    """ Save hyperparameters to a JSON file.

    Args:
        hparams_file (str): Model hyperparameter file path
        hparams (dict | None): Updated hyperparameter values

    Returns:
        bool: File save status
    """
    # Load default hyperparameters
    hp = _default_hparams.copy()
    # Update hyperparameters
    if isinstance(hparams, dict):
        hp.update(hparams)
    # Write file
    with open(hparams_file, 'w') as fp:
        json.dump(hp, fp, indent=2)
    return True


def load_hparams(hparams_file=None, debug=False):
    """ Load model hyperparameters JSON file, use default if file unavailable.

    Args:
        hparams_file (str | None): Model hyperparameter file path (default: None = load default hyperparameters)
        debug (bool): Model debug mode flag (default: False)

    Returns:
        Model hyperparameters
    """
    # Load default hyperparameters
    hp = _default_hparams.copy()
    # Update hyperparameters if file exist
    if (hparams_file is not None) and os.path.isfile(hparams_file):
        with open(hparams_file, 'r') as fp:
            hparams = json.load(fp)
        hp.update(hparams)
    # Debug mode
    if debug:
        print("Set hyperparameters for debugging mode")
        hp.update(_debug_hparams)
    return hp


def load_all_datasets(dataset_dir, seq_len, batch_size, data_hparams):
    """ Get training/validation/testing dataset loader from defined folder.

    Args:
        dataset_dir (str): Dataset folder, should contain training/validation/testing sets
        seq_len (int): Model sequence length
        batch_size (int): Model batch size
        data_hparams (dict[str, int]): Dataset hyperparameters
            - n_trn_samples (int): Training set sample number
            - n_vld_samples (int): Validation set sample number
            - n_tst_samples (int): Testing set sample number
            - n_worker (int): Multiprocess worker number for data loading

    Returns:
        tuple[data.DataLoader, data.DataLoader, data.DataLoader]: Data loaders for each dataset, in trn/vld/tst order
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
    """ Save current model with optimizer info.

    Args:
        save_dir (str): Target folder for saving checkpoint
        model (torch.nn.Module): Current model
        optimizer (torch.optim.optimizer.Optimizer): Current optimizer
        epoch (int): Current epoch number
        description (str | None): Checkpoint description
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


def load_model(ckpt_path, model):
    """ Load model checkpoint from file.

    Args:
        ckpt_path (str): Model saved checkpoint path
        model (torch.nn.Module): Current model
    """
    ckpt = torch.load(ckpt_path)
    model.load_state_dict(ckpt['model_state_dict'])
    return model


def write_train_log(fp, ep, stp, lr, tls, vls, t, tot_ep, curr_loss=float('inf')):
    """ Write records to model training log file.

    Args:
        fp (TextIO): {'r+' | 'w+' | 'a+'} Log file pointer
        ep (int): Epoch number
        stp (int): In epoch step number
        lr (float): Learning rate
        tls (float): Training loss
        vls (float): Validation loss
        t (float): Time used for this step
        tot_ep (int): Total number of epoches
        curr_loss (float): Current minimum loss in the training
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
    """ Write model training history file in JSON format.

    Args:
        fp (TextIO): {'r+' | 'w+' | 'a+'} Training history file pointer
        ep (int): Epoch number
        stp (int): In epoch step number
        lr (float): Learning rate
        tls (float): Training loss
        vls (float): Validation loss
        t (float): Time used for this step
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
