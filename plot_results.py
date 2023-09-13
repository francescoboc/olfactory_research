from olfactory_plot_utils import *

folder = 'turbulent/maxt_50ts'
# folder = 'turbulent/maxt_10ts'

x_label = r'Trust parameter $\beta$'

legend = True

# beta = 0.85

radii = [0.1, 0.5, 1, 5, 10]

# particle_dts = [1, 0.5, 0.2, 0.1, 0.05, 0.02]
# thrs = [0.0001, 0.0005, 0.001, 0.002, 0.003, 0.005, 0.01]

shift = 0.4
kelast = 1
n_agents = 100
decision_time = 1
threshold = 0.0008

title = f'shift={shift}, N={n_agents}'

index = 0
for visual_radius in radii:
    filename = f'{folder}/r280_ra{visual_radius}_dt{decision_time}_thr{threshold}_k{kelast}_shift{shift}_N{n_agents}'
    # filename = f'{folder}/free_ra{visual_radius}_dt{decision_time}_thr{threshold}_k{kelast}_shift{shift}_N{n_agents}'

    # load results in a dataframe
    try: 
        results_raw = pd.read_pickle(f'results/{filename}.pkl')
        present = True
    except: 
        print(f'{filename} does not exist!')
        present = False

    if present:
        # make a clean dataframe without raw data
        results = results_raw.copy()
        results = results.drop(['times', 'n_agents', 'seeds'], axis='columns')

        # calculate means and stds
        results['time_avg'] = results_raw['times'].apply(np.mean)
        results['nagents_avg'] = results_raw['n_agents'].apply(np.mean)
        results['time_std'] = results_raw['times'].apply(np.std)
        results['nagents_std'] = results_raw['n_agents'].apply(np.std)

        # normalise
        results_norm = results.copy()
        Ts = results.attrs['Lx']/results.attrs['speed']
        N_agents = results.attrs['n_agents']
        N_episodes = len(results_raw['times'].values[0])
        results_norm['time_avg'] = results['time_avg']/Ts
        results_norm['nagents_avg'] = results['nagents_avg']/N_agents
        results_norm['time_std'] = results['time_std']/Ts
        results_norm['nagents_std'] = results['nagents_std']/N_agents
        results_norm['fails'] = results['fails']/(N_episodes+results['fails'])

        plt.figure(1)
        plt.plot(results.index, 'fails', data=results_norm, marker=markers[index], label=f'$r_a={visual_radius}$')
        # plt.plot(results.index, 'fails', data=results_norm, marker=markers[index], label=thr)

        plt.figure(2)
        plt.errorbar(results.index, 'time_avg', yerr='time_std', data=results_norm, marker=markers[index], label=f'$r_a={visual_radius}$')

        # plt.figure(3)
        # plt.errorbar(results.index, 'nagents_avg', yerr='nagents_std', data=results_norm, marker=markers[index])

        index += 1

plt.figure(1)
plt.xlabel(x_label)
plt.ylabel(r'Fraction of failed episodes')
plt.title(title)
if legend: plt.legend()

plt.figure(2)
plt.axhline(1, c='k', lw=1, ls='--')
plt.xlabel(x_label)
plt.ylabel(r'$T/T_s$')
plt.title(title)
if legend: plt.legend()

# plt.figure(3)
# plt.xlabel(x_label)
# plt.ylabel(r'Fraction of agents $< R_b$')
# # plt.title(title)
# if legend: plt.legend()

# # MIHIR DATA
# foldername = 'nonuniform10'
# # foldername = 'uniform10'
# betas = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
# mean_agents, std_agents = [], []
# mean_time, std_time = [], []
# for beta in betas:
#     Nagents_raw = np.loadtxt(f'mihir_results/{foldername}/{beta:.2f}/Less_than_Rb.txt')
#     time_raw = np.loadtxt(f'mihir_results/{foldername}/{beta:.2f}/reach_time.txt')
#     Nagents = []
#     for entry in Nagents_raw:
#         Nagents.append(entry[1])
#     mean_agents.append(np.mean(Nagents)/len(Nagents))
#     std_agents.append(np.std(Nagents)/len(Nagents))
#     times = []
#     for entry in time_raw:
#         times.append(entry[1])
#     mean_time.append(np.mean(times)/Ts)
#     std_time.append(np.std(times)/Ts)

# plt.figure(1)
# plt.errorbar(betas, mean_time, yerr=std_time, label='mihir', marker=markers[index])
# plt.legend()

# plt.figure(2)
# plt.errorbar(betas, mean_agents, yerr=std_agents, label='mihir', marker=markers[index])
# plt.legend()

plt.ion(); plt.show()
