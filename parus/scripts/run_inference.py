import os
import torch
import torch.nn as nn
from torch.utils import data
import argparse

__package__ = 'parus.scripts'
from ..model.transformer import EncoderTransformer
from ..train.dataset import InferenceDataset
from ..train.experiment import setup_workdir, load_hparams, load_model
from ..train.eval import inference
from ..fio import pklz_write


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusDatInf", description="Parus data inference",
                                 epilog="Inference raw recoding data and perform spike detection")
parser.add_argument('-v', '--version', action='version', version="Parus - Data inference: v1.0")
parser.add_argument('ckpt', type=str, help="[%(type)s] Absolute path to pre-trained model checkpoint")
parser.add_argument('inf_dat', type=str, help="[%(type)s] Path to recoding data to be processed")
parser.add_argument('out_dir', type=str, help="[%(type)s] Path to store results")
parser.add_argument('-bs', '--batch', dest='bat_sz', type=int, default=1, metavar="[int]",
                    help="Processing batch size (default: %(default)s)")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    # Create experiment folder and save hyperparameters
    dataset_name = os.path.basename(args.inf_dat)
    cur_out_dir_path, inf_pred_folder = setup_workdir("inf", dataset_name, args.out_dir, train=False)
    
    # Locate pre-trained model for inference
    if os.path.isfile(args.ckpt):
        print(f"Model located at {args.ckpt}")
    else:
        raise FileNotFoundError("Cannot find model checkpoint at defined path!")
    # Locate model hyperparameters
    hparam_file = os.path.join(os.path.dirname(args.ckpt), "hparams.json")
    if os.path.isfile(hparam_file):
        hparams = load_hparams(hparam_file)
        print(f"Hyperparameters loaded from {hparam_file}")
        model_hparams = hparams["model"]
        print(f"Current model hyperparameters: {model_hparams}")
        # Load data information
        spk_grp = hparams["data"]["spike_groups"]
        rec_frq = hparams["data"]["sampling_frequency"]
    else:
        raise FileNotFoundError("Model hyperparameter missing!\n"
                                "[hparams.json] file must be located in the same folder as defined model checkpoint.")

    # Build model
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
    print(f"Model successfully loaded!")

    # Run inference on new data
    inf_dat = args.inf_dat
    filename_lst = os.listdir(inf_dat)

    # Process each file in the inference folder
    model.eval()
    with torch.no_grad():
        for filename in filename_lst:
            file_path = os.path.join(inf_dat, filename)
            print(f"Processing {file_path}")
            inf_dataset = InferenceDataset(file_path, model_hparams["sequence_length"])
            inf_datagen = data.DataLoader(
                dataset=inf_dataset,
                batch_size=args.bat_sz,
                shuffle=False,
                num_workers=model_hparams["n_worker"])

            pklz_dct = inference(model, inf_datagen, device)
            pklz_dct['grp'] = spk_grp
            pklz_dct['frq'] = rec_frq
            pklz_write(os.path.join(inf_pred_folder, filename), pklz_dct)
