import os
import torch
import torch.nn as nn
import argparse

__package__ = 'parus.scripts'
from ..model.transformer import EncoderTransformer
from ..train.experiment import load_hparams, setup_experiment, get_all_training_datagen
from ..train.train import train
from ..train.eval import inference
from ..fio import pklz_write


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusModelTrain", description="Train Parus signal model",
                                 epilog="Creat signal separation model for spike detection")
parser.add_argument('-v', '--version', action='version', version="Parus - Train signal model: v1.0")
parser.add_argument('art_dir', type=str, help="[%(type)s] Path to store model training artifacts")
parser.add_argument('dat_dir', type=str, help="[%(type)s] Path to training datasets")
parser.add_argument('hparam', type=str, help="[%(type)s] Path to hyperparameter definition JSON file")
parser.add_argument('-db', '--debug', dest='debug', default=False, action="store_true", help="Run with debug settings")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    # Load hyperparameters from JSON file
    hparams = load_hparams(args.hparam, args.debug)
    model_hparams = hparams["model"]
    data_hparams = hparams["data"]
    train_hparams = hparams["train"]

    # Create experiment folder and save hyperparameters
    cur_art_dir_path, tst_pred_folder = setup_experiment(
        model_hparams["model_name"], data_hparams["dataset_name"], args.art_dir)

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
    model.to(device)

    # Build datagens by discovering .sim files under data folders
    trn_datagen, val_datagen, tst_datagen = get_all_training_datagen(
        data_root_folder=args.dat_dir,
        seq_len=model_hparams["sequence_length"],
        batch_size=train_hparams["batch_size"],
        data_hparams=data_hparams,
    )
    spk_grp = trn_datagen.dataset.meta['grp_str']

    # Train model and save results
    train(model, model_hparams["d_model"], trn_datagen, val_datagen, cur_art_dir_path, train_hparams, device)

    # Create test predictions directory and run testing
    model.eval()
    with torch.no_grad():
        pklz_dct = inference(model, tst_datagen, device, test=True)
        pklz_write(os.path.join(tst_pred_folder, "test_pred.pklz"), pklz_dct)
