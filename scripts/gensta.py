import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from parus.data.file_io import cjsh_read

mpl.use('TkAgg')  # Use TkAgg backend


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="ParusGenStat", description="Visualize simulated signals generation status")
parser.add_argument('-v', '--version', action='version', version="Parus - Visualize simulated signals generation: v1.6")
parser.add_argument('file', type=str, metavar="reportFile", help="[%(type)s] Generation report file path")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #


# Read file
gen_feat = cjsh_read(args.file)
# Initialize figure
fig, axs = plt.subplots(2, 3, num="Simulated Neural Signal Generation Overview")
fig.suptitle("Simulated Neural Signal Generation Overview [%d @ %1.1fkHz * %d]" %
             (gen_feat['args']['tot_len'], gen_feat['args']['freq'] / 1000, gen_feat['args']['num_sim']))
fig.tight_layout()


# Plotting signal randomized multiplier with Histogram
ax = axs[0][0]
ax.set_title("Signal Multiplier Distribution")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel("Multiplier Value")
ax.set_ylabel("Multiplier Occurrence")
# Plot data
smp_n, _, smp_pch = ax.hist(gen_feat['prop']['sig_fac'], bins=100, alpha=0.75)
# Plot distribution info
if gen_feat['args']['sig_fac'] is not None:
    # Plot set min/max
    smp_min = gen_feat['args']['sig_fac'][0]
    ax.axvline(smp_min, label="Min: %.2f" % smp_min, ls='--', color='peru')
    smp_max = gen_feat['args']['sig_fac'][1]
    ax.axvline(smp_max, label="Max: %.2f" % smp_max, ls='--', color='sienna')
    # Plot stats
    smp_avg = np.mean(gen_feat['prop']['sig_fac']).item()
    smp_std = np.std(gen_feat['prop']['sig_fac']).item()
    ax.axvline(smp_avg, label="Avg: %.2f±%.2f" % (smp_avg, smp_std), ls='--', color='crimson')
    # Set legend
    ax.set_ylim(0, ax.get_ylim()[1] * 1.2)
    ax.legend(loc='upper right')
# Set histogram color
smp_norm = (smp_n - smp_n.min()) / (smp_n.max() - smp_n.min())
for f, p in zip(smp_norm, smp_pch):
    color = mpl.colormaps['viridis'](f)
    p.set_facecolor(color)


# Plotting noise randomized multiplier with Histogram
ax = axs[0][1]
ax.set_title("Noise Multiplier Distribution")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel("Multiplier Value")
ax.set_ylabel("Multiplier Occurrence")
# Plot data
nmp_n, _, nmp_pch = ax.hist(gen_feat['prop']['noi_fac'], bins=100, alpha=0.75)
# Plot distribution info
if gen_feat['args']['noi_fac'] is not None:
    # Plot set min/max
    nmp_min = gen_feat['args']['noi_fac'][0]
    ax.axvline(nmp_min, label="Min: %.2f" % nmp_min, ls='--', color='steelblue')
    nmp_max = gen_feat['args']['noi_fac'][1]
    ax.axvline(nmp_max, label="Max: %.2f" % nmp_max, ls='--', color='royalblue')
    # Plot stats
    nmp_avg = np.mean(gen_feat['prop']['noi_fac']).item()
    nmp_std = np.std(gen_feat['prop']['noi_fac']).item()
    ax.axvline(nmp_avg, label="Avg: %.2f±%.2f" % (nmp_avg, nmp_std), ls='--', color='forestgreen')
    # Set legend
    ax.set_ylim(0, ax.get_ylim()[1] * 1.2)
    ax.legend(loc='upper right')
# Set histogram color
nmp_norm = (nmp_n - nmp_n.min()) / (nmp_n.max() - nmp_n.min())
for f, p in zip(nmp_norm, nmp_pch):
    color = mpl.colormaps['plasma'](f)
    p.set_facecolor(color)


# Plotting baseline shift mode ratio of with Pie Chart
ax = axs[0][2]
ax.set_title("Simulated Baseline Shift Mode")
ax.axis('equal')  # Ensures pie is drawn as a circle
# Arrange baseline shift data
if gen_feat['args']['bsl_meth'] is None:
    sft_lbl = ["No Shift"]
    sft_dat = [1]
    sft_explode = [0]
else:
    sft_dic = {'cst': "Constant", 'lin': "Linear", 'sin': "Sinusoid", 'nos': "No Shift"}
    sft_lbl = [sft_dic[k] for k in gen_feat['prop']['bsl_cnt']]
    sft_dat = [gen_feat['prop']['bsl_cnt'][k] for k in gen_feat['prop']['bsl_cnt']]
    sft_explode = [0.1] * len(sft_lbl)
# Plot data
ax.pie(sft_dat, labels=sft_lbl, explode=sft_explode, autopct='%1.1f%%', shadow=True, startangle=90, counterclock=False)


# Plotting occurrence ratio of signal groups with Pie Chart
ax = axs[1][0]
ax.set_title("Signal Group Occurrence Ratio")
ax.axis('equal')  # Ensures pie is drawn as a circle
# Arrange group data
if gen_feat['args']['sig_grp'] is None:
    grp_lbl = ["No Grouping"]
    grp_dat = [1]
    grp_explode = [0]
else:
    grp_lbl = [k.upper() for k in gen_feat['prop']['grp_cnt']]
    grp_dat = [sum(gen_feat['prop']['grp_cnt'][k]) for k in gen_feat['prop']['grp_cnt']]
    grp_explode = [0.1] * len(grp_lbl)
# Plot data
ax.pie(grp_dat, labels=grp_lbl, explode=grp_explode,
       autopct='%1.1f%%', wedgeprops=dict(width=0.75), startangle=90, counterclock=False)


