from utils import *
from select_file import *

fig, ax1 = plt.subplots(figsize=square_figsize)
ax2 = ax1.twinx()

l_x = 75
h_y = 0 

# theta
mu = 0

# sigmas = [0, np.pi/2, np.pi]
sigmas = [0, np.pi/4, np.pi/2]
labels=['$0$', '$\pi/4$', '$\pi/2$']

trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

# color_fpt = colors[0]
# color_rate = colors[3]

visual_radius = 5*rd

print(f'r_v={visual_radius}')

c=0
legend_handles = []  # Store marker-only plots for legend
for sigma in sigmas:

    trusts_plot = []
    fpts, rates = [], []
    fpts_std = []
    for trust in trusts:

        source_coordinates = [l_x, h_y]
        fpt_folder = f'../first_passages/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/source_coord{source_coordinates[0]}_{source_coordinates[1]}/trust{trust:.1f}'
        try:
            reach_times = np.load(f'{fpt_folder}/reach_times.npy')

            straight_line_time = np.sqrt((l_x-spawn_radius)**2 + h_y**2)/speed

            mean_time = np.mean(reach_times[~np.isinf(reach_times)])
            std_time = np.std(reach_times[~np.isinf(reach_times)])/straight_line_time
            fpt_source = mean_time/straight_line_time

            success_rate_source = 1 - np.count_nonzero(np.isinf(reach_times))/len(reach_times)

            fpts.append(fpt_source)
            fpts_std.append(std_time)
            rates.append(success_rate_source)
            trusts_plot.append(trust)
        except:
            print(f'sigma {sigma:.2f}, trust {trust} missing')

    # convert lists into numpy arrays for easier manipulation
    fpts = np.array(fpts)
    rates = np.array(rates)

    # fpt_plot = ax1.plot(trusts_plot, fpts, ':', color=colors[c], marker=markers[c])
    # fpt_plot = shaded_errorbar(trusts_plot, fpts, fpts_std, ls='-', c=colors[c], m=markers[c], ax=ax1)
    fpt_plot = ax1.errorbar(trusts_plot, fpts, yerr=fpts_std, ls=':', color=colors[c], marker=markers[c])

    rate_plot = ax2.plot(trusts_plot, rates, '-', color=colors[c], marker=markers[c])

    # "Ghost" plot: Only markers (no lines), stored for legend
    marker_handle, = ax2.plot([], [], color=colors[c], marker=markers[c], linestyle='', label=labels[c])
    legend_handles.append(marker_handle)  # Store for later use

    c+=1

ax1.axhline(1, lw=0.5, c='k', ls='-', alpha=0.6, zorder=0)
ax1.text(0.27, 1, r'$\tau = 1$', fontsize=15, color='black', ha='center', va='center', alpha=0.6,
         bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2'))

ax1.set_ylabel(r'Average normalized FPT $\tau$')
# ax1.set_yscale('log')

ax2.set_ylabel(r'Average success rate $\rho$')
# ax2.set_ylabel(r'Standard deviation')
ax2.set_ylim(-0.02, 1.02)


ax1.set_xlabel(r'Trust $\beta$')

# plt.title(r'Varying initial angle STD $\sigma$ ($H=0, \theta=0$)')

# ax1.yaxis.label.set_color(color_fpt)
# ax2.yaxis.label.set_color(color_rate)

# Create custom legend handles
import matplotlib.lines as mlines
fpt_handle = mlines.Line2D([], [], color='grey', linestyle=':', label=r'$\tau$')
rho_handle = mlines.Line2D([], [], color='grey', linestyle='-', label=r'$\rho$')

ax1.legend(handles=[fpt_handle, rho_handle], handlelength=1, handletextpad=0.5, loc=6, bbox_to_anchor=(0,0.35))
ax2.legend(handles=legend_handles, handletextpad=0.0, loc='lower left',
    title=r'STD $\sigma$')

ax1.text(0.015, 0.5, r'$(c)$', transform=ax1.transAxes, fontsize=15, color='black', ha='left', va='center')

# ax1.set_ylim(-1.41, 52.03)

show_and_check_ipython()

# filename = 'perf_std_finiterange.pdf'
# fig.savefig(save_directory + filename)

