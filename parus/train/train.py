import os
import numpy as np
import torch
import torch.nn as nn
from parus.util import plt_mdl_perf


def train(model, criterion, optimizer, scheduler, train_datagen, val_datagen, train_hparams):

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    experiment_folder_path = train_hparams["experiment_folder_path"]
    f_path = os.path.join(experiment_folder_path, "log.txt")
    f = open(f_path, "w+")
    f.close()

    # training loop
    counter = 0
    valid_loss_min = np.Inf

    for i in range(train_hparams["epoch"]):
        for inputs, labels in train_datagen:
            model.train()
            model.zero_grad()
            inputs, labels = inputs.to(device), labels.to(device)
            output = model(inputs)
            loss = criterion(output, labels.float())
            loss.backward()
            optimizer.step()
            nn.utils.clip_grad_norm_(
                model.parameters(), train_hparams["model_param_clip"])

            counter += 1

            if counter % train_hparams["steps_every_print"] == 0:
                model.eval()
                val_losses = []
                print_sample = True
                for inp, lab in val_datagen:
                    inp, lab = inp.to(device), lab.to(device)
                    out = model(inp)
                    inp_print = inp.clone().detach()
                    inp_print = inp_print.cpu().numpy()[0][0]
                    out_print = out.cpu().clone().detach().numpy()[0][0]
                    lab_print = lab.cpu().clone().detach().numpy()[0][0] 
                    if print_sample:
                        plt_mdl_perf(out_print, inp_print, lab_print, size=(256, 32))
                        print_sample = False
                    val_loss = criterion(out, lab.float())
                    val_losses.append(val_loss.item())

                status_str = "".join(["Epoch: {}/{}...".format(i + 1, train_hparams["epoch"]),
                                      "Step: {}...".format(counter),
                                      "Learning Rate: {}...".format(optimizer.param_groups[0]['lr']),
                                      "Loss: {:.6f}...".format(loss.item()),
                                      "Val Loss: {:.6f}".format(np.mean(val_losses))])
                f = open(f_path, "a")
                f.write(status_str+"\n")
                f.close()
                print(status_str)
                if np.mean(val_losses) <= valid_loss_min:
                    model_path = os.path.join(
                        experiment_folder_path, "epoch" + str(i) + ".model")
                    torch.save(model, model_path)
                    ckpt_path = os.path.join(
                        experiment_folder_path, "epoch" + str(i) + ".ckpt")
                    torch.save(model.state_dict(), ckpt_path)
                    saving_str = 'Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
                        valid_loss_min, np.mean(val_losses))
                    f = open(f_path, "a")
                    f.write(saving_str+"\n")
                    f.close()
                    print(saving_str)
                    valid_loss_min = np.mean(val_losses)

        scheduler.step()

