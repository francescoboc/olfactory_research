from utils import *
from select_file import *

colormap = 'viridis'

dicts_folder = f'beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'
# dicts_folder_scrambled = f'beta_dicts/scrambled_agents/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dicts
fpt_betas = np.load(f'{dicts_folder}/fpt_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
prob_betas = np.load(f'{dicts_folder}/prob_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
if center_of_mass:
    rate_betas = np.load(f'{dicts_folder}/com_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
else:
    rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
# rate_betas = np.load(f'{dicts_folder_scrambled}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

# convert the dictionaries into masked arrays, preserving masks
fpt_map_stacked = np.ma.stack(list(fpt_betas.values()), axis=1)
rate_map_stacked = np.ma.stack(list(rate_betas.values()), axis=1)
prob_map_stacked = np.ma.stack(list(prob_betas.values()), axis=1)

# apply mask of the fpt map to the rate and prob maps
mask_fpt_map = np.ma.getmask(fpt_map_stacked)
rate_map_stacked = np.ma.array(rate_map_stacked, mask=mask_fpt_map)
prob_map_stacked = np.ma.array(prob_map_stacked, mask=mask_fpt_map)

# initialize arrays with nan (default value when no trust meets the threshold)
best_trust_rate = np.full(rate_map_stacked.shape[0], np.nan)
best_trust_prob = np.full(prob_map_stacked.shape[0], np.nan)

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

# find the highest beta at which the prob threshold is met
for trust in trusts:
    # get the corresponding trust id
    trust_id = trusts.index(trust)

    # select the rate map corresponsing to the current trust
    selected_map = prob_map_stacked[:,trust_id]

    # check where the threshold condition is met
    mask_threshold = selected_map >= prob_threshold

    # update the best_trust_rate for entries where the threshold condition is met
    for i in range(best_trust_prob.shape[0]):
        if mask_threshold[i]:  # only update where the threshold condition is met
            if np.isnan(best_trust_prob[i]) or trust > best_trust_prob[i]:
                best_trust_prob[i] = trust

# the calculation for FPT is easier because we are simply looking for the min in each row
min_indices_fpt = np.argmin(fpt_map_stacked, axis=1)
best_trust_fpt = np.array([trusts[idx] for idx in min_indices_fpt])

# mask bins based on the fpt mask at the lowest beta
best_trust_fpt = np.ma.array(best_trust_fpt, mask=np.ma.getmask(fpt_map_stacked[:,0]))


########## PLOT RATE MAP ##########
plt.figure()
cmap = plt.colormaps[colormap].resampled(len(trusts))
hb = plt.hexbin([0], [0], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap=cmap)

# create a mask for bins where the x-coordinate is less than x_threshold
x_threshold = final_x
bin_coords = hb.get_offsets()  
x_edges, y_edges = bin_coords.T
mask_below_threshold = x_edges > x_threshold

# apply mask to all the trust maps
best_trust_rate = np.ma.masked_where(mask_below_threshold, best_trust_rate)
best_trust_prob = np.ma.masked_where(mask_below_threshold, best_trust_prob)
best_trust_fpt = np.ma.masked_where(mask_below_threshold, best_trust_fpt)

# set values of hexbin and add colorbar with the correct limits
hb.set_array(best_trust_rate)
plt.clim(min(trusts)-0.05, max(trusts)+0.05) 
plt.colorbar(hb, label=r'$\beta^*_\rho$', ticks=trusts)
plt.title(fr'Highest trust $\beta^*_\rho$ at which $\rho \geq {rate_threshold:.2f}$')
add_decorations()


########## PLOT FPT MAP ##########
plt.figure()
hb = plt.hexbin([0], [0], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap=cmap)

# set values of hexbin and add colorbar with the correct limits
hb.set_array(best_trust_fpt)
plt.clim(min(trusts)-0.05, max(trusts)+0.05) 
plt.colorbar(hb, label=r'$\beta^*_\tau$', ticks=trusts)
plt.title(r'Trust $\beta^*_\tau}$ at which $\tau$ is minimal')
add_decorations()


# ########## PLOT PROB MAP ##########
# plt.figure()
# hb = plt.hexbin([0], [0], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap=cmap)
# # #
# # set values of hexbin and add colorbar with the correct limits
# hb.set_array(best_trust_prob)
# plt.clim(min(trusts)-0.05, max(trusts)+0.05) 
# plt.colorbar(hb, label=r'$\beta^*_P$', ticks=trusts)
# plt.title(fr'Highest trust $\beta^*_P$ at which $P \geq {prob_threshold:.2f}$')
# add_decorations()


########## PLOT HEATMAPS OF AGREEMENT ##########
plt.figure()

# plt.plot(best_trust_rate, best_trust_prob, 'o')
# plt.plot(best_trust_fpt, best_trust_prob, 'o')

# jitter = 0.01
# x_jittered = best_trust_prob + np.random.uniform(-jitter, jitter, len(best_trust_prob))
# y_jittered = best_trust_rate + np.random.uniform(-jitter, jitter, len(best_trust_rate))
# plt.plot(x_jittered, y_jittered, 'o', mfc='blue', mec='none', alpha=0.1)

# compute the 2D histogram (aka heatmap)
edges = np.arange(0.05, 1.0, 0.1)
heatmap_rate, _, _ = np.histogram2d(best_trust_prob, best_trust_rate, bins=(edges, edges))

# plot the heatmap
plt.imshow(heatmap_rate.T, origin='lower', extent=[0.05, 0.95, 0.05, 0.95], cmap='Blues', norm='log')
plt.colorbar(label='Counts')
plt.title(fr'Thresholds: $\rho \geq {rate_threshold:.2f}$, $P \geq {prob_threshold:.2f}$')
text = fr'Total counts ${int(np.sum(heatmap_rate))}$'
plt.text(0.985, 0.01, text, transform=plt.gca().transAxes, ha='right', va='bottom'), 
plt.xlabel(r'$\beta^*_P$ ')
plt.ylabel(r'$\beta^*_\rho$ ')
plt.xticks(trusts)
plt.yticks(trusts)
plt.axis('square')

# # same thing for the fpt
# plt.figure()
# heatmap_fpt, _, _ = np.histogram2d(best_trust_prob, best_trust_fpt, bins=(edges, edges))
# plt.imshow(heatmap_fpt.T, origin='lower', extent=[0.05, 0.95, 0.05, 0.95], cmap='Blues', norm='log')
# plt.colorbar(label='Counts')
# plt.title(fr'Threshold: $P \geq {prob_threshold:.2f}$')
# plt.xlabel(r'$\beta^*_P$ ')
# plt.ylabel(r'$\beta^*_\tau$ ')
# plt.xticks(trusts)
# plt.yticks(trusts)
# plt.axis('square')

show_and_check_ipython()
