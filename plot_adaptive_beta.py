from olfactory_lib import *
import pandas as pd

folder = 'adaptive_beta'
# filename = 'adaptive_beta_elastic_decay4_refined'
filename = 'adaptive_beta_elastic_decay4'

# load results in a dataframe
results_raw = pd.read_pickle(f'results/{folder}/{filename}.pkl')

trust_inf, trust_uninf = [], []
for tu, ti in results_raw.index.values:
    trust_inf.append(ti)
    trust_uninf.append(tu)

trust_inf = np.unique(trust_inf)
trust_uninf = np.unique(trust_uninf)

n_samples = len(results_raw.loc[(trust_uninf[0], trust_inf[0])]['times'])

# calculate parameters
v0 = results_raw.attrs['speed']
Lx = results_raw.attrs['Lx']
N = results_raw.attrs['n_agents']
Ts = Lx/v0

times = np.zeros([len(trust_inf), len(trust_uninf)])
times_std = times.copy()
nagents = times.copy()
nagents_std = times.copy()
fails = times.copy()

for i_tu in range(len(trust_uninf)):
    tu = trust_uninf[i_tu]
    for i_ti in range(len(trust_inf)):
        ti = trust_inf[i_ti]

        arrival_times = results_raw.loc[(tu, ti)]['times']
        arrival_agents = results_raw.loc[(tu, ti)]['n_agents']
        fail_counter = results_raw.loc[(tu, ti)]['fails']

        times[i_ti][i_tu] = np.mean(arrival_times)
        times[i_ti][i_tu] = arrival_times[0]
        times_std[i_ti][i_tu] = np.std(arrival_times)
        nagents[i_ti][i_tu] = np.mean(arrival_agents)
        nagents_std[i_ti][i_tu] = np.std(arrival_agents)
        fails[i_ti][i_tu] = fail_counter

x_lab, y_lab = results_raw.index.names[0], results_raw.index.names[1]
x_ticks, y_ticks = trust_uninf, trust_inf

plt.figure()
# plt.imshow(times/Ts, origin='lower')
plt.imshow(Ts/times, origin='lower', cmap='inferno')
plt.colorbar(label='$T_s/T$')
plt.title(f'Inverse time to reach source'); plt.xlabel(x_lab); plt.ylabel(y_lab);
plt.xticks(range(len(x_ticks)), labels=x_ticks); plt.yticks(range(len(y_ticks)), labels=y_ticks)

plt.figure()
plt.imshow(fails/(fails+n_samples), origin='lower')
plt.colorbar(label='Fraction of failed epi')
plt.title(f'Fraction of failed episodes'); plt.xlabel(x_lab); plt.ylabel(y_lab)
plt.xticks(range(len(x_ticks)), labels=x_ticks); plt.yticks(range(len(y_ticks)), labels=y_ticks)

# plt.figure()
# plt.imshow(nagents/N, origin='lower')
# plt.colorbar(label='Frac of agents $< R_b$')
# plt.title(fr'{mode}'); plt.xlabel(x_lab); plt.ylabel(y_lab)
# plt.xticks(range(len(x_ticks)), labels=x_ticks); plt.yticks(range(len(y_ticks)), labels=y_ticks)

# plt.figure()
# plt.imshow(nagents_std/N, origin='lower')
# plt.colorbar(label='std(frac of agents $< R_b$)')
# plt.title(fr'{mode}'); plt.xlabel(x_lab); plt.ylabel(y_lab)
# plt.xticks(range(len(x_ticks)), labels=x_ticks); plt.yticks(range(len(y_ticks)), labels=y_ticks)

plt.ion(); plt.show()
