import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# extract default colors and markers
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
# markers = list(plt.Line2D.markers.keys())
markers = ['o', 's', 'd', 'v', '^', '<', '>']

def print_attributes(dataframe):
    for key in dataframe.attrs.keys():
        print(f'{key} = {dataframe.attrs[key]}')

# update matplotlib parameters globally
plt.rcParams['lines.markerfacecolor'] = 'none'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['errorbar.capsize'] = 2
plt.rcParams['legend.fancybox'] = False

# filename = 'nonuniform10'
# filename = 'uniform10'
# filename = 'nonuniform_j5'
# filename = 'nonuniform_j5'

# filename = 'dt0.001'
# filename = 'approx_dt0.01'
# filename = 'approx_dt0.1'
# filename = 'exact_dt0.01'
# filename = 'exact_dt0.1'

# filename = 'free_j10_v0.2'
# filename = 'elastic_j10_v0.2'

# filename = 'vary_radius_free1'
# filename = 'vary_radius_free'
filename = 'vary_radius_elastic'

# x_label = r'Trust parameter $\beta$'
x_label = r'Swarm radius $R_b$'

legend = True

# dts to plot
# particle_dts = [1, 0.5, 0.2, 0.1, 0.05, 0.02]
# particle_dts = [0.2, 0.1, 0.05, 0.02]
particle_dts = [0.1]

# beta = 0.85

index = 0
for particle_dt in particle_dts:
    # label = f'$\delta t={particle_dt:.2f}$'
    # label = 'Unconstrained'
    label = 'Elastic constrain'

    # load results in a dataframe
    try: 
        results_raw = pd.read_pickle(f'results/{filename}.pkl')
        present = True
    except: present = False

    if present:
        # print details of the simulation
        print_attributes(results_raw)

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

        # plot
        plt.figure(1)
        plt.errorbar(results.index, 'time_avg', yerr='time_std', data=results_norm, 
                label=label, marker=markers[index])

        plt.figure(2)
        plt.errorbar(results.index, 'nagents_avg', yerr='nagents_std', data=results_norm, 
                label=label, marker=markers[index])

        plt.figure(3)
        plt.plot(results.index, 'fails', data=results_norm, label=label, marker=markers[index])

        index += 1

J = results.attrs['particle_rate']
v0 = results.attrs['speed']
title = f'$J={J}, v_0={v0}$'

print(results)

plt.figure(1)
plt.axhline(1, c='k', lw=1)
plt.xlabel(x_label)
plt.ylabel(r'$T/T_s$')
plt.title(title)
if legend: plt.legend()

plt.figure(2)
plt.xlabel(x_label)
plt.ylabel(r'Fraction of agents $< R_b$')
plt.title(title)
if legend: plt.legend()

plt.figure(3)
plt.xlabel(x_label)
plt.ylabel(r'Fraction of failed episodes')
plt.title(title)
if legend: plt.legend()



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
