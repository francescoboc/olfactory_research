from olfactory_plot_utils import *

folder = 'turbulent/maxt_50ts'

x_label = r'Trust parameter $\beta$'

visual_radius = 1000
decision_time = 1
threshold = 0.0008
kelast = 1
shift = 0.0
n_agents = 50
speed = 1
olfactory_radius = 0.1

filename = f'{folder}/free_ra{visual_radius}_dt{decision_time}_thr{threshold}_k{kelast}_shift{shift}_N{n_agents}_speed{speed}_ro{olfactory_radius}'

# filename = f'free_j10_v0.2'
# filename = f'elastic_j10_v0.2'

lab = 'new flow elastic $r_a=0.5$'
# lab = 'old flow free, $r_a=1$'
# lab = 'old flow elastic, $r_a=1$'

# load results in a dataframe
results_raw = pd.read_pickle(f'results/{filename}.pkl')

print_attributes(results_raw)

# make a clean dataframe without raw data
results = results_raw.copy()
results = results.drop(['times', 'n_agents', 'seeds'], axis='columns')

# calculate means and stds
results['time_avg'] = results_raw['times'].apply(np.mean)
results['nagents_avg'] = results_raw['n_agents'].apply(np.mean)
results['time_std'] = results_raw['times'].apply(np.std)
results['nagents_std'] = results_raw['n_agents'].apply(np.std)

# maybe plot Ts/T?

# normalise
results_norm = results.copy()
Ts = results.attrs['Lx']/results.attrs['speed']
N_agents = results.attrs['n_agents']
N_episodes = len(results_raw['times'].values[0])
results_norm['time_avg'] = results['time_avg']/Ts
results_norm['nagents_avg'] = results['nagents_avg']/N_agents
results_norm['time_std'] = results['time_std']/Ts
results_norm['nagents_std'] = results['nagents_std']/N_agents
# results_norm['fails'] = results['fails']/(N_episodes+results['fails'])
results_norm['fails'] = results['fails']/(N_episodes)

# marker index
index = 0

betas = results.index

plt.figure(1)
plt.plot(betas, 'fails', data=results_norm, marker=markers[index], label=lab)

plt.figure(2)
plt.errorbar(betas, 'time_avg', yerr='time_std', data=results_norm, marker=markers[index], label=lab)

# plt.figure(3)
# plt.errorbar(betas, 'nagents_avg', yerr='nagents_std', data=results_norm, marker=markers[index], label=lab)

plt.figure(1)
plt.xlabel(x_label)
plt.ylabel(r'Fraction of failed episodes')
# plt.title(title)

plt.figure(2)
plt.axhline(1, c='k', lw=1, ls='--')
plt.xlabel(x_label)
plt.ylabel(r'$T/T_s$')
# plt.title(title)

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
