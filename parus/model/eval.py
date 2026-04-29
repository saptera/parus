# -*- coding: utf-8 -*-

"""Model evaluation and inference module

End-to-end inference helpers and quantitative evaluation routines for the PARUS spike-detection model.
"""

import threading
import queue
import numpy as np
import torch

__package__ = 'parus.model'
__name__ = 'parus.model.eval'
from ..data import sig_merge
from ..util import plt_mod_cli, plt_mod_img, prog_print
from .post import peak_fwd_torch

__all__ = ['Inference', 'validation', 'testing', 'eval_bin_cls']
"""
Public class list:

- Inference(model, datagen, channel, device, cmp_lvl, disp)        : Threaded inference and HDF5 result storage

Public function list:

- validation(model, datagen, criterion, device, hint, image)       : Compute validation loss for one epoch
- testing(model, datagen, channel, device, th)                     : Run the full testing set and collect predictions
- eval_bin_cls(prediction, reference, allowed_distance, ...)       : Binary detection evaluation with tolerance
"""


class Inference:
    """Run model inference over a recording and stream results to an HDF5 file.

    Two threads are used: the main thread runs the model and pushes per-batch results onto an internal
    queue; a background thread merges those batches with :func:`parus.data.sig.sig_merge` and writes them
    to per-channel datasets under ``spk/`` in the recording HDF5 file.

    Note:
        Calling :meth:`run` overwrites any existing ``spk`` group in the recording file. The underlying
        HDF5 file remains open through the dataset's lifecycle; close it via the dataset's ``close()``
        method.
    """

    def __init__(self, model, datagen, channel, device, cmp_lvl=4, disp=8):
        """Set up the inference runner and pre-allocate the per-channel output datasets.

        Args:
            model (torch.nn.Module): PyTorch model to run
            datagen (torch.utils.data.DataLoader): DataLoader wrapping a
                :class:`~parus.model.dset.InferenceDataset`
            channel (list[str]): Output channel names; one HDF5 dataset is created per name
            device (torch.device): Device to which input batches are moved
            cmp_lvl (int): gzip compression level for the per-channel datasets in ``[0, 9]``
                (default: ``4``)
            disp (int | None): Indent (in spaces) for terminal progress prints; pass :data:`None` to
                silence progress output (default: ``8``)
        """
        # Store arguments
        self.model = model
        self.channel = channel
        self.device = device
        self.datagen = datagen
        self.bs = datagen.batch_size
        self.cmp = cmp_lvl
        # Get dataset attributes
        self.__fp = self.datagen.dataset.fp
        self.tot = self.datagen.dataset.total
        self.nsp = self.datagen.dataset.n_sample
        self.seq = self.datagen.dataset.seq_len
        self.ovp = self.datagen.dataset.overlap
        self.stp = self.seq - self.ovp
        self.blk = self.stp * self.bs + self.ovp
        # Process control attributes
        self.__res_queue = queue.Queue()
        self.__file_th = threading.Thread(target=self._write_file)
        self.__proc_fin = False  # Model process finalized flag
        # Print out initialization
        self.cnt = len(self.datagen)
        self.__prog_pfx = False if disp is None else ' ' * disp + 'Data progress:'
        self.__inf_prt = False if disp is None else ' ' * disp + 'Model inference finished, results may still saving'
        self.__fio_prt = False if disp is None else ' ' * disp + 'All results have been saved to file'
        # Output initialization
        self.init_output()

    def init_output(self):
        """Pre-allocate the per-channel output datasets in the underlying HDF5 file.

        Removes any existing ``spk`` group, creates a fresh one, and adds one gzip-compressed dataset of
        shape ``(n_channels, n_samples)`` per name in ``self.channel``.
        """
        shape = self.datagen.dataset.data.shape
        # Remove existing groups
        if 'spk' in self.__fp:
            del self.__fp['spk']
        grp = self.__fp.create_group('spk')
        # Creating datasets in file
        for k in self.channel:
            grp.create_dataset(name=k, shape=shape, dtype=np.float32, chunks=True,
                               compression='gzip', compression_opts=self.cmp)

    def _model_proc(self):
        """Run the model over every batch from ``self.datagen`` and push the outputs onto the result queue."""
        self.__proc_fin = False
        for count, inputs in enumerate(self.datagen):
            # Process inference
            inputs = inputs.to(self.device)
            outputs = self.model(inputs)
            res = outputs.cpu().numpy()
            # Put result to queue
            self.__res_queue.put((count, res))
            self.__prog_pfx and prog_print(count, self.cnt, prefix=self.__prog_pfx)
        # Inform file saving thread
        self.__proc_fin = True
        self.__inf_prt and print(self.__inf_prt)

    def _write_file(self):
        """Drain the result queue and merge each batch into the per-channel HDF5 datasets.

        Runs until the model thread has finished and the queue is empty. Overlapping samples between
        consecutive sliding windows are averaged so the merged trace is continuous across batch boundaries.
        """
        while not (self.__proc_fin and self.__res_queue.empty()):
            count, res = self.__res_queue.get()
            # Process saving
            bat_loc = count * self.bs  # Batched data starting index
            bat_end = bat_loc + res.shape[0]  # Batched data terminal index
            bat_pnt = 0  # Batch index pointer
            while bat_loc < bat_end:
                chn_num, smp_idx = divmod(bat_loc, self.nsp)  # Get current raw data channel and sampling step indices
                i = smp_idx * self.stp  # Data elements starting index
                smp_end = min(self.nsp, bat_end - bat_loc + smp_idx)
                e = smp_end * self.stp + self.ovp  # Data elements terminal index
                # Store results
                l = smp_end - smp_idx  # Total number of sampling steps
                trim = e - self.tot if e > self.tot else 0
                for n, k in enumerate(self.channel):
                    arr = sig_merge(res[bat_pnt:bat_pnt+l, n, :], overlap=self.ovp, trim=trim)
                    if i != 0:
                        arr[:self.ovp] = (arr[:self.ovp] + self.__fp['spk'][k][chn_num, i:i+self.ovp]) / 2
                    self.__fp['spk'][k][chn_num, i:e] = arr
                # Counter
                bat_pnt += l
                bat_loc += l
        self.__fio_prt and print(self.__fio_prt)

    def run(self):
        """Start the file-writer thread, run the model on the main thread, and wait for both to finish."""
        self.__file_th.start()
        self._model_proc()  # Running model on the main thread
        self.__file_th.join()


