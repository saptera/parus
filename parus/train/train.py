import os
import time
import numpy as np
import torch
import torch.nn as nn
from parus.train.eval import training_validation
from parus.train.experiment import write_train_log, write_train_history, save

LOSS_FUNCTION_OPTIONS = {
    "mse": nn.MSELoss(reduction='mean'),
    "l1": nn.L1Loss(reduction='mean'),
    "bce": nn.BCEWithLogitsLoss(),
}

def get_learning_rate(step, model_size, factor, warmup):
    if step == 0:
        step = 1
    rate = factor * (model_size ** (-0.5) * min(step ** (-0.5), step * warmup ** (-1.5)))
    if step % 1000 == 0:
        print(step, rate)
    return rate


def train(model, model_size, train_datagen, val_datagen, cur_exp_folder_path, train_hparams, device):
    loss_fn = LOSS_FUNCTION_OPTIONS[train_hparams["loss_function"]]
    optimizer = torch.optim.AdamW(model.parameters(), lr=train_hparams["base_learning_rate"])
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer=optimizer, 
        lr_lambda=lambda step: get_learning_rate(
            step, 
            model_size, 
            train_hparams["learning_rate_factor"], 
            train_hparams["learning_rate_warmup"]
        )
    )

    val_loss_min = np.Inf
    log_file_path = os.path.join(cur_exp_folder_path, "training.log")
    history_file_path = os.path.join(cur_exp_folder_path, "training_history.json")

    with open(log_file_path, "a+") as log_fp, open(history_file_path, "a+") as history_fp:
        for epoch_i in range(train_hparams["start_epoch"], train_hparams["total_epoch"] + 1):
            start_time = time.perf_counter()
            for step_i, (inputs, labels, _) in enumerate(train_datagen):
                model.train()
                optimizer.zero_grad()
                inputs, labels = inputs.to(device), labels.to(device)
                output = model(inputs)
                loss = loss_fn(output, labels.float())
                loss.backward()
                optimizer.step()
                scheduler.step()
                nn.utils.clip_grad_norm_(
                    # clipping to avoid exploding gradient
                    model.parameters(), train_hparams["model_param_clip"])

                if step_i != 0 and step_i % train_hparams["steps_per_eval"] == 0:
                    model.eval()
                    with torch.no_grad():
                        val_loss = training_validation(model, val_datagen, loss_fn, device)

                    # Save checkpoint on improvement or at the final epoch
                    if val_loss <= val_loss_min or epoch_i == train_hparams["total_epoch"]:
                        save(cur_exp_folder_path, model, optimizer, epoch_i)

                    # Log metrics to training.log and append JSON record to training_history.json
                    finish_time = time.perf_counter()
                    elapsed_time = finish_time - start_time
                    current_lr = optimizer.param_groups[0]['lr']

                    write_train_log(
                        log_fp,
                        ep=epoch_i,
                        stp=step_i,
                        lr=current_lr,
                        tls=loss.item(),
                        vls=val_loss,
                        t=elapsed_time,
                        tot_ep=train_hparams["total_epoch"],
                        curr_loss=val_loss_min,
                    )

                    write_train_history(
                        history_fp,
                        ep=epoch_i,
                        stp=step_i,
                        lr=current_lr,
                        tls=loss.item(),
                        vls=val_loss,
                        t=elapsed_time,
                    )

                    # Update best validation loss after logging
                    if val_loss <= val_loss_min:
                        val_loss_min = val_loss

                    # Reset timer for next interval
                    start_time = time.perf_counter()