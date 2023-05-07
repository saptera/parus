import os
import json
import time
import shutil
import torch
import torch.nn as nn
from parus.model.temporal_transformer import TemporalTransformer
from parus.train.datagen import get_train_datagen, get_val_datagen, get_test_datagen
from parus.train.train import train
from parus.train.inference import inference

if __name__ == '__main__':
    hparams_file = open('hparams.json')
    hparams = json.load(hparams_file)
    print(hparams)
    train_data_hparams = {'batch_size': hparams["batch_size"],
                          'shuffle': True,
                          'num_workers': 10}

    test_data_hparams = {'batch_size': 1,
                         'shuffle': False,
                         'num_workers': 1}

    data_folder_path = hparams["data_folder"]
    sequence_length = hparams["sequence_length"]

    train_datagen = get_train_datagen(
        os.path.join(data_folder_path, "trn"), sequence_length, train_data_hparams)
    val_datagen = get_val_datagen(
        os.path.join(data_folder_path, "val"), sequence_length, train_data_hparams)
    test_datagen = get_test_datagen(
        os.path.join(data_folder_path, "tst"), sequence_length, test_data_hparams)

    # setup experiments folder
    experiment_name = "_".join(
        [hparams["model_name"], time.strftime("%Y-%m-%d_%H:%M")])
    experiment_folder_path = os.path.join(
        hparams["experiment_folder"], experiment_name)
    os.mkdir(experiment_folder_path)
    print("Directory '% s' created" % experiment_folder_path)
    shutil.copy2('hparams.json', experiment_folder_path)
    print("Copied hparams.json to '% s' " % experiment_folder_path)

    train_hparams = {'epoch': hparams["epoch"],
                     'model_param_clip': hparams["model_param_clip"],
                     'steps_every_print': hparams["steps_every_print"],
                     'experiment_folder_path': experiment_folder_path,
                     'model_name': hparams["model_name"]}

    test_hparams = {
        'experiment_folder_path': experiment_folder_path}

    # sequence_length, embedding_dim, n_head, n_stack
    model = TemporalTransformer(300, 16, 4, 6)
    criterion = nn.L1Loss(reduction='mean')
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=hparams["learning_rate"])
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, 1.0, gamma=hparams["lr_decay"])

    train(model, criterion, optimizer, scheduler,
          train_datagen, val_datagen, train_hparams)
    inference(model, test_datagen, test_hparams)
