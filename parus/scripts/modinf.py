import os
import time
import h5py as h5
import numpy as np
import torch
import torch.nn as nn
from torch.utils import data
import argparse
import warnings

__package__ = 'parus.scripts'
from ..model import EncoderTransformer, InferenceDataset, load_hparams, load_model, inference
from ..data import sig_merge
from ..util import make_outdir


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusDatInf", description="Parus data inference",
                                 epilog="Inference raw recoding data with trained model")
parser.add_argument('-v', '--version', action='version', version="Parus - Data inference: v2.0")
# Model definition (positional)
parser.add_argument('ckpt', type=str, help="[%(type)s] Absolute path to pre-trained model checkpoint")
# File IO arguments (optional, but at least one file/directory should be defined)
pg_io = parser.add_argument_group("Data IO arguments")
pg_io.add_argument('-f', '--file', dest='file', nargs='+', type=str, default=argparse.SUPPRESS, metavar="[str]",
                   help="List of files (*.sig, *.pkl, *.pklz) to inference")
pg_io.add_argument('-d', '--dirs', dest='dirs', nargs='+', type=str, default=argparse.SUPPRESS, metavar="[str]",
                   help="List of directories containing signals (*.sig, *.pkl, *.pklz) to inference")
pg_io.add_argument('-o', '--out', dest='out', type=str, default=argparse.SUPPRESS, metavar="[str]",
                   help="Output directory, store at the same directory as the input files if undefined")
# Data process arguments (optional)
pg_dt = parser.add_argument_group("Data process arguments")
pg_dt.add_argument('-lp', '--overlap', dest='overlap', type=int, default=10, metavar="[int]",
                   help="Overlapping size between each sample step (default: %(default)s)")
pg_dt.add_argument('-bs', '--batch', dest='bat_sz', type=int, default=2048, metavar="[int]",
                   help="Processing batch size, greater value will make process faster at a cost of larger VRAM usage "
                        "(default: %(default)s)")
pg_dt.add_argument('-cp', '--compress', dest='cmp_lvl', type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], default=4,
                   metavar="[int(0-9)]", help="Output file compression level (default: %(default)s)")
