from  olfactory_lib_coordinates import *
from input_file import *
from utils import *
import platform
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

read_h5 = False

plt.rcParams['font.size'] = 16
plt.rcParams['legend.fontsize'] = 13 
plt.rcParams['figure.constrained_layout.use'] = True

def run_simulation(n):
    # path of the turbulent flow
    if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
    else: path = 'flow/re280_small_source'
    # initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)
    # create objects
    if no_odor: cloud = None
    else: cloud = Cloud_turbulent(path, read_h5, source_coordinates, odor_delta_x)
    swarm = Swarm(private_behavior, n_agents, spawn_radius, speed, visual_radius, 
            olfactoy_radius, sensing_noise, wind_noise, trust, length, height, 
            rand_casting_steps, rand_casting_direction, dt, memory_time, decision_time, 
            threshold, cloud, method, mu, sigma)
    sim = Simulation(final_time, final_x, swarm, cloud, real_time_plot, pause_time, save_frames)

    sim.run()
    return sim


visual_radius = 100*spawn_radius
spawn_radius = 10*rd 
rand_casting_steps = 0
rand_casting_direction = 0

# mu = 0
mu = np.pi/4
# mu = np.pi/2
n_agents = 2

final_time = 1000
final_x = 1000

trusts = [1, 0.95, 0.9, 0.85, 0.8, 0]

# plt.figure(figsize=square_figsize)
fig, ax = plt.subplots(figsize=square_figsize)  # crea figura e asse principali
fig.set_size_inches(4.5, 4.5)

for trust in trusts:
    sim = run_simulation(0)

    ax.plot(sim.swarm.coord_x[1], sim.swarm.coord_y[1], c='grey', alpha=0.5)
    ax.plot(sim.swarm.coord_x[0], sim.swarm.coord_y[0], label=rf'$\beta={trust}$')

    ax.plot(sim.swarm.coord_x[1][-1], sim.swarm.coord_y[1][-1], marker='.', color='grey')
    ax.plot(sim.swarm.coord_x[0][-1], sim.swarm.coord_y[0][-1], marker='.', color='k')

ax.legend(loc='center right')
add_decorations(white_circle=False, color='k')

ax.set_yticks(ax.get_xticks())

ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')

ax.set_xlim(-10, 170)
ax.set_ylim(-10, 170)


axins = inset_axes(ax,
                   width="45%",  # width relative to parent
                   height="45%",  # height relative to parent
                   loc='upper left',  # ignored if bbox_to_anchor used
                   bbox_to_anchor=(0.001, -0.001, 1.0, 1.0),  # (x0, y0, width, height)
                   bbox_transform=ax.transAxes,)
                   # borderpad=2.0)

for trust in trusts:
    sim = run_simulation(0)
    axins.plot(sim.swarm.coord_x[1], sim.swarm.coord_y[1], c='grey', alpha=0.5)
    axins.plot(sim.swarm.coord_x[0], sim.swarm.coord_y[0], label=rf'$\beta={trust}$')

    axins.plot(sim.swarm.coord_x[1][-1], sim.swarm.coord_y[1][-1], marker='.', color='grey')
    axins.plot(sim.swarm.coord_x[0][-1], sim.swarm.coord_y[0][-1], marker='.', color='k')

add_decorations(white_circle=False, color='k', arrow_length=2.5, hl=1.5, hw=1.5, w=0.3)

axins.set_xlim(-3, 10)
axins.set_ylim(-6.5, 6.5)
axins.set_xticks([])
axins.set_yticks([])

mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5", alpha=0.5)

show_and_check_ipython()
