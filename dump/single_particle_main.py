from  single_particle_lib import *
from single_particle_input import *
import multiprocessing as mp
import platform

# in case we need to reload the libraries
import sys
from importlib import reload
reload(sys.modules['single_particle_lib'])
reload(sys.modules['single_particle_input'])
from  single_particle_lib import *
from single_particle_input import *

show_and_check_ipython()

def run_simulation(n):
    print(f'\nTrust = {trust:.2f}')
    # path of the turbulent flow
    if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
    else: path = 'flow/re280_small_source'
    # initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)
    # create objects
    cloud = Cloud_turbulent(path, read_h5, source_coordinates, odor_delta_x)
    swarm = Swarm(n_agents, spawn_center, spawn_radius, speed, visual_radius, olfactoy_radius, sensing_noise, wind_noise, adaptive_trust, trust, trust_informed, trust_uninformed, length, height, source_coordinates, reach_radius, dt, memory_time, decision_time, threshold, cloud, method, mu, sigma)
    sim = Simulation(final_time, swarm, cloud, constrained, real_time_plot, pause_time, save_frames)
    # run simulation
    arrival_time, count, success = sim.run()
    return arrival_time, count, success, seed 

# read h5 flow file (on the cluster) or not
if platform.node() == 'swift': read_h5 = False
elif platform.node() == 'e4-seminara.csita.unige.local': read_h5 = True

# check if we are using too many CPUs
if parallel and os.cpu_count() < n_threads:
    raise Warning(f'Too many threads!')

# check if file already exists
if parallel and os.path.isfile(f'results/{folder}/{filename}.pkl'):
    raise Warning(f'File results/{folder}/{filename}.pkl already exists!')

os.makedirs(folder, exist_ok=True)

# print info to the terminal
print(f'Filename = {filename}')
print(f'Visual radius = {visual_radius}, Threshold = {threshold}, N agents = {n_agents}')
print(f'Constrained = {constrained}, Adaptive trust = {adaptive_trust}')

if save_frames: os.system(f"rm -f frames/frame*.png")

if parallel:
    trusts = np.round(np.arange(trust_init, trust_final + trust_step, trust_step),2) 

    # create empty dataframe to store results
    results = pd.DataFrame(index=trusts, columns=['times', 'n_agents', 'fails', 'seeds'])

    # attributes to save in results metadata
    attributes = ['constrained', 'adaptive_trust', 'n_samples', 'final_time', 'memory_time', 'dt', 'rd', 'n_agents', 'visual_radius', 'spawn_radius', 'reach_radius', 'lx', 'length', 'height', 'speed', 'spawn_center', 'source_coordinates', 'shift', 'mu', 'sigma']
    # add metadata to dataframe
    for attr in attributes: results.attrs[attr] = globals()[attr]

    for trust in trusts:
        # initialise counters and lists
        arrival_times, arrival_agents, seeds = [], [], []
        fail_counter, success_counter = 0, 0
        fails_in_a_row = 0

        # create and run a pool of parallel workers
        pool = mp.Pool(processes = n_threads)
        for arrival_time, agents_in_Rb, success, seed in pool.imap_unordered(run_simulation, range(limit)):
            # save seed of the rng
            seeds.append(seed)

            # if the run was successfull, save results into the dataframe
            if success:
                arrival_times.append(arrival_time)
                arrival_agents.append(agents_in_Rb)
                success_counter += 1
                fails_in_a_row = 0
            # otherwise, increase fail cunter
            else:
                fail_counter += 1
                fails_in_a_row += 1

            # if we reached the desired number of samples, stop
            if success_counter == n_samples:
                break

            # if if we fail 10 times in a row, we stop
            if fails_in_a_row == 10:
                print('10 fails in a row')
                break

        # terminate the pool of workers
        pool.terminate(); pool.join() 

        # save results in dataframe
        results.loc[trust]['times'] = arrival_times
        results.loc[trust]['n_agents'] = arrival_agents
        results.loc[trust]['fails'] = fail_counter
        results.loc[trust]['seeds'] = seeds

    # save to disk
    results.to_pickle(f'{folder}/{filename}.pkl')

else:
    # run single simulation
    arrival_time, count, success, seed = run_simulation(0)

if real_time_plot and save_frames:
    if save_gif:
        os.system(f"ffmpeg -hide_banner -loglevel error -i 'frames/frame%d.png' -vf palettegen frames/palette.png")
        os.system(f"ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 -i 'frames/frame%d.png' -i frames/palette.png -lavfi paletteuse videos/{filename}.gif")
    else:
        os.system(f"ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 -i 'frames/frame%d.png' -c:v libx264 videos/{filename}.mp4")
