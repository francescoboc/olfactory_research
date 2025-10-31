from utils import *
from select_file import *
import matplotlib.gridspec as gridspec

plt.rcParams['figure.constrained_layout.use'] = False

visual_radius = 100*spawn_radius

def calc_best_trust(rate_betas):
    # convert the dictionaries into masked arrays, preserving masks
    rate_map_stacked = np.ma.stack(list(rate_betas.values()), axis=1)

    # initialize arrays with nan (default value when no trust meets the threshold)
    best_trust_rate = np.full(rate_map_stacked.shape[0], np.nan)

    # find the highest beta at which the rate threshold is met
    for trust in trusts:
        # get the corresponding trust id
        trust_id = trusts.index(trust)

        # select the rate map corresponsing to the current trust
        selected_map = rate_map_stacked[:,trust_id]

        # check where the threshold condition is met
        mask_threshold = selected_map >= rate_threshold

        # update the best_trust_rate for entries where the threshold condition is met
        for i in range(best_trust_rate.shape[0]):
            if mask_threshold[i]:  # only update where the threshold condition is met
                if np.isnan(best_trust_rate[i]) or trust > best_trust_rate[i]:
                    best_trust_rate[i] = trust

    return best_trust_rate 


def plot_best_trust_map(best_trust_rate, subtitle, ax, cax=None):
    cmap = plt.colormaps[colormap].resampled(len(trusts))
    hb = ax.hexbin([0], [0], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap=cmap)

    # Mask bins
    x_threshold = final_x
    # x_threshold = 98
    bin_coords = hb.get_offsets()
    x_edges, y_edges = bin_coords.T
    mask_below_threshold = x_edges > x_threshold
    best_trust_rate = np.ma.masked_where(mask_below_threshold, best_trust_rate)

    # Set array and limits
    hb.set_array(best_trust_rate)
    hb.set_clim(min(trusts)-0.05, max(trusts)+0.05)

    if cax is not None:
        plt.colorbar(hb, cax=cax, label=r'$\beta^*_\rho$', ticks=trusts)

    # ax.set_title(fr'$\beta^*_\rho$ where $\rho \geq {rate_threshold:.2f}$')
    # ax.text(0.5, 0.95, subtitle, ha='center', va='center', transform=ax.transAxes)
    ax.set_title(subtitle)

    ax.set_xticks([])
    ax.set_yticks([])

    add_decorations(30, ax=ax)

fig = plt.figure(figsize=(10, 5))

plt.subplots_adjust(top=0.85,
bottom=0.015,
left=0.005,
right=0.925,
hspace=0.2,
wspace=0.2)

gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 0.05], wspace=0.1, hspace=1)

ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
cax = fig.add_subplot(gs[2])  # colorbar axis

# fig.suptitle(fr'$\beta^*_\rho$ where $\rho \geq {rate_threshold:.2f}$')
# fig.subplots_adjust(top=0.85) 

# colormap = 'viridis_r'
colormap = 'viridis'

