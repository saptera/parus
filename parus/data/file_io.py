import os
import warnings
import base64
import json
import zlib
import hashlib
import pickle as pkl
import matplotlib.pyplot as plt

"""Function list:
# Basic file IO functions:
    pklz_read(file): Read compressed pickled data from a file.
    pklz_write(file, data): Write compressed pickled data to a file.
    cjsh_read(file): Compressed JSON with Secure Hash embedded (CJSH) file, reading function.
    cjsh_write(file, data): Compressed JSON with Secure Hash embedded (CJSH) file, writing function.
# Neural data file IO functions:
  -> ARC data structure definition
    arc_read(arc_file): Read archival neural signal data file.
    arc_write(arc_file, arc_data): Write archival neural signal data file.
    arc_plot(arc_file, save=False): Plot archival neural signal data.
  -> NOI data structure definition
    noi_read(noi_file): Read recording noise sample file.
    noi_write(noi_file, noi_data): Write recording noise sample file.
"""


# Basic file IO functions -------------------------------------------------------------------------------------------- #

def pklz_read(file):
    """ Read compressed pickled data from a file.

    Args:
        file (str): File contained compressed pickled data (*.*).

    Returns:
        data: Imported data.
    """
    with open(file, 'rb') as infile:
        comp = pkl.load(infile)
    data = pkl.loads(zlib.decompress(comp))
    return data


def pklz_write(file, data):
    """ Write compressed pickled data to a file.

    Args:
        file (str): File to write data (*.*).
        data: Any type of picklable data.

    Returns:
        bool: File creation status.
    """
    comp = zlib.compress(pkl.dumps(data, protocol=None))
    with open(file, 'wb') as outfile:
        pkl.dump(comp, outfile, protocol=None)
    return True


