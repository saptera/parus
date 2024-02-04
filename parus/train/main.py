import os
import json
import time
import shutil
import torch
import torch.nn as nn
import argparse
from torch.utils import data
from parus.model.transformer import EncoderTransformer
from parus.train.dataset import LabelledMultipleFileDataset, NoLabelSingleFileDataset, DuoLabelMultipleFileDataset
from parus.train.train import train, load_model
from parus.train.inference import duo_test, test, inference


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


def get_lbl_datagen(sig_folder, lbl_folder, seq_len, batch_size, data_hparams, train_mode="trn", lbl2_folder=None):
    if train_mode == "trn":
        dataset = LabelledMultipleFileDataset(
            sig_folder, lbl_folder, data_hparams["n_trn_samples"], seq_len)
    elif train_mode == "val":
        dataset = LabelledMultipleFileDataset(
            sig_folder, lbl_folder, data_hparams["n_val_samples"], seq_len)
    elif train_mode == "tst":
        dataset = LabelledMultipleFileDataset(
            sig_folder, lbl_folder, data_hparams["n_tst_samples"], seq_len)
    elif train_mode == "duo":
        dataset = DuoLabelMultipleFileDataset(
            sig_folder, lbl_folder, lbl2_folder, data_hparams["n_tst_samples"], seq_len)
    else:
        raise Exception("invalid training mode, must be trn, val, or tst")

    if train_mode in ["trn", "val"]:
        datagen = data.DataLoader(
            dataset, batch_size=batch_size, shuffle=True, num_workers=data_hparams["n_worker"])
    else:
        datagen = data.DataLoader(
            dataset, batch_size=batch_size, shuffle=False, num_workers=data_hparams["n_worker"])
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
    argParser.add_argument(
        "--train", help="run training", action="store_true")
    argParser.add_argument(
        "--inference", help="run inference", action="store_true")
    argParser.add_argument(
        "--load_model", help="load model from saved checkpoint", action="store_true")
    args = argParser.parse_args()

    # load hparams
    hparams = load_hparams("hparams.json", args.debug)
    model_hparams = hparams["model"]
    data_hparams = hparams["data"]

    # setup experiment folder
    cur_experiment_folder_path = setup_experiment(
        model_hparams["model_name"], model_hparams["experiment_folder"])

    # initial training objects
    model = EncoderTransformer(input_dim=model_hparams["sequence_length"],
                               context_dim=model_hparams["d_context"],
                               d_model=model_hparams["d_model"],
                               nhead=model_hparams["n_head"],
                               num_layers=model_hparams["n_layers"],
                               dim_feedforward=model_hparams["d_feedforward"])
    if torch.cuda.device_count() > 1:
        model = nn.DataParallel(model)

    if args.load_model:
        model = load_model(model_hparams["checkpoint_file"], model)

    if args.train:
        train_hparams = hparams["train"]

        #criterion = nn.L1Loss(reduction='mean')
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=train_hparams["learning_rate"])
        scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer, 1.0, gamma=train_hparams["lr_decay"])

        # get datagen
        trn_folder = os.path.join(data_hparams["data_folder"], "trn")
        trn_datagen = get_lbl_datagen(os.path.join(trn_folder, "sig"), os.path.join(
            trn_folder, "pos"), model_hparams["sequence_length"], train_hparams["batch_size"], data_hparams, "trn")
        val_folder = os.path.join(data_hparams["data_folder"], "val")
        val_datagen = get_lbl_datagen(os.path.join(val_folder, "sig"), os.path.join(
            val_folder, "pos"), model_hparams["sequence_length"], train_hparams["batch_size"], data_hparams, "val")
        tst_folder = os.path.join(data_hparams["data_folder"], "tst")
        tst_datagen = get_lbl_datagen(os.path.join(tst_folder, "sig"), os.path.join(
            tst_folder, "lbl"), model_hparams["sequence_length"], 1, data_hparams, "duo", os.path.join(
            tst_folder, "pos"))

        # run experiment with labelled data
        train(model, criterion, optimizer, scheduler,
              trn_datagen, val_datagen, cur_experiment_folder_path, train_hparams)

        # make prediction folder
        tst_pred_folder = os.path.join(
            cur_experiment_folder_path, "test_pred")
        os.mkdir(tst_pred_folder)
        # test(model, tst_datagen, tst_pred_folder)
        checkpoint_file = model_hparams["checkpoint_file"]
        spk_hparams = load_hparams(os.path.join(model_hparams["experiment_folder"], "transformer_encoder_2024-01-28_10:40/hparams.json"), args.debug)
        model_hparams = spk_hparams["model"]
        spk_model = EncoderTransformer(input_dim=model_hparams["sequence_length"],
                                       context_dim=model_hparams["d_context"],
                                       d_model=model_hparams["d_model"],
                                       nhead=model_hparams["n_head"],
                                       num_layers=model_hparams["n_layers"],
                                       dim_feedforward=model_hparams["d_feedforward"])
        spk_model = nn.DataParallel(spk_model)
        spk_model = load_model(checkpoint_file, spk_model)
        pos_model = model
        duo_test(spk_model, pos_model, tst_datagen, tst_pred_folder)

    if args.inference:
        inference_hparams = hparams["inference"]
        inference_data_folder = inference_hparams["inference_data_folder"]
        filename_lst = os.listdir(inference_data_folder)

        # make prediction folder
        inference_pred_folder = os.path.join(
            cur_experiment_folder_path, "inference_pred")
        os.mkdir(inference_pred_folder)

        for filename in filename_lst:
            file_path = os.path.join(inference_data_folder, filename)
            print(file_path)
            inference_dataset = NoLabelSingleFileDataset(
                file_path, model_hparams["sequence_length"])
            inference_datagen = data.DataLoader(
                dataset=inference_dataset,
                batch_size=inference_hparams["batch_size"],
                shuffle=False,
                num_workers=data_hparams["n_worker"])

            inference(model, inference_datagen,
                      filename, inference_pred_folder)
