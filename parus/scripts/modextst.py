import os
import time
import torch
import torch.nn as nn
from torch.utils import data
import argparse

__package__ = 'parus.scripts'
from ..model.transformer import EncoderTransformer
from ..train.dataset import TrainingDataset
from ..train.experiment import load_hparams, load_model
from ..train.eval import inference
from ..fio import pklz_write
from ..util import make_outdir


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusModExTst", description="Parus model checkpoint extra test",
                                 epilog="Evaluate model checkpoint performance with extra test dataset")
parser.add_argument('-v', '--version', action='version', version="Parus - Model extra test: v1.0")
parser.add_argument('ckpt', type=str, help="[%(type)s] Absolute path to pre-trained model checkpoint")
parser.add_argument('dset', type=str, help="[%(type)s] Path to test dataset")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    print("Parus model extra data test starting")

    # Locate required files
    if os.path.isfile(args.ckpt):
        print("Model located at [%s]" % args.ckpt)
        ckpt_path, full_name = os.path.split(args.ckpt)
        ckpt_name = os.path.splitext(full_name)[0]
    else:
        raise FileNotFoundError("Cannot find model checkpoint at defined path!")
    if os.path.isfile(args.dset):
        dset_name = os.path.splitext(os.path.basename(args.dset))[0]
    else:
        raise FileNotFoundError("Cannot find test dataset at defined path!")
    # Locate output folder
    out_dir = make_outdir(os.path.join(ckpt_path, "tst_prd/"))
    out_dat = '_'.join(['tst', ckpt_name, dset_name, time.strftime("%Y%m%dT%H%M") + '.pklz'])
    # Locate model hyperparameters
    hparam_file = os.path.join(ckpt_path, "hparams.json")
    if os.path.isfile(hparam_file):
        hparams = load_hparams(hparam_file)
        print("Hyperparameters loaded from [%s]" % hparam_file)
        model_hparams = hparams["model"]
        print(f"Current model hyperparameters: {model_hparams}")
    else:
        raise FileNotFoundError("Model hyperparameter missing!\n"
                                "[hparams.json] file must be located in the same folder as defined model checkpoint.")

    # Check multiprocessing context
    try:
        torch.multiprocessing.set_start_method('fork')
        n_worker = hparams["data"]["n_worker"]
    except ValueError:
        torch.multiprocessing.set_start_method('spawn')
        n_worker = 0
    # Load test dataset
    dataset = TrainingDataset(args.dset, hparams["data"]["n_tst_samples"], hparams["model"]["sequence_length"])
    datagen = data.DataLoader(dataset, hparams["train"]["batch_size"], shuffle=False, num_workers=n_worker)

    # Build model
    print("Loading model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = EncoderTransformer(input_dim=model_hparams["sequence_length"],
                               context_dim=model_hparams["d_context"],
                               d_model=model_hparams["d_model"],
                               nhead=model_hparams["n_head"],
                               num_layers=model_hparams["n_layers"],
                               dim_feedforward=model_hparams["d_feedforward"],
                               output_channels=model_hparams["output_channels"])
    model = nn.DataParallel(model)
    model = load_model(args.ckpt, model)
    model.to(device)
    print("    -> Success!")

    # Process extra tests
    print("Inferencing test data...")
    model.eval()
    with torch.no_grad():
        pklz_dct = inference(model, datagen, device, test=True)
        pklz_dct['grp'] = hparams["data"]["spike_groups"]
        pklz_dct['frq'] = hparams["data"]["sampling_frequency"]
        pklz_write(os.path.join(out_dir, out_dat), pklz_dct)
    print("    -> Done!")
    print("Parus model checkpoint extra test finalized")
