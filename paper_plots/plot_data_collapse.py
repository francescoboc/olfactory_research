from utils import *
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

sigma = np.pi/2
# sigma = 0

speed = 0.2
# speed = 0.5
# speed = 1.0

n_samples = 10

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 

# visual_radius = rd
# visual_radius = 2*rd
visual_radius = 5*rd

# visual_radius = 10*rd #manca dt0.2.pkl
# visual_radius = 25*rd
# visual_radius = 50*rd

threshold = 1.0

shift = 0.0

n_agents = 100

# distance from the source
lx = 50

# noise on the estimate of the mean wind and on public 0elocity
sensing_noise = 0.0 # eta
wind_noise = 0.0

dts = [1.0, 0.5, 0.2, 0.1]

if speed == 0.2:
    dts = [0.5, 0.2, 0.1]
elif speed == 0.5:
    dts = [1.0, 0.2, 0.1]

lx = 50
# speed = 0.2 # v0
Ts = lx/speed # straight-line time

if visual_radius == 10*rd:
    dts = [1.0, 0.5, 0.1]


fig, ax = plt.subplots()  # crea figura e asse principali

axins = inset_axes(ax,
                   width="40%",  # width relative to parent
                   height="40%",  # height relative to parent
                   loc='upper left',  # ignored if bbox_to_anchor used
                   bbox_to_anchor=(0.055, -0.03, 1.0, 1.0),  # (x0, y0, width, height)
                   bbox_transform=ax.transAxes,)
                   # borderpad=2.0)

for i, dt  in enumerate(dts):
    folder = f'data_collapse/results/thr{threshold}/sigma{sigma:.2f}/speed{speed}/vr{visual_radius}_N{n_agents}_sr{spawn_radius}'
    # folder = f'data_collapse/results/thr{threshold}/vr{visual_radius}_N{n_agents}_sr{spawn_radius}'
    filename = f'dt{dt}'
    reach_times = pd.read_pickle(f'{folder}/{filename}.pkl')
    # print(reach_times.attrs)

    trusts = np.array(reach_times.index)

    best_times_avg, best_times_std = [], []
    mean_times_avg, mean_times_std = [], []
    for trust in trusts:
        times_runs = reach_times.loc[trust]['times']

        best_times = [times[0] for times in times_runs if len(times) > 0]

        best_times_avg.append(np.mean(best_times))
        best_times_std.append(np.std(best_times))

        mean_times = [np.mean(times) for times in times_runs]
        mean_times_avg.append(np.mean(mean_times))
        mean_times_std.append(np.std(mean_times))

    best_times_avg = np.array(best_times_avg)/Ts
    best_times_std = np.array(best_times_std)/Ts

    x_vals = (1 - trusts) / dt
    # x_vals = (1 - trusts) / (dt*speed)

    # shaded_errorbar(x_vals, best_times_avg, best_times_std, color=colors[i], marker=markers[i], label= r'$t_{\textrm{mem}}'+f'={dt}$', ax = ax)
    shaded_errorbar(x_vals, best_times_avg, best_times_std, color=colors[i], marker=markers[i], label= r'$ t_{\textrm{mem}}'+f'={dt}$', ax = ax)
    # shaded_errorbar(x_vals, best_times_avg, best_times_std, color=colors[i], marker=markers[i], label= r'$dt'+f'={dt}$')

    # inset
    shaded_errorbar(x_vals, best_times_avg, yerr=best_times_std, color=colors[i], marker=markers[i], ax=axins)

    # shaded_errorbar((1-trusts)/dt, mean_times_avg, mean_times_std, lab= fr'$dt={dt}$')

# axins.set_xlim(0, 0.18)
# axins.set_ylim(0.8, 1.6)
axins.set_xlim(0, 0.35)
axins.set_ylim(0.7, 3.7)
axins.tick_params(axis='both', which='both', labelsize=14)
axins.set_xticks([0,0.1,0.2,0.3])

# Collega il box allo zoom
mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5", alpha=0.5)

ax.set_xlabel(r'$(1-\beta)/t_{\textrm{mem}}$')
# ax.set_xlabel(r'$(1-\beta)/(dt v_0)$')
ax.set_ylabel(r'$\tau$')
ax.legend(loc='lower right')

# # ax.set_xlabel(r'$(1-\beta)/t_{\textrm{mem}}$')
# plt.xlabel(r'$(1-\beta)/(dt v_0)$')
# plt.ylabel(r'$\tau$')
# # ax.legend(loc='lower right')

# plt.figure(1)
# plt.xlabel(r'$(1-\beta)/{\Delta t}$')
# plt.ylabel('average arrival time')
# plt.legend()

# ax.set_title(speed)

show_and_check_ipython()

