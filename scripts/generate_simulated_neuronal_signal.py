import os
import numpy as np
from parus.utils.base_func import make_outdir, pklz_write, prog_print
from parus.data.data_proc import arc_read, noi_read

"""This SCRIPT creates simulated neuronal signal data.
"""
""" Parameters:
      # Sample source definition
        arc_dir (str): Directory containing archived neuronal signal data (*.arc).
        noise_file (str): A file containing noise of recording.
      # Simulated data generation properties
        min_gap (int): Minimum index difference between 2 signal events.
        max_gap (int): Maximum index difference between 2 signal events.
        total_length (int): Total length of final signal sample (in index).
      # Simulated data randomization properties
        sig_fac (tuple[float, float] or None): Signal amplitude multiplication factor (low, high), [None] to disable.
        noi_fac (tuple[float, float] or None): Noise level multiplication factor (low, high), [None] to disable.
        baseline_rng (tuple[float, float] or None): Baseline random shifting value (low, high), [None] to disable.
      # Outputs parameters
        n_sim_data (int): Number of simulated data to be generated.
        output_dir (str): Output directory.
"""

# Parameters input  -------------------------------------------------------------------------------------------------- #
# Sample source definition
arc_dir = "../data"
noise_file = "../data/cb_vms_2.noi"
# Simulated data generation properties
min_gap = 20
max_gap = 80
total_length = 300
# Simulated data randomization properties
sig_fac = (0.8, 1.5)
noi_fac = (0.5, 2.0)
baseline_rng = (-5.0, 5.0)
# Outputs parameters
n_sim_data = 100000
output_dir = "../../dataset/complex_spike/complex100000_min20_max80_len300"
# -------------------------------------------------------------------------------------------------------------------- #


def sig_asgn_lst(low, high, max_pos, sig_count):
    """ Get 2 lists for assigning signals to the final sample.

    Args:
        low (int): Minimum index difference between 2 signal events.
        high (int): Maximum index difference between 2 signal events.
        max_pos (int): Total length of final signal sample (in index).
        sig_count (int): Number of different signals to be assigned.

    Returns:
        tuple[list[int], list[int]]: sel_list (list[int]): Signal selection list.
                                     pos_lst (list[int]): Signal position list.
    """
    sel_lst = []  # INIT VAR
    pos_lst = []  # INIT VAR
    current_pos = np.random.randint(0, high)
    while current_pos < max_pos:
        sel_lst.append(np.random.randint(0, sig_count))
        pos_lst.append(current_pos)
        current_pos += np.random.randint(low, high)
    return sel_lst, pos_lst


# Acquire archived neuronal signal data
arc_file = [os.path.join(arc_dir, f) for f in os.listdir(arc_dir) if f.endswith('.arc')]
arc_sig = []  # INIT VAR
arc_pos_a = []  # INIT VAR
arc_pos_p = []  # INIT VAR
for f in arc_file:
    arc_data = arc_read(f)
    # Get samples
    arc_sig.append(arc_data['sig'][arc_data['rng'][0]:arc_data['rng'][1]])
    # Get signal position
    arc_pos_a.append(arc_data['pos'] - arc_data['rng'][0])
    arc_pos_p.append(arc_data['rng'][1] - arc_data['pos'])
# Read noise data
noise = noi_read(noise_file)['noise']

# Make output directories
lbl_out_dir = make_outdir(os.path.join(output_dir, "lbl/"), err_msg="Invalid simulated labels output directory!")
sig_out_dir = make_outdir(os.path.join(output_dir, "sig/"), err_msg="Invalid simulated signal output directory!")

# Main process loop
for n in range(n_sim_data):
    # Initialize label output
    lbl = {'noise': None, 'signal': []}
    for i in range(len(arc_sig)):
        lbl['signal'].append(np.zeros(total_length, dtype=np.float64))

    # Get simulated signals
    sel, pos = sig_asgn_lst(min_gap, max_gap, total_length, len(arc_sig))
    for i in range(len(pos)):
        if arc_pos_a[sel[i]] > pos[i]:
            asgn_p = pos[i] + arc_pos_p[sel[i]]
            rang_a = arc_pos_a[sel[i]] - pos[i]
            if sig_fac is None:
                lbl['signal'][sel[i]][:asgn_p] = arc_sig[sel[i]][rang_a:]
            else:
                lbl['signal'][sel[i]][:asgn_p] = arc_sig[sel[i]][rang_a:] * np.random.uniform(sig_fac[0], sig_fac[1])
        elif arc_pos_p[sel[i]] + pos[i] > total_length:
            asgn_a = pos[i] - arc_pos_a[sel[i]]
            rang_p = total_length - pos[i] + arc_pos_a[sel[i]]
            if sig_fac is None:
                lbl['signal'][sel[i]][asgn_a:] = arc_sig[sel[i]][:rang_p]
            else:
                lbl['signal'][sel[i]][asgn_a:] = arc_sig[sel[i]][:rang_p] * np.random.uniform(sig_fac[0], sig_fac[1])
        else:
            asgn_a = pos[i] - arc_pos_a[sel[i]]
            asgn_p = pos[i] + arc_pos_p[sel[i]]
            if sig_fac is None:
                lbl['signal'][sel[i]][asgn_a:asgn_p] = arc_sig[sel[i]]
            else:
                lbl['signal'][sel[i]][asgn_a:asgn_p] = arc_sig[sel[i]] * np.random.uniform(sig_fac[0], sig_fac[1])

    # Get simulated noise
    noise_pos = np.random.randint(total_length, len(noise))
    if noi_fac is None:
        lbl['noise'] = noise[(noise_pos - total_length):noise_pos]
    else:
        lbl['noise'] = noise[(noise_pos - total_length):noise_pos] * np.random.uniform(noi_fac[0], noi_fac[1])
    if baseline_rng is not None:
        lbl['noise'] = np.add(lbl['noise'], np.random.uniform(baseline_rng[0], baseline_rng[1]))

    # Create simulated signal
    sig = np.copy(lbl['noise'])
    for i in lbl['signal']:
        sig = np.add(sig, i)

    # Save and report
    pklz_write(os.path.join(lbl_out_dir, "lbl_%05d.sim" % n), lbl)  # Write label file
    pklz_write(os.path.join(sig_out_dir, "sig_%05d.sim" % n), sig)  # Write signal file
    prog_print(n + 1, n_sim_data, "Progress:", "simulated data created.")
