from utils import *
from select_file import *

from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize

# trusts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
trusts = [ 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

# Supponiamo che 'labels' sia una lista di stringhe (una per curva)
N = len(trusts)

# Colormap discretizzata
cmap = get_cmap('rainbow', N)   # o qualsiasi colormap
norm = Normalize(vmin=0, vmax=N-1)

plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams['legend.fontsize'] = 14 
plt.rcParams['legend.title_fontsize'] = 12

# simulation without odor
no_odor = 1

variable = 'shift'
# variable = 'angle'
# variable = 'sigma'

filename = rf'perf_{variable}_finiterange.pdf'
savefig = True

visual_radius = 5*rd
# visual_radius = 100*spawn_radius
print(f'r_v={visual_radius}')

# fig, ax1 = plt.subplots(figsize=square_figsize)
# fig, ax1 = plt.subplots()

# fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True)
fig, (ax1, ax2) = plt.subplots(1, 2)
fig.set_size_inches(7, 3.5)

if variable == 'shift':
    iterable = [0, 10, 16, 20]
    # iterable = np.arange(0,21,2)
    # iterable = [0]
    l_x = 75
    mu = 0
    sigma = 0
    labels = [rf'${h}$' for h in iterable]
    legend_title=r'Shift $H$'
elif variable == 'angle':
    iterable = [0, np.pi/4, np.pi/2]
    labels=['$0$', '$\pi/4$', '$\pi/2$']
    l_x = 75
    h_y = 0 
    sigma = 0
    legend_title=r'Mean $\mu$'
elif variable == 'sigma':
    iterable = [0, np.pi/4, np.pi/2]
    labels=['$0$', '$\pi/4$', '$\pi/2$']
    l_x = 75
    h_y = 0 
    mu = 0
    legend_title=r'STD $\sigma$'

color_fpt = colors[0]
color_rate = colors[3]

c=0

for item in iterable:
    if variable == 'shift': h_y = item
    elif variable == 'angle': mu = item
    elif variable == 'sigma': sigma = item

    trusts_plot = []
    fpts, rates = [], []
    fpts_std = []
    std_above, std_below = [], []
    for trust in trusts:

        source_coordinates = [l_x, h_y]

        if no_odor:
            fpt_folder = f'../first_passages/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/source_coord{source_coordinates[0]}_{source_coordinates[1]}/trust{trust}'
        else:
            fpt_folder = f'../first_passages_odor/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/source_coord{source_coordinates[0]}_{source_coordinates[1]}/trust{trust}'

        try:
            reach_times = np.load(f'{fpt_folder}/reach_times.npy')

            straight_line_time = np.sqrt((l_x-spawn_radius)**2 + h_y**2)/speed

            mean_time = np.mean(reach_times[~np.isinf(reach_times)])
            std_time = np.std(reach_times[~np.isinf(reach_times)])/straight_line_time
            fpt_source = mean_time/straight_line_time

            reach_times_noinf = reach_times[~np.isinf(reach_times)]
            std_above.append(np.std(reach_times_noinf[reach_times_noinf>mean_time])/straight_line_time)
            std_below.append(np.std(reach_times_noinf[reach_times_noinf<mean_time])/straight_line_time)

            success_rate_source = 1 - np.count_nonzero(np.isinf(reach_times))/len(reach_times)

            fpts.append(fpt_source)
            fpts_std.append(std_time)
            rates.append(success_rate_source)
            trusts_plot.append(trust)
        except:
            print(f'shift {h_y}, trust {trust} missing')

    # convert lists into numpy arrays for easier manipulation
    rates = np.array(rates)

    shaded_errorbar(trusts_plot, fpts, yerr=(std_below, std_above), ls='-', color=colors[c], marker=markers[c], ax=ax1, label=labels[c])
    ax2.plot(trusts_plot, rates, ls='--', color=colors[c], marker=markers[c], label=labels[c])

    # shaded_errorbar(trusts_plot, fpts, yerr=(std_below, std_above), ls='-', ax=ax1, label=labels[c], color = cmap(norm(c)))
    # ax2.plot(trusts_plot, rates, ls='--', label=labels[c], color = cmap(norm(c)))

    c+=1

ax1.axhline(1, lw=0.5, c='k', ls='-', alpha=0.6, zorder=0)
ax1.text(0.15, 1, r'$\tau = 1$', fontsize=13, color='black', ha='center', va='center', alpha=0.6, 
        bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1'))
ax1.set_ylabel(r'Average normalized FPT $\tau$')
ax1.set_yscale('log')

ax2.set_ylabel(r'Success rate $\rho$')
margin = 0.03
ax2.set_ylim(-margin, 1+margin)

# ax2.legend(title=legend_title, loc='lower left')
ax1.legend(title=legend_title, loc='upper center')
# ax1.set_xlabel(r'Trust $\beta$')
# ax2.set_xlabel(r'Trust $\beta$')

ax1.set_xticks([0.25, 0.5, 0.75])
ax2.set_xticks([0.25, 0.5, 0.75])

# ax1.set_title('Finite visual range')
# ax1.text(0.5, 0.95, 'Finite visual range', transform=ax1.transAxes, va='top', ha='center')


# from matplotlib.cm import ScalarMappable
# from matplotlib.colors import BoundaryNorm

# # boundaries per N colori: N+1 bordi
# boundaries = np.linspace(-0.5, N - 0.5, N + 1)
# norm = BoundaryNorm(boundaries, cmap.N)

# # centri dei bin
# centers = 0.5 * (boundaries[:-1] + boundaries[1:])

# sm = ScalarMappable(norm=norm, cmap=cmap)
# sm.set_array([])

# cbar = fig.colorbar(sm, ax=[ax1, ax2], pad=0.02)

# # ✔ tick al centro esatto
# cbar.set_ticks(centers)
# cbar.set_ticklabels(labels)

# cbar.set_label(r"Shift $H$")


show_and_check_ipython()

# if savefig: fig.savefig(save_directory + filename)
