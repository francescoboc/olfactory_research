from utils import *
from select_file import *
import os

dicts_folder = f'beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

dummy_fig, dummy_ax = plt.subplots()
hb = dummy_ax.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y])
plt.close(dummy_fig)
bin_coords = hb.get_offsets()  

def get_success_rate_source(trust, x, y):
    rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

    success_rate = rate_betas[trust]

    # calculate the distance to each hexbin center and find the closest bin to the source
    distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
    bin_idx = np.argmin(distances)
    success_rate_source = success_rate[bin_idx]

    return success_rate_source

def get_first_passage_source(trust, x, y):
    fpt_betas = np.load(f'{dicts_folder}/fpt_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

    avg_fpt = fpt_betas[trust]

    # Calculate the distance to each hexbin center and find the closest bin to the source
    distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
    bin_idx = np.argmin(distances)
    fpt_source = avg_fpt[bin_idx]

    x_s, y_s = bin_coords[bin_idx][0], bin_coords[bin_idx][1]
    straight_line_time = np.sqrt((x_s-spawn_radius)**2 + y_s**2)/speed

    return fpt_source/straight_line_time

trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

# TODO add errorbars!
# TODO change marker with color (just use -- for rho and - for tau)

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, r_v={visual_radius}')

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

lxs = [50,50,50]
hys = [0,4,8]

c=0
for l_x, h_y in zip(lxs, hys):

    fpts, rates = [], []
    for trust in trusts:
        fpt_source = get_first_passage_source(trust, l_x, h_y)
        success_rate_source = get_success_rate_source(trust, l_x, h_y)
        fpts.append(fpt_source)
        rates.append(success_rate_source)

    # convert lists into numpy arrays for easier manipulation
    fpts = np.array(fpts)
    rates = np.array(rates)

    fpt_plot = ax1.plot(trusts, fpts, 'o-', color=colors[c], label=f'{h_y}')
    rate_plot = ax2.plot(trusts, rates, 's--', color=colors[c])

    c+=1

all_plots = fpt_plot + rate_plot
labels = [p.get_label() for p in all_plots]
plt.legend(all_plots, labels)

ax1.set_ylabel(r'Average normalized first passage time $\tau$')
# ax1.set_ylabel(r'Average first passage time $\tau$')
ax2.set_ylabel(r'Average success rate $\rho$')
ax2.set_ylim(-0.02, 1.02)

ax1.set_xlabel(r'Trust $\beta$')

# plt.title(rf'$\mu={mu:.2f}, \sigma={sigma:.2f}, L={l_x}, H={h_y}, r_v={visual_radius}$')
# plt.title(rf'Source position B')
# plt.title(rf'Varying initial angle')
plt.title(rf'Varying shift H')

show_and_check_ipython()
