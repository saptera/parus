# -*- coding: utf-8 -*-

"""PARUS model training script

Train a PARUS signal-separation model on a simulated dataset, periodically validate it, and run a final testing pass.
Hyperparameters can be overridden one-by-one on the command line; unspecified ones fall
back to the project's persisted defaults.
"""

import os
import time
import torch
import torch.nn as nn
import argparse

__package__ = 'parus.scripts'
from .. import pkg_data
from ..fio import pklz_write
from ..model import EncoderTransformer, load_hparams, save_hparams, load_all_datasets, train, load_model, testing
from ..util import make_outdir


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusModTrn", description="Train PARUS signal model",
                                 epilog="Train signal-separation model for spike detection")
parser.add_argument('-v', '--version', action='version', version="Parus - Train signal model: v2.6")
# Path definition (positional)
parser.add_argument('art_dir', type=str, help="[%(type)s] Output directory for training artifacts")
parser.add_argument('dat_dir', type=str, help="[%(type)s] Directory containing the training datasets")
# Dataset hyperparameters (optional)
pg_d = parser.add_argument_group("Dataset arguments")
pg_d.add_argument('-dtn', '--smptrn', dest='n_trn_samples', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Number of samples for training")
pg_d.add_argument('-dvl', '--smpvld', dest='n_vld_samples', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Number of samples for validation")
pg_d.add_argument('-dts', '--smptst', dest='n_tst_samples', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Number of samples for testing")
pg_d.add_argument('-dwk', '--numwkr', dest='n_worker', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Worker thread count for dataset loading")
# Model definitions (optional)
pg_m = parser.add_argument_group("Model definitions")
pg_m.add_argument('-mid', '--modstr', dest='model_name', type=str, default=argparse.SUPPRESS, metavar="[str]",
                  help="Trained model name")
pg_m.add_argument('-mls', '--lenseq', dest='sequence_length', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Model sequence length")
pg_m.add_argument('-mdc', '--dimctx', dest='d_context', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Context loader element count")
pg_m.add_argument('-mdm', '--dimmod', dest='d_model', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Expected input feature count")
pg_m.add_argument('-mnh', '--nummhd', dest='n_head', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Multi-head attention head count")
pg_m.add_argument('-mnl', '--numlyr', dest='n_layers', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Sub-encoder layer count")
pg_m.add_argument('-mdf', '--dimffd', dest='d_feedforward', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Feed-forward network dimension")
# Training settings (optional)
pg_t = parser.add_argument_group("Training settings")
pg_t.add_argument('-tep', '--numeps', dest='total_epoch', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Total training epochs")
pg_t.add_argument('-tbs', '--szsbat', dest='batch_size', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Training batch size")
pg_t.add_argument('-tev', '--stpevl', dest='steps_per_eval', type=int, default=argparse.SUPPRESS, metavar="[int]",
                  help="Steps between validations")
pg_t.add_argument('-tlr', '--lrbase', dest='base_learning_rate', type=float, default=argparse.SUPPRESS,
                  metavar="[float]", help="Base learning rate")
pg_t.add_argument('-tlf', '--lrfact', dest='learning_rate_factor', type=float, default=argparse.SUPPRESS,
                  metavar="[float]", help="Dynamic learning-rate factor")
pg_t.add_argument('-tlw', '--lrwarm', dest='learning_rate_warmup', type=int, default=argparse.SUPPRESS,
                  metavar="[int]", help="Learning-rate warm-up steps")
pg_t.add_argument('-tpc', '--prmclp', dest='model_param_clip', type=float, default=argparse.SUPPRESS,
                  metavar="[float]", help="Gradient-norm clip value")
pg_t.add_argument('-tls', '--lossfn', dest='loss_function', type=str, choices=['l1', 'mse', 'bce'],
                  default=argparse.SUPPRESS, metavar="{mse, l1, bce}",
                  help="Loss function (l1: MAE, mse: MSE, bce: BCE with sigmoid)")
# Extra options
parser.add_argument('-pth', '--pkdths', dest='pk_th', type=float, default=-50.0, metavar="[float]",
                    help="Post-inference peak threshold (default: %(default)s)")
parser.add_argument('-t', '--hint', dest='hint', type=str, choices=['text', 'disp', 'save', 'none'], default='text',
                    metavar="{text, disp, save, none}", help="Validation snapshot mode (default: %(default)s)")
parser.add_argument('-d', '--debug', dest='debug', default=False, action="store_true", help="Run with debug settings")
# Parse inputs
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    print("PARUS model training script initialized at " + time.strftime('%Y-%m-%d %H:%M:%S'))
    dat_name = os.path.basename(args.dat_dir.rstrip('/\\'))

    # Load and update hyperparameters
    hparams = load_hparams(os.path.join(pkg_data, '_hparams.json'), debug=args.debug)
    hparams['data'].update({k: args.__dict__[k] for k in hparams['data'] if k in args})
    hparams['model'].update({k: args.__dict__[k] for k in hparams['model'] if k in args})
    hparams['train'].update({k: args.__dict__[k] for k in hparams['train'] if k in args})
    print("Hyperparameters successfully loaded")

    # Create working directories for artifacts
    set_name = '__'.join([hparams['model']['model_name'], dat_name, time.strftime('%Y%m%d-%H%M')])
    work_dir = make_outdir(os.path.join(args.art_dir, set_name), err_msg="Creating working directory failed!")
    print("Working directory successfully created")

    # Build data loaders class
    print("Building data generators...")
    # Creat all needed classes
    trn_datagen, vld_datagen, tst_datagen = load_all_datasets(
        dataset_dir=args.dat_dir,
        seq_len=hparams['model']['sequence_length'],
        batch_size=hparams['train']['batch_size'],
        data_hparams=hparams['data']
    )
    print("    -> Success!")

    # Get extended hyperparameters with source data information
    spk_grp = trn_datagen.dataset.meta['grp_str']
    rec_frq = trn_datagen.dataset.meta['freq']
    hparams['data']['dataset_name'] = dat_name
    hparams['data']['spike_groups'] = spk_grp
    hparams['data']['sampling_frequency'] = rec_frq
    hparams['model']['output_channels'] = len(spk_grp)
    # Write root hyperparameter file for next run
    if not args.debug:
        save_hparams(os.path.join(pkg_data, '_hparams.json'), hparams)
    # Update sample numbers to actual value
    hparams['data']['n_trn_samples'] = trn_datagen.dataset.n_sample
    hparams['data']['n_vld_samples'] = vld_datagen.dataset.n_sample
    hparams['data']['n_tst_samples'] = tst_datagen.dataset.n_sample
    # Write current model hyperparameter for future loading
    save_hparams(os.path.join(work_dir, 'hparams.json'), hparams)
    print("Current hyperparameters saved")

    # Build model and move to device
    print("Building model...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = EncoderTransformer(input_dim=hparams['model']['sequence_length'],
                               context_dim=hparams['model']['d_context'],
                               d_model=hparams['model']['d_model'],
                               nhead=hparams['model']['n_head'],
                               num_layers=hparams['model']['n_layers'],
                               dim_feedforward=hparams['model']['d_feedforward'],
                               output_channels=hparams['model']['output_channels'])
    model = nn.DataParallel(model)
    model.to(device)
    print("    -> Success!")

    # Train model and save checkpoints
    print("\nTraining started")
    train(model, hparams['model']['d_model'], trn_datagen, vld_datagen, work_dir, hparams['train'], device, args.hint)

    # Run testing for final model
    print("\nInferencing test data with final model...")
    model.eval()
    with torch.no_grad():
        pklz_dct = testing(model, tst_datagen, hparams['model']['output_channels'], device, th=args.pk_th)
        pklz_dct['grp'] = spk_grp
        pklz_dct['frq'] = rec_frq
        pklz_write(os.path.join(work_dir, "tst_fin.pklz"), pklz_dct)
    print("    -> Done!")
    print("Inferencing test data with optimum model...")
    # Run testing for optimum model
    model = load_model(os.path.join(work_dir, "optimum.ckpt"), model, remap=device)  # Override with optimum checkpoint
    model.eval()
    with torch.no_grad():
        pklz_dct = testing(model, tst_datagen, hparams['model']['output_channels'], device, th=args.pk_th)
        pklz_dct['grp'] = spk_grp
        pklz_dct['frq'] = rec_frq
        pklz_write(os.path.join(work_dir, "tst_opt.pklz"), pklz_dct)
    print("    -> Done!")
    # Close test dataset
    tst_datagen.dataset.close()

    print("PARUS model training finalized at " + time.strftime('%Y-%m-%d %H:%M:%S'))
