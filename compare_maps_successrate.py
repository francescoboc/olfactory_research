from utils import *
from select_file import *

def calc_best_trust(rate_betas):
    # convert the dictionaries into masked arrays, preserving masks
    rate_map_stacked = np.ma.stack(list(rate_betas.values()), axis=1)

    # apply mask of the fpt map to the rate and prob maps
    mask_rate_map = np.ma.getmask(rate_map_stacked)
    rate_map_stacked = np.ma.array(rate_map_stacked, mask=mask_rate_map)

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

def plot_best_trust_map(best_trust_rate, subtitle):
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

    # set values of hexbin and add colorbar with the correct limits
    hb.set_array(best_trust_rate)
    plt.clim(min(trusts)-0.05, max(trusts)+0.05) 
    plt.colorbar(hb, label=r'$\beta^*_\rho$', ticks=trusts)
    plt.title(fr'Highest trust $\beta^*_\rho$ at which $\rho \geq {rate_threshold:.2f}$')
    plt.text(0.5,0.95, subtitle, ha='center', va='center', transform=plt.gca().transAxes)

    add_decorations()

colormap = 'viridis'

dicts_folder = f'beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dicts
rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
rate_betas_com = np.load(f'{dicts_folder}/com_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
rate_betas_com_theo = np.load(f'{dicts_folder}/com_theo_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

best_trust_rate = calc_best_trust(rate_betas)
best_trust_rate_com = calc_best_trust(rate_betas_com)
best_trust_rate_com_theo = calc_best_trust(rate_betas_com_theo)

plot_best_trust_map(best_trust_rate, 'Real trajectories')
plot_best_trust_map(best_trust_rate_com, 'Real COM traj + real std ellipse')
# plot_best_trust_map(best_trust_rate_com_theo, 'Theo COM traj + real std ellipse')

show_and_check_ipython()
