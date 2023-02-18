import os
import argparse
import numpy as np
from parus.utils.base_func import make_outdir, prog_print
from parus.data.file_io import pklz_write, cjsh_write, arc_read, noi_read
from parus.data.sig_proc import bsl_sft_lin, bsl_sft_sin
import warnings


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusGenSim", description="Generate simulated neural signals",
                                 epilog="Generated simulated neural signal data use for model training ONLY")
parser.add_argument('-v', '--version', action='version', version="Parus - Generate simulated neural signals: v4.0")
# Sample source definition (positional)
parser.add_argument('arc_dir', type=str, metavar="signalFolder",
                    help="[%(type)s] Directory containing archived signal data (*.arc)")
parser.add_argument('noi_dir', type=str, metavar="noiseFolder",
                    help="[%(type)s] Directory containing sample noise data (*.noi)")
# Outputs parameters (positional)
parser.add_argument('out_dir', type=str, metavar="outputFolder",
                    help="[%(type)s] Output directory of simulated data (*.sim)")
parser.add_argument('num_sim', type=int, metavar="sampleNumber",
                    help="[%(type)s] Number of simulated data to be generated")
# Simulated data generation properties (optional)
parser.add_argument('-l', '--length', dest='tot_len', type=int, default=300, metavar="[int]",
                    help="Total length of final signal sample (default: %(default)s)")
parser.add_argument('-f', '--freq', dest='freq', type=int or float, default=20000, metavar="[int or float]",
                    help="Sampling frequency (Hz) of the system (default: %(default)s)")
parser.add_argument('-ig', '--mingap', dest='min_gap', type=int, default=20, metavar="[int]",
                    help="Minimum index gap of signal events (default: %(default)s)")
parser.add_argument('-xg', '--maxgap', dest='max_gap', type=int, default=80, metavar="[int]",
                    help="Maximum index gap of signal events (default: %(default)s)")
parser.add_argument('-gp', '--group', dest='sig_grp', type=str, choices=['typ', 'spk'], default=None,
                    metavar="{typ, spk}",
                    help="Grouping method: 'typ' = cell type, 'spk' = spike type (default: %(default)s = disabled)")
parser.add_argument('-gr', '--grpratio', dest='grp_rat', nargs='+', type=int or float, default=None,
                    metavar="[int or float]",
                    help="Occurrence ratio of groups, the order is associated with the group names alphabetical order, "
                         "and suggested to be the same length of group number (default: %(default)s = equally occurs)")
# Simulated data randomized weighing properties (optional)
parser.add_argument('-sf', '--sigfac', dest='sig_fac', nargs=2, type=float, default=None, metavar="[float]",
                    help="Signal amplitude multiplication factor [low] [high] (default: %(default)s = disabled)")
parser.add_argument('-nf', '--noifac', dest='noi_fac', nargs=2, type=float, default=None, metavar="[float]",
                    help="Noise level multiplication factor [low] [high] (default: %(default)s = disabled)")
# Simulated baseline shifting (optional)
parser.add_argument('-bs', '--baseshift', dest='bsl_meth', nargs='+', type=str, choices=['cst', 'lin', 'sin', 'esc'],
                    default=None, metavar=("{cst, lin, sin, esc}", ""),
                    help="Baseline random shifting method: 'cst' = constant, 'lin' = linear, 'sin' = sinusoid, "
                         "'esc' = no-shift (default: %(default)s = disabled)")
parser.add_argument('-bp', '--basecomp', dest='bsl_comp', nargs='+', type=int or float, default=None,
                    metavar="[int or float]",
                    help="Baseline shift composition ratio of each method, suggested to be the same length as methods "
                         "(default: %(default)s = equally occurs)")
parser.add_argument('-ba', '--baseamps', dest='bsl_amps', nargs=2, type=float, default=None, metavar="[float]",
                    help="Randomize baseline shift amplitude [low] [high] (default: %(default)s = disabled)")
