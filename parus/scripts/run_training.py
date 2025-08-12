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
    print("Parus model training starting")
    dat_name = os.path.basename(args.dat_dir.rstrip('/\\'))

    # Load hyperparameters from JSON file
    hparams = load_hparams(args.hparam, args.debug)
    print("Hyperparameters successfully loaded")

    # Create working directories for artifacts
    set_name = '__'.join([hparams["model"]["model_name"], dat_name, time.strftime("%Y%m%d-%H%M")])
    work_dir = make_outdir(os.path.join(args.art_dir, set_name), err_msg="Creating working directory failed!")
    tst_dir = make_outdir(os.path.join(work_dir, "tst_prd"), err_msg="Creating test output directory failed!")
    print("Working directories successfully created")

    # Build DataGens class
    print("Building data generators...")
    data_hprams = hparams["data"].copy()  # Make a copy of data hyperparameters, do not store further changes
    # Check multiprocessing context
    try:
        torch.multiprocessing.set_start_method('fork')
    except ValueError:
        torch.multiprocessing.set_start_method('spawn')
        data_hprams["n_worker"] = 0  # Disable multiprocess, keep original settings, inference not affected
        print("    Unable to multiprocess DataLoader, data will be loaded in the main process")
    # Creat all needed classes
    trn_datagen, val_datagen, tst_datagen = get_all_training_datagen(
        data_root_folder=args.dat_dir,
        seq_len=hparams["model"]["sequence_length"],
        batch_size=hparams["train"]["batch_size"],
        data_hparams=data_hprams,
    )
    print("    -> Success!")

    # Get extended hyperparameters with source data information
    spk_grp = trn_datagen.dataset.meta['grp_str']
    rec_frq = trn_datagen.dataset.meta['freq']
    hparams["data"]["dataset_name"] = dat_name
    hparams["data"]["spike_groups"] = spk_grp
    hparams["data"]["sampling_frequency"] = rec_frq
    hparams["model"]["output_channels"] = len(spk_grp)
    # Write hyperparameter JSON file
    update_hparams(hparams, os.path.join(work_dir, 'hparams.json'))
    print("Current hyperparameters saved to working directory")

    # Build model and move to device
    print("Building model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = EncoderTransformer(input_dim=hparams["model"]["sequence_length"],
                               context_dim=hparams["model"]["d_context"],
                               d_model=hparams["model"]["d_model"],
                               nhead=hparams["model"]["n_head"],
                               num_layers=hparams["model"]["n_layers"],
                               dim_feedforward=hparams["model"]["d_feedforward"],
                               output_channels=hparams["model"]["output_channels"])
    model = nn.DataParallel(model)
    model.to(device)
    print("    -> Success!")

    # Train model and save checkpoints
    print("\nTraining started")
    train(model, hparams["model"]["d_model"], trn_datagen, val_datagen, work_dir, hparams["train"], device)

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
