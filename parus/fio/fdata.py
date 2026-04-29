# -*- coding: utf-8 -*-

"""Customized data file IO module

Readers, writers, and helpers for PARUS-defined data files.
"""

import os
import warnings
import base64
import json
import zlib
import hashlib
import pickle as pkl
import h5py as h5
import matplotlib.pyplot as plt

__package__ = 'parus.fio'
__name__ = 'parus.fio.fdata'

__all__ = [
    'pklz_read', 'pklz_write', 'cjsh_read', 'cjsh_write',
    'arc_read', 'arc_write', 'arc_plot', 'noi_read', 'noi_write',
    'sim_args_read', 'sim_data_read'
]
"""
Public function list:

- Generic compressed-payload IO:

    - pklz_read(file)                          : Read compressed pickled data from a file
    - pklz_write(file, data, level)            : Write compressed pickled data to a file
    - cjsh_read(file)                          : Read a compressed JSON with secure hash (CJSH) file
    - cjsh_write(file, data, level)            : Write a compressed JSON with secure hash (CJSH) file

- Neural data file IO:

    - arc_read(arc_file)                       : Read an archival neural signal data file (`*.arc`)
    - arc_write(arc_file, arc_data)            : Write an archival neural signal data file (`*.arc`)
    - arc_plot(arc_file, save, close_on_save)  : Plot an archival neural signal sample
    - noi_read(noi_file)                       : Read a recording noise sample file (`*.noi`)
    - noi_write(noi_file, noi_data)            : Write a recording noise sample file (`*.noi`)

- Simulated data IO:

    - sim_args_read(sim_fp)                    : Read simulated signal generation parameters
    - sim_data_read(sim_fp, idx, ex)           : Read a single simulated signal sample
"""


# Basic file IO functions -------------------------------------------------------------------------------------------- #

def pklz_read(file):
    """Read compressed-pickled data from a file.

    The on-disk format is the output of :func:`pklz_write`: a zlib-compressed pickle stream wrapped inside
    an outer pickle stream.

    Args:
        file (str): Path to the compressed-pickle file (``*.pkl`` | ``*.pkz`` | ``*.pklz``)

    Returns:
        Any: The decoded payload
    """
    with open(file, 'rb') as infile:
        comp = pkl.load(infile)
    data = pkl.loads(zlib.decompress(comp))
    return data


def pklz_write(file, data, level=-1):
    """Write compressed-pickled data to a file.

    The payload is pickled, zlib-compressed at level ``level``, and the resulting bytes are pickled again
    into ``file`` so the wrapper stays a single pickle object.

    Args:
        file (str): Path to the output file (``*.pkl`` | ``*.pkz`` | ``*.pklz``)
        data (Any): Picklable payload
        level (int): zlib compression level in ``[-1, 9]``; ``-1`` selects zlib's default (default: ``-1``)

    Returns:
        bool: :data:`True` on success, :data:`False` when an :class:`OSError` is raised while writing

    Warns:
        Warning: Emitted with the original :class:`OSError` message when the file cannot be written
    """
    comp = zlib.compress(pkl.dumps(data, protocol=None), level=level)
    try:
        with open(file, 'wb') as outfile:
            pkl.dump(comp, outfile, protocol=None)
        return True
    except OSError as x:
        warnings.warn("[Errno %d] when writing file '%s': %s" % (x.errno, file, x.strerror), Warning, stacklevel=2)
        return False


def cjsh_read(file):
    """Read a compressed JSON with secure hash (CJSH) file.

    The on-disk format is a zlib-compressed outer JSON document of the form
    ``{"arc": <base64(zlib(payload_json))>, "cks": <sha256(payload_json)>}``. After decompression, the SHA-256
    checksum of the payload is recomputed and compared against the stored ``cks`` field.

    Args:
        file (str): Path to the CJSH file (``*.cjh`` | ``*.cjsh``)

    Returns:
        Any | None: The decoded payload, or :data:`None` when the recomputed SHA-256 does not match the
            stored checksum
    """
    # Read data from the file
    with open(file, 'rb') as infile:
        indata = json.loads(zlib.decompress(infile.read()).decode('ascii'))
    # Decode the data and compute the hash value
    serialized = zlib.decompress(base64.b64decode(indata['arc'].encode('ascii')))
    checksum = hashlib.sha256(serialized).hexdigest()
    # Verify and output the decoded data
    if checksum == indata['cks']:
        data = json.loads(serialized.decode('utf-8'))
    else:
        print('Data corrupted in file: %s!' % file)
        data = None
    return data


