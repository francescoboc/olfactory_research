from utils import *
from select_file import *

plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams['legend.fontsize'] = 14 
plt.rcParams['legend.title_fontsize'] = 12

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

variable = 'shift'
# variable = 'angle'
# variable = 'sigma'

filename = rf'perf_{variable}_infiniterange.pdf'
savefig = True

# fig, ax1 = plt.subplots(figsize=square_figsize)
# fig, ax1 = plt.subplots()

# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
fig, (ax1, ax2) = plt.subplots(1, 2)
fig.set_size_inches(7, 3.5)

if variable == 'shift':
    iterable = [0, 10, 16, 20]
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
    legend_title=r'Angle $\theta$'
elif variable == 'sigma':
    iterable = [0, np.pi/4, np.pi/2]
    labels=['$0$', '$\pi/4$', '$\pi/2$']
    l_x = 75
    h_y = 0 
    mu = 0
    legend_title=r'STD $\sigma$'

visual_radius = 100*spawn_radius
print(f'r_v={visual_radius}')

dummy_fig, dummy_ax = plt.subplots()
hb = dummy_ax.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y])
plt.close(dummy_fig)
bin_coords = hb.get_offsets()  

c=0

for item in iterable:
    if variable == 'shift': h_y = item
    elif variable == 'angle': mu = item
    elif variable == 'sigma': sigma = item

    dicts_folder = f'../beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

    fpts, rates = [], []
    for trust in trusts:
        fpt_source = get_first_passage_source(trust, l_x, h_y)
        success_rate_source = get_success_rate_source(trust, l_x, h_y)
        fpts.append(fpt_source)
        rates.append(success_rate_source)

    # convert lists into numpy arrays for easier manipulation
    rates = np.array(rates)

    ax1.plot(trusts, fpts, '-', color=colors[c], marker=markers[c], label=labels[c])
    ax2.plot(trusts, rates, '--', color=colors[c], marker=markers[c], label=labels[c])

    c+=1

ax1.axhline(1, lw=0.5, c='k', ls='-', alpha=0.6, zorder=0)
ax1.text(0.15, 1, r'$\tau = 1$', fontsize=13, color='black', ha='center', va='center', alpha=0.6, 
        bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2'))
ax1.set_ylabel(r'Average normalized FPT $\tau$')
ax1.set_yscale('log')

ax2.set_ylabel(r'Success rate $\rho$')
margin = 0.03
plt.ylim(-margin, 1+margin)

ax1.legend(title=legend_title)
ax1.set_xlabel(r'Trust $\beta$')
ax2.set_xlabel(r'Trust $\beta$')

# ax1.set_title('Infinite visual range')
# ax1.text(0.5, 0.95, 'Infinite visual range', transform=ax1.transAxes, va='top', ha='center')

if variable == 'shift':
    ax1.set_ylim(0.7103375391714687, 1189.7595744425619)

show_and_check_ipython()

# if savefig: fig.savefig(save_directory + filename)
