import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# extract default colors and markers
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
markers = list(plt.Line2D.markers.keys())
# markers = ['o', 's', 'd', 'v', '^', '<', '>']

def print_attributes(dataframe):
    for key in dataframe.attrs.keys():
        print(f'{key} = {dataframe.attrs[key]}')

# update matplotlib parameters globally
plt.rcParams['lines.markerfacecolor'] = 'none'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['errorbar.capsize'] = 2
plt.rcParams['legend.fancybox'] = False

# name = 'square'
# name = 'zeroamp' # amplitudes of wind noise are initialised at 0
# name = 'lownoise' # fluct_intensity is reduced by half
# name = 'J5square' # higher particle rate
# name = 'new' 
name = 'elastic' 

# dts to plot
# particle_dts = [1, 0.5, 0.2, 0.1, 0.05, 0.02]
# particle_dts = [0.2, 0.1, 0.05, 0.02]
particle_dts = [0.1]

index = 2
for particle_dt in particle_dts:
    # load results in a dataframe
    try: 
        results = pd.read_pickle(f'results/{name}_results_dt{particle_dt:.2f}.pkl')
        present = True
    except: present = False

    if present:
        # calculate means and stds
        results['time_avg'] = results['times'].apply(np.mean)
        results['nagents_avg'] = results['n_agents'].apply(np.mean)
        results['time_std'] = results['times'].apply(np.std)
        results['nagents_std'] = results['n_agents'].apply(np.std)

        # remove raw data
        results = results.drop(['times', 'n_agents'], axis='columns')
        print_attributes(results)

        # normalise
        results_norm = results.copy()
        Ts = results.attrs['Lx']/results.attrs['speed']
        N_agents = results.attrs['n_agents']
        results_norm['time_avg'] = results['time_avg']/Ts
        results_norm['nagents_avg'] = results['nagents_avg']/N_agents
        results_norm['time_std'] = results['time_std']/Ts
        results_norm['nagents_std'] = results['nagents_std']/N_agents

        # plot
        plt.figure(1)
        plt.errorbar(results.index, 'time_avg', yerr='time_std', data=results_norm, 
                label=f'$\delta t={particle_dt:.2f}$', marker=markers[index])

        plt.figure(2)
        plt.errorbar(results.index, 'nagents_avg', yerr='nagents_std', data=results_norm, 
                label=f'$\delta t={particle_dt:.2f}$', marker=markers[index])

        index += 1

plt.figure(1)
plt.axhline(1, c='k', lw=1)
plt.xlabel(r'Trust parameter $\beta$')
plt.ylabel(r'$T/T_s$')
plt.title(f'{name}')
plt.legend()

plt.figure(2)
plt.xlabel(r'Trust parameter $\beta$')
plt.ylabel(r'Fraction of agents $< R_b$')
plt.title(f'{name}')
plt.legend()

plt.ion(); plt.show()