def cjsh_read(file):
    """ Compressed JSON with Secure Hash embedded (CJSH) file, reading function.

    Args:
        file (str): File contained compressed JSON data (*.*).

    Returns:
        Imported data.
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


def cjsh_write(file, data):
    """ Compressed JSON with Secure Hash embedded (CJSH) file, writing function.

    Args:
        file (str): Output file name.
        data: Any type of data that is JSON serializable.

    Returns:
        bool: File creation status.
    """
    # Serialize input data to JSON format
    serialized = json.dumps(data, skipkeys=False, ensure_ascii=False, allow_nan=True).encode('utf-8')
    # Compress and hash the serialized data
    compressed = base64.b64encode(zlib.compress(serialized, level=9)).decode('ascii')
    checksum = hashlib.sha256(serialized).hexdigest()
    # Compress the processed data with its hash value
    outdata = zlib.compress(json.dumps({'arc': compressed, 'cks': checksum}).encode('ascii'), level=9)
    # Write to the file
    with open(file, 'wb') as outfile:
        outfile.write(outdata)
    return True


# Neural data file IO functions -------------------------------------------------------------------------------------- #

""" ARC data structure definition:
    arc_data (dict): archival neural signal: {
        data (dict): signal data structure {
            sig (list[float]): neural signal data
            pos (int): index of spike location in [sig]
            rng (list[int, int] or None): 2 indices to define refined signal range
            freq (int or float): recording frequency of [sig]
        }
        meta (dict): metadata structure of the signal {
            organism (dict): organism for the signal recording {
                gn (str): generic name
                se (str): specific epithet
                st (str): strain,
                mod (str or None): genetic modification, None for wildtype
                note (Any): extra notes
            }
            region (list): recoding region(s) of the signal
            neuron (dict): neural cell information {
                typ (str): cell type
                spk (str): spike type - 'ss' for simple spike, 'cs' for complex spike or 'fp' for field potential
                note (Any): extra notes
            }
            system (dict): recording system information {
                typ (str): system type - 'd' for digital or 'a' for analog
                mfr (str): system manufacture
                pn (str): manufacture part number or model
                sn (str): manufacture serial number or batch number
                soc (int or float or str): Socket in system for recording
                note (Any): extra notes
            }
            probe (dict): recording probe information {
                typ (str): probe type - 'si' for silicon, 'w' for tungsten, 'gls' for glass pipette etc.
                mfr (str): probe manufacture
                pn (str): manufacture part number or model
                sn (str): manufacture serial number or batch number
                chn (int or float): recording site channel number
                note (Any): extra notes
            }
            datetime (str[datetime.ISO-format]): recording date and time information
        }
"""


def arc_read(arc_file):
    """ Read archival neural signal data file.

    Args:
        arc_file (str): File contained archival neuronal signal data (*.arc).

    Returns:
        dict: Archival neuronal signal sample, defined above.
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
    """ Write archival neural signal data file.

    Args:
        arc_file (str): File to write archival neuronal signal data (*.arc).
        arc_data (dict): Archival neuronal signal, defined above.

    Returns:
        bool: File creation status.
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
    cjsh_write(arc_file, arc_data)
    return True


def arc_plot(arc_file, save=False):
    """ Plot archival neural signal data.

    Args:
        arc_file (str): File contained archival neuronal signal data (*.arc).
        save (bool): Defines if the figure should be saved. (default: False)

    Returns:
        str: Name of created figure.
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
    name = "Archival Signal of [%s]" % os.path.split(arc_file)[1].rstrip('.arc')
    plt.figure(name)
    plt.title(name)
    plt.xlabel('Data Point')
    plt.ylabel('Amplitude')
    # Plotting
    plt.plot(t, data['sig'], zorder=1)
    plt.scatter(peak_t, peak_sig, marker='x', c='r', alpha=0.75, zorder=3)
    if sig_rng is not None:
        plt.axvline(sig_rng[0], c='gray', ls='-.', alpha=0.75, zorder=2)
        plt.axvline(sig_rng[1], c='gray', ls='-.', alpha=0.75, zorder=2)
    # Saving function
    if save:
        plt.savefig(os.path.splitext(arc_file)[0] + '.png')
    # Return figure name
    return name


""" NOI data structure definition:
    noi_data (dict): recording noise signal: {
        data (dict): neural recording noise data structure {
            noi (list[float]): neural recording noise data
            freq (int or float): recording frequency of [noi]
        }
        meta (dict): metadata structure of the noise {
            organism (dict): organism for the signal recording {
                gn (str): generic name
                se (str): specific epithet
                st (str): strain,
                mod (str or None): genetic modification, None for wildtype
                note (Any): extra notes
            }
            region (list): recoding region(s) of the signal
            feature (dict): recorded features in the noise signal {
                typ (list[str]): existing noise - 'fp' for field potential, 'ele' for elec-sti, 'opto' for opto-sti etc.
                note (Any): extra notes
            }
            system (dict): recording system information {
                typ (str): system type - 'd' for digital or 'a' for analog
                mfr (str): system manufacture
                pn (str): manufacture part number or model
                sn (str): manufacture serial number or batch number
                soc (int or float or str): Socket in system for recording
                note (Any): extra notes
            }
            probe (dict): recording probe information {
                typ (str): probe type - 'si' for silicon, 'w' for tungsten, 'gls' for glass pipette etc.
                mfr (str): probe manufacture
                pn (str): manufacture part number or model
                sn (str): manufacture serial number or batch number
                chn (int or float): recording site channel number
                note (Any): extra notes
            }
            datetime (str[datetime.ISO-format]): recording date and time information
        }
"""


def noi_read(noi_file):
    """ Read recording noise sample file.

    Args:
        noi_file (str): File contained archival neuronal signal data (*.noi).

    Returns:
        dict: Neuronal recording noise sample, defined above.
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
    """ Write recording noise sample file.

    Args:
        noi_file (str): File to write recording noise sample data (*.noi).
        noi_data (dict): Neuronal recording noise sample, defined above.

    Returns:
        bool: File creation status.
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
    cjsh_write(noi_file, noi_data)
    return True
