from olfactory_plot_utils import *

# exp = 'unconstrained'
exp = 'single_particle'
# exp = 'delta_informed'

# exp = 'constrained'

no_odor = 0

legend = True
x_label = r'Trust parameter $\beta$'

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 

# olfactory threshold
if no_odor: threshold = 1.0
else: threshold = 0.0005

# # initial conditions
# shifts = np.linspace(0, 3, 6)*spawn_radius
# shift = shifts[0]

# shifts=[3.0,9.0,15.0]
shifts=[0]

# visual_radii = np.array([1, 2, 5, 10, 25])*rd
# visual_radii = np.array([1, 5, 25])*rd
visual_radii = np.array([5])*rd
visual_radius = 5*rd

if exp=='single_particle':
    visual_radii = range(1)

n_agents = 100
# n_agents = 10

# if no_odor: title = f'shift={shift}, N={n_agents}, no odor'
# else: title = f'shift={shift}, N={n_agents}'

if no_odor: title = f'visual radius={visual_radius}, N={n_agents}, no odor'
else: title = f'visual radius={visual_radius}, N={n_agents}'

# distance from the source
lx = 65

# noise on the estimate of the mean wind and on public velocity
sensing_noise = 0.0 # eta
wind_noise = 0.0 

index = 0

for shift in shifts:
# for visual_radius in visual_radii:
    folder = f'results/{exp}/shift%.3f'%shift
    if no_odor: folder += '/casting'

    if exp=='single_particle':
        filename = f'thr{threshold}_N{n_agents}_snoise{sensing_noise}_wnoise{wind_noise}'
    else:
        filename = f'vr{visual_radius}_thr{threshold}_N{n_agents}_snoise{sensing_noise}_wnoise{wind_noise}'

    filename += '_sigma_pi'

    # load results from a dataframe
    try: 
        results_raw = pd.read_pickle(f'{folder}/{filename}.pkl')
        present = True
    except: 
        print(f'{folder}/{filename}.pkl does not exist!')
        present = False

    if present:
        # make a clean dataframe without raw data
        results = results_raw.copy()
        results = results.drop(['times', 'n_agents', 'seeds'], axis='columns')

        # check which trust runs have reached the desired number of samples
        reached_desired_samples = [len(results_raw['times'][trust]) == results_raw.attrs['n_samples'] for trust in results_raw.index]

        # calculate means and stds
        results['successes'] = results_raw['times'].apply(len)
        results['time_avg'] = results_raw['times'].apply(np.mean)
        results['nagents_avg'] = results_raw['n_agents'].apply(np.mean)
        results['time_std'] = results_raw['times'].apply(np.std)
        results['nagents_std'] = results_raw['n_agents'].apply(np.std)

        # normalise
        results_norm = results.copy()
        # Ts = results.attrs['lx']/results.attrs['speed']
        lx = results.attrs['lx']
        line_distance = (lx**2 + shift**2)**0.5
        Ts = line_distance/results.attrs['speed']
        N_agents = results.attrs['n_agents']
        results_norm['time_avg'] = results['time_avg']/Ts
        results_norm['nagents_avg'] = results['nagents_avg']/N_agents
        results_norm['time_std'] = results['time_std']/Ts
        results_norm['nagents_std'] = results['nagents_std']/N_agents
        results_norm['fails'] = results['fails']/(results['successes']+results['fails'])

        plt.figure(0)
        plt.plot(results.index, 'fails', data=results_norm, marker=markers[index], label=f'$r_v={visual_radius}$')
        # plt.plot(results.index, 'fails', data=results_norm, marker=markers[index], label=f'shift={shift}')
        plt.xlabel(x_label)
        plt.ylabel(r'Fraction of failed episodes')
        plt.title(title)
        plt.xlim(min(results.index)-0.05, max(results.index)+0.05)
        if legend: plt.legend(loc=2)

        plt.figure(1)
        # shaded_errorbar(results.index[reached_desired_samples], results_norm['time_avg'][reached_desired_samples], results_norm['time_std'][reached_desired_samples], m=markers[index], lab=f'$r_v={visual_radius}$')
        # shaded_errorbar(results.index[reached_desired_samples], results_norm['time_avg'][reached_desired_samples], results_norm['time_std'][reached_desired_samples], m=markers[index], lab=f'shift={shift}')
        shaded_errorbar(results.index[reached_desired_samples], results_norm['time_avg'][reached_desired_samples], 
                # results_norm['time_std'][reached_desired_samples], m=markers[index], lab=f'Full model, with odor')
                results_norm['time_std'][reached_desired_samples], m=markers[index], lab=f'Independent agents, with odor')
        # plt.axhline(1, c='k', lw=1, ls='--')
        plt.xlabel(x_label)
        plt.ylabel(r'$T/T_s$')
        plt.title(title)
        plt.xlim(min(results.index)-0.05, max(results.index)+0.05)
        # plt.ylim(0, 14)
        if legend: plt.legend(loc=2)

        # plt.figure(2)
        # shaded_errorbar(results.index[reached_desired_samples], results_norm['nagents_avg'][reached_desired_samples], results_norm['nagents_std'][reached_desired_samples], m=markers[index], lab=f'$r_v={visual_radius}$')
        # plt.xlabel(x_label)
        # plt.ylabel(r'Fraction of agents $< R_b$')
        # plt.title(title)
        # plt.xlim(min(results.index)-0.05, max(results.index)+0.05)
        # if legend: plt.legend(loc=2)

        index += 1

# plt.ylim(0,35)
# plt.xlim(0.35,1.05)

plt.ylim(0.5,4)
plt.xlim(0.05,1.05)

plt.ion(); plt.show()
