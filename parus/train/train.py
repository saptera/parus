import os
import time
import numpy as np
import torch
import torch.nn as nn
from parus.util import plt_mdl_perf


def train(model, criterion, optimizer, scheduler, train_datagen, val_datagen, train_hparams):
    # load model onto gpu
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # make an empty log.txt file in the experiment folder
    log_file_path = os.path.join(
        train_hparams["experiment_folder"], "log.txt")
    f = open(log_file_path, "w+")
    f.close()

    # training loop
    val_loss_min = np.Inf
    for epoch_i in range(train_hparams["start_epoch"], train_hparams["total_epoch"] + 1):
        start_time = time.perf_counter()
        for step_i, (inputs, labels) in enumerate(train_datagen):
            model.train()
            optimizer.zero_grad()
            inputs, labels = inputs.to(device), labels.to(device)
            output = model(inputs)
            loss = criterion(output, labels.float())
            loss.backward()
            optimizer.step()
            nn.utils.clip_grad_norm_(
                model.parameters(), train_hparams["model_param_clip"])  # clipping to avoid exploding gradient

            if step_i != 0 and step_i % train_hparams["steps_per_eval"] == 0:
                val_loss = evaluate(model, val_datagen, criterion, device)
                scheduler.step()  # learning rate updates everytime the loop prints
                if val_loss <= val_loss_min:
                    save(train_hparams["experiment_folder"],
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
                                      "Val Loss: {:.6f}".format(val_loss)],
                                     "Time: {}s".format(finish_time-start_time))
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

    for i, (inputs, labels) in enumerate(val_datagen):
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        cur_val_loss = criterion(outputs, labels.float())
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


def resume(ckpt_path, model, optimizer, criterion, scheduler, train_datagen, val_datagen, train_hparams):
    ckpt = torch.load(ckpt_path)

    model.load_state_dict(ckpt['model_state_dict'])
    optimizer.load_state_dict(ckpt['optimizer_state_dict'])
    # TODO maybe need to load/update scheduler to match original training process
    train_hparams['start_epoch'] = ckpt['epoch']

    train(model, criterion, optimizer, scheduler,
          train_datagen, val_datagen, train_hparams)
