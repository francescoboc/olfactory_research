from  olfactory_lib import *
import multiprocessing as mp
from input_file import *
import platform

# in case we need to reload the libraries
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
reload(sys.modules['input_file'])
from  olfactory_lib import *
from input_file import *

show_and_check_ipython()

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
    swarm = Swarm(private_behavior, n_agents, spawn_center, spawn_radius, speed, visual_radius, 
            olfactoy_radius, sensing_noise, wind_noise, trust, length, height, source_coordinates, 
            reach_radius, dt, memory_time, decision_time, threshold, cloud, method, mu, sigma)
    sim = Simulation(final_time, swarm, cloud, real_time_plot, pause_time, save_frames, first_passage)
    # run simulation
    reach_times, success, count = sim.run()
    print(f'sim {n+1}/{n_samples} done!')
    return reach_times, success, count, seed, sim

# read h5 flow file (on the cluster) or not
if platform.node() == 'swift': read_h5 = False
elif platform.node() == 'e4-seminara.csita.unige.local': read_h5 = True

if not dry_run:
    os.makedirs(f'{full_folder}/{trust:.2f}', exist_ok=True)

# print info to the terminal
if dry_run: print(f'{tc.red}-----DRY RUN-----{tc.end}')
print(folder)
print(folder1)
print(f'Trust = {trust:.2f}')

if n_threads > 1:
    assert real_time_plot == False, 'Real time plot only available with 1 thread!'
    pool = mp.Pool(processes = n_threads)
    times_list, count_list, seed_list = [], [], []
    for res in pool.map(run_simulation, range(n_samples)):
        reach_times, success, count = res[0], res[1], res[2]

        # NB if first_passage is True, reach_times is just a scalar
        # reach_times, success, count, seed, sim = run_simulation(0)

        times_list.append(reach_times)
        # count_list.append(count)

        if not dry_run:
            np.savetxt(f'{full_folder}/{trust:.2f}/times.txt', times_list, fmt=('%.2f'))

else:
    reach_times, success, count, seed, sim = run_simulation(0)

# attributes to save in logfile
attributes = ['n_samples', 'final_time', 'memory_time', 'dt', 'rd', 'n_agents', 'visual_radius', 'spawn_radius', 'reach_radius', 'lx', 'length', 'height', 'speed', 'spawn_center', 'source_coordinates', 'shift', 'mu', 'sigma']
# save logfile
log = {}
for attr in attributes: log[attr] = globals()[attr]
if not dry_run:
    np.save(f'{full_folder}/log', log)

# run_n = sys.argv[1]
# print(run_n)

coord_folder = f'coordinates/detection_cone/vr{visual_radius}/trust{trust}'
os.makedirs(f'{coord_folder}/run{run_n}', exist_ok=True)
np.save(f'{coord_folder}/run{run_n}/coord_x', sim.swarm.coord_x)
np.save(f'{coord_folder}/run{run_n}/coord_y', sim.swarm.coord_y)