parser.add_argument('-bf', '--basefreq', dest='bsl_freq', nargs=2, type=float, default=None, metavar="[float]",
                    help="Randomize baseline frequency (Hz) [low] [high], 'sin' only (default: %(default)s = disabled)")
# Extra example generation (optional)
parser.add_argument('-eg', '--example', dest='num_eg', type=int, default=None, metavar="[int]",
                    help="Number of extra examples to be generated (default: %(default)s = disabled)")
# Parse inputs
args = parser.parse_args()
# Ignore group ratio info at no grouping
if args.sig_grp is None:
    args.grp_rat = None
# Validate baseline method inputs
if args.bsl_meth is None:
    args.bsl_comp = None  # Ignore baseline composition info at no baseline shift
else:
    _, base_meth_idx = np.unique(args.bsl_meth, return_index=True)  # Get unique indices from inputs
    args.bsl_meth = [args.bsl_meth[i] for i in np.sort(base_meth_idx)]  # Get unique methods with input order
# -------------------------------------------------------------------------------------------------------------------- #


# Generation statistics recording variable
gen_rep = {'args': vars(args), 'file': {'sig': [], 'noi': []}, 'prop': {}}  # INIT VAR, generation reporting dictionary
arc_stat = []  # INIT VAR, ARC file occurrence recorder
grp_stat = {}  # INIT VAR, grouped signal occurrence recorder
sig_fac_stat = []  # INIT VAR, signal amplitude multiplier recorder
noi_fac_stat = []  # INIT VAR, noise amplitude multiplier recorder
noi_bls_stat = {'cst': 0, 'lin': 0, 'sin': 0, 'esc': 0}  # INIT VAR, noise baseline shift mode occurrence recorder

# Acquire archived neuronal signal data
arc_file = [os.path.join(args.arc_dir, f) for f in os.listdir(args.arc_dir) if f.endswith('.arc')]
arc_sig = []  # INIT VAR
arc_typ = []  # INIT VAR
arc_pos_a = []  # INIT VAR, _a = anterior, same for all variables ends with [_a] below
arc_pos_p = []  # INIT VAR, _p = posterior, same for all variables ends with [_p] below
print("Reading archived neural signal data.")
for f in arc_file:
    arc_data = arc_read(f)
    arc_stat.append(0)
    # Get samples
    arc_sig.append(np.array(arc_data['data']['sig'][arc_data['data']['rng'][0]:arc_data['data']['rng'][1]]))
    arc_typ.append(None if args.sig_grp is None else arc_data['meta']['neuron'][args.sig_grp])
    # Get signal position
    arc_pos_a.append(arc_data['data']['pos'] - arc_data['data']['rng'][0])
    arc_pos_p.append(arc_data['data']['rng'][1] - arc_data['data']['pos'])
# Read noise data
noi_file = [os.path.join(args.noi_dir, f) for f in os.listdir(args.noi_dir) if f.endswith('.noi')]
noise = []  # INIT VAR
print("Reading archived recoding noise data.")
for f in noi_file:
    noise.append(np.array(noi_read(f)['data']['noi']))
# Get grouping information
grp_dic = {}  # INIT VAR
if args.sig_grp is not None:
    # Get groups
    i = 0
    for sg in np.unique(arc_typ):
        grp_dic[sg] = i
        grp_stat[sg] = []
        i += 1
    # Assign signal index to groups
    sig_idx = [[] for _ in grp_dic]  # INIT VAR
    for i in range(len(arc_typ)):
        sig_idx[grp_dic[arc_typ[i]]].append(i)
else:
    sig_idx = [list(range(len(arc_sig)))]
    grp_stat['none'] = []
# Save input file information to generation reporting dictionary
gen_rep['file']['sig'] = [os.path.splitext(os.path.split(f)[1])[0] for f in arc_file]
gen_rep['file']['noi'] = [os.path.splitext(os.path.split(f)[1])[0] for f in noi_file]