def cjsh_write(file, data, level=-1):
    """Write data to a compressed JSON with secure hash (CJSH) file.

    The payload is JSON-encoded, base64-wrapped after zlib compression, and stored together with its SHA-256 checksum
    in an outer JSON document; the outer document is then zlib-compressed again before being written.

    Args:
        file (str): Path to the output file (``*.cjh`` | ``*.cjsh``)
        data (Any): JSON-serialisable payload
        level (int): zlib compression level for the inner payload in ``[-1, 9]``; ``-1`` selects zlib's
            default (default: ``-1``)

    Returns:
        bool: :data:`True` on success, :data:`False` when an :class:`OSError` is raised while writing

    Warns:
        Warning: Emitted with the original :class:`OSError` message when the file cannot be written
    """
    # Serialize input data to JSON format
    serialized = json.dumps(data, skipkeys=False, ensure_ascii=False, allow_nan=True).encode('utf-8')
    # Compress and hash the serialized data
    compressed = base64.b64encode(zlib.compress(serialized, level=level)).decode('ascii')
    checksum = hashlib.sha256(serialized).hexdigest()
    # Compress the processed data with its hash value
    outdata = zlib.compress(json.dumps({'arc': compressed, 'cks': checksum}).encode('ascii'), level=0)
    # Write to the file
    try:
        with open(file, 'wb') as outfile:
            outfile.write(outdata)
        return True
    except OSError as x:
        warnings.warn("[Errno %d] when writing file '%s': %s" % (x.errno, file, x.strerror), Warning, stacklevel=2)
        return False


# Neural data file IO functions -------------------------------------------------------------------------------------- #

"""ARC data structure definition:

arc_data (dict)                       : Archival neural signal sample
    data (dict)                           : Signal data
        sig (list[float])                     : Neural signal samples
        pos (int)                             : Index of the spike location within `sig`
        rng (list[int, int] | None)           : Two indices defining the refined signal range
        freq (int | float)                    : Recording sampling frequency of `sig`
    meta (dict)                       : Metadata accompanying the signal
        organism (dict)                   : Organism the signal was recorded from
            gn (str)                          : Generic (genus) name
            se (str)                          : Specific epithet
            st (str)                          : Strain
            mod (str | None)                  : Genetic modification, None for wildtype
            note (Any)                        : Free-form notes
        region (list)                     : Recording region(s) of the signal
        neuron (dict)                     : Neural cell information
            typ (str)                         : Cell type
            spk (str)                         : Spike type - 'ss' simple spike, 'cs' complex spike, 'fp' field potential
            note (Any)                        : Free-form notes
        system (dict)                     : Recording system information
            typ (str)                         : System type - 'd' digital or 'a' analog
            mfr (str)                         : System manufacturer
            pn (str)                          : Manufacturer part number or model
            sn (str)                          : Manufacturer serial number or batch number
            soc (int | float | str)           : Socket in the system used for recording
            note (Any)                        : Free-form notes
        probe (dict)                      : Recording probe information
            typ (str)                         : Probe type - 'si' silicon, 'w' tungsten, 'gls' glass pipette, etc.
            mfr (str)                         : Probe manufacturer
            pn (str)                          : Manufacturer part number or model
            sn (str)                          : Manufacturer serial number or batch number
            chn (int | float)                 : Recording site channel number
            note (Any)                        : Free-form notes
        datetime (str)                    : Recording date and time in ISO-8601 format
"""


