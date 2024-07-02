from  olfactory_lib import *
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

def run_simulation():
    print(f'\nTrust = {trust:.2f}')
    # path of the turbulent flow
    if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
    else: path = '../flow/re280_small_source'
    # initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)
    # create objects
    cloud = Cloud_turbulent(path, read_h5, source_coordinates, odor_delta_x)
    swarm = Swarm(n_agents, spawn_center, spawn_radius, speed, visual_radius, olfactoy_radius, sensing_noise, wind_noise, trust, length, height, source_coordinates, reach_radius, dt, memory_time, decision_time, threshold, cloud, method, mu, sigma)
    sim = Simulation(final_time, swarm, cloud, real_time_plot, pause_time, save_frames)
    # run simulation
    velocities = sim.run()
    return velocities, seed

# read h5 flow file (on the cluster) or not
if platform.node() == 'swift': read_h5 = False
elif platform.node() == 'e4-seminara.csita.unige.local': read_h5 = True

for visual_radius in vis_radii:
    folder = f'results/trust{trust}/vr{visual_radius}'
    filename = f'N{n_agents}_sr{spawn_radius}'

    full_folder = f'{folder}/{filename}'
    os.makedirs(f'{full_folder}', exist_ok=True)

    # attributes to save in results metadata
    attributes = ['final_time', 'memory_time', 'dt', 'rd', 'lx', 'length', 'height', 'speed', 'spawn_center', 'source_coordinates', 'shift', 'mu', 'sigma']

    # print info to the terminal
    print(f'Filename = {filename}')
    print(f'Visual radius = {visual_radius}, Trust = {trust}, N agents = {n_agents}')

    # run single simulation
    velocities, seed = run_simulation()

    # save logfile
    log = {}
    for attr in attributes: log[attr] = globals()[attr]
    np.save(f'{full_folder}/log', log)

    # save data
    np.save(f'{full_folder}/velocities', velocities)