# Verify and set group occurrence ratio settings
if args.grp_rat is None:
    if args.sig_grp is not None:
        args.grp_rat = [1 / len(grp_dic) for _ in grp_dic]
else:
    if len(args.grp_rat) < len(grp_dic):
        warnings.warn_explicit("Group ratio entries (%d) < number of groups (%d), pad with average."
                               % (len(args.grp_rat), len(grp_dic)),
                               category=RuntimeWarning, filename="ParusGenSim ['-gr', '--grpratio']", lineno=6)
        grp_rat_pad = sum(args.grp_rat) / len(args.grp_rat)
        grp_rat_fit = args.grp_rat + [grp_rat_pad for _ in range(len(grp_dic) - len(args.grp_rat))]  # Pad
        args.grp_rat = [i / sum(grp_rat_fit) for i in grp_rat_fit]  # Normalize to probabilities associations
    elif len(args.grp_rat) > len(grp_dic):
        warnings.warn_explicit("Group ratio entries (%d) > number of groups (%d), discard extra."
                               % (len(args.grp_rat), len(grp_dic)),
                               category=RuntimeWarning, filename="ParusGenSim ['-gr', '--grpratio']", lineno=6)
        grp_rat_fit = args.grp_rat[0:len(grp_dic)]  # Slice
        args.grp_rat = [i / sum(grp_rat_fit) for i in grp_rat_fit]  # Normalize to probabilities associations
    else:
        args.grp_rat = [i / sum(args.grp_rat) for i in args.grp_rat]  # Normalize to probabilities associations
# Verify and set baseline composition ratio settings
if args.bsl_comp is None:
    if args.bsl_meth is not None:
        args.bsl_comp = [1 / len(args.bsl_meth) for _ in args.bsl_meth]
else:
    if len(args.bsl_comp) < len(args.bsl_meth):
        warnings.warn_explicit("Baseline ratio entries (%d) < baseline methods (%d), pad with average."
                               % (len(args.bsl_comp), len(args.bsl_meth)),
                               category=RuntimeWarning, filename="ParusGenSim ['-bp', '--basecomp'", lineno=10)
        bsl_comp_pad = sum(args.bsl_comp) / len(args.bsl_comp)
        bsl_comp_fit = args.bsl_comp + [bsl_comp_pad for _ in range(len(args.bsl_meth) - len(args.bsl_comp))]  # Pad
        args.bsl_comp = [i / sum(bsl_comp_fit) for i in bsl_comp_fit]  # Normalize to probabilities associations
    elif len(args.bsl_comp) > len(args.bsl_meth):
        warnings.warn_explicit("Baseline ratio entries (%d) > baseline methods (%d), discard extra."
                               % (len(args.bsl_comp), len(args.bsl_meth)),
                               category=RuntimeWarning, filename="ParusGenSim ['-bp', '--basecomp']", lineno=10)
        bsl_comp_fit = args.bsl_comp[0:len(args.bsl_meth)]  # Slice
        args.bsl_comp = [i / sum(bsl_comp_fit) for i in bsl_comp_fit]  # Normalize to probabilities associations
    else:
        args.bsl_comp = [i / sum(args.bsl_comp) for i in args.bsl_comp]  # Normalize to probabilities associations

# Make output directories
lbl_out_dir = make_outdir(os.path.join(args.out_dir, "lbl/"), err_msg="Invalid simulated labels output directory!")
sig_out_dir = make_outdir(os.path.join(args.out_dir, "sig/"), err_msg="Invalid simulated signal output directory!")
if args.num_eg is not None:
    eg_out_dir = make_outdir(os.path.join(args.out_dir, "egp/"), err_msg="Invalid extra example output directory!")


# Define local functions --------------------------------------------------------------------------------------------- #