def validation(model, datagen, criterion, device, hint='text', image=None):
    """Run a validation pass and return the mean loss across the loader.

    Optionally renders the prediction-vs-label snapshot of the first sample using
    :func:`parus.util.disp.plt_mod_cli` or :func:`parus.util.disp.plt_mod_img` according to ``hint``.

    Args:
        model (torch.nn.Module): PyTorch model
        datagen (torch.utils.data.DataLoader): Validation dataset loader
        criterion (torch.nn.Module): Loss function
        device (torch.device): Device on which the model and data live
        hint (str): Visualisation method for the first-sample snapshot; one of ``{'text', 'disp', 'save', 'none'}``
            (default: ``'text'``)

            - ``'text'``: render an ASCII plot via ``plotext`` (recommended for CLI training)
            - ``'disp'``: open a Matplotlib figure window
            - ``'save'``: save the Matplotlib figure to ``image`` (recommended for GUI training)
            - ``'none'``: skip the snapshot

        image (str | None): Output PNG path used when ``hint == 'save'`` (default: ``None``)

    Returns:
        float: Mean of the per-batch validation losses
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
    """Run the full testing set and collect inputs, predictions, and references in a single dictionary.

    Builds binary spike-position predictions from the raw model output via :func:`parus.model.post.peak_fwd_torch`
    with threshold ``th``.

    Args:
        model (torch.nn.Module): PyTorch model
        datagen (torch.utils.data.DataLoader): Testing dataset loader
        channel (int): Number of model output channels
        device (torch.device): Device on which the model and data live
        th (int | float): Minimum peak threshold for :func:`parus.model.post.peak_fwd_torch`; the default
            ``-1`` is chosen so the threshold sits below typical baseline fluctuation (default: ``-1``)

    Returns:
        dict: Per-sample testing results

            - inp (np.ndarray): {3D-float32} Input signal arrays
            - prd (dict): Model prediction
                - spk (np.ndarray): {3D-float32} Predicted spike signal
                - pos (np.ndarray): {3D-int8} Predicted spike position (one-hot)
            - lbl (dict): Ground-truth labels
                - spk (np.ndarray): {3D-float32} Reference spike signal
                - pos (np.ndarray): {3D-int8} Reference spike position (one-hot)
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
        inp_arr[s:e] = inputs.cpu().numpy().squeeze()
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


def eval_bin_cls(prediction, reference, allowed_distance=0, binary_threshold=0.5):
    """Evaluate binary spike detections with an index tolerance and report sensitivity/specificity factors.

    Reports two numbers: the on-target accuracy (the percentage of reference spikes that have at least one
    prediction within ``allowed_distance`` samples) and a per-element confusion vector summarising true
    positives, true negatives, false positives, and false negatives across the whole tensor.

    Args:
        prediction (torch.Tensor): {3D} Model prediction tensor
        reference (torch.Tensor): {3D} Ground-truth reference tensor with the same shape as ``prediction``
        allowed_distance (int): Index tolerance in samples for the on-target accuracy (default: ``0``)
        binary_threshold (int | float): Threshold used to binarise both tensors before counting (default: ``0.5``)

    Returns:
        tuple[float, dict[str, int]]: On-target accuracy and confusion factors

            - ota (float): On-target accuracy as a percentage
            - sas (dict[str, int]): Confusion factors with keys ``tp``, ``tn``, ``fp``, ``fn``
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
