import os
import numpy as np
from parus.data.intan_func import intan_time_read, intan_amp_read
from parus.data.rec_info_io import read_probe_data, read_spk_info
from parus.utils.base_func import norm_lst_gen, laplace_lst_gen, prog_print
from parus.utils.cli_func import yn_query, cli_path_in, cli_outdir, cli_file_in, cli_int_in, cli_float_in, cli_list_sel
from parus.data.data_proc import spk_merge, neuron_rnd_samp, nsd_write, nsd_asgnv

"""
Command line interface for random sampling signal data form Intan "One File Per Channel" formatted data.
Simply run this script from Python console and following the prompt instructions.
"""

print()
print("                                     ====================================")
print("                                     ‖  INTAN DATA SAMPLING CLI SYSTEM  ‖")
print("                                     ====================================")
print()


# Define Intan recording raw data --------------------------------------------------------------------------------------
print("------------------------------- Define following information for Intan raw data -------------------------------")
# Get data folder input
dat_path = cli_path_in(msg_ppt="Please define the absolute path of Intan data folder: ",
                       msg_err="    Invalid data folder, please try again: ")
# Scan for signal data in data folder
sig_list = [f for f in os.listdir(dat_path) if f.startswith("amp-") and f.endswith(".dat")]
port = sorted(set([f.lstrip("amp-")[0] for f in sig_list]))
if len(port) == 0:
    print("No signal data found in the data folder, system out!")
    exit()
elif len(port) == 1:
    port_id = port[0]
else:
    port_id = cli_list_sel(port, msg_ppt="Please select from following ports - ",
                           msg_err="    Invalid port, please try again: ")
del port

# Scan for time data in data folder
if os.path.isfile(os.path.join(dat_path, "time.dat")):
    time_file = os.path.join(dat_path, "time.dat")
    flag_time = True
else:
    if yn_query("Missing [time.dat] in data folder, define manually? Infer from signal data if 'No'", default=False):
        time_file = cli_file_in(msg_ppt="    Please define the absolute path of Intan time file: ",
                                msg_err="        Invalid time file, please try again: ")
        flag_time = True
    else:
        print("    Infer time from signal data...")
        flag_time = False
# Define recording frequency
rec_freq = cli_int_in(msg_ppt="Please define signal recording frequency: ",
                      msg_err="    Invalid input, please try again: ")


# Define Intan recording annotation info -------------------------------------------------------------------------------
print()
print("------------------------------ Define following information for annotation data -------------------------------")
# Define probe geometry file
prb_file = cli_file_in(msg_ppt="Please define the absolute path of probe geometry file related to recording: ",
                       msg_err="    Invalid time file, please try again: ")
prb_info = read_probe_data(prb_file)
# Re-make [sig_list] and morph to [sig_dict]
sig_list = [os.path.join(dat_path, "amp-%s-%03d.dat" % (port_id, f)) for f in range(len(prb_info))]
sig_dict = {}  # INIT VAR
for i in range(len(prb_info)):
    if os.path.isfile(sig_list[i]):
        sig_dict[i] = sig_list[i]
    else:
        sig_dict[i] = None
del i, sig_list

# Define spike annotation file
spk_file = cli_file_in(msg_ppt="Please define the absolute path of spike annotation file related to recording: ",
                       msg_err="    Invalid time file, please try again: ")


# Define site ID input
site_id = cli_int_in(low=0, high=len(sig_dict) - 1,
                     msg_ppt="%d channels detected in [%s], please define target channel: " % (len(sig_dict), dat_path),
                     msg_err="    Channel ID MUST be an integer! Please redefine: ",
                     msg_rng="    Channel ID MUST be from 0 to %d! Please redefine: " % (len(sig_dict) - 1))
while True:
    if sig_dict[prb_info[site_id]['id']] is None:
        site_id = cli_int_in(low=0, high=len(sig_dict) - 1,
                             msg_ppt="    Defined channel has no recording data, please choose another channel: ",
                             msg_err="        Channel ID MUST be an integer! Please redefine: ",
                             msg_rng="        Channel ID MUST be from 0 to %d! Please redefine: " % (len(sig_dict) - 1))
    else:
        break


# Random sampling of recording data ------------------------------------------------------------------------------------
print()
print("----------------------------------- Define following arguments for sampling -----------------------------------")
num_samp = cli_int_in(msg_ppt="Please define number of samples to extract: ",
                      msg_err="    Invalid input, please try again: ")
# Value assign arguments
val_peak = cli_float_in(msg_ppt="Please define annotation peak value for spike: ",
                        msg_err="    Invalid input, please try again: ")
rng_asgn = cli_int_in(msg_ppt="Please define number of side points to assign gradient: ",
                      msg_err="    Invalid input, please try again: ")
grad_mtd = cli_list_sel(['norm', 'laplace'], msg_ppt="Please select gradient generation method in ",
                        msg_err="    Invalid method, please try again: ")
if grad_mtd == "norm":
    val_lst = norm_lst_gen(peak=val_peak, side=rng_asgn, level=2)
else:
    val_lst = laplace_lst_gen(peak=val_peak, side=rng_asgn, scale=1)


# Define output path ---------------------------------------------------------------------------------------------------
print()
print("------------------------------- Define following information for output folder --------------------------------")
out_path = cli_outdir(msg_ppt="Please define output folder for samples: ",
                      msg_err="    Invalid output path, please redefine: ")


# Read-in and process defined data -------------------------------------------------------------------------------------
print()
print("----------------------------------- Processing data with defined arguments ------------------------------------")
# Read signal
print("Importing signal...")
sig_data = intan_amp_read(sig_dict[prb_info[site_id]['id']])
# Read timestamp
print("Importing timestamp...")
if flag_time:
    sig_time = intan_time_read(os.path.join(dat_path, "time.dat"), rec_freq)
else:
    sig_time = np.divide(np.arange(len(sig_data)), rec_freq)
# Read spike annotation data
print("Importing spike annotation...")
spk_data = spk_merge(read_spk_info(spk_file, cell_mode=False, trim_negat=True, trim_noise=True))
print("Data successfully imported!")

# Sampling data
print("Sampling data...")
sig_samp = neuron_rnd_samp(sig_data, sig_time, spk_data[site_id], num=num_samp, size=150)
# Saving sampled data
n = len(sig_samp)
for i in range(n):
    sig_data = nsd_asgnv(sig_samp[i], rng_asgn, val_lst, method='min', rng_srch=10)
    sig_path = os.path.join(out_path, "sig_%05d.nsd" % (i + 49999))
    nsd_write(sig_path, sig_data)
    prog_print(i + 1, n, "    Saving: ", " done.")
