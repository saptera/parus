# -*- coding: utf-8 -*-

"""Hierarchical Data Format (HDF) file IO module

Helpers for reading HDF5 datasets and pickle-compatible wrappers around the ``h5py`` high-level objects so
that file/group/dataset handles can survive ``multiprocessing`` ``spawn`` start.
"""

import h5py as h5

__package__ = 'parus.fio'
__name__ = 'parus.fio.hdf'

__all__ = ['h5_load_dat', 'h5_load_ref', 'H5PklDataset', 'H5PklGroup', 'H5PklFile']
"""
Public function list:

- h5_load_dat(pnt)        : Recursively load every dataset reachable from a file/group/dataset pointer
- h5_load_ref(ref, pnt)   : Resolve an HDF5 reference and load the referenced data

Public class list:

- H5PklDataset            : Pickle-serialisation-compatible HDF5 dataset object
- H5PklGroup              : Pickle-serialisation-compatible HDF5 group object
- H5PklFile               : Pickle-serialisation-compatible HDF5 file object

Private members:

- _hpo_record (dict)      : Cache of pickle-compatible HDF5 file objects, keyed by argument hash
- _H5PklObj               : Common pickling mixin used by :class:`H5PklDataset` and :class:`H5PklGroup`
"""


# Standard HDF5 file IOs --------------------------------------------------------------------------------------------- #

def h5_load_dat(pnt):
    """Recursively load every dataset reachable from an HDF5 file, group, or dataset pointer.

    A dataset is materialised via ``[()]``, while a file or group is walked breadth-first and returned as a nested
    :class:`dict` mirroring the on-disk hierarchy.

    Args:
        pnt (h5.File | h5.Group | h5.Dataset): HDF5 file, group, or dataset handle

    Returns:
        Loaded data; an :class:`numpy.ndarray` (or scalar) when ``pnt`` is a dataset, otherwise a nested
            dictionary mirroring the group structure
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
    """Resolve an HDF5 reference and load the referenced data.

    A region reference is dereferenced directly against ``pnt`` to obtain the selected slice, while an object reference
    is dereferenced and then handed to :func:`h5_load_dat` for recursive loading.

    Args:
        ref (h5.Reference | h5.RegionReference): HDF5 object or region reference to dereference
        pnt (h5.File | h5.Dataset): File handle that contains the referenced object, or the dataset that
            holds the reference's region selection

    Returns:
        Loaded data; an :class:`numpy.ndarray` slice for a region reference, otherwise the result of
            :func:`h5_load_dat` on the dereferenced target
    """
    if isinstance(ref, h5.RegionReference):
        return pnt[ref]
    else:
        tgt = pnt[ref]
        return h5_load_dat(tgt)


# Pickle compatible HDF5 object -------------------------------------------------------------------------------------- #

_hpo_record = {}  # Dictionary to record pickle compatible HDF file objects


class _H5PklObj(h5.HLObject):
    """Private mixin that adds pickle support to ``h5py`` high-level objects.

    Adapted from the `h5pickle <https://github.com/DaanVanVugt/h5pickle>`_ package by Daan van Vugt et al.
    Used as a base class by :class:`H5PklDataset` and :class:`H5PklGroup`.
    """

    def __getstate__(self):
        """Capture the object's HDF5 path together with a reference to its root file."""
        return {'name': self.name, 'file': self.file_info}

    def __setstate__(self, state):
        """Reopen the object via its parent file and adopt the resulting identity.

        Args:
            state (dict): Pickled state produced by :meth:`__getstate__`
        """
        self.__init__(state['file'][state['name']].id)
        self.file_info = state['file']

    def __getnewargs__(self):
        """Return an empty tuple so ``pickle`` protocols ``>=2`` skip ``__new__`` reconstruction."""
        return ()


class H5PklDataset(_H5PklObj, h5.Dataset):
    """Pickle-serialisation-compatible HDF5 dataset object.

    Combines ``_H5PklObj`` and :class:`h5py.Dataset` so dataset handles can be transferred across process boundaries.
    Adapted from the `h5pickle <https://github.com/DaanVanVugt/h5pickle>`_ package by Daan van Vugt et al.
    """
    pass


class H5PklGroup(_H5PklObj, h5.Group):
    """Pickle-serialisation-compatible HDF5 group object.

    Combines ``_H5PklObj`` and :class:`h5py.Group` so group handles can be transferred across process boundaries.
    Indexing returns wrapped pickle-compatible children rather than raw ``h5py`` objects. Adapted from the
    `h5pickle <https://github.com/DaanVanVugt/h5pickle>`_ package by Daan van Vugt et al.
    """

    def __getitem__(self, name):
        """Return a pickle-compatible wrapper around the child object referenced by ``name``.

        Args:
            name (str): Name of the child dataset or group to retrieve

        Returns:
            H5PklDataset | H5PklGroup | H5PklFile | object: Pickle-compatible wrapper for HDF5 children, or
                the underlying ``h5py`` object when no wrapper applies
        """
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
    """Pickle-serialisation-compatible HDF5 file object.

    Caches every successfully opened file by its constructor arguments so that subsequent calls return the existing
    handle rather than reopening the file. Indexing returns pickle-compatible wrappers in the same way as
    :class:`H5PklGroup`. Adapted from the `h5pickle <https://github.com/DaanVanVugt/h5pickle>`_ package by Daan van
    Vugt et al.

    Note:
        The handle is cached in ``_hpo_record``. Pass ``skip_record=True`` to bypass the cache when an independent
        handle is required (for example when reopening the same file in a different mode).
    """

    def __init__(self, *args, **kwargs):
        """Document the constructor arguments forwarded by ``__new__``.

        Args:
            *args: Positional arguments forwarded to :class:`h5py.File`
            **kwargs: Keyword arguments forwarded to :class:`h5py.File`; the additional flag
                ``skip_record`` (bool) bypasses the open-file cache when set to :data:`True`

        Note:
            The actual file initialisation happens in ``__new__``; this no-op overrides the inherited
            :class:`h5py.File` constructor so it does not run a second time after ``__new__``.
        """
        pass

    def __new__(cls, *args, **kwargs):
        """Return a cached file object when available, otherwise create a new one.

        The constructor arguments are hashed and stored on the returned instance so the file can be reopened
        transparently after unpickling.

        Returns:
            H5PklFile: The cached or newly constructed file handle
        """
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
        """Return a pickle-compatible wrapper around the top-level child referenced by ``name``.

        Args:
            name (str): Name of the child dataset or group to retrieve

        Returns:
            H5PklDataset | H5PklGroup | H5PklFile | object: Pickle-compatible wrapper for HDF5 children, or
                the underlying ``h5py`` object when no wrapper applies
        """
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
        """No-op state capture so ``pickle`` protocols ``0`` and ``1`` succeed without raising."""
        pass

    def __getnewargs_ex__(self):
        """Return the original ``args`` and ``kwargs`` so ``pickle`` protocols ``>=2`` rebuild via ``__new__``.

        Returns:
            tuple[tuple, dict]: The positional and keyword arguments stored at construction time
        """
        return self.init_args, self.init_kwargs

    def close(self):
        """Close the underlying file and remove the corresponding entry from the open-file cache."""
        h5.File.close(self)
        _hpo_record.pop(self.arg_hash, None)
