import os
import numpy
import torch
import time
from parus.fio import pklz_write
from parus.model.post_proc import peak_det_diff, eval_pos

"""Function list:
test(model, tst_datagen, pred_save_folder): Test a single model and save predictions
duo_test(spk_model, pos_model, tst_datagen, pred_save_folder): Test spike and position models together
inference(model, inference_datagen, filename, pred_save_folder): Run inference with a single model
duo_inference(pos_model, spk_model, inference_datagen, filename, pred_save_folder): Run inference with spike and position models
flt_pos(sig_inp, pos_prd, min_dst=5, th=0.5): Filter position predictions for multiple points in a window
"""


def test(model, tst_datagen, pred_save_folder):
    """ Test a single model and save predictions.

    Args:
        model (torch.nn.Module): Neural network model
        tst_datagen (DataLoader): Test data generator
        pred_save_folder (str): Folder path to save predictions

    Returns:
        None: Saves prediction files to specified folder
    """
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
    """ Test spike and position models together.

    Args:
        spk_model (torch.nn.Module): Spike detection model
        pos_model (torch.nn.Module): Position detection model
        tst_datagen (DataLoader): Test data generator
        pred_save_folder (str): Folder path to save predictions

    Returns:
        None: Saves prediction files and prints average false negative/positive rates
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # prediction and saving
    count = 0
    total_fn = 0
    total_fp = 0
    with torch.no_grad():
        for inputs, labels, file_num_str in tst_datagen:
            inputs = inputs.to(device)
            spk_model.to(device)
            spk_outputs = spk_model(inputs)
            print(spk_outputs.shape) 
            pos_outputs = peak_det_diff(spk_outputs, th=-100, neg=True, gap=20)
            #print("pos", pos_outputs.device)
            #print(pos_outputs)
            #print("label", labels.device)
            #print(labels.to(torch.int32))
            fn, fp = eval_pos(pos_outputs.cpu(), labels.to(torch.int32))
            print("fn", fn)
            print("fp", fp)
            count += 1
            total_fn += fn
            total_fp += fp
            #diff = torch.bitwise_xor(pos_outputs.cpu(), labels.to(torch.int32))
            #miss = torch.sum(diff)
            #print("Miss: ", miss)
            #pos_model.to(device)
            #pos_outputs = pos_model(spk_outputs)

            inp = inputs.squeeze().cpu().numpy()
            spk_pred = spk_outputs.squeeze().cpu().numpy()
            pos_pred = pos_outputs.squeeze().cpu().numpy()
            pos_lbl = labels.squeeze().cpu().numpy()

            pred_dict = {"spk": spk_pred, "pos": pos_pred}

            filename = "pred_" + file_num_str[0] + ".sim"
            pklz_write(os.path.join(pred_save_folder, filename),
                    {"inp": inp,  "prd": pred_dict, "lbl": labels})
    print("average fn: ", total_fn / count)
    print("average fp: ", total_fp / count)


def inference(model, inference_datagen, filename, pred_save_folder):
    """ Run inference with a single model.

    Args:
        model (torch.nn.Module): Neural network model
        inference_datagen (DataLoader): Inference data generator
        filename (str): Name for output file
        pred_save_folder (str): Folder path to save predictions

    Returns:
        None: Saves prediction files to specified folder
    """
    #model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # prediction and saving
    with torch.no_grad():
        inp_numpy_lst = []
        pred_numpy_lst = []
        for inputs in inference_datagen:
            start_time = time.time()
            inputs = inputs.to(device)
            outputs = model(inputs)

            inp = inputs.squeeze().cpu().numpy()
            pred = outputs.squeeze().cpu().numpy()
            inp_numpy_lst.append(inp)
            pred_numpy_lst.append(pred)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Elapsed time: {elapsed_time} seconds")

        pred_filename = "pred_" + filename
        pklz_write(os.path.join(pred_save_folder, pred_filename),
                   {"inp": numpy.concatenate(inp_numpy_lst, axis=0),
                    "prd": numpy.concatenate(pred_numpy_lst, axis=0)})


def duo_inference(pos_model, spk_model, inference_datagen, filename, pred_save_folder):
    """ Run inference with spike and position models.

    Args:
        pos_model (torch.nn.Module): Position detection model
        spk_model (torch.nn.Module): Spike detection model
        inference_datagen (DataLoader): Inference data generator
        filename (str): Name for output file
        pred_save_folder (str): Folder path to save predictions

    Returns:
        None: Saves prediction files to specified folder with timing information
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pos_model.to(device)
    spk_model.to(device)

    # prediction and saving
    with torch.no_grad():
        inp_numpy_lst = []  
        spk_pred_numpy_lst = []
        pos_pred_numpy_lst = []
        for inputs in inference_datagen:
            start_time = time.time()
            inputs = inputs.to(device)
            input_end_time = time.time()
            input_elapsed_time = input_end_time - start_time
            #print(f"Load Input Time: {input_elapsed_time} seconds")
            spk_outputs = spk_model(inputs)
            pos_start_time = time.time()
            model_time = pos_start_time - input_end_time
            #print(f"Spk Model Time: {model_time} seconds")
            #pos_outputs = pos_model(spk_outputs)
            pos_outputs = peak_det_diff(spk_outputs, th=-50, neg=True, gap=20)
            pos_end_time = time.time()
            pos_elapsed_time = pos_end_time - pos_start_time
            pre_pos_time = pos_start_time - start_time
            #print(f"Pre Pos time: {pre_pos_time} seconds")
            #print(f"Pos Elapsed time: {pos_elapsed_time} seconds")

            inp = inputs.squeeze().cpu().numpy()
            spk_pred = spk_outputs.squeeze().cpu().numpy()
            pos_pred = pos_outputs.squeeze().cpu().numpy()
            inp_numpy_lst.append(inp)
            spk_pred_numpy_lst.append(spk_pred)
            pos_pred_numpy_lst.append(pos_pred)

            end_time = time.time()
            post_pos_time = end_time - pos_end_time
            elapsed_time = end_time - start_time
            #print(f"Post Pos Time: {post_pos_time} seconds" )
            #print(f"Elapsed time: {elapsed_time} seconds\n")

        pred_filename = "pred_" + filename
        inp_numpy = numpy.concatenate(inp_numpy_lst, axis=0)
        pred_numpy_dict = {"spk": numpy.concatenate(spk_pred_numpy_lst, axis=0),
                           "pos": numpy.concatenate(pos_pred_numpy_lst, axis=0)}

        pklz_write(os.path.join(pred_save_folder, pred_filename),
                   {"inp": inp_numpy,
                    "prd": pred_numpy_dict})


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
