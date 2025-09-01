import os
import time
import torch
import torch.nn as nn
from torch.utils import data
import argparse

__package__ = 'parus.scripts'
from ..model.transformer import EncoderTransformer
from ..train.dataset import InferenceDataset
from ..train.experiment import load_hparams, load_model
from ..train.eval import inference
from ..fio import pklz_write
from ..util import make_outdir


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusDatInf", description="Parus data inference",
                                 epilog="Inference raw recoding data and perform spike detection")
parser.add_argument('-v', '--version', action='version', version="Parus - Data inference: v1.0")
parser.add_argument('ckpt', type=str, help="[%(type)s] Absolute path to pre-trained model checkpoint")
parser.add_argument('src_dir', type=str, help="[%(type)s] Path to recoding data to be processed")
parser.add_argument('out_dir', type=str, help="[%(type)s] Path to store results")
parser.add_argument('-bs', '--batch', dest='bat_sz', type=int, default=1, metavar="[int]",
                    help="Processing batch size (default: %(default)s)")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    print("Parus data inference starting")

    # Create output directory
    dat_name = os.path.basename(args.src_dir.rstrip('/\\'))
    out_name = '_'.join(['inf', dat_name, time.strftime("%Y%m%d-%H%M")])
    out_dir = make_outdir(os.path.join(args.out_dir, out_name), err_msg="Creating output directory failed!")
    print("Results output directory successfully created")

    # Locate pre-trained model for inference
    if os.path.isfile(args.ckpt):
        print("Model located at [%s]" % args.ckpt)
    else:
        raise FileNotFoundError("Cannot find model checkpoint at defined path!")

    # Locate model hyperparameters
    hparam_file = os.path.join(os.path.dirname(args.ckpt), "hparams.json")
    if os.path.isfile(hparam_file):
        hparams = load_hparams(hparam_file)
        print("Hyperparameters loaded from [%s]" % hparam_file)
        model_hparams = hparams["model"]
        print(f"Current model hyperparameters: {model_hparams}")
        # Load data information
        spk_grp = hparams["data"]["spike_groups"]
        rec_frq = hparams["data"]["sampling_frequency"]
    else:
        raise FileNotFoundError("Model hyperparameter missing!\n"
                                "[hparams.json] file must be located in the same folder as defined model checkpoint.")

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

    # Process each file in the inference folder
    filename_lst = [f for f in os.listdir(args.src_dir) if f.endswith('.sig')]
    tot_len = len(filename_lst)
    print("Inferencing data:")
    model.eval()
    with torch.no_grad():
        for i, filename in enumerate(filename_lst):
            file_path = os.path.join(args.src_dir, filename)
            # Model inference
            t_init = time.time()  # Start time
            inf_dataset = InferenceDataset(file_path, model_hparams["sequence_length"], overlap=10)
            inf_datagen = data.DataLoader(
                dataset=inf_dataset,
                batch_size=args.bat_sz,
                shuffle=False,
                num_workers=hparams["data"]["n_worker"])
            pklz_dct = inference(model, inf_datagen, device)
            t_stop = time.time()
            # Add metadata and save output
            pklz_dct['grp'] = spk_grp
            pklz_dct['frq'] = inf_dataset.frq
            pklz_dct['overlap'] = inf_dataset.overlap
            pklz_dct['padsize'] = inf_dataset.pad
            pklz_write(os.path.join(out_dir, filename), pklz_dct)
            # CLI print
            dur = t_stop - t_init
            print("    File [%s] processed in %.4f seconds (%d/%d)" % (filename, dur, i + 1, tot_len))

    print("Parus data inference finalized")
