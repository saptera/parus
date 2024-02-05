import os
import numpy
import torch
from parus.fio import pklz_write

"""
need: 
- test data
    - input and label
- model
- generate a file with input, prediciton, label.
"""


def test(model, tst_datagen, pred_save_folder):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # prediction and saving
    with torch.no_grad():
        for inputs, labels, file_num_str in tst_datagen:
            inputs = inputs.to(device)
            outputs = model(inputs)

            inp = inputs.squeeze().cpu().numpy()
            pred = outputs.squeeze().cpu().numpy()
            labels = labels.squeeze().cpu().numpy()

            filename = "pred_" + file_num_str[0] + ".sim"
            pklz_write(os.path.join(pred_save_folder, filename),
                       {"inp": inp,  "prd": pred, "lbl": labels})


def duo_test(spk_model, pos_model, tst_datagen, pred_save_folder):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # prediction and saving
    with torch.no_grad():
        for inputs, spk_labels, pos_labels, file_num_str in tst_datagen:
            inputs = inputs.to(device)
            spk_model.to(device)
            spk_outputs = spk_model(inputs)
            pos_model.to(device)
            pos_outputs = pos_model(inputs)

            inp = inputs.squeeze().cpu().numpy()
            spk_pred = spk_outputs.squeeze().cpu().numpy()
            pos_pred = pos_outputs.squeeze().cpu().numpy()
            spk_lbl = spk_labels.squeeze().cpu().numpy()
            pos_lbl = pos_labels.squeeze().cpu().numpy()

            pred_dict = {"spk": spk_pred, "pos": pos_pred}
            lbls_dict = {"spk": spk_lbl, "pos": pos_lbl}

            filename = "pred_" + file_num_str[0] + ".sim"
            pklz_write(os.path.join(pred_save_folder, filename),
                       {"inp": inp,  "prd": pred_dict, "lbl": lbls_dict})


def inference(model, inference_datagen, filename, pred_save_folder):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # prediction and saving
    with torch.no_grad():
        inp_numpy_lst = []
        pred_numpy_lst = []
        for inputs in inference_datagen:
            inputs = inputs.to(device)
            outputs = model(inputs)

            inp = inputs.squeeze().cpu().numpy()
            pred = outputs.squeeze().cpu().numpy()
            inp_numpy_lst.append(inp)
            pred_numpy_lst.append(pred)

        pred_filename = "pred_" + filename
        pklz_write(os.path.join(pred_save_folder, pred_filename),
                   {"inp": numpy.concatenate(inp_numpy_lst, axis=0),
                    "prd": numpy.concatenate(pred_numpy_lst, axis=0)})


def flt_pos(sig_inp, pos_prd, min_dst=5, th=0.5):
    """ Filter position prediction for multiple points in a window.

    Args:
        sig_inp (torch.Tensor): Raw signal inputs
        pos_prd (torch.Tensor): Predicted position, the same shape as [sig_inp]
        min_dst (int): Window tolerance for binary detection (default: 5)
        th (int | float): Threshold to make binary tensor (default: 0.5)

    Returns:
        torch.Tensor: Filtered position prediction
    """
    pos = torch.where(pos_prd > th, 1, 0)
    for k in range(min_dst, 0, -1):
        win = pos.unfold(dimension=2, size=min_dst, step=k)
        accu = torch.sum(win, dim=3)
        chkw = torch.where(accu > 1)
        for i in range(chkw[0].nelement()):
            # Find location
            init = chkw[2][i] * k
            stop = init + min_dst
            loc = torch.argmin(sig_inp[chkw[0][i], chkw[1][i], init:stop])
            # Set value
            cast = torch.zeros(min_dst, dtype=torch.int)
            cast[loc] = 1
            pos[chkw[0][i], chkw[1][i], init:stop] = cast
    return pos
