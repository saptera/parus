import os
import torch
import torch.nn as nn
import argparse
from torch.utils import data
from parus.model.transformer import EncoderTransformer
from parus.train.dataset import InferenceDataset
from parus.train.experiment import setup_experiment, load_hparams, load_model
from parus.train.eval import inference
from parus.fio import pklz_write


# Parse command line arguments
argParser = argparse.ArgumentParser()
argParser.add_argument(
    "--exp_folder", help="path to experiment folder", type=str, required=True)
argParser.add_argument(
    "--model_folder", help="path to pre-trained model folder", type=str, required=True)
argParser.add_argument(
    "--ckpt_name", help="name of checkpoint file", type=str, required=True)
argParser.add_argument(
    "--inf_dataset_folder", help="path to inference dataset folder", type=str, required=True)
argParser.add_argument(
    "--inf_batch_size", help="batch size for inference", type=int, required=True)
args = argParser.parse_args()

if __name__ == '__main__':
    # Create experiment folder and save hyperparameters
    dataset_name = os.path.basename(args.inf_dataset_folder)
    cur_exp_folder_path, inf_pred_folder = setup_experiment("inf", dataset_name, args.exp_folder, mode="inf")
    
    # Load pre-trained model for inference
    model_ckpt = os.path.join(args.model_folder, args.ckpt_name)
    print(f"found model_ckpt at {model_ckpt}")
    ckpt_hparams = load_hparams(os.path.join(args.model_folder, "hparams.json"))
    print(f"loaded ckpt_hparams from {os.path.join(args.model_folder, 'hparams.json')}")
    model_hparams = ckpt_hparams["model"]
    print(f"model_hparams: {model_hparams}")

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
    model = load_model(model_ckpt, model)
    model.to(device)
    print(f"loaded model from {model_ckpt}")

    # Run inference on new data
    inf_dataset_folder = args.inf_dataset_folder
    filename_lst = os.listdir(inf_dataset_folder)

    # Process each file in the inference folder
    model.eval()
    with torch.no_grad():
        for filename in filename_lst:
            file_path = os.path.join(inf_dataset_folder, filename)
            print(f"processing {file_path}")
            inf_dataset = InferenceDataset(file_path, model_hparams["sequence_length"])
            inf_datagen = data.DataLoader(
                dataset=inf_dataset,
                batch_size=args.inf_batch_size,
                shuffle=False,
                num_workers=model_hparams["n_worker"])

            pklz_dct = inference(model, inf_datagen, device)
            pklz_write(os.path.join(inf_pred_folder, filename), pklz_dct)
        


