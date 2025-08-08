# Hierarchical Data Format (HDF) file IO functions

import h5py as h5

__all__ = ['h5_load_dat', 'h5_load_ref']
"""
Function list:
  h5_load_dat(pnt): Load HDF5 data.
  h5_load_ref(ref, pnt): Load HDF5 data by reference.
"""


def h5_load_dat(pnt):
    """ Load HDF5 data.

    Args:
        pnt (h5.File | h5.Group | h5.Dataset): HDF5 file/group/dataset pointer

    Returns:
        Loaded data
    """
    # Read single dataset
    if isinstance(pnt, h5.Dataset):
        return pnt[()]

    # Read HDF5 file or group
    rtv = {}  # INIT VAR
    for k in pnt.keys():
        if isinstance(pnt[k], h5.Dataset):
            rtv[k] = pnt[k][()]
        else:
            rtv[k] = h5_load_dat(pnt[k])
    return rtv


def h5_load_ref(ref, pnt):
    """ Load HDF5 data by reference.

    Args:
        ref (h5.Reference | h5.RegionReference): HDF5 object reference
        pnt (h5.File | h5.Dataset): HDF5 file/dataset pointer

    Returns:
        Loaded data
    """
    if isinstance(ref, h5.RegionReference):
        return pnt[ref]
    else:
        tgt = pnt[ref]
        return h5_load_dat(tgt)
