# Model evaluation and inference functions

import numpy as np
import torch

__package__ = 'parus.model'
from ..util import plt_mod_cli, plt_mod_img
from .post import peak_fwd_torch

__all__ = ['validation', 'testing', 'inference', 'eval_bin_cls']
"""
Function list:
  validation(model, datagen, criterion, device): Validation for model training.
  testing(model, datagen, channel, device, th=-1): Testing for model training.
  inference(model, datagen, channel, device): Inference data.
  eval_bin_cls(prediction, reference, allowed_distance=0, binary_threshold=0.5): Binary detection evaluation.
"""


def validation(model, datagen, criterion, device, hint='text', image=None):
    """ Validation for model training.

    Args:
        model (torch.nn.Module): PyTorch model
        datagen (torch.utils.data.DataLoader): Dataset loader
        criterion (torch.nn.Module): Loss function
        device (torch.device): Device for model training
        hint (str): {'text' | 'disp' | 'save' | 'none'} Result hinting method (default: 'text')
            - 'text': Plot text image with [plotext] in the console, recommended for training in CLI
            - 'disp': Show image with [matplotlib]
            - 'save': Save image with [matplotlib] to the work directory, recommended for training in GUI
            - 'none': No hinting (fallback for invalid method input)
        image (str | None): Image save path for [hint = 'save']

    Returns:
        float: Mean loss
    """
    val_losses = []
    for i, (inputs, labels, _) in enumerate(datagen):
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        cur_val_loss = criterion(outputs, labels.float())
        val_losses.append(cur_val_loss.item())

        # Plot for visual prediction result of the first sample
        if (i == 0) and (hint != 'none'):
            prd_print = outputs.cpu().clone().detach().numpy()[0][0]
            inp_print = inputs.cpu().clone().detach().numpy()[0][0]
            lbl_print = labels.cpu().clone().detach().numpy()[0][0]
            if hint == 'text':
                plt_mod_cli(prd_print, inp_print, lbl_print, size=(256, 32))
            elif hint == 'disp':
                fig, ax = plt_mod_img(prd_print, inp_print, lbl_print, img=None)
                fig.show()
            elif hint == 'save':
                plt_mod_img(prd_print, inp_print, lbl_print, img=image)

    return np.mean(val_losses)


def testing(model, datagen, channel, device, th=-1):
    """ Testing for model training.

    Args:
        model (torch.nn.Module): PyTorch model
        datagen (torch.utils.data.DataLoader): Dataset loader
        channel (int): Number of output channels of model
        device (torch.device): Device for model training
        th (int | float): Minimum peak threshold (default: -1 = avoid baseline fluctuation)

    Returns:
        dict: {3D (Index, Channel, Sample)}Test dataset results
            - 'inp': (np.ndarray): {3D-float32} Input signal
            - 'prd': (dict): Model prediction results
                - 'spk' (np.ndarray): {3D-float32} Predicted spike signal
                - 'pos' (np.ndarray): {3D-int8} Predicted spike position
            - 'lbl': (np.ndarray): Signal label
                - 'spk' (np.ndarray): {3D-float32} Reference spike signal
                - 'pos' (np.ndarray): {3D-int8} Reference spike position
    """
    bs = datagen.batch_size
    shape = (datagen.dataset.n_sample, channel, datagen.dataset.seq_len)
    # Initialize lists
    inp_arr = np.zeros((datagen.dataset.n_sample, datagen.dataset.seq_len), dtype=np.float32)
    spk_lbl = np.zeros(shape, dtype=np.float32)
    pos_lbl = np.zeros(shape, dtype=np.int8)
    spk_prd = np.zeros(shape, dtype=np.float32)
    pos_prd = np.zeros(shape, dtype=np.int8)
    # Inference
    for i, item in enumerate(datagen):
        s = i * bs
        e = s + bs
        # Arrange inputs
        inputs, spk_labels, pos_labels = item
        inp_arr[s:e] = inputs.cpu().numpy()
        spk_lbl[s:e] = spk_labels.cpu().numpy()
        pos_lbl[s:e] = pos_labels.cpu().numpy()
        # Process inference
        inputs = inputs.to(device)
        spk_outputs = model(inputs)
        pos_outputs = peak_fwd_torch(spk_outputs, th=th, neg=True, gap=None)
        # Store results
        spk_prd[s:e] = spk_outputs.cpu().numpy()
        pos_prd[s:e] = pos_outputs.cpu().numpy()
    # Arrange outputs
    return {'inp': inp_arr, 'prd': {'spk': spk_prd, 'pos': pos_prd}, 'lbl': {'spk': spk_lbl, 'pos': pos_lbl}}


