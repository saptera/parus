import torch
import numpy as np
from parus.model.post_proc import peak_det_diff
from parus.util import plt_mdl_perf
import numpy

def training_validation(model, datagen, criterion, device):
    val_losses = []
    for i, (inputs, labels, _) in enumerate(datagen):
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        cur_val_loss = criterion(outputs, labels.float())
        val_losses.append(cur_val_loss.item())

        # print visual prediction result of the first sample
        if i == 0:
            inp_print = inputs.cpu().clone().detach().numpy()[0][0]
            out_print = outputs.cpu().clone().detach().numpy()[0][0]
            lab_print = labels.cpu().clone().detach().numpy()[0][0]
            plt_mdl_perf(out_print, inp_print, lab_print, size=(256, 32))

    return np.mean(val_losses)


def inference(model, datagen, device, th=-50, neg=True, gap=20, test=False):
    # Initialize lists
    inp_numpy_lst = []
    spk_lbl_numpy_lst = []
    pos_lbl_numpy_lst = []
    spk_pred_numpy_lst = []
    pos_pred_numpy_lst = []
    # Inference
    for item in datagen:
        if test:
            inputs, spk_labels, pos_labels = item
            spk_lbl_numpy_lst.append(spk_labels.squeeze().cpu().numpy())
            pos_lbl_numpy_lst.append(pos_labels.squeeze().cpu().numpy())
        else:
            inputs = item
        inputs = inputs.to(device)
        spk_outputs = model(inputs)
        pos_outputs = peak_det_diff(spk_outputs, th=th, neg=neg, gap=gap)

        inp_numpy_lst.append(inputs.squeeze().cpu().numpy())
        spk_pred_numpy_lst.append(spk_outputs.squeeze().cpu().numpy())
        pos_pred_numpy_lst.append(pos_outputs.squeeze().cpu().numpy())
    # Arrange outputs
    inp_numpy = numpy.concatenate(inp_numpy_lst, axis=0).astype('float32')
    pred_numpy_dict = {'spk': numpy.concatenate(spk_pred_numpy_lst, axis=0).astype('float32'),
                       'pos': numpy.concatenate(pos_pred_numpy_lst, axis=0).astype('int8')}
    pklz_dct = {'inp': inp_numpy, 'prd': pred_numpy_dict}
    if test:
        lbl_dict = {'spk': numpy.concatenate(spk_lbl_numpy_lst, axis=0).astype('float32'),
                    'pos': numpy.concatenate(pos_lbl_numpy_lst, axis=0).astype('int8')}
        pklz_dct['lbl'] = lbl_dict
    return pklz_dct


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