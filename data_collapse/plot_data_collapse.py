from olfactory_plot_utils import *

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

lx = 50
speed = 0.2 # v0
Ts = lx/speed # straight-line time

if visual_radius == 10*rd:
    dts = [1.0, 0.5, 0.1]

for dt in dts:
    folder = f'results/thr{threshold}/vr{visual_radius}_N{n_agents}_sr{spawn_radius}'
    filename = f'dt{dt}'
    reach_times = pd.read_pickle(f'{folder}/{filename}.pkl')

    trusts = np.array(reach_times.index)

    best_times_avg, best_times_std = [], []
    mean_times_avg, mean_times_std = [], []
    for trust in trusts:
        times_runs = reach_times.loc[trust]['times']
        best_times = []
        for times in times_runs:
            if len(times)>0:
                best_times.append(times[0])
            # best_times = [times[0] for times in times_runs]
        # best_times = [times[0] for times in times_runs]
        best_times_avg.append(np.mean(best_times))
        best_times_std.append(np.std(best_times))

        mean_times = [np.mean(times) for times in times_runs]
        mean_times_avg.append(np.mean(mean_times))
        mean_times_std.append(np.std(mean_times))

    best_times_avg = np.array(best_times_avg)/Ts
    best_times_std = np.array(best_times_std)/Ts

    plt.figure(0)
    shaded_errorbar((1-trusts)/dt, best_times_avg, best_times_std, lab= fr'$\Delta t={dt}$')

    # plt.figure(1)
    # shaded_errorbar((1-trusts)/dt, mean_times_avg, mean_times_std, lab= fr'$dt={dt}$')

plt.figure(0)
plt.xlabel(r'$(1-\beta)/{\Delta t}$')
# plt.ylabel('first passage time')
plt.ylabel(r'$T/T_s$')
plt.legend()

# plt.figure(1)
# plt.xlabel(r'$(1-\beta)/{\Delta t}$')
# plt.ylabel('average arrival time')
# plt.legend()

show_and_check_ipython()