def sig_asgn_lst(low, high, max_pos, sig_lst, grp_pas=None):
    """ Get 2 lists for assigning signals to the final sample.

    Args:
        low (int): Minimum index difference between 2 signal events
        high (int): Maximum index difference between 2 signal events
        max_pos (int): Total length of final signal sample (in index)
        sig_lst (list[list[int]]): Signal sample indices arranged by group
        grp_pas (list[float] or None): Probabilities associations of each group (default: None)

    Returns:
        tuple[list[int], list[int]]: sel_lst (list[int]): Signal selection list
                                     pos_lst (list[int]): Signal position list
    """
    sel_lst = []  # INIT VAR
    pos_lst = []  # INIT VAR
    current_pos = np.random.randint(0, high)
    while current_pos < max_pos:
        # Get random selection
        if grp_pas is None:
            curr_grp = 0
        else:
            curr_grp = np.random.choice(len(grp_pas), size=None, replace=True, p=grp_pas)
        curr_sig = np.random.choice(sig_lst[curr_grp], size=None, replace=True)
        # Assign values and move position
        sel_lst.append(curr_sig)
        pos_lst.append(current_pos)
        current_pos += np.random.randint(low, high)
    return sel_lst, pos_lst


def gen_sim_sig():
    """ Generate single simulated signal with its label.

    Returns:
        tuple[np.ndarray, dict[str, np.ndarray, str, list[np.ndarray]]]: Generated signal and label
            sig (np.ndarray): {1D} Simulated signal data
            lbl (dict[str, np.ndarray, str, list[np.ndarray]]): Ground truth of [sig]
                - 'noise' (np.ndarray): {1D} Noise ground truth of [sig]
                - 'signal' (list[np.ndarray]): {1D} Grouped noise-free signal of [sig]
    """
    # Initialize label output
    lbl = {'noise': None, 'signal': []}
    for i in range(len(arc_sig if args.sig_grp is None else grp_dic)):
        lbl['signal'].append(np.zeros(args.tot_len, dtype=np.float64))
    grp_temp = {k: 0 for k in grp_stat.keys()}  # STAT VAR, grouped signal occurrence per file

    # Get simulated signals
    sel, pos = sig_asgn_lst(args.min_gap, args.max_gap, args.tot_len, sig_idx, args.grp_rat)
    for i in range(len(pos)):
        curr_fac = 1.0 if args.sig_fac is None else np.random.uniform(args.sig_fac[0], args.sig_fac[1])
        arc_stat[sel[i]] += 1  # STAT
        sig_fac_stat.append(curr_fac)  # STAT
        if arc_pos_a[sel[i]] > pos[i]:
            asgn_p = pos[i] + arc_pos_p[sel[i]]
            rang_a = arc_pos_a[sel[i]] - pos[i]
            if args.sig_grp is None:
                lbl['signal'][sel[i]][:asgn_p] = arc_sig[sel[i]][rang_a:] * curr_fac
                grp_temp['none'] += 1  # STAT
            else:
                lbl['signal'][grp_dic[arc_typ[sel[i]]]][:asgn_p] = arc_sig[sel[i]][rang_a:] * curr_fac
                grp_temp[arc_typ[sel[i]]] += 1  # STAT
        elif arc_pos_p[sel[i]] + pos[i] > args.tot_len:
            asgn_a = pos[i] - arc_pos_a[sel[i]]
            rang_p = args.tot_len - pos[i] + arc_pos_a[sel[i]]
            if args.sig_grp is None:
                lbl['signal'][sel[i]][asgn_a:] = arc_sig[sel[i]][:rang_p] * curr_fac
                grp_temp['none'] += 1  # STAT
            else:
                lbl['signal'][grp_dic[arc_typ[sel[i]]]][asgn_a:] = arc_sig[sel[i]][:rang_p] * curr_fac
                grp_temp[arc_typ[sel[i]]] += 1  # STAT
        else:
            asgn_a = pos[i] - arc_pos_a[sel[i]]
            asgn_p = pos[i] + arc_pos_p[sel[i]]
            if args.sig_grp is None:
                lbl['signal'][sel[i]][asgn_a:asgn_p] = arc_sig[sel[i]] * curr_fac
                grp_temp['none'] += 1  # STAT
            else:
                lbl['signal'][grp_dic[arc_typ[sel[i]]]][asgn_a:asgn_p] = arc_sig[sel[i]] * curr_fac
                grp_temp[arc_typ[sel[i]]] += 1  # STAT
    [grp_stat[k].append(grp_temp[k]) for k in grp_stat.keys()]  # STAT SUM

    # Get simulated noise
    noi_idx = np.random.randint(0, len(noise))
    noi_pos = np.random.randint(args.tot_len, len(noise[noi_idx]))
    if args.noi_fac is None:
        noi_fac_stat.append(1.0)  # STAT
        lbl['noise'] = noise[noi_idx][(noi_pos - args.tot_len):noi_pos]
    else:
        curr_fac = np.random.uniform(args.noi_fac[0], args.noi_fac[1])
        noi_fac_stat.append(curr_fac)  # STAT
        lbl['noise'] = np.multiply(noise[noi_idx][(noi_pos - args.tot_len):noi_pos], curr_fac)
    # Apply baseline shifting
    if args.bsl_meth is not None:
        meth = np.random.choice(args.bsl_meth, size=None, replace=True, p=args.bsl_comp)
        noi_bls_stat[meth] += 1  # STAT
        if meth == 'cst':
            lbl['noise'] = np.add(lbl['noise'], np.random.uniform(args.bsl_amps[0], args.bsl_amps[1]))
        elif meth == 'lin':
            lbl['noise'] = np.add(lbl['noise'], bsl_sft_lin(args.tot_len, args.bsl_amps))
        elif meth == 'sin':
            lbl['noise'] = np.add(lbl['noise'], bsl_sft_sin(args.tot_len, args.freq, args.bsl_amps, args.bsl_freq))
        else:
            pass

    # Create simulated signal
    sig = np.copy(lbl['noise'])
    for i in lbl['signal']:
        sig = np.add(sig, i)
    # Return generation
    return sig, lbl

