import os
import time
import json
import torch
from torch.utils import data
from typing import TextIO
from parus.train.dataset import TrainingDataset


def load_hparams(hparams_file_path='hparams.json', debug=False):
    hparams_file = open(hparams_file_path)
    hparams = json.load(hparams_file)

    if debug:
        print("updating hparams for debugging mode")
        debug_hparams = hparams["debug"]
        for section in debug_hparams.keys():
            for k, v in debug_hparams[section].items():
                hparams[section][k] = v

    return hparams


def update_hparams(hparams, hparams_file_path='hparams.json'):
    with open(hparams_file_path, 'w') as fp:
        json.dump(hparams, fp, indent=2)
    return True


def get_file_datagen(data_file_path, seq_len, batch_size, data_hparams, mode="trn"):
    # Define sample counts for each mode
    sample_counts = {
        "trn": data_hparams["n_trn_samples"],
        "val": data_hparams["n_val_samples"],
        "tst": data_hparams["n_tst_samples"]
    }
    
    if mode not in sample_counts:
        raise ValueError(f"Invalid training mode '{mode}'. Must be one of: {list(sample_counts.keys())}")
    
    # Create dataset
    dataset = TrainingDataset(
        data_file_path, 
        sample_counts[mode], 
        seq_len
    )
    
    # Create data loader with appropriate shuffle setting
    shuffle = mode in ["trn", "val"]
    datagen = data.DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=shuffle, 
        num_workers=data_hparams["n_worker"]
    )
    
    return datagen


def _find_first_sim_file(folder_path):
    if not os.path.isdir(folder_path):
        return None
    sim_files = [f for f in os.listdir(folder_path) if f.endswith('.sim')]
    if not sim_files:
        return None
    return os.path.join(folder_path, sim_files[0])


def get_all_training_datagen(data_root_folder, seq_len, batch_size, data_hparams):
    modes = ["trn", "val", "tst"]
    datagens = {}
    for mode in modes:
        folder = os.path.join(data_root_folder, mode)
        sim_path = _find_first_sim_file(folder)
        if sim_path is None:
            raise FileNotFoundError(f"No .sim files found in {folder}")
        datagens[mode] = get_file_datagen(sim_path, seq_len, batch_size, data_hparams, mode)

    return datagens["trn"], datagens["val"], datagens["tst"]


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
    """ Write model training history file in JSON format

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