def arc_read(arc_file):
    """Read an archival neural signal data file.

    The function delegates to :func:`cjsh_read` and validates that the decoded dictionary has the expected ARC layout
    (a ``data`` and ``meta`` block, each with the required keys).

    Args:
        arc_file (str): Path to the archival neural signal file (``*.arc``)

    Returns:
        dict | None: The ARC dictionary on success, or :data:`None` when the payload is missing required
            sections or has illegal keys (see the ARC schema in this module)

    Warns:
        Warning: Emitted when ``data`` or ``meta`` is missing, or when their key sets do not match the ARC schema
    """
    # Read file
    arc_data = cjsh_read(arc_file)
    # Verify signal data
    if 'data' in arc_data:
        if {'sig', 'pos', 'rng', 'freq'} != set(arc_data['data']):
            warnings.warn("Illegal signal data in [%s], file not imported!" % arc_file, Warning, stacklevel=2)
            return None
    else:
        warnings.warn("Missing signal data in [%s], file not imported!" % arc_file, Warning, stacklevel=2)
        return None
    # Verify metadata
    if 'meta' in arc_data:
        if {'organism', 'region', 'neuron', 'system', 'probe', 'datetime'} != set(arc_data['meta']):
            warnings.warn("Illegal metadata in [%s], file not imported!" % arc_file, Warning, stacklevel=2)
            return None
    else:
        warnings.warn("Missing metadata in [%s], file not imported!" % arc_file, Warning, stacklevel=2)
        return None
    # Return data after validation
    return arc_data


def arc_write(arc_file, arc_data):
    """Write an archival neural signal data file.

    The ARC dictionary is validated against the expected layout and written via :func:`cjsh_write` at the maximum
    compression level (``9``).

    Args:
        arc_file (str): Path to the output archival neural signal file (``*.arc``)
        arc_data (dict): ARC dictionary as defined by the ARC schema in this module

    Returns:
        bool: :data:`True` when the file was written, :data:`False` when ``arc_data`` failed validation

    Warns:
        Warning: Emitted when ``data`` or ``meta`` is missing, or when their key sets do not match the ARC schema
    """
    # Verify signal data
    if 'data' in arc_data:
        if {'sig', 'pos', 'rng', 'freq'} != set(arc_data['data']):
            warnings.warn("Illegal signal data in [%s], file not created!" % arc_file, Warning, stacklevel=2)
            return False
    else:
        warnings.warn("Missing signal data in [%s], file not created!" % arc_file, Warning, stacklevel=2)
        return False
    # Verify metadata
    if 'meta' in arc_data:
        if {'organism', 'region', 'neuron', 'system', 'probe', 'datetime'} != set(arc_data['meta']):
            warnings.warn("Illegal metadata in [%s], file not created!" % arc_file, Warning, stacklevel=2)
            return False
    else:
        warnings.warn("Missing metadata in [%s], file not created!" % arc_file, Warning, stacklevel=2)
        return False
    # Saving data
    cjsh_write(arc_file, arc_data, level=9)
    return True


def arc_plot(arc_file, save=None, close_on_save=True):
    """Plot the signal trace of an archival neural signal file.

    The signal is rendered as a line plot with the spike peak marked, and the refined signal range (if provided)
    drawn as two vertical reference lines.

    Args:
        arc_file (str): Path to the archival neural signal file (``*.arc``)
        save (str | bool | None): Output PNG path; pass :data:`True` to reuse ``arc_file`` (with the
            extension swapped to ``.png``); pass :data:`None` or :data:`False` to skip saving
            (default: ``None``)
        close_on_save (bool): When :data:`True` and ``save`` is truthy, close the figure after saving and
            return ``(None, None)`` instead of the live handles (default: ``True``)

    Returns:
        tuple[plt.Figure | None, plt.Axes | None]: Figure and axes objects, or ``(None, None)`` when the
            figure was saved and closed
    """
    # Import data
    data = arc_read(arc_file)['data']
    t = list(range(len(data['sig'])))
    # Get spike peak labels
    peak_t = t[data['pos']]
    peak_sig = data['sig'][data['pos']]
    # Get signal range
    sig_rng = data['rng'] if data['rng'] is not None else None
    # Setup plot
    name = os.path.basename(arc_file).rstrip('.arc')
    fig, ax = plt.subplots(1, 1, num="Archival Signal of [%s]" % name, dpi=150)
    fig.set_layout_engine(layout='tight')
    ax.set_title("Archival Signal\n[%s]" % name, fontsize=12, fontweight='bold')
    ax.set_xlabel("Data Point", fontsize=12)
    ax.set_ylabel("Amplitude", fontsize=12)
    # Plotting
    ax.plot(t, data['sig'], lw=1.5, zorder=1)
    ax.scatter(peak_t, peak_sig, marker='x', c='r', s=64, alpha=0.75, zorder=4)
    # Add reference lines
    ax.axhline(0, c='darkgray', lw=0.5, alpha=0.75, zorder=2)
    if sig_rng is not None:
        ax.axvline(sig_rng[0], c='gray', ls='-.', lw=1, alpha=0.75, zorder=3)
        ax.axvline(sig_rng[1], c='gray', ls='-.', lw=1, alpha=0.75, zorder=3)
    # Saving function
    if save:
        if isinstance(save, str):
            fig.savefig(os.path.splitext(save)[0] + '.png', format='png')
        else:
            fig.savefig(os.path.splitext(arc_file)[0] + '.png', format='png')
        # Close figure
        if close_on_save:
            plt.close(fig)
            return None, None
    # Return figure
    return fig, ax