# -------------------------------------------------------------------------------------------------------------------- #


# Main process loop
for n in range(args.num_sim):
    gen_sig, gen_lbl = gen_sim_sig()
    # Save and report
    pklz_write(os.path.join(sig_out_dir, "sig_%05d.sim" % n), gen_sig, level=-1)  # Write signal file
    pklz_write(os.path.join(lbl_out_dir, "lbl_%05d.sim" % n), gen_lbl, level=-1)  # Write label file
    prog_print(n + 1, args.num_sim, "Progress:", "simulated data created.")

# Arrange and save generation statistics
print("Saving generation report file.")
rep_file = os.path.join(args.out_dir, "gen_rep.cjh")
gen_rep['prop'] = {
    'arc_cnt': arc_stat, 'grp_cnt': grp_stat, 'sig_fac': sig_fac_stat, 'noi_fac': noi_fac_stat, 'bsl_cnt': noi_bls_stat
}
cjsh_write(rep_file, gen_rep, level=9)

# Generate extra examples
if args.num_eg is not None:
    for n in range(args.num_eg):
        gen_sig, gen_lbl = gen_sim_sig()
        pklz_write(os.path.join(eg_out_dir, "sig_eg_%05d.sim" % n), gen_sig, level=-1)  # Write signal file
        pklz_write(os.path.join(eg_out_dir, "lbl_eg_%05d.sim" % n), gen_lbl, level=-1)  # Write label file
        prog_print(n + 1, args.num_eg, "Progress:", "extra example created.")

print("Process done, call [python gensta.py %s] to visualize generation statistics." % rep_file)
