import torch
import torch.nn as nn
import argparse
from parus.model.transformer import EncoderTransformer
from parus.train.experiment import load_hparams, setup_experiment, get_all_training_datagen
from parus.train.train import train
from parus.train.eval import inference

# Parse command line arguments
argParser = argparse.ArgumentParser()
argParser.add_argument(
    "--exp_folder", help="path to experiment folder", type=str, required=True)
argParser.add_argument(
    "--dataset_folder", help="path to dataset folder", type=str, required=True)
argParser.add_argument(
    "--hparams_path", help="path to hparams.json", type=str, required=True)
argParser.add_argument(
    "--debug", help="run training with debug hparams", action="store_true")
args = argParser.parse_args()

if __name__ == '__main__':
    # Load hyperparameters from JSON file
    hparams = load_hparams(args.hparams_path, args.debug)
    model_hparams = hparams["model"]
    data_hparams = hparams["data"]
    train_hparams = hparams["train"]

    # Create experiment folder and save hyperparameters
    cur_exp_folder_path, tst_pred_folder = setup_experiment(
        model_hparams["model_name"], data_hparams["dataset_name"], args.exp_folder)

    # Build model and move to device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = EncoderTransformer(input_dim=model_hparams["sequence_length"],
                            context_dim=model_hparams["d_context"],
                            d_model=model_hparams["d_model"],
                            nhead=model_hparams["n_head"],
                            num_layers=model_hparams["n_layers"],
                            dim_feedforward=model_hparams["d_feedforward"],
                            output_channels=model_hparams["output_channels"])
    model = nn.DataParallel(model)

    # Build datagens by discovering .sim files under data folders
    trn_datagen, val_datagen, tst_datagen = get_all_training_datagen(
        data_root_folder=args.dataset_folder,
        seq_len=model_hparams["sequence_length"],
        batch_size=train_hparams["batch_size"],
        data_hparams=data_hparams,
    )

    # Train model and save results
    train(model, model_hparams["d_model"], trn_datagen, val_datagen, cur_exp_folder_path, train_hparams, device)

    # Create test predictions directory and run testing
    inference(model, tst_datagen, tst_pred_folder, device, mode="tst")

   
