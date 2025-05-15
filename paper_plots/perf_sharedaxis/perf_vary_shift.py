from utils import *
from select_file import *

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

dicts_folder = f'../beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

dummy_fig, dummy_ax = plt.subplots()
hb = dummy_ax.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y])
plt.close(dummy_fig)
bin_coords = hb.get_offsets()  

fig, ax1 = plt.subplots(figsize=square_figsize_reduced)
ax2 = ax1.twinx()

# hys = [0, 5, 10, 12, 14, 16]
hys = [0,10, 16, 20]
lxs = [75 for h in hys]
labels = [rf'${h}$' for h in hys]

# theta
mu = 0

sigma = 0

# color_fpt = colors[0]
# color_rate = colors[3]

print(f'r_v={visual_radius}')

c=0
legend_handles = []  # Store marker-only plots for legend
for l_x, h_y in zip(lxs, hys):

    fpts, rates = [], []
    for trust in trusts:
        fpt_source = get_first_passage_source(trust, l_x, h_y)
        success_rate_source = get_success_rate_source(trust, l_x, h_y)
        fpts.append(fpt_source)
        rates.append(success_rate_source)

    # convert lists into numpy arrays for easier manipulation
    # fpts = 1/np.array(fpts)
    rates = np.array(rates)

    fpt_plot = ax1.plot(trusts, fpts, '-', color=colors[c], marker=markers[c])
    rate_plot = ax2.plot(trusts, rates, ':', color=colors[c], marker=markers[c])

    # "Ghost" plot: Only markers (no lines), stored for legend
    marker_handle, = ax2.plot([], [], color=colors[c], marker=markers[c], linestyle='', label=labels[c])
    legend_handles.append(marker_handle)  # Store for later use

    c+=1

ax1.axhline(1, lw=0.5, c='k', ls='-', alpha=0.6, zorder=0)
ax1.text(0.21, 1, r'$\tau = 1$', fontsize=15, color='black', ha='center', va='center', alpha=0.6,
         bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2'))

ax1.set_ylabel(r'Average normalized FPT $\tau$')
ax2.set_ylabel(r'Average success rate $\rho$')
ax2.set_ylim(-0.02, 1.02)

# # ax1.set_xlabel(r'Trust $\beta$')
# ax1.set_xticklabels([])

# plt.title(r'Varying initial shift $H$ ($\theta=0, \sigma=0$)')

# ax1.yaxis.label.set_color(color_fpt)
# ax2.yaxis.label.set_color(color_rate)

# Create custom legend handles
import matplotlib.lines as mlines
fpt_handle = mlines.Line2D([], [], color='grey', linestyle='-', label=r'$\tau$')
rho_handle = mlines.Line2D([], [], color='grey', linestyle=':', label=r'$\rho$')

ax1.legend(handles=[fpt_handle, rho_handle], handlelength=1, handletextpad=0.5, loc=6, 
        bbox_to_anchor=(0,0.35))
ax2.legend(handles=legend_handles, handletextpad=0.0, loc='center right',
    title=r'Shift $H$')
        
ax1.text(0.015, 0.5, r'$(a)$', transform=ax1.transAxes, fontsize=15, color='black', ha='left', va='center')

# ax1.set_ylim(-1.41, 52.03)
ax1.set_yscale('log')

show_and_check_ipython()

filename = 'perf_shift.pdf'
fig.savefig(save_directory + filename)
