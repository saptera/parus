# Hierarchical Data Format (HDF) file IO module

import h5py as h5

__package__ = 'parus.fio'
__name__ = 'parus.fio.hdf'

__all__ = ['h5_load_dat', 'h5_load_ref', 'H5PklDataset', 'H5PklGroup', 'H5PklFile']
"""
Function list:
  # Standard HDF5 file IOs
    h5_load_dat(pnt): Load HDF5 data.
    h5_load_ref(ref, pnt): Load HDF5 data by reference.
  # Pickle enabled HDF5 object
    _hpo_cache {dict}: Dictionary to record pickle enabled HDF5 file objects.
    _H5PklObj: Overriding [h5py] high level object, and serve as a base class for Group and Dataset.
    H5PklDataset: Pickle serialization enabled HDF5 dataset object.
    H5PklGroup: Pickle serialization enabled HDF5 group object.
    H5PklFile: Pickle serialization enabled HDF5 file object.
"""


# Standard HDF5 file IOs --------------------------------------------------------------------------------------------- #

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


# Pickle enabled HDF5 object ----------------------------------------------------------------------------------------- #

_hpo_record = {}  # Dictionary to record pickle enabled HDF file objects


class _H5PklObj(h5.HLObject):
    """ Overriding [h5py] high level object, and serve as a base class for Group and Dataset.
        Modified from [h5pickle] package by Daan van Vugt et al. [https://github.com/DaanVanVugt/h5pickle].
    """
    def __getstate__(self):
        """ Save the current name and a reference to the root file object. """
        return {'name': self.name, 'file': self.file_info}

    def __setstate__(self, state):
        """ Reopened reference by pickle. Create steal identity of created object. """
        self.__init__(state['file'][state['name']].id)
        self.file_info = state['file']

    def __getnewargs__(self):
        """ Bypass the error raised by Pickle protocols >=2 as unable to pickle object. """
        return ()


class H5PklDataset(_H5PklObj, h5.Dataset):
    """ Pickle serialization enabled HDF5 dataset object.
        Modified from [h5pickle] package by Daan van Vugt et al. [https://github.com/DaanVanVugt/h5pickle].
    """
    pass


class H5PklGroup(_H5PklObj, h5.Group):
    """ Pickle serialization enabled HDF5 group object.
        Modified from [h5pickle] package by Daan van Vugt et al. [https://github.com/DaanVanVugt/h5pickle].
    """
    def __getitem__(self, name):
        """ Overriding standard [h5py] objects. """
        obj = h5.Group.__getitem__(self, name)
        if isinstance(obj, h5.Dataset):
            ret_obj = H5PklDataset(obj.id)
            ret_obj.file_info = self.file_info
            return ret_obj
        elif isinstance(obj, h5.Group):
            ret_obj = H5PklGroup(obj.id)
            ret_obj.file_info = self.file_info
            return ret_obj
        elif isinstance(obj, h5.File):
            return H5PklFile(obj.id)
        else:
            return obj


class H5PklFile(h5.File):
    """ Pickle serialization enabled HDF5 file object.
        Modified from [h5pickle] package by Daan van Vugt et al. [https://github.com/DaanVanVugt/h5pickle].
    """
    def __new__(cls, *args, **kwargs):
        """ Create a new HDF5 file object, or recreate with stored arguments if object no longer valid. """
        # Prepare arguments
        skip_record = kwargs.pop('skip_record', False)
        arg_hash = hash((args, tuple(sorted(kwargs.items()))))

        if skip_record or (arg_hash not in _hpo_record):
            # Create object
            self = object.__new__(cls)
            h5.File.__init__(self, *args, **kwargs)  # Open HDF5 file
            # Store args and kwargs for pickling
            self.init_args = args
            self.init_kwargs = kwargs.copy()
            self.init_kwargs['skip_record'] = skip_record
            # Record object
            if skip_record:
                self.arg_hash = None  # Disable hash record
            else:
                self.arg_hash = arg_hash  # Store argument hash value
                _hpo_record[arg_hash] = self
        else:
            # Return existing object
            self = _hpo_record[arg_hash]
        return self

    def __getitem__(self, name):
        """ Overriding standard [h5py] objects. """
        obj = h5.Group.__getitem__(self, name)
        if isinstance(obj, h5.Dataset):
            ret_obj = H5PklDataset(obj.id)
            ret_obj.file_info = self
            return ret_obj
        elif isinstance(obj, h5.Group):
            ret_obj = H5PklGroup(obj.id)
            ret_obj.file_info = self
            return ret_obj
        elif isinstance(obj, h5.File):
            return H5PklFile(obj.id)
        else:
            return obj

    def __getstate__(self):
        """ Bypass the error raised by Pickle protocols 0, 1 as unable to pickle object. """
        pass

    def __getnewargs_ex__(self):
        """ Pickle protocols >=2, dictate values passed to the [__new__]. """
        return self.init_args, self.init_kwargs

    def close(self):
        """ Override the close function to remove the file also from the cache. """
        h5.File.close(self)
        _hpo_record.pop(self.arg_hash, None)