def inference(model, datagen, channel, device):
    """ Inference data.

    Args:
        model (torch.nn.Module): PyTorch model
        datagen (torch.utils.data.DataLoader): Dataset loader
        channel (int): Number of output channels of model
        device (torch.device): Device for model training

    Returns:
        np.ndarray: {3D-float32 (Index, Channel, Sample)} Inference results
    """
    bs = datagen.batch_size
    shape = (datagen.dataset.n_sample, channel, datagen.dataset.seq_len)
    # Initialize return
    spk = np.zeros(shape, dtype=np.float32)
    # Inference
    for i, inputs in enumerate(datagen):
        s = i * bs
        e = s + bs
        # Process inference
        inputs = inputs.to(device)
        outputs = model(inputs)
        # Store results
        spk[s:e] = outputs.cpu().numpy()
    # Return results
    return spk


def eval_bin_cls(prediction, reference, allowed_distance=0, binary_threshold=0.5):
    """ Binary detection evaluation.

    Args:
        prediction (torch.Tensor): Prediction tensor
        reference (torch.Tensor): Ground truth tensor, the same shape as [prediction]
        allowed_distance (int): Index tolerance for binary detection (default: 2)
        binary_threshold (int | float): Threshold to make binary tensor (default: 0.5)

    Returns:
        tuple[float, dict[str, int]]:
            - ota (float): On-target accuracy (%) of binary detection, with allowance defined by [allowed_distance]
            - sas (dict[str, int]): Four factors for sensitivity and specificity (actual raw values)
    """
    # On-target accuracy #
    # Get basic info
    win = allowed_distance * 2 + 1
    pos_prd = torch.where(prediction > binary_threshold)
    pos_ref = torch.where(reference > binary_threshold)
    tot_spk = pos_ref[0].nelement()
    # Get target allowed indices
    accu_chk = [torch.repeat_interleave(p, win) for p in pos_ref]
    for i in range(win):
        accu_chk[2][i::win] = accu_chk[2][i::win] - allowed_distance + i
    accu_chk[2] = torch.clip(accu_chk[2], min=0, max=reference.size(2) - 1)
    # Set target value matrix
    accu_mat = torch.clone(reference)
    for i in range(tot_spk * (allowed_distance * 2 + 1)):
        accu_mat[accu_chk[0][i], accu_chk[1][i], accu_chk[2][i]] = 1.0
    # Check prediction
    tot_det = 0
    for i in range(pos_prd[0].nelement()):
        if accu_mat[pos_prd[0][i], pos_prd[1][i], pos_prd[2][i]] > binary_threshold:
            tot_det += 1
    # Summarize
    ota = tot_det / tot_spk * 100

    # Sensitivity and specificity #
    # Get confusion vector
    bin_prd = torch.where(prediction > binary_threshold, 1.0, 0.0)
    bin_ref = torch.where(reference > binary_threshold, 1.0, 0.0)
    confusion = bin_prd / bin_ref
    # Compute four factors
    tp = torch.sum(confusion == 1).item()
    tn = torch.sum(torch.isnan(confusion)).item()
    fp = torch.sum(confusion == float('inf')).item()
    fn = torch.sum(confusion == 0).item()

    return ota, {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn}
