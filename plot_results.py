import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# extract default colors and markers
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
markers = list(plt.Line2D.markers.keys())

# update matplotlib parameters globally
plt.rcParams['lines.markerfacecolor'] = 'none'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['errorbar.capsize'] = 2
plt.rcParams['legend.fancybox'] = False

# dts to plot
particle_dts = [1, 0.2, 0.1]

index = 2
for particle_dt in particle_dts:
    # import results in a dataframe
    results = pd.read_pickle(f'results_dt{particle_dt:.2f}.pkl')

    # calculate means and stds
    results['time_avg'] = results['times'].apply(np.mean)
    results['nagents_avg'] = results['n_agents'].apply(np.mean)
    results['time_std'] = results['times'].apply(np.std)
    results['nagents_std'] = results['n_agents'].apply(np.std)

    # remove raw data
    results = results.drop(['times', 'n_agents'], axis='columns')

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
plt.legend()

plt.figure(2)
plt.xlabel(r'Trust parameter $\beta$')
plt.ylabel(r'Fraction of agents $< R_b$')
plt.legend()

plt.ion(); plt.show()
