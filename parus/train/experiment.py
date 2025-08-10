import json
import os
import shutil
import time
import torch
from torch.utils import data
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


def setup_experiment(model_name, dataset_name, experiment_folder_path, mode="trn"):
    experiment_name = "_".join(
        [model_name, dataset_name, time.strftime("%Y-%m-%d_%H:%M")])
    cur_exp_folder_path = os.path.join(
        experiment_folder_path, experiment_name)
    os.mkdir(cur_exp_folder_path)
    print("Directory '% s' created" % cur_exp_folder_path)
    shutil.copy2('hparams.json', cur_exp_folder_path)
    print("Copied hparams.json to '% s' " % cur_exp_folder_path)
    
    if mode == "trn":
        tst_pred_folder = os.path.join(cur_exp_folder_path, "test_pred")
        os.mkdir(tst_pred_folder)
        print("Test Predictions Folder '% s' created" % tst_pred_folder)
        return cur_exp_folder_path, tst_pred_folder
    elif mode == "inf":
        inference_pred_folder = os.path.join(cur_exp_folder_path, "inf_pred")
        os.mkdir(inference_pred_folder)
        print("Inference Predictions Folder '% s' created" % inference_pred_folder)
        return cur_exp_folder_path, inference_pred_folder
    else:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: trn, inf")


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


def save(experiment_folder_path, model, optimizer, cur_epoch):
    ckpt = {
        "epoch": cur_epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict()
    }
    ckpt_path = os.path.join(
        experiment_folder_path, "epoch" + str(cur_epoch) + ".ckpt")

    torch.save(ckpt, ckpt_path)


def load_model(ckpt_path, model):
    ckpt = torch.load(ckpt_path)
    model.load_state_dict(ckpt['model_state_dict'])
    return model


def write_train_log(fp, ep, stp, lr, tls, vls, t, tot_ep, curr_loss=float('inf')):
    if '+' in fp.mode:
        if vls < curr_loss:
            extra = "\nValidation loss decreased (%.6f --> %.6f).  Saving model ...\n\n" % (curr_loss, vls)
            fp.write(extra)
        stat = "Epoch: %d/%d - Step: %d - Learning Rate: %.6f - Trn Loss: %.6f - Val Loss: %.6f - Time: %.4f\n" % (
            ep, tot_ep, stp, lr, tls, vls, t)
        fp.write(stat)
        fp.flush()  # Update immediately
    else:
        print("Invalid file mode!")


def write_train_history(fp, ep, stp, lr, tls, vls, t):
    if '+' in fp.mode:
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
    else:
        print("Invalid file mode!")