dicts_folder = f'../beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dicts
rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
rate_betas_com = np.load(f'{dicts_folder}/com_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
# rate_betas_com_theo = np.load(f'{dicts_folder}/com_theo_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
# rate_betas_com_theo = np.load(f'{dicts_folder}/com_fulltheo_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
rate_betas_com_theo = np.load(f'{dicts_folder}/com_fulltheo_betav0_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

best_trust_rate = calc_best_trust(rate_betas)
best_trust_rate_com = calc_best_trust(rate_betas_com)
best_trust_rate_com_theo = calc_best_trust(rate_betas_com_theo)

# plot_best_trust_map(best_trust_rate, 'Simulation')
plot_best_trust_map(best_trust_rate, 'Simulation', ax=ax1, cax=cax)

# plot_best_trust_map(best_trust_rate_com_theo, 'Theory')
plot_best_trust_map(best_trust_rate_com_theo, 'Theory', ax=ax2)

# TODO check the inverse of non-predicted points: points that exists in the theoretical map but NOT in the real one

########## PLOT HEATMAP OF AGREEMENT ##########
plt.figure(figsize=(6.4, 5.9))

beta_ref =  best_trust_rate
beta_check =  best_trust_rate_com_theo

# # jittered scatter plot
# jitter = 0.05
# x_jittered = beta_ref + np.random.uniform(-jitter, jitter, len(beta_ref))
# y_jittered = beta_check + np.random.uniform(-jitter, jitter, len(beta_check))
# plt.plot(x_jittered, y_jittered, 'o', mfc='blue', mec='none', alpha=0.1)

# beta_ref_counts = []
# beta_check_counts = []
# for trust in trusts:
#     beta_ref_counts.append(len(np.flatnonzero(beta_ref==trust)))
#     beta_check_counts.append(len(np.flatnonzero(beta_check==trust)))

# calculate heatmap of agreement
hmap = np.zeros([9,10])

for p in range(len(beta_ref)):
    br = beta_ref[p]
    bc = beta_check[p]

    if not np.isnan(br):
        if not np.isnan(bc):
            hmap[trusts.index(br)][trusts.index(bc)] += 1
        else:
            hmap[trusts.index(br)][9] += 1

# obtain total number of points per each ref beta
tot_ref = np.sum(hmap, axis=1)

# normalize heatmap
for c in range(hmap.shape[0]):
    hmap[c,:] /= tot_ref[c]

# set to nan gridpoints that are empty (so they are not colored)
hmap[np.where(hmap==0.0)]=np.nan

# # 2D histogram (aka heatmap)
# edges = np.arange(0.05, 1.0, 0.1)
# heatmap_rate, _, _ = np.histogram2d(beta_ref, beta_check, bins=(edges, edges))
# heatmap_rate = heatmap_rate.T

# for col in range(heatmap_rate.shape[1]):
#     heatmap_rate[:,col] /= total_reference[trusts[col]]

# plt.imshow(heatmap_rate, origin='lower', extent=[0.05, 0.95, 0.05, 0.95], cmap='Blues')#, norm='log')
plt.imshow(hmap, origin='lower', extent=[0.05, 0.95+0.1, 0.05, 0.95], cmap='YlOrRd')#, norm='log')

total_points = np.count_nonzero(~np.isnan(best_trust_rate)) 
# txt = fr'N. counts: ${int(np.sum(heatmap_rate))}/{total_points}$'

# txt = fr'Tot mismatched points: ${np.sum(list(mismatched.values()))}$'
# plt.text(0.985, 0.01, txt, transform=plt.gca().transAxes, ha='right', va='bottom', fontsize=15) 

trusts_str = [str(t) for t in trusts]
trusts_str.append(r'N.C.')

plt.title(r'Agreement of $\beta^*_\rho$')
# plt.xlabel('Real trajectories')
plt.xlabel(r'$\beta^*_\rho$ Simulation')
# plt.ylabel('Theo COM traj + theo std ellipse')
plt.ylabel(r'$\beta^*_\rho$Theory')
plt.xticks(ticks=trusts+[1], labels=trusts_str)
plt.yticks(trusts)
# plt.axis('square')

plt.tight_layout()

plt.axvline(0.95, ls='--', c='k')

# plt.colorbar(label=r'Fraction of points (per $\beta^*_\rho$)', pad=0.04)
plt.colorbar(label=r'Fraction of points (per $\beta^*_\rho$)', orientation='horizontal', shrink=0.47)

plt.subplots_adjust(top=0.93,
bottom=0.133,
left=0.0,
right=0.983,
hspace=0.2,
wspace=0.2)

# plt.figure()

# total_white_points = sum(list(white_points.values()))
# plt.bar(white_points.keys(), np.array(list(white_points.values()))/total_white_points, width=0.09, color=colors[1])
# plt.xticks(trusts)
# plt.xlabel(r'$\beta$')
# plt.ylabel(r'Fraction of non-predicted points')
# # plt.ylabel(r'')

# matched = [100*(tot-mis)/tot for tot, mis in zip(total_reference.values(), mismatched.values())]
# plt.bar(trusts, matched, width=0.09, color=colors[1])

# matched_perc = [(tot-mis)/total_points for tot, mis in zip(total_reference.values(), mismatched.values())]
# # miscounted_perc = [misc/total_points for misc in list(mismatched.values())]
# plt.bar(trusts, matched_perc, width=0.09, color=colors[1])

# plt.bar(mismatched.keys(), mismatched.values(), width=0.09, color=colors[1])
# plt.xticks(trusts)
# plt.xlabel(r'$\beta$')
# plt.ylabel(r'Mismatched points')
# # plt.ylabel(r'')

show_and_check_ipython()
