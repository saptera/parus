import os
import time
import torch
import torch.nn as nn
import argparse

__package__ = 'parus.scripts'
from ..model.transformer import EncoderTransformer
from ..train.experiment import load_hparams, update_hparams, get_all_training_datagen
from ..train.train import train
from ..train.eval import inference
from ..fio import pklz_write
from ..util import make_outdir


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
    print("Parus model training start")

    # Load hyperparameters from JSON file
    hparams = load_hparams(args.hparam, args.debug)
    model_hparams = hparams["model"]
    data_hparams = hparams["data"]
    train_hparams = hparams["train"]
    print("Hyperparameters successfully loaded")

    # Create working directories for artifacts
    set_name = '__'.join([model_hparams["model_name"], data_hparams["dataset_name"], time.strftime("%Y%m%d-%H%M")])
    work_dir = make_outdir(os.path.join(args.art_dir, set_name), err_msg="Creating working directory failed!")
    tst_dir = make_outdir(os.path.join(work_dir, "tst_prd"), err_msg="Creating test output directory failed!")
    print("Working directories successfully created")

    # Build model and move to device
    print("Building model...")
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
    print("    -> Success!")

    # Build DataGens class
    print("Building data generators...")
    trn_datagen, val_datagen, tst_datagen = get_all_training_datagen(
        data_root_folder=args.dat_dir,
        seq_len=model_hparams["sequence_length"],
        batch_size=train_hparams["batch_size"],
        data_hparams=data_hparams,
    )
    print("    -> Success!")

    # Save extended hyperparameters with source data information
    spk_grp = trn_datagen.dataset.meta['grp_str']
    rec_frq = trn_datagen.dataset.meta['freq']
    hparams["data"]["spike_groups"] = spk_grp
    hparams["data"]["sampling_frequency"] = rec_frq
    update_hparams(hparams, os.path.join(work_dir, 'hparams.json'))
    print("Current hyperparameters saved to working directory")

    # Train model and save checkpoints
    print("\nTraining started")
    train(model, model_hparams["d_model"], trn_datagen, val_datagen, work_dir, train_hparams, device)

    # Create test predictions directory and run testing
    print("\nInferencing test data...")
    model.eval()
    with torch.no_grad():
        pklz_dct = inference(model, tst_datagen, device, test=True)
        pklz_dct['grp'] = spk_grp
        pklz_dct['frq'] = rec_frq
        pklz_write(os.path.join(tst_dir, "test_pred.pklz"), pklz_dct)
    print("    -> Done!")

    print("Parus model training finalized")