# Plotting occurrence ratio of sample signals with Pie Chart
ax = axs[1][1]
ax.set_title("Sample Signal Occurrence Ratio")
ax.axis('equal')  # Ensures pie is drawn as a circle
# Get spectrum for each signal
arc_n = len(gen_feat['prop']['arc_cnt'])
arc_crng = np.concatenate((np.linspace(0.85, 0, arc_n - arc_n // 2), np.linspace(0, 0.85, arc_n // 2)), axis=None)
arc_crng[1::2] += 0.15
arc_color = mpl.colormaps['rainbow'](arc_crng)
# Plot data
arc_wedges, _ = ax.pie(gen_feat['prop']['arc_cnt'],
                       wedgeprops=dict(width=0.75), startangle=90, counterclock=False, colors=arc_color)
ax.set_xlabel("Total Number of Signals: %d" % arc_n)
# Annotate plotted chart
arc_annot = {}  # INIT VAR
kw = dict(arrowprops=dict(arrowstyle="->", connectionstyle=""), zorder=0, va="center",
          bbox=dict(boxstyle="round,pad=0.3", fc="w", ec="k", lw=0.72))
arc_ratio = np.divide(gen_feat['prop']['arc_cnt'], sum(gen_feat['prop']['arc_cnt'])) * 100
for i, p in enumerate(arc_wedges):
    txt = "%s\n $\\bf{%.2f\\%%}$ (%d)" % (gen_feat['file']['sig'][i], arc_ratio[i], gen_feat['prop']['arc_cnt'][i])
    ang = (p.theta2 - p.theta1) / 2 + p.theta1
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))
    ha = "right" if x < 0 else "left"
    kw["arrowprops"]["connectionstyle"] = "angle,angleA=0,angleB=%d" % ang
    arc_annot[i] = ax.annotate(txt, xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y), horizontalalignment=ha, **kw)
    arc_annot[i].set_visible(False)


# Plotting average signal occurrence number of each simulated file with Bar Chart
ax = axs[1][2]
ax.set_title("Signal Feature")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel("Signal Composition")
ax.set_ylabel("Occurrence Probability (%)")
plt.xticks(rotation=45)
# Arrange data
noi_only = False  # Has pure noise data check flag
if gen_feat['args']['sig_grp'] is None:
    # Acquire and count unique occurrence
    occ_dat = np.asarray(gen_feat['prop']['grp_cnt']['none'])
    occ_uni, occ_cnt = np.unique(occ_dat, return_counts=True)
    # Convert counting to plot ratio information
    if occ_uni[0] == 0:
        noi_only = True  # Set flag
    occ_plt = [occ_cnt / gen_feat['args']['num_sim'] * 100]
    occ_cmp = [str(item) for item in occ_uni]
    # Statistics for legend
    occ_avg = [np.mean(occ_dat).item()]
    occ_std = [np.std(occ_dat).item()]
    occ_lbl = ["Signal (%.2f±%.2f)" % (occ_avg[0], occ_std[0])]
    occ_color = [mpl.colormaps['cividis'](0.25)]
else:
    # Acquire and count unique compositions
    occ_dat = np.asarray([gen_feat['prop']['grp_cnt'][k] for k in gen_feat['prop']['grp_cnt']])
    occ_uni, occ_cnt = np.unique(occ_dat, return_counts=True, axis=1)
    # Convert counting to plot ratio information
    if np.all(occ_uni[:, 0] == 0):
        occ_uni[0, 0] = 1  # Temporary padding
        noi_only = True  # Set flag
    occ_plt = occ_cnt / np.sum(occ_uni, axis=0) * occ_uni / gen_feat['args']['num_sim'] * 100
    occ_cmp = ['-'.join([str(item) for item in pair]) for pair in occ_uni.T]
    # Statistics for legend
    occ_avg = np.mean(occ_dat, axis=1)
    occ_std = np.std(occ_dat, axis=1)
    occ_lbl = ["%s (%.2f±%.2f)" % (k.upper(), m, s) for k, m, s in zip(gen_feat['prop']['grp_cnt'], occ_avg, occ_std)]
    occ_color = [mpl.colormaps['cividis'](i * 0.6 / (len(occ_lbl) - 1) + 0.2) for i in range(len(occ_lbl))]
# Set data for noise only signals
if noi_only:
    occ_plt = np.r_[occ_plt, [np.zeros_like(occ_plt[0])]]
    occ_plt[-1, 0] = occ_plt[0, 0]
    occ_plt[0, 0] = 0
    occ_cmp[0] = "None"
    occ_lbl.append("Noise Only (%.1f%%)" % occ_plt[-1, 0])
    occ_color.append((0.25, 0.25, 0.25, 1))

# Plot data
for i in range(len(occ_lbl)):
    if i == 0:
        ax.bar(occ_cmp, occ_plt[i], label=occ_lbl[i], color=occ_color[i])
    else:
        ax.bar(occ_cmp, occ_plt[i], label=occ_lbl[i], color=occ_color[i], bottom=occ_plt[i-1])
ax.legend()


# Mouse hover event handler
def hover(event):
    for a in axs.flatten():
        if event.inaxes == a:
            a.set_zorder(255)
        else:
            a.set_zorder(0)
        fig.canvas.draw_idle()
    # Set dynamic annotation for sample signal occurrence plot
    if event.inaxes == axs[1][1]:
        for idx, prt in enumerate(arc_wedges):
            cont, _ = prt.contains(event)
            arc_annot[idx].set_visible(cont)
            fig.canvas.draw_idle()


# Show plot
fig.canvas.mpl_connect('motion_notify_event', hover)
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
plt.show()
