from olfactory_plot_utils import *

# body radius
rd = 0.2
spawn_radius = 25*rd # Rb

mus = np.linspace(1, 3/2, 6)*np.pi
mu = mus[0]

# IC
shifts = np.linspace(0, 3, 6)*spawn_radius
shift = shifts[5]

threshold = 0.0005

# visual_radius = 0.2
# visual_radius = 1.0
visual_radius = 2.0
# visual_radius = 5.0

# visual_radii = np.array([1, 2, 5, 10, 25])*rd
# visual_radii = np.array([25])*rd

dt = 1.0
# dt = 0.1
# dt = 0.01
# dt = 0.001

# dt = 0.5
# dt = 0.25

n_agents = 100
# n_agents = 10
# n_agents = 2

# memory_time = 2
memory_time = 1
# memory_time = 0.5
# memory_time = 0.1

# decision_time = 0.5
decision_time = 1

# method = 'kernel'; dt = 0.01
method = 'no_kernel'; dt = decision_time

# trusts = np.round(np.arange(0.0, 1.01, 0.01),2) 
trusts_inf = np.round(np.arange(0.0, 1.01, 0.01),2) 

# for shift in shifts:
# for mu in mus:
# for visual_radius in visual_radii:
# for trust_inf in trusts_inf:
optimal_betas = []

# folder = 'results/casting/vary_initial_angle/pbc/%s/mu%.3f/'%(method,mu)
# folder = 'results/casting/vary_initial_shift/%s/shift%.3f/'%(method,shift)

# folder = 'results/turbulent/threshold_%f/vary_initial_angle/%s/mu%.3f/'%(threshold,method,mu)
# folder = 'results/turbulent/threshold_%f/vary_initial_shift/%s/shift%.3f'%(threshold,method,shift)
# folder = 'results/turbulent/threshold_%f/vary_initial_shift/%s/vr%.3f/shift%.3f'%(threshold, method, visual_radius, shift)
# folder = 'results/turbulent/threshold_%f/vary_initial_shift/%s/lx%.3f/shift%.3f'%(threshold, method, 50, shift)
# folder = 'results/turbulent/threshold_%f/vary_visual_radius/%s/vr%.3f_shift%.3f'%(threshold, method, visual_radius, shift)
folder = 'results/turbulent/threshold_%f/vary_visual_radius/%s/vr%.3f_shift%.3f/trust_uninf0.700/'%(threshold, method, visual_radius, shift)

times_avg, counts_avg, successes_avg = [], [], []
times_std, counts_std, successes_std = [], [], []

trusts_plot = []
# for trust in trusts:
for trust_inf in trusts_inf:
    try:
        # times = np.load('%s/n%i_times_trust%.3f.npy'%(folder,n_agents,trust))
        # counts = np.load('%s/n%i_counts_trust%.3f.npy'%(folder,n_agents,trust))
        # successes = np.load('%s/n%i_successes_trust%.3f.npy'%(folder,n_agents,trust))
        counts = np.load('%s/n%i_counts_trust_inf%.3f.npy'%(folder,n_agents,trust_inf))
        successes = np.load('%s/n%i_successes_trust_inf%.3f.npy'%(folder,n_agents,trust_inf))
        times = np.load('%s/n%i_times_trust_inf%.3f.npy'%(folder,n_agents,trust_inf))
        trusts_plot.append(trust_inf)
    except: continue

    # keep only the successful episodes
    times = times[successes]
    print(times)

    times_avg.append(np.mean(times))
    times_std.append(np.std(times))

    successes_avg.append(np.sum(successes))
    # successes_std.append(np.std(successes))

    # counts_avg.append(np.mean(counts))
    # counts_std.append(np.std(counts))

rd = 0.2
lx = 250*rd
speed = 0.2 # v0
Ts = lx/speed # straight-line time

# optimal_betas.append(trusts_plot[np.argmin(times_avg)])

samples = 100

mu -= np.pi
mu *= 180/np.pi 

plt.figure(2)
# plt.errorbar(trusts_plot, np.array(times_avg)/Ts, yerr=np.array(times_std)/Ts, marker='.', label=rf'$\tau={memory_time}$, dt={dt}')
# shaded_errorbar(trusts_plot, np.array(times_avg)/Ts, np.array(times_std)/Ts, lab=rf'$\tau={memory_time}$', m='.', alpha=.2)
shaded_errorbar(trusts_plot, np.array(times_avg)/Ts, np.array(times_std)/Ts, lab=rf'${shift}$', m='.', alpha=.2)
# shaded_errorbar(trusts_plot, np.array(times_avg)/Ts, np.array(times_std)/Ts, lab=rf'${visual_radius}$', m='.', alpha=.2)
# shaded_errorbar(trusts_plot, np.array(times_avg)/Ts, np.array(times_std)/Ts, lab=rf'${mu:.2f}$', m='.', alpha=.2)
# plt.scatter(trusts_plot[np.argmin(times_avg)], np.min(times_avg)/Ts, marker='v', c='k', zorder=10)
plt.xlabel(r'Trust parameter $\beta$')
plt.ylabel(r'$T/T_s$')
plt.legend(title='Shift')
# plt.legend(title='Visual radius')
# plt.legend(title='Average angle')
# plt.title(rf'Visual radius = {visual_radius}')

plt.xlim(0,1)

# print( trusts_plot[np.argmin(times_avg)])
# plt.figure(1)
# # plt.errorbar(trusts_plot, np.array(counts_avg), yerr=np.array(counts_avg), marker='.', label=f'tau={memory_time}, dt={dt}')
# plt.plot(trusts_plot, np.array(counts_avg), marker='.', label=f'tau={memory_time}, dt={dt}')
# plt.scatter(trusts_plot[np.argmax(counts_avg)], np.max(counts_avg), marker='^', c='k', zorder=10)

plt.figure(3)
# plt.errorbar(trusts_plot, np.array(successes_std)/100, yerr=np.array(successes_std)/100, marker='.', label=rf'$\tau={memory_time}$, dt={dt}')
plt.plot(trusts_plot, np.array(successes_avg)/samples, marker='.', label=rf'${shift}$')
# plt.plot(trusts_plot, np.array(successes_avg)/samples, marker='.', label=rf'${visual_radius}$')
# plt.plot(trusts_plot, np.array(successes_avg)/samples, marker='.', label=rf'${mu:.2f}$')
plt.xlabel(r'Trust parameter $\beta$')
plt.ylabel('Success ratio')
plt.legend(title='Shift')
# plt.legend(title='Visual radius')
# plt.legend(title='Average angle')
# plt.title(rf'Visual radius = {visual_radius}')

show_and_check_ipython()

# plt.figure()

# betastar = [0.86, 0.89,0.94, 0.98]
# taus = [ 2, 1, 0.5, 0.1]
# plt.plot(taus, betastar, marker='o')
# plt.xlabel(r'$\tau$')
# plt.ylabel(r'Optimal $\beta$')

# logfile = np.load(f'{folder}/log.npy', allow_pickle=True)
# print(logfile)
