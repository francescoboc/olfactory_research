from  test_lib import *
from olfactory_plot_utils import *
import multiprocessing as mp

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['test_lib'])
from  test_lib import *

def run_simulation(trust):
    # initialise the rng
    # seed = random.randrange(sys.maxsize)
    seed = 66
    initialise_rng(seed)
    # create objects
    swarm = Swarm(n_agents, spawn_center, spawn_radius, speed, visual_radius, sensing_noise, wind_noise, trust, length, height, source_coordinates, reach_radius, dt, memory_time, decision_time, method)
    sim = Simulation(final_time, swarm, real_time_plot, pause_time, save_frames)
    # run simulation
    arrival_time, count, success = sim.run()
    return arrival_time, count, success, sim 

# plotting parameters 
real_time_plot = False
save_frames = False
pause_time = 0.001

shift = 0.0

n_turns = 50

# delta t
decision_time = 1

# tau
# memory_time = 0.995 *decision_time
memory_time = 1.0 *decision_time

# beta
trust = 0.8

methods = ['no_kernel', 'kernel']

# -------------------------------------------------------------------------------------

rd = 0.2

# number of agents
n_agents = 2 

# visual_radius = 5*rd
visual_radius = 25*rd

# body radius
spawn_radius = 25*rd # Rb

reach_radius = rd

lx = 250*rd

b = 20
length, height = b*lx, b*lx

# noise on the estimate of the mean wind and on public vel
sensing_noise = 0.0 # eta
wind_noise = 0.0 

# v0
# speed = 0.2 
speed = 1

# spawn position and source coordinates 
spawn_center = [length/1.5, height/2 + shift]
source_coordinates = [spawn_center[0]-lx, height/2]
 
plt.figure(0)
plt.clf()
for method in methods:
    if method == 'kernel': dt = 0.01
    elif method == 'no_kernel': dt = decision_time

    n_dec_time = n_turns + 2*np.sum(range(n_turns+1))
    final_time = n_dec_time*decision_time

    arrival_time, count, success, sim = run_simulation(trust)

    vel_x = np.array([vel[0] for vel in sim.swarm.vel_t])
    vel_y = np.array([vel[1] for vel in sim.swarm.vel_t])
    coord_x = np.array([coord[0] for coord in sim.swarm.traj])
    coord_y = np.array([coord[1] for coord in sim.swarm.traj])

    axes = plt.subplot(aspect='equal', adjustable='box')
    # plt = plt.subplot(aspect='equal', adjustable='box', xlim=(coord_x[-1]-1, coord_x[-1]+1), ylim=(coord_y[-1]-1, coord_y[-1]+1))

    # axes.add_patch( plt.Circle(sim.swarm.spawn_center, sim.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2) )
    # axes.add_patch( plt.Circle(source_coordinates, 0.2, color='k') )
    # axes.axhline( source_coordinates[1], lw=1, ls='--', c='k', alpha=.2 )

    if method == 'kernel':
        lab = rf'{method}, $\tau = {memory_time} \Delta t$'
    elif method == 'no_kernel':
        lab = rf'{method}'

    axes.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1, label=lab)

    # folder = f'results/casting/geometric/lx{lx:.3f}_shift{shift:.3f}/memory_time{memory_time:.3f}/dt{dt:.3f}_dec_time{decision_time:.3f}/trust{trust:.3f}'
    # os.makedirs(f'{folder}', exist_ok=True)
    # np.save(f'{folder}/vel_x', vel_x)
    # np.save(f'{folder}/vel_y', vel_y)
    # np.save(f'{folder}/coord_x', coord_x)
    # np.save(f'{folder}/coord_y', coord_y)
    # # save logfile
    # log = {}
    # for attr in attributes: log[attr] = locals()[attr]
    # np.save(f'{folder}/log', log)

# plt.xlim(coord_x[-1]-1, coord_x[-1]+1)
# plt.ylim(coord_y[-1]-1, coord_y[-1]+1)

plt.text(0.5,0.92,rf'$\beta = {trust}, \Delta t = {decision_time}$',ha='center',va='bottom',transform=plt.gca().transAxes)
plt.legend(loc=4)

show_and_check_ipython()


