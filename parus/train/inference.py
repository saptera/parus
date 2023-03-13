import os
import torch
from parus.fio import pklz_write

def inference(model, test_datagen, test_hparams):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    pred_folder_path = os.path.join(test_hparams["experiment_folder_path"] ,"pred")
    os.mkdir(pred_folder_path)
    # prediction and saving
    with torch.no_grad():
        counter = 0
        for inputs, labels in test_datagen:
            inputs = inputs.to(device)
            outputs = model(inputs)
            
            inp = inputs.squeeze().cpu().numpy()
            pred = outputs.squeeze().cpu().numpy()
            labels = labels.squeeze().cpu().numpy()
            
            filename = "pred_" + str(counter).zfill(5) + ".sim"
            pklz_write(os.path.join(pred_folder_path, filename), {"inp":inp,  "prd": pred, "lbl": labels})
            counter += 1
