import os
import json
import time
import shutil
import torch
import torch.nn as nn
# import torchvision.ops as tv
import argparse
from torch.utils import data
from parus.model.transformer import EncoderTransformer
from parus.model.peak_cnn import PeakCNN
from parus.train.dataset import LabelledMultipleFileDataset, NoLabelSingleFileDataset, DuoLabelMultipleFileDataset, MultipleLabelMultipleFileDataset, LabelledSingleFileDataset
from parus.train.train import train, cascade_train, load_model
from parus.train.inference import duo_test, test, duo_inference, inference


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


def get_file_datagen(data_file_path, seq_len, batch_size, data_hparams, train_mode="trn"):
    if train_mode == "trn":
        dataset = LabelledSingleFileDataset(data_file_path, data_hparams["n_trn_samples"], seq_len)
    elif train_mode == "val":
        dataset = LabelledSingleFileDataset(data_file_path, data_hparams["n_val_samples"], seq_len)
    elif train_mode == "tst":
        dataset = LabelledSingleFileDataset(data_file_path, data_hparams["n_tst_samples"], seq_len)
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

    
    spk_ckpt = model_hparams["spk_checkpoint_file"]
    print("found spk_ckpt")
    spk_ckpt_hparams = load_hparams(os.path.join(
        model_hparams["experiment_folder"], "transformer_encoder_2024-06-30_18:39/hparams.json"), args.debug)
    spk_model_hparams = spk_ckpt_hparams["model"]
    spk_model = EncoderTransformer(input_dim=spk_model_hparams["sequence_length"],
                                context_dim=spk_model_hparams["d_context"],
                                d_model=spk_model_hparams["d_model"],
                                nhead=spk_model_hparams["n_head"],
                                num_layers=spk_model_hparams["n_layers"],
                                dim_feedforward=spk_model_hparams["d_feedforward"])
    spk_model = nn.DataParallel(spk_model)
    spk_model = load_model(spk_ckpt, spk_model)
    print("loaded spk model")

    pos_model = PeakCNN()

    if args.train:
        train_hparams = hparams["train"]

        # criterion = nn.MSELoss(reduction='mean')
        # criterion = nn.L1Loss(reduction='mean')
        criterion = nn.BCEWithLogitsLoss()
        # criterion = tv.sigmoid_focal_loss
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=train_hparams["learning_rate"])
        
        # def rate(step, model_size, factor, warmup):
        #     if step == 0:
        #         step = 1
        #     rate = factor * (model_size ** (-0.5) * min(step ** (-0.5), step * warmup ** (-1.5)))
        #     if step % 1000 == 0:
        #         print(step, rate)
        #     return rate
        # scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer=optimizer, lr_lambda=lambda step: rate(step, 256, 1, 7000))
        scheduler = torch.optim.lr_scheduler.StepLR(
           optimizer, 1.0, gamma=train_hparams["lr_decay"])

        # get datagen
        trn_folder = os.path.join(data_hparams["data_folder"], "trn")
        trn_datagen = get_file_datagen(os.path.join(trn_folder, "20240630_064841.sim"), model_hparams["sequence_length"], train_hparams["batch_size"], data_hparams, "trn")
        val_folder = os.path.join(data_hparams["data_folder"], "val")
        val_datagen = get_file_datagen(os.path.join(val_folder, "20240630_171849.sim"), model_hparams["sequence_length"], train_hparams["batch_size"], data_hparams, "val")
        tst_folder = os.path.join(data_hparams["data_folder"], "tst")
        tst_datagen = get_file_datagen(os.path.join(tst_folder, "20240630_172006.sim"), model_hparams["sequence_length"], 1, data_hparams, "tst")

        # run experiment with labelled data
        cascade_train(pos_model, spk_model, criterion, optimizer, scheduler, trn_datagen,
              val_datagen, cur_experiment_folder_path, train_hparams)

        # make prediction folder
        tst_pred_folder = os.path.join(
            cur_experiment_folder_path, "test_pred")
        os.mkdir(tst_pred_folder)
        test(model, tst_datagen, tst_pred_folder)

    if args.inference:
        inference_hparams = hparams["inference"]
        inference_data_folder = inference_hparams["inference_data_folder"]
        filename_lst = os.listdir(inference_data_folder)

        # make prediction folder
        inference_pred_folder = os.path.join(
            cur_experiment_folder_path, "inference_pred")
        os.mkdir(inference_pred_folder)
        print("made inference")

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

            duo_inference(model, inference_datagen,
                      filename, inference_pred_folder)