# Parse inputs
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    print("Parus model inference script initialized at %s\n" % time.strftime('%Y-%m-%d %H:%M:%S'))

    # Get IO items --------------------------------------------------------------------------------------------------- #
    print("Preparing IO files and directories:")
    # Get output directory
    if 'out' in args:
        print("    Creating defined output directory....")
        out_dir = make_outdir(args.out, err_msg="    Creating output directory failed!")
        print("        -> Results output directory successfully created")
    else:
        out_dir = None
    # Initialize IO list
    src_lst = []
    dst_lst = []

    # Get list of input files
    if 'file' in args:
        print("    Checking input files...")
        name_chk = []  # INIT VAR
        for f in args.file:
            if os.path.isfile(f) and f.endswith(('.sig', '.pkl' '.pklz')):
                src_lst.append(f.replace('\\', '/'))
                # Get file parts
                base, name = os.path.split(f)
                name, ext = os.path.splitext(name)
                # Get output file name
                if out_dir is None:
                    dst_lst.append(os.path.join(base, 'inf_' + name + '.h5').replace('\\', '/'))
                else:
                    # Check name conflicts
                    n = 0
                    while name in name_chk:
                        n += 1
                        name += '_%03d' % n
                    # Update lists
                    name_chk.append(name)
                    dst_lst.append(os.path.join(out_dir, 'inf_' + name+ '.h5').replace('\\', '/'))
            else:
                warnings.warn("File [%s] is invalid for process" % f, RuntimeWarning, stacklevel=1)
        print("        -> All valid files have been added to process")

    # Get list of files in the input directory
    if 'dirs' in args:
        print("    Checking input directories...")
        name_chk = []  # INIT VAR
        for d in args.dirs:
            if os.path.isdir(d):
                src_lst += [os.path.join(d, f).replace('\\', '/')
                            for f in os.listdir(d) if f.endswith(('.sig', '.pkl' '.pklz'))]
                # Get directory path and name
                if out_dir is None:
                    dst_lst += [os.path.join(d, 'inf_' + f).replace('\\', '/')
                                for f in os.listdir(d) if f.endswith(('.sig', '.pkl' '.pklz'))]
                else:
                    base, name = os.path.split(d.rstrip('/\\'))
                    # Check name conflicts
                    n = 0
                    while name in name_chk:
                        n += 1
                        name += '_%03d' % n
                    name_chk.append(name)
                    # Get output target
                    od = make_outdir(os.path.join(out_dir, name), err_msg="        Failed to make folder [%s]" % name)
                    dst_lst += [os.path.join(od, 'inf_' + os.path.splitext(f)[0] + '.h5').replace('\\', '/')
                                for f in os.listdir(d) if f.endswith(('.sig', '.pkl' '.pklz'))]
            else:
                warnings.warn("Cannot locate directory [%s]" % d, RuntimeWarning, stacklevel=1)
        print("        -> All valid directories and their files have been added to process")

    # Check number of input files
    if src_lst:
        print("Files have been located successfully\n")
    else:
        print("No valid files to process, system out!")
        exit(0)

    # Loading pre-trained model -------------------------------------------------------------------------------------- #
    print("Loading model for inference:")
    if os.path.isfile(args.ckpt):
        print("    Pretrained weights located at [%s]" % args.ckpt.replace('\\', '/'))
    else:
        raise FileNotFoundError("Cannot find model checkpoint at defined path!")

    # Locate model hyperparameters
    hparam_file = os.path.join(os.path.dirname(args.ckpt), 'hparams.json')
    if os.path.isfile(hparam_file):
        hparams = load_hparams(hparam_file)
        print("    Hyperparameters loaded from [%s]" % hparam_file.replace('\\', '/'))
        model_hparams = hparams['model']
        # Load data information
        spk_grp = hparams['data']['spike_groups']
        rec_frq = hparams['data']['sampling_frequency']
    else:
        raise FileNotFoundError("Model hyperparameter missing!\n"
                                "[hparams.json] file must be located in the same folder as defined model checkpoint.")

    # Check sampling arguments
    if args.overlap >= model_hparams['sequence_length']:
        raise ValueError("Sample overlap size must be less than model sequence length!\n"
                         "Current values: overlap=%d, sequence=%d" % (args.overlap, model_hparams['sequence_length']))

    # Build model
    print("    Building the model with pretrained weights")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = EncoderTransformer(input_dim=model_hparams['sequence_length'],
                               context_dim=model_hparams['d_context'],
                               d_model=model_hparams['d_model'],
                               nhead=model_hparams['n_head'],
                               num_layers=model_hparams['n_layers'],
                               dim_feedforward=model_hparams['d_feedforward'],
                               output_channels=model_hparams['output_channels'])
    model = nn.DataParallel(model)    
    model = load_model(args.ckpt, model)
    model.to(device)
    print("        -> Model [%s] successfully built" % model_hparams['model_name'])
    print("Model is ready for inference\n")

    # Process -------------------------------------------------------------------------------------------------------- #
    print("Inferencing data:")
    tot_len = len(src_lst)
    model.eval()
    with torch.no_grad():
        for i, (src, dst) in enumerate(zip(src_lst, dst_lst)):
            # Model inference
            t_init = time.time()  # Start time
            inf_dataset = InferenceDataset(src, model_hparams['sequence_length'], overlap=args.overlap)
            inf_datagen = data.DataLoader(
                dataset=inf_dataset,
                batch_size=args.bat_sz,
                shuffle=False,
                num_workers=hparams['data']['n_worker'])
            res = inference(model, inf_datagen, model_hparams['output_channels'], device)
            spk = {g: sig_merge(res[:, c, :], args.overlap, inf_dataset.pad) for c, g in enumerate(spk_grp)}
            # CLI print
            t_proc = time.time()  # Process time
            print("    Data [%s] processed in %.4f seconds (%d/%d)" % (src, t_proc - t_init, i + 1, tot_len))

            # Save outputs
            fp = h5.File(dst, 'w')
            fp.create_dataset(name='src', data=src, dtype=h5.string_dtype(encoding='utf-8', length=None))
            fp.create_dataset(name='frq', data=np.asarray(inf_dataset.frq, dtype=np.float32))
            fp.create_dataset(name='inp', data=inf_dataset.raw[0], compression="gzip", compression_opts=args.cmp_lvl)
            grp = fp.create_group('spk')
            for g in spk:
                grp.create_dataset(name=g, data=spk[g], compression="gzip", compression_opts=args.cmp_lvl)
            fp.close()
            # CLI print
            t_save = time.time()  # File writing time
            print("        -> Results saved to [%s] in %.4f seconds" % (dst, t_save - t_proc))

    print("Inference successful completed\n")
    print("Parus data inference finalized at " + time.strftime('%Y-%m-%d %H:%M:%S'))
