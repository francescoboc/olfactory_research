from  test_lib import *
from olfactory_plot_utils import *
import multiprocessing as mp

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['test_lib'])
from  test_lib import *

show_and_check_ipython()

def run_simulation(trust):
    path = 'flow/re280_small_source'
    read_h5 = False
    # initialise the rng
    seed = random.randrange(sys.maxsize)
    # seed = 66
    initialise_rng(seed)
    # create objects
    swarm = Swarm(n_agents, spawn_center, spawn_radius, speed, visual_radius, sensing_noise, wind_noise, trust, length, height, source_coordinates, reach_radius, dt, memory_time, decision_time, threshold, method, mu, sigma)
    sim = Simulation(final_time, swarm, real_time_plot, pause_time, save_frames)
    # run simulation
    arrival_time, count, success = sim.run()
    return arrival_time, count, success, sim 

def trust_batch_run(trust):
    # folder name
    # folder = 'results/casting/vary_initial_angle/shift%.3f/tau%.3f/dt%.3f'%(shift,memory_time,dt)
    # folder = 'results/casting/vary_initial_angle/%s/mu%.3f'%(method,mu)
    folder = 'results/casting/vary_initial_shift/%s/shift%.3f'%(method,shift)

    # check if file already exists
    file_exists = True
    try: np.load('%s/n%i_times_trust%.3f.npy'%(folder,n_agents,trust))
    except: file_exists = False

    # run batch of simulations
    if not file_exists:
        os.makedirs(f'{folder}', exist_ok=True)
        # create empty lists for results
        times = []
        counts = []
        successes = []
        for sample in np.arange(samples):
            arrival_time, count, success, sim = run_simulation(trust)
            times.append(arrival_time)
            counts.append(count)
            successes.append(success)
        np.save('%s/n%i_times_trust%.3f.npy'%(folder,n_agents,trust), times)
        np.save('%s/n%i_counts_trust%.3f.npy'%(folder,n_agents,trust), counts)
        np.save('%s/n%i_successes_trust%.3f.npy'%(folder,n_agents,trust), successes)
        print('END! trust =', trust)

        # attributes to save in logfile
        attributes = ['final_time', 'memory_time', 'dt', 'rd', 'n_agents', 'visual_radius', 'spawn_radius', 
                'reach_radius', 'lx', 'length', 'height', 'speed', 'spawn_center', 'source_coordinates', 
                'mu', 'sigma']
        # save logfile
        log = {}
        for attr in attributes: log[attr] = globals()[attr]
        np.save(f'{folder}/log', log)

    else:
        print('%s/n%i_times_trust%.3f.npy already exists!'%(folder,n_agents,trust))

# plotting parameters 
real_time_plot = True
save_frames = False
pause_time = 0.001
# pause_time = 1/2

final_time = 100

# body radius
rd = 0.2
spawn_radius = 25*rd # Rb

# IC
shifts = np.linspace(0, 3, 6)*spawn_radius
shift = shifts[0]

mus = np.linspace(1, 3/2, 6)*np.pi
mu = mus[0]

sigma = np.pi/20

parallel = False
n_threads = 10
samples = 20

# delta t
decision_time = 1

# tau
memory_time = 1.0 *decision_time

# smelling threshold
threshold = 0.0005

# # beta
# trust = 1.0

# method = 'kernel'; dt = 0.01

method = 'no_kernel'; dt = decision_time

# beta
if parallel:
    trust_init = 0.0
    trust_final = 1.0
    trust_step = 0.05
    trusts = np.round(np.arange(trust_init, trust_final + trust_step, trust_step),2) 
else:
    # trust = float(sys.argv[1])
    trust = 0.8

# number of agents
n_agents = 100 
# n_agents = 31 
# n_agents = 10
# n_agents = 2 

# visual_radius = 5*rd
visual_radius = 25*rd

reach_radius = rd

lx = 250*rd

length, height = 2.5*lx, 2.5*lx

# noise on the estimate of the mean wind and on public vel
sensing_noise = 0.0 # eta
wind_noise = 0.0 

# v0
speed = 0.2 

# spawn position and source coordinates 
spawn_center = [length/1.5, height/2 + shift]
source_coordinates = [spawn_center[0]-lx, height/2]
 
if parallel:
    # create and run a pool of parallel workers
    pool = mp.Pool(processes = n_threads)
    pool.map(trust_batch_run, trusts)
    # close the pool of workers
    pool.close(); pool.join()
else:
    arrival_time, count, success, sim = run_simulation(trust)

# -------------------------------------------------------------------------------------

# vel_x = np.array([vel[0] for vel in sim.swarm.vel_t])
# vel_y = np.array([vel[1] for vel in sim.swarm.vel_t])
# coord_x = np.array([coord[0] for coord in sim.swarm.traj])
# coord_y = np.array([coord[1] for coord in sim.swarm.traj])

# plt.figure(0)
# plt.clf()
# # create axes for plotting
# # axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, length), ylim=(0, height))
# axes = plt.subplot(aspect='equal', adjustable='box')
# # add patches for source and spawn circle 

# axes.add_patch( plt.Circle(sim.swarm.spawn_center, sim.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2) )
# axes.add_patch( plt.Circle(source_coordinates, 0.2, color='k') )
# axes.axhline( source_coordinates[1], lw=1, ls='--', c='k', alpha=.2 )

# # add agents points and visual circles
# index = 0
# for agent in sim.swarm.agents:
#     color_id = min([len(colors), index%len(colors)]) 
#     agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[color_id], label=index)
#     visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[color_id], alpha=0.1)
#     # visual_circle = plt.Circle(agent.coordinates, reach_radius, fill=False, color=colors[color_id], alpha=0.1)
#     axes.add_patch(agent_point); axes.add_patch(visual_circle)
#     index += 1

# axes.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1)
# # axes.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1, marker='o', mfc='none', ms=3)

