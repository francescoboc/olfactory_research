from utils import *
from select_file import *

dicts_folder = f'beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dicts
fpt_betas = np.load(f'{dicts_folder}/fpt_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, r_v={visual_radius}')

# create an empty hexbin to get grid structure
hb = plt.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y])
bin_coords = hb.get_offsets()
plt.close()

straight_line_times = get_straight_line_times(bin_coords, spawn_radius, speed)

# TODO add error bars

fpts, rates = [], []
for trust in trusts:

    # extract the map at the current beta
    fpt_map = fpt_betas[trust]
    rate_map = rate_betas[trust]

    bin_idx = get_closest_bin(bin_coords, l_x, h_y)

    fpt_source = fpt_map[bin_idx]/straight_line_times[bin_idx]
    success_rate_source = rate_map[bin_idx]

    fpts.append(fpt_source)
    rates.append(success_rate_source)

# convert lists into numpy arrays for easier manipulation
fpts = np.array(fpts)
rates = np.array(rates)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

fpt_plot = ax1.plot(trusts, fpts, 'o-', color=colors[0], label=r'$\tau$')
rate_plot = ax2.plot(trusts, rates, 's--', color=colors[1], label=r'$\rho$')

all_plots = fpt_plot + rate_plot
labels = [p.get_label() for p in all_plots]
plt.legend(all_plots, labels)

ax1.set_ylabel(r'Average normalized FPT $\tau$')
ax2.set_ylabel(r'Average success rate $\rho$')
ax2.set_ylim(-0.02, 1.02)

ax1.set_xlabel(r'Trust $\beta$')

plt.title(rf'$\mu={mu:.2f}, \sigma={sigma:.2f}, L={l_x}, H={h_y}, r_v={visual_radius}$')

ax1.axhline(1, lw=1, c='k', alpha=0.5)

show_and_check_ipython()
