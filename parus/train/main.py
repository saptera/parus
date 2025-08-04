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
from parus.train.dataset import LabelledMultipleFileDataset, NoLabelSingleFileDataset, DuoLabelMultipleFileDataset, MultipleLabelMultipleFileDataset, LabelledSingleFileDataset
from parus.train.train import train, cascade_train, load_model
from parus.train.inference import duo_test, test, duo_inference, inference

"""Function list:
load_hparams(hparams_file_path, debug): Load hyperparameters from JSON file with optional debug mode
get_file_datagen(data_file_path, seq_len, batch_size, data_hparams, train_mode): Create data generator for training/validation/testing
setup_experiment(model_name, experiment_folder_path): Create experiment directory and copy hyperparameters
"""

def load_hparams(hparams_file_path='hparams.json', debug=False):
    """Load hyperparameters from JSON file with optional debug mode.

    Args:
        hparams_file_path (str): Path to hyperparameters JSON file (default: 'hparams.json')
        debug (bool): Whether to use debug hyperparameters (default: False)

    Returns:
        dict: Loaded hyperparameters
    """
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
    """Create data generator for training/validation/testing.

    Args:
        data_file_path (str): Path to data file
        seq_len (int): Sequence length for model input
        batch_size (int): Batch size for data loading
        data_hparams (dict): Data hyperparameters
        train_mode (str): Mode of operation - "trn", "val", or "tst" (default: "trn")

    Returns:
        DataLoader: PyTorch data loader object
    """
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
    """Create experiment directory and copy hyperparameters.

    Args:
        model_name (str): Name of the model
        experiment_folder_path (str): Path to experiments folder

    Returns:
        str: Path to current experiment folder
    """
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
    # Parse command line arguments
    argParser = argparse.ArgumentParser()
    argParser.add_argument(
        "--debug", help="run training with debug hparams", action="store_true")
    argParser.add_argument(
        "--train", help="run training", action="store_true")
    argParser.add_argument(
        "--inference", help="run inference", action="store_true")
    args = argParser.parse_args()

    # Load hyperparameters from JSON file
    hparams = load_hparams("hparams.json", args.debug)
    model_hparams = hparams["model"]
    data_hparams = hparams["data"]
    inference_hparams = hparams["inference"]

    # Create experiment folder and save hyperparameters
    cur_experiment_folder_path = setup_experiment(
        model_hparams["model_name"], model_hparams["experiment_folder"])
    
    model = None
    # spk_ckpt = model_hparams["spk_checkpoint_file"]
    # print("found spk_ckpt")
    # spk_ckpt_hparams = load_hparams(os.path.join(
    #     model_hparams["experiment_folder"], "transformer_encoder_2024-06-30_18:39/hparams.json"), args.debug)
    # spk_model_hparams = spk_ckpt_hparams["model"]
    # spk_model = EncoderTransformer(input_dim=spk_model_hparams["sequence_length"],
    #                             context_dim=spk_model_hparams["d_context"],
    #                             d_model=spk_model_hparams["d_model"],
    #                             nhead=spk_model_hparams["n_head"],
    #                             num_layers=spk_model_hparams["n_layers"],
    #                             dim_feedforward=spk_model_hparams["d_feedforward"],
    #                             output_channels=1)
    # spk_model = nn.DataParallel(spk_model)
    # spk_model = load_model(spk_ckpt, spk_model)
    # print("loaded spk model")

    # pos_ckpt = model_hparams["pos_checkpoint_file"]
    # print("found pos_ckpt")
    # pos_ckpt_hparams = load_hparams(os.path.join(
    #     model_hparams["experiment_folder"], "transformer_encoder_2024-10-06_17:56/hparams.json"), args.debug)
    # pos_model_hparams = pos_ckpt_hparams["model"]
    # pos_model = EncoderTransformer(input_dim=pos_model_hparams["sequence_length"],
    #                             context_dim=pos_model_hparams["d_context"],
    #                             d_model=pos_model_hparams["d_model"],
    #                             nhead=pos_model_hparams["n_head"],
    #                             num_layers=pos_model_hparams["n_layers"],
    #                             dim_feedforward=pos_model_hparams["d_feedforward"],
    #                             output_channels=1)
    # pos_model = nn.DataParallel(pos_model)
    # pos_model = load_model(pos_ckpt, pos_model)
    # print("loaded pos model")

    if args.train:
        model = EncoderTransformer(input_dim=model_hparams["sequence_length"],
                                context_dim=model_hparams["d_context"],
                                d_model=model_hparams["d_model"],
                                nhead=model_hparams["n_head"],
                                num_layers=model_hparams["n_layers"],
                                dim_feedforward=model_hparams["d_feedforward"],
                                output_channels=1)

        train_hparams = hparams["train"]

        # criterion = nn.MSELoss(reduction='mean')
        criterion = nn.L1Loss(reduction='mean')
        # criterion = nn.BCEWithLogitsLoss()
        # criterion = tv.sigmoid_focal_loss
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=train_hparams["learning_rate"])
        
        def rate(step, model_size, factor, warmup):
            if step == 0:
                step = 1
            rate = factor * (model_size ** (-0.5) * min(step ** (-0.5), step * warmup ** (-1.5)))
            if step % 1000 == 0:
                print(step, rate)
            return rate
        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer=optimizer, lr_lambda=lambda step: rate(step, 256, 1, 7000))
        # scheduler = torch.optim.lr_scheduler.StepLR(
        #    optimizer, 1.0, gamma=train_hparams["lr_decay"])

        # Create data generators for training, validation and testing
        trn_folder = os.path.join(data_hparams["data_folder"], "trn")
        trn_datagen = get_file_datagen(os.path.join(trn_folder, "20250804_035526.sim"), 
                                     model_hparams["sequence_length"], 
                                     train_hparams["batch_size"], 
                                     data_hparams, "trn")
        val_folder = os.path.join(data_hparams["data_folder"], "val")
        val_datagen = get_file_datagen(os.path.join(val_folder, "20250804_070005.sim"), model_hparams["sequence_length"], train_hparams["batch_size"], data_hparams, "val")
        tst_folder = os.path.join(data_hparams["data_folder"], "tst")
        tst_datagen = get_file_datagen(os.path.join(tst_folder, "20250804_070109.sim"), model_hparams["sequence_length"], 1, data_hparams, "tst")

        # Train model and save results
        train(model, criterion, optimizer, scheduler, trn_datagen,
              val_datagen, cur_experiment_folder_path, train_hparams)

        # Create test predictions directory and run testing
        tst_pred_folder = os.path.join(cur_experiment_folder_path, "test_pred")
        os.mkdir(tst_pred_folder)
        test(model, tst_datagen, tst_pred_folder)

    if args.inference:
        spk_ckpt = inference_hparams["spk_ckpt"]
        print("found spk_ckpt")
        spk_ckpt_hparams = load_hparams(os.path.join(inference_hparams["spk_ckpt_folder"], "hparams.json"), args.debug)
        spk_model_hparams = spk_ckpt_hparams["model"]
        model = EncoderTransformer(input_dim=spk_model_hparams["sequence_length"],
                                    context_dim=spk_model_hparams["d_context"],
                                    d_model=spk_model_hparams["d_model"],
                                    nhead=spk_model_hparams["n_head"],
                                    num_layers=spk_model_hparams["n_layers"],
                                    dim_feedforward=spk_model_hparams["d_feedforward"],
                                    output_channels=1)
        model = nn.DataParallel(model)
        model = load_model(spk_ckpt, model)
        print("loaded spk model")

        # Run inference on new data
        inference_data_folder = inference_hparams["inference_data_folder"]
        filename_lst = os.listdir(inference_data_folder)

        # Create inference predictions directory
        inference_pred_folder = os.path.join(
            cur_experiment_folder_path, "inference_pred")
        os.mkdir(inference_pred_folder)

        # Process each file in the inference folder
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

            duo_inference(model, model, inference_datagen,
                      filename, inference_pred_folder)
