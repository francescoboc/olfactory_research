from olfactory_plot_utils import *
from scipy.interpolate import CubicSpline

shift = 0
final_time = 500
rd = 0.2
n_agents = 31 
visual_radius = 25*rd
spawn_radius = 25*rd # Rb
reach_radius = rd
lx = 250*rd
speed = 0.2 
# b = 2.5
b = 5
length, height = b*lx, b*lx

memory_time = 1.0
decision_time = 1
dt = 0.01

# spawn position and source coordinates 
spawn_center = [length/1.5, height/2]
source_coordinates = [spawn_center[0]-lx, height/2]

# trust = 0.90
# trust = 0.906
# trust = 0.907
trust = 0.91

folder = f'results/casting/geometric/lx{lx:.3f}_shift{shift:.3f}/memory_time{memory_time:.3f}/dt{dt:.3f}_dec_time{decision_time:.3f}/trust{trust:.3f}'
vel_x = np.load(f'{folder}/vel_x.npy')
vel_y = np.load(f'{folder}/vel_y.npy')
coord_x = np.load(f'{folder}/coord_x.npy')
coord_y = np.load(f'{folder}/coord_y.npy')

tot_time_steps = int(final_time/dt)
time_steps = np.arange(tot_time_steps)

sign_changes = np.where(vel_y[:-1] * vel_y[1:] < 0 )[0] + 1 
max_x = coord_x[sign_changes]
max_y = coord_y[sign_changes]

times_max = time_steps[sign_changes]*dt

dist_from_centerline = []
amplitude = []
times_max_even = []
for i in range(len(max_y)-1):
    if i%2 == 0:
        p1, p2 = np.flip(max_y)[i], np.flip(max_y)[i+1]
        amp = abs((p1 -p2))
        center_amplitude = amp/2
        dist_from_centerline.append( source_coordinates[1] - (center_amplitude + min(p1,p2)) )
        amplitude.append(amp)
        times_max_even.append(np.flip(times_max)[i])

amplitude = np.flip(amplitude)
dist_from_centerline = np.flip(dist_from_centerline)
times_max_even = np.flip(times_max_even)

displacement = spawn_center[0] - coord_x

tstar_idx = (np.abs(displacement[1:] - lx)).argmin()
tstar = time_steps[tstar_idx]*dt

# plt.figure()
plt.clf()

if trust == 0.9 or trust ==0.91: discard = 0
else: discard = 1
y = amplitude[discard:]/2+spawn_radius+reach_radius
x = times_max_even[discard:]
plt.plot(x, y, label=r'$a/2+\mathrm{R_b}$', ls='', marker='o', c='b')

cs = CubicSpline(x, y)
cs_x = np.arange(start=min(x), stop=300, step=0.1)
plt.plot(cs_x, cs(cs_x), ls='--', c='b')

# popt = np.polyfit(x, y, deg=1)
# plt.plot(x, popt[1] + popt[0]*x, ls='--', c='b')

plt.plot(times_max_even, dist_from_centerline, label=r'$d$', ls='', marker='o', c='r')

cs = CubicSpline(times_max_even, dist_from_centerline)
cs_x = np.arange(start=min(times_max_even), stop=300, step=0.1)
plt.plot(cs_x, cs(cs_x), ls='--', c='r')

# from scipy.optimize import curve_fit
# def func(x, a, b):
#     return a * np.log(x) + b
# popt, pcov = curve_fit(func, times_max_even, dist_from_centerline)
# plt.plot(times_max_even, func(times_max_even, *popt))

# plt.xscale('log')
plt.axvline(tstar, c='k', alpha=0.5, label=rf'$t^*={tstar:.1f}$')
plt.title(rf'$\beta = {trust}$')
plt.xlabel('time')
plt.legend()

plt.gca().set_xlim(0,300)

show_and_check_ipython()
