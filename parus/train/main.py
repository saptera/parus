import os
import json
import time
import shutil
import torch
import torch.nn as nn
import argparse
from torch.utils import data
from parus.model.transformer import EncoderTransformer
from parus.train.dataset import LabelledMultipleFileDataset
from parus.train.train import train
#from parus.train.inference import test


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


def get_lbl_datagen(sig_folder, lbl_folder, seq_len, data_hparams, train_mode="trn"):
    if train_mode == "trn":
        dataset = LabelledMultipleFileDataset(
            sig_folder, lbl_folder, data_hparams["n_trn_samples"], seq_len)
    elif train_mode == "val":
        dataset = LabelledMultipleFileDataset(
            sig_folder, lbl_folder, data_hparams["n_val_samples"], seq_len)
    elif train_mode == "tst":
        dataset = LabelledMultipleFileDataset(
            sig_folder, lbl_folder, data_hparams["n_tst_samples"], seq_len)
    else:
        raise Exception("invalid training mode, must be trn, val, or tst")

    if train_mode in ["trn", "val"]:
        datagen = data.DataLoader(
            dataset, batch_size=data_hparams["batch_size_train"], shuffle=True, num_workers=data_hparams["n_worker"])
    else:
        datagen = data.DataLoader(
            dataset, batch_size=data_hparams["batch_size_inference"], shuffle=True, num_workers=data_hparams["n_worker"])
    return datagen


def setup_experiment(model_name, experiment_folder_path):
    experiment_name = "_".join(
        [model_name, time.strftime("%Y-%m-%d_%H:%M")])
    cur_experiment_folder_path = os.path.join(
        experiment_folder_path, experiment_name)
    os.mkdir(cur_experiment_folder_path)
    print("Directory '% s' created" % cur_experiment_folder_path)
    shutil.copy2('hparams.json', cur_experiment_folder_path)
    print("Copied hparams.json to '% s' " % cur_experiment_folder_path)
    
    return cur_experiment_folder_path

if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument(
        "--debug", help="run training with debug hparams", action="store_true")
    args = argParser.parse_args()

    # load hparams
    hparams = load_hparams("hparams.json", args.debug)
    model_hparams = hparams["model"]
    train_hparams = hparams["train"]
    data_hparams = hparams["data"]

    # setup experiment folder
    cur_experiment_folder_path = setup_experiment(model_hparams["model_name"], train_hparams["experiment_folder"])

    # initial training objects
    model = EncoderTransformer(input_dim=model_hparams["sequence_length"],
                               context_dim=model_hparams["d_context"],
                               d_model=model_hparams["d_model"],
                               nhead=model_hparams["n_head"],
                               num_layers=model_hparams["n_layers"],
                               dim_feedforward=model_hparams["d_feedforward"])
    if torch.cuda.device_count() > 1:
        model = nn.DataParallel(model)

    criterion = nn.L1Loss(reduction='mean')
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=train_hparams["learning_rate"])
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, 1.0, gamma=train_hparams["lr_decay"])

    # get datagen
    trn_folder = os.path.join(data_hparams["data_folder"], "trn")
    trn_datagen = get_lbl_datagen(os.path.join(trn_folder, "sig"), os.path.join(
        trn_folder, "lbl"), model_hparams["sequence_length"], data_hparams, "trn")
    val_folder = os.path.join(data_hparams["data_folder"], "val")
    val_datagen = get_lbl_datagen(os.path.join(val_folder, "sig"), os.path.join(
        val_folder, "lbl"), model_hparams["sequence_length"], data_hparams, "val")
    tst_folder = os.path.join(data_hparams["data_folder"], "tst")
    tst_datagen = get_lbl_datagen(os.path.join(tst_folder, "sig"), os.path.join(
        tst_folder, "lbl"), model_hparams["sequence_length"], data_hparams, "tst")

    # run experiment with labelled data
    train(model, criterion, optimizer, scheduler,
          trn_datagen, val_datagen, cur_experiment_folder_path, train_hparams)
    #test(model, tst_datagen, train_hparams["experiment_folder"])
