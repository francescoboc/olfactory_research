from utils import *

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 
visual_radius = 5*rd
# visual_radius = 2*spawn_radius
olfactoy_radius = rd
reach_radius = 1.0

# initial angle
# sigma = np.pi/3
sigma = 0
mus = np.linspace(1, 3/2, 6)*np.pi
mu = mus[0]
 
# initial conditions
shifts = np.linspace(0, 5, 6)*spawn_radius
shift = shifts[2]

# distance from the source
lx_max = 65
lxs = np.linspace(0, 1, 6)[1:]*lx_max
lx = lxs[4]

no_odor = 1

# olfactory threshold
if no_odor:
    threshold = np.inf
else:
    threshold = 0.0005

# number of agents
n_agents = 100

# v0
speed = 0.2

# noise on the estimate of the mean wind and on public velocity
sensing_noise = 0.0 # eta
wind_noise = 0.0 

straight_distance = ((lx-spawn_radius)**2 + shift**2)**0.5
straight_time = straight_distance/speed

trusts = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# trusts = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

mean_times, std_times, frac_fails = [], [], []
for trust in trusts:
    # define folder and filename
    root_folder = 'results_cs'
    folder = f'mu{mu:.3f}_sigma{sigma:.3f}/lx{lx:.3f}/shift{shift:.3f}'
    folder1 = f'vr{visual_radius}_thr{threshold}_N{n_agents}_v{speed}_snoise{sensing_noise}_wnoise{wind_noise}'
    full_folder = f'{root_folder}/{folder}/{folder1}'

    times = np.loadtxt(f'{full_folder}/{trust:.2f}/times.txt')
    fails = len(np.flatnonzero(times==np.inf))

    frac_fails.append(fails/len(times))

    times_noinf = times[np.argwhere(times!=np.inf)]
    norm_times = times_noinf/straight_time
    mean_times.append(np.mean(norm_times))
    std_times.append(np.std(norm_times))

h_over_l = f'{shift/lx:.2f}'

plt.figure(0)
# shaded_errorbar(trusts, mean_times, std_times, lab=h_over_l)
shaded_errorbar(trusts, mean_times, std_times, lab=shift)
plt.ylabel('normalized fpt')
plt.xlabel('trust')
plt.yscale('log')
# plt.legend(title='H/L')
plt.legend(title='shift')

plt.figure(1)
# plt.plot(trusts, frac_fails, '-s', label=h_over_l)
plt.plot(trusts, frac_fails, '-s', label=shift)
plt.ylabel('fail fraction')
plt.xlabel('trust')
# plt.legend(title='H/L')
plt.legend(title='shift')

show_and_check_ipython()
