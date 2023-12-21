from  olfactory_lib import *
import multiprocessing as mp

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from  olfactory_lib import *

show_and_check_ipython()

def run_simulation(trust):
    # path of the turbulent flow
    if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
    else: path = 'flow/re280_small_source'

    # initialise the rng
    seed = random.randrange(sys.maxsize)
    # seed = 666
    initialise_rng(seed)
    # create objects
    cloud = Cloud_turbulent(path, read_h5, source_coordinates, odor_delta_x)
    swarm = Swarm(n_agents, spawn_center, spawn_radius, speed, visual_radius, olfactoy_radius, sensing_noise, wind_noise, trust, length, height, source_coordinates, reach_radius, dt, memory_time, decision_time, threshold, cloud, method, mu, sigma)
    sim = Simulation(final_time, swarm, cloud, real_time_plot, pause_time, save_frames)
    # run simulation
    arrival_time, count, success = sim.run()
    return arrival_time, count, success, sim 

def trust_batch_run(trust):
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
save_frames = True
pause_time = 0.001

# read h5 flow file (on the cluster) or not
read_h5 = False

parallel = False
n_threads = 10
samples = 10

# max simulation time
final_time = int(1e5)
# final_time = int(100)

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 
visual_radius = 5*rd
olfactoy_radius = rd
reach_radius = visual_radius

# initial conditions
shifts = np.linspace(0, 3, 6)*spawn_radius
shift = shifts[0]

sigma = np.pi/20
mus = np.linspace(1, 3/2, 6)*np.pi
mu = mus[0]
 
# beta (only for parallel = False option)
trust = 0.55

# delta t
decision_time = 1

# tau
memory_time = 1.0 *decision_time

# olfactory threshold
threshold = 0.0005

# space bin for the odor field
odor_delta_x = 0.1

# use the memory kernel for the public velocity or not
# method = 'kernel'; dt = 0.01
method = 'no_kernel'; dt = decision_time

# folder = 'results/turbulent/threshold_%f/vary_initial_angle/%s/mu%.3f'%(threshold, method, mu)
folder = 'results/turbulent/threshold_%f/vary_initial_shift/%s/shift%.3f'%(threshold, method, shift)

# number of agents
n_agents = 100 

# distance from the source
lx = 250*rd

# simulation box size
length, height = 2.5*lx, 2.5*lx

# noise on the estimate of the mean wind and on public velocity
sensing_noise = 0.0 # eta
wind_noise = 0.0 

# v0
speed = 0.2 

# spawn position and source coordinates 
spawn_center = [length/1.5, height/2 + shift]
source_coordinates = [spawn_center[0]-lx, height/2]
 
# delete old frames
if save_frames: os.system(f"rm -f frames/frame*.png")

if parallel:
    # beta values to check
    trust_init = 0.0
    trust_final = 1.0
    trust_step = 0.05
    trusts = np.round(np.arange(trust_init, trust_final + trust_step, trust_step),2) 

    # create and run a pool of parallel workers
    pool = mp.Pool(processes = n_threads)
    pool.map(trust_batch_run, trusts)
    # close the pool of workers
    pool.close(); pool.join()
else:
    # single simulation
    arrival_time, count, success, sim = run_simulation(trust)

filename = 'pimlb_presentation_no_shift'
# os.system(f"ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 -i 'frames/frame%d.png' -c:v libx264 videos/{filename}.mp4")
# os.system(f"ffmpeg -hide_banner -loglevel error -i 'frames/frame%d.png' -vf palettegen frames/palette.png")
os.system(f"ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 -i 'frames/frame%d.png' -i frames/palette.png -lavfi paletteuse videos/{filename}.gif")
