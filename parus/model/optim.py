# -*- coding: utf-8 -*-

"""Model training and optimization module

Training-loop driver and the dynamic learning-rate schedule used by the PARUS spike-detection model.
"""

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
Public function list:

- get_learning_rate(step, model_size, factor, warmup)              : Compute the dynamic learning rate at a step
- train(model, model_size, trn_data, vld_data, work_dir, ...)      : Drive the full model training loop

Protected constants:

- _loss_function_options (dict[str, nn.Module])                    : Mapping from loss-function name to module
"""


_loss_function_options = {
    'l1': nn.L1Loss(reduction='mean'),  # Mean Absolute Error
    'mse': nn.MSELoss(reduction='mean'),  # Mean Squared Error
    'bce': nn.BCEWithLogitsLoss()  # Binary Cross Entropy with Sigmoid
}


def get_learning_rate(step, model_size, factor, warmup):
    """Compute the dynamic learning rate at a given training step.

    Implements the Transformer-style schedule
    ``rate = factor * model_size ** -0.5 * min(step ** -0.5, step * warmup ** -1.5)``.

    Args:
        step (int): Current training step (one-based; ``0`` is treated as ``1``)
        model_size (int): Size of the model used to scale the schedule
        factor (int | float): Multiplicative scaling factor
        warmup (int): Warm-up step count after which the schedule decays as ``step ** -0.5``

    Returns:
        float: Target learning rate for the step
    """
    if step == 0:
        step = 1
    rate = factor * (model_size ** (-0.5) * min(step ** (-0.5), step * warmup ** (-1.5)))
    return rate


def train(model, model_size, trn_data, vld_data, work_dir, train_hparams, device, hint='text'):
    """Drive a full model training run from start to finish.

    Sets up :class:`~torch.optim.AdamW` with a :class:`~torch.optim.lr_scheduler.LambdaLR` schedule built from
    :func:`get_learning_rate`, loops over epochs, validates every ``steps_per_eval`` steps, saves the best and final
    checkpoint to ``work_dir``, and writes both a human-readable log and a JSON training history.

    Args:
        model (nn.Module): PyTorch model to train
        model_size (int): Number of expected features in the model input
        trn_data (torch.utils.data.DataLoader): Training dataset loader
        vld_data (torch.utils.data.DataLoader): Validation dataset loader
        work_dir (str): Working directory for checkpoints, logs, and history
        train_hparams (dict): Training hyperparameters

            - start_epoch (int): Initial epoch number
            - total_epoch (int): Total number of epochs to run
            - batch_size (int): Training batch size
            - steps_per_eval (int): Number of training steps between validations
            - base_learning_rate (float): Base rate passed to :class:`~torch.optim.AdamW`
            - learning_rate_factor (float): Schedule scaling factor
            - learning_rate_warmup (int): Warm-up step count
            - model_param_clip (float): Gradient-norm clipping value
            - loss_function (str): One of ``{'mse', 'l1', 'bce'}``

        device (torch.device): Device on which the model and data live
        hint (str): Visualisation method for the validation snapshot; one of
            ``{'text', 'disp', 'save', 'none'}`` (default: ``'text'``)

            - ``'text'``: render an ASCII plot via ``plotext`` (recommended for CLI training)
            - ``'disp'``: open a Matplotlib figure window
            - ``'save'``: save the Matplotlib figure to ``work_dir`` (recommended for GUI training)
            - ``'none'``: skip the validation snapshot

    Note:
        Side effects: writes ``train.log``, ``history.json``, and per-improvement checkpoints to
        ``work_dir``; closes the underlying datasets of ``trn_data`` and ``vld_data`` after the final checkpoint.
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
