import os
import time
import numpy as np
import torch
import torch.nn as nn
from parus.util import plt_mdl_perf


def train(model, criterion, optimizer, scheduler, train_datagen, val_datagen, cur_experiment_folder_path, train_hparams):
    # load model onto gpu
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # make an empty log.txt file in the experiment folder
    log_file_path = os.path.join(cur_experiment_folder_path, "log.txt")
    f = open(log_file_path, "w+")
    f.close()

    # training loop
    val_loss_min = np.Inf
    for epoch_i in range(train_hparams["start_epoch"], train_hparams["total_epoch"] + 1):
        start_time = time.perf_counter()
        for step_i, (inputs, labels, _) in enumerate(train_datagen):
            model.train()
            optimizer.zero_grad()
            inputs, labels = inputs.to(device), labels.to(device)
            output = model(inputs)
            loss = criterion(output, labels.float())
            loss.backward()
            optimizer.step()
            scheduler.step()
            nn.utils.clip_grad_norm_(
                # clipping to avoid exploding gradient
                model.parameters(), train_hparams["model_param_clip"])

            if step_i != 0 and step_i % train_hparams["steps_per_eval"] == 0:
                val_loss = evaluate(model, val_datagen, criterion, device)
                # scheduler.step()  # learning rate updates everytime the loop prints
                if val_loss <= val_loss_min or epoch_i == train_hparams["total_epoch"]:
                    save(cur_experiment_folder_path,
                         model, optimizer, epoch_i)
                    saving_str = 'Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
                        val_loss_min, val_loss)
                    log_and_print(log_file_path, saving_str)
                    val_loss_min = val_loss

                # log and print status, reset time counter
                finish_time = time.perf_counter()
                status_str = "".join(["Epoch: {}/{}...".format(epoch_i, train_hparams["total_epoch"]),
                                      "Step: {}...".format(step_i),
                                      "Learning Rate: {}...".format(
                                          optimizer.param_groups[0]['lr']),
                                      "Loss: {:.6f}...".format(loss.item()),
                                      "Val Loss: {:.6f}...".format(val_loss),
                                     "Time: {}s...".format(finish_time-start_time)])
                log_and_print(log_file_path, status_str)
                start_time = time.perf_counter()


def cascade_train(model, spk_model, criterion, optimizer, scheduler, train_datagen, val_datagen, cur_experiment_folder_path, train_hparams):
    # load model onto gpu
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    spk_model.to(device)

    # make an empty log.txt file in the experiment folder
    log_file_path = os.path.join(cur_experiment_folder_path, "log.txt")
    f = open(log_file_path, "w+")
    f.close()

    # training loop
    val_loss_min = np.Inf
    for epoch_i in range(train_hparams["start_epoch"], train_hparams["total_epoch"] + 1):
        start_time = time.perf_counter()
        for step_i, (inputs, labels, _) in enumerate(train_datagen):
            model.train()
            spk_model.eval()
            optimizer.zero_grad()
            inputs, labels = inputs.to(device), labels.to(device)
            with torch.no_grad():
                spk_output = spk_model(inputs)
            output = model(spk_output)
            loss = criterion(output,
                             labels.float())
                             # alpha=0.95,
                             #reduction="mean")
            loss.backward()
            optimizer.step()
            nn.utils.clip_grad_norm_(
                # clipping to avoid exploding gradient
                model.parameters(), train_hparams["model_param_clip"])

            if step_i != 0 and step_i % train_hparams["steps_per_eval"] == 0:
                val_loss = evaluate(model, val_datagen, criterion, device)
                scheduler.step()  # learning rate updates everytime the loop prints
                if val_loss <= val_loss_min or epoch_i == train_hparams["total_epoch"]:
                    save(cur_experiment_folder_path,
                         model, optimizer, epoch_i)
                    saving_str = 'Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
                        val_loss_min, val_loss)
                    log_and_print(log_file_path, saving_str)
                    val_loss_min = val_loss

                # log and print status, reset time counter
                finish_time = time.perf_counter()
                status_str = "".join(["Epoch: {}/{}...".format(epoch_i, train_hparams["total_epoch"]),
                                      "Step: {}...".format(step_i),
                                      "Learning Rate: {}...".format(
                                          optimizer.param_groups[0]['lr']),
                                      "Loss: {:.6f}...".format(loss.item()),
                                      "Val Loss: {:.6f}...".format(val_loss),
                                     "Time: {}s...".format(finish_time-start_time)])
                log_and_print(log_file_path, status_str)
                start_time = time.perf_counter()


def log_and_print(log_file_path, status_str):
    f = open(log_file_path, "a")
    f.write(status_str+"\n")
    f.close()
    print(status_str)


def evaluate(model, val_datagen, criterion, device):
    model.eval()
    val_losses = []

    for i, (inputs, labels, _) in enumerate(val_datagen):
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        cur_val_loss = criterion(
            outputs,
            labels.float())
        #cur_val_ota, cur_val_metrics_dct = eval_bin_cls(
        #    outputs, labels.float())
        #tp = cur_val_metrics_dct["tp"]
        #tn = cur_val_metrics_dct["tn"]
        #fp = cur_val_metrics_dct["fp"]
        #fn = cur_val_metrics_dct["fn"]
        #print("batch on target accuracy: ", cur_val_ota)
        #print("tp", tp)
        #print("tn", tn)
        #print("fp", fp)
        #print("fn", fn)
        #print("f1", (2*tp)/(2*tp + fp + fn))
        #print("recall", tp/((tp + fn) + 1))
        #print("precision", tp/((tp + fp) + 1))
        #print("accuracy", (tp + tn)/(tp + tn + fp + fn))

        val_losses.append(cur_val_loss.item())

        if i == 0:
            # print visual prediction result of the first sample
            inp_print = inputs.cpu().clone().detach().numpy()[0][0]
            out_print = outputs.cpu().clone().detach().numpy()[0][0]
            lab_print = labels.cpu().clone().detach().numpy()[0][0]
            plt_mdl_perf(out_print, inp_print,
                         lab_print, size=(256, 32))

    return np.mean(val_losses)


def save(experiment_folder_path, model, optimizer, cur_epoch):
    ckpt = {
        "epoch": cur_epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict()
    }
    ckpt_path = os.path.join(
        experiment_folder_path, "epoch" + str(cur_epoch) + ".ckpt")

    torch.save(ckpt, ckpt_path)


def load_model(ckpt_path, model):
    ckpt = torch.load(ckpt_path)
    model.load_state_dict(ckpt['model_state_dict'])
    return model


def resume(ckpt_path, model, optimizer, criterion, scheduler, train_datagen, val_datagen, cur_experiment_folder_path, train_hparams):
    ckpt = torch.load(ckpt_path)

    model.load_state_dict(ckpt['model_state_dict'])
    optimizer.load_state_dict(ckpt['optimizer_state_dict'])
    # TODO maybe need to load/update scheduler to match original training process
    train_hparams['start_epoch'] = ckpt['epoch']

    train(model, criterion, optimizer, scheduler,
          train_datagen, val_datagen, cur_experiment_folder_path, train_hparams)


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