"""NOI data structure definition:

noi_data (dict)                 : Recording noise sample
    data (dict)                     : Noise data
        noi (list[float])               : Recording noise samples
        freq (int | float)              : Recording sampling frequency of `noi`
    meta (dict)                 : Metadata accompanying the noise sample
        organism (dict)             : Organism the signal was recorded from
            gn (str)                    : Generic (genus) name
            se (str)                    : Specific epithet
            st (str)                    : Strain
            mod (str | None)            : Genetic modification, None for wildtype
            note (Any)                  : Free-form notes
        region (list)               : Recording region(s) of the signal
        feature (dict)              : Recorded features in the noise signal
            typ (list[str])             : Existing noise - 'fp' field potential, 'ele' elec-stim, 'opto' opto-stim, etc.
            note (Any)                  : Free-form notes
        system (dict)               : Recording system information
            typ (str)                   : System type - 'd' digital or 'a' analog
            mfr (str)                   : System manufacturer
            pn (str)                    : Manufacturer part number or model
            sn (str)                    : Manufacturer serial number or batch number
            soc (int | float | str)     : Socket in the system used for recording
            note (Any)                  : Free-form notes
        probe (dict)                : Recording probe information
            typ (str)                   : Probe type - 'si' silicon, 'w' tungsten, 'gls' glass pipette, etc.
            mfr (str)                   : Probe manufacturer
            pn (str)                    : Manufacturer part number or model
            sn (str)                    : Manufacturer serial number or batch number
            chn (int | float)           : Recording site channel number
            note (Any)                  : Free-form notes
        datetime (str)              : Recording date and time in ISO 8601 format
"""


def noi_read(noi_file):
    """Read a recording noise sample file.

    The function delegates to :func:`cjsh_read` and validates that the decoded dictionary has the expected NOI layout
    (a ``data`` and ``meta`` block, each with the required keys).

    Args:
        noi_file (str): Path to the recording noise sample file (``*.noi``)

    Returns:
        dict | None: The NOI dictionary on success, or :data:`None` when the payload is missing required
            sections or has illegal keys (see the NOI schema in this module)

    Warns:
        Warning: Emitted when ``data`` or ``meta`` is missing, or when their key sets do not match the NOI schema
    """
    # Read file
    noi_data = cjsh_read(noi_file)
    # Verify noise data
    if 'data' in noi_data:
        if {'noi', 'freq'} != set(noi_data['data']):
            warnings.warn("Illegal noise data in [%s], file not imported!" % noi_file, Warning, stacklevel=2)
            return None
    else:
        warnings.warn("Missing noise data in [%s], file not imported!" % noi_file, Warning, stacklevel=2)
        return None
    # Verify metadata
    if 'meta' in noi_data:
        if {'organism', 'region', 'feature', 'system', 'probe', 'datetime'} != set(noi_data['meta']):
            warnings.warn("Illegal metadata in [%s], file not imported!" % noi_file, Warning, stacklevel=2)
            return None
    else:
        warnings.warn("Missing metadata in [%s], file not imported!" % noi_file, Warning, stacklevel=2)
        return None
    # Return data after validation
    return noi_data


