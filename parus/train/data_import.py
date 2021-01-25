import numpy as np
from parus.data.intan_func import intan_amp_read


def import_intan_amp(amp_file, length=300, overlap=50):
    """ Import IntanTech RHD2000 amplifier data for model inference.

    Args:
        amp_file (str): IntanTech RHD2000 "One File Per Channel" formatted amplifier file.
        length (int): Length of cut sample from amplifier data.
        overlap (int): Overlap length between 2 cut sample.

    Returns:
        np.ndarray: {2D} Imported IntanTech RHD2000 amplifier data for model inference.
    """
    # Import data
    data = intan_amp_read(amp_file)
    # Get range
    idx_start = np.arange(start=0, stop=len(data), step=length - overlap, dtype=np.uint32)
    idx_stop = np.add(idx_start, length)
    # Padding data
    pad_len = idx_stop[-1] - len(data)
    if pad_len >= 0:
        data = np.append(data, np.full(pad_len, data[-1]))
    # Rearrange data into a 2D-array
    dst = np.empty((len(idx_start), length), dtype=data.dtype)
    for i in range(len(idx_start)):
        dst[i] = data[idx_start[i]:idx_stop[i]]
    return dst
