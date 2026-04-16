# Model training and optimization module

import os
import time
import numpy as np
import torch
import torch.nn as nn

__package__ = 'parus.model'
__name__ = 'parus.model.optim'
from .mio import save_model, write_train_log, write_train_history
from .eval import validation

__all__ = ['get_learning_rate', 'train']
"""
Function list:
  get_learning_rate(step, model_size, factor, warmup): Compute dynamic learning rate based on training steps.
  train(model, model_size, trn_data, vld_data, work_dir, train_hparams, device): General training function for models.
Protected constant:
  _loss_function_options {dict}: Selection of loss functions.
"""


_loss_function_options = {
    'l1': nn.L1Loss(reduction='mean'),  # Mean Absolute Error
    'mse': nn.MSELoss(reduction='mean'),  # Mean Squared Error
    'bce': nn.BCEWithLogitsLoss()  # Binary Cross Entropy with Sigmoid
}


def get_learning_rate(step, model_size, factor, warmup):
    """ Compute dynamic learning rate based on training steps.

    Args:
        step (int): Current model training step
        model_size (int): Size of the model
        factor (int | float): Learning rate factor for dynamic learning rate
        warmup (int): Warmup steps for applying dynamic learning rate

    Returns:
        float: Target learning rate
    """
    if step == 0:
        step = 1
    rate = factor * (model_size ** (-0.5) * min(step ** (-0.5), step * warmup ** (-1.5)))
    return rate


def train(model, model_size, trn_data, vld_data, work_dir, train_hparams, device, hint='text'):
    """ General training function for models.

    Args:
        model (nn.Module): PyTorch model
        model_size (int): Number of expected features in the model input
        trn_data (torch.utils.data.DataLoader): Training dataset loader
        vld_data (torch.utils.data.DataLoader): Validation dataset loader
        work_dir (str): Working directory to save model training artifacts
        train_hparams (dict): Training hyperparameters

            - start_epoch (int): Initial epoch number
            - total_epoch (int): Total number of epoches for training
            - batch_size (int): Training batch size
            - steps_per_eval (str): Number of training steps between each model validation
            - base_learning_rate (float): Base rate for dynamic learning rate
            - learning_rate_factor (float): Learning rate factor for dynamic learning rate
            - learning_rate_warmup (int): Warmup steps for applying dynamic learning rate
            - model_param_clip (float): Clipping value to avoid exploding gradient
            - loss_function (str): {mse, l1, bce} Loss function name

        device (torch.device): Device for model training
        hint (str): {'text' | 'disp' | 'save' | 'none'} Result hinting method (default: 'text')

            - 'text': Plot text image with [plotext] in the console, recommended for training in CLI
            - 'disp': Show image with [matplotlib]
            - 'save': Save image with [matplotlib] to the work directory, recommended for training in GUI
            - 'none': No hinting (fallback for invalid method input)

    """
    # Set loss function
    criterion = _loss_function_options[train_hparams['loss_function']]
    # Set optimization algorithm
    optimizer = torch.optim.AdamW(model.parameters(), lr=train_hparams['base_learning_rate'])
    # Set learning rate scheduler
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer=optimizer, 
        lr_lambda=lambda step: get_learning_rate(
            step, model_size, train_hparams['learning_rate_factor'], train_hparams['learning_rate_warmup']
        )
    )

    # Initialize training recording variables
    val_loss_min = np.inf
    log_file_path = os.path.join(work_dir, "train.log")
    history_file_path = os.path.join(work_dir, "history.json")
    # Get recording file pointers ('+' mode required)
    log_fp = open(log_file_path, 'a+')
    hst_fp = open(history_file_path, 'a+')
    # Write initial log
    log_fp.write("Parus model training started at: " + time.strftime('%Y-%m-%d %H:%M:%S') + '\n\n')
    log_fp.flush()  # Update immediately

    # Train loop
    for ep in range(train_hparams['start_epoch'], train_hparams['total_epoch'] + 1):
        start_time = time.perf_counter()
        for stp, (inputs, labels, _) in enumerate(trn_data):
            # Train
            model.train()
            optimizer.zero_grad()
            inputs, labels = inputs.to(device), labels.to(device)
            output = model(inputs)
            loss = criterion(output, labels.float())
            loss.backward()
            optimizer.step()
            scheduler.step()
            nn.utils.clip_grad_norm_(model.parameters(), train_hparams['model_param_clip'])  # Avoid exploding gradient

            # Validation and logging
            stp = stp + 1  # Covert to one-based
            if stp % train_hparams['steps_per_eval'] == 0:
                model.eval()
                with torch.no_grad():
                    image = os.path.join(work_dir, "vld_ep%02d_stp%04d.png" % (ep, stp))
                    val_loss = validation(model, vld_data, criterion, device, hint, image)

                # Log metrics to [train.log] and training history to [history.json]
                elapsed_time = time.perf_counter() - start_time
                current_lr = optimizer.param_groups[0]['lr']
                write_train_log(log_fp, ep=ep, stp=stp, lr=current_lr, tls=loss.item(), vls=val_loss,
                                t=elapsed_time, tot_ep=train_hparams['total_epoch'], curr_loss=val_loss_min)
                write_train_history(hst_fp, ep=ep, stp=stp, lr=current_lr, tls=loss.item(), vls=val_loss,
                                    t=elapsed_time)

                # Save checkpoint on improvement
                if val_loss <= val_loss_min:
                    save_model(work_dir, model, optimizer, ep, 'optimum')
                    val_loss_min = val_loss  # Update best loss
                # Reset timer for next interval
                start_time = time.perf_counter()

    # Save final model
    save_model(work_dir, model, optimizer, train_hparams['total_epoch'], 'final')
    # Close log files
    log_fp.close()
    hst_fp.close()
    # Close datasets
    trn_data.dataset.close()
    vld_data.dataset.close()