def noi_write(noi_file, noi_data):
    """Write a recording noise sample file.

    The NOI dictionary is validated against the expected layout and written via :func:`cjsh_write` at the maximum
    compression level (``9``).

    Args:
        noi_file (str): Path to the output recording noise sample file (``*.noi``)
        noi_data (dict): NOI dictionary as defined by the NOI schema in this module

    Returns:
        bool: :data:`True` when the file was written, :data:`False` when ``noi_data`` failed validation

    Warns:
        Warning: Emitted when ``data`` or ``meta`` is missing, or when their key sets do not match the NOI schema
    """
    # Verify noise data
    if 'data' in noi_data:
        if {'noi', 'freq'} != set(noi_data['data']):
            warnings.warn("Illegal noise data in [%s], file not created!" % noi_file, Warning, stacklevel=2)
            return False
    else:
        warnings.warn("Missing noise data in [%s], file not created!" % noi_file, Warning, stacklevel=2)
        return False
    # Verify metadata
    if 'meta' in noi_data:
        if {'organism', 'region', 'feature', 'system', 'probe', 'datetime'} != set(noi_data['meta']):
            warnings.warn("Illegal metadata in [%s], file not created!" % noi_file, Warning, stacklevel=2)
            return False
    else:
        warnings.warn("Missing metadata in [%s], file not created!" % noi_file, Warning, stacklevel=2)
        return False
    # Saving data
    cjsh_write(noi_file, noi_data, level=9)
    return True


# Simulated data reading functions ----------------------------------------------------------------------------------- #

def sim_args_read(sim_fp):
    """Read the generation parameters of a simulated signal HDF5 file.

    Walks the ``args`` group of ``sim_fp`` and converts the stored values back to native Python types: byte strings
    are decoded as UTF-8 (with the literal sentinel ``"NULL"`` mapped to :data:`None`), arrays of byte strings are
    decoded element-wise, and scalar arrays are unwrapped via :meth:`numpy.ndarray.item`.

    Args:
        sim_fp (h5.File): Open simulated signal data file

    Returns:
        dict[str, Any]: Generation parameter name to native value mapping
    """
    kl = list(sim_fp['args'].keys())
    arg = {k: None for k in kl}  # INIT VAR
    for k in kl:
        v = sim_fp['args'][k][()]
        if isinstance(v, bytes):
            dc = v.decode('utf-8')
            if dc != 'NULL':
                arg[k] = dc
        elif v.dtype.kind == 'S':
            arg[k] = [i.decode() for i in v]
        else:
            if v.size == 1:
                arg[k] = v.item()
            else:
                arg[k] = v.tolist()
    return arg


def sim_data_read(sim_fp, idx, ex=False):
    """Read a single simulated signal sample from a simulated signal HDF5 file.

    Standard simulated samples live under the ``sims`` group; extra (validation/special) samples live under the
    ``exeg`` group. The function returns :data:`None` and warns when ``idx`` does not exist.

    Args:
        sim_fp (h5.File): Open simulated signal data file
        idx (int): Sample index to read
        ex (bool): When :data:`True` read from the ``exeg`` group of extra samples; when :data:`False`
            read from the ``sims`` group of standard samples (default: ``False``)

    Returns:
        dict | None: Sample dictionary, or :data:`None` when ``idx`` is not present in the requested group

            - sig (np.ndarray): {1D-scalar} Simulated signal data
            - lbl (dict[str, list[np.ndarray] | np.ndarray]): Ground truth of ``sig``

                - signal (list[np.ndarray]): {1D-scalar} Grouped noise-free signal contributions
                - noise (np.ndarray): {1D-scalar} Noise ground truth of ``sig``

            - pos (np.ndarray): {1D-0|1} One-hot spike position label of ``sig``
            - typ (str): Sample generation type (``'sim'`` standard, ``'nrm'`` extra standard, ``'spc'``
              extra special)

    Warns:
        RuntimeWarning: Emitted when ``idx`` is not present in the requested group
    """
    grp = 'exeg' if ex else 'sims'
    pos_ref = sim_fp.get("%s/%d" % (grp, idx), None)
    if pos_ref is None:
        warnings.warn("Invalid index: %d" % idx, RuntimeWarning, stacklevel=2)
        return None
    else:
        return {
            'sig': sim_fp[grp][str(idx)]['sig'][()],
            'lbl': {k: sim_fp[grp][str(idx)]['lbl'][k][()] for k in ['signal', 'noise']},
            'pos': sim_fp[grp][str(idx)]['pos'][()],
            'typ': sim_fp[grp][str(idx)].attrs.get('type', None)
        }
