from  olfactory_lib_firstpassage import *
from input_file import *
import platform

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
            source_coordinates, reach_radius, 
            rand_casting_steps, rand_casting_direction, dt, memory_time, decision_time, 
            threshold, cloud, method, mu, sigma)
    sim = Simulation(final_time, swarm, cloud, real_time_plot, pause_time, save_frames)

    # run simulation
    time, success = sim.run()
    # print(f'sim {n+1}/{n_samples} done!')
    return time, success, seed, sim

    # sim.run()
    # return sim

# read h5 flow file (on the cluster) or not
if platform.node() == 'swift': read_h5 = False
elif platform.node() == 'e4-seminara.csita.unige.local': read_h5 = True

# print info to the terminal
# print(folder)
# print(folder1)
print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}')
print(f'trust = {trust:.2f}')
print(f'source coord = {source_coordinates[0]}, {source_coordinates[1]}')

# if final_time == 0:
#     coord_folder = f'../storage/coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
# else:
#     coord_folder = f'../storage/coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

# os.makedirs(coord_folder, exist_ok=True)

# coord_folder = f'../storage/first_passages/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/source_coord{source_coordinates[0]}_{source_coordinates[1]}/trust{trust}'
if no_odor:
    fpt_folder = f'first_passages/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/source_coord{source_coordinates[0]}_{source_coordinates[1]}/trust{trust}'
else:
    fpt_folder = f'first_passages_odor/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/source_coord{source_coordinates[0]}_{source_coordinates[1]}/trust{trust}'

os.makedirs(fpt_folder, exist_ok=True)

# save logfile
attributes = ['final_time', 'memory_time', 'dt', 'rd', 'n_agents', 'visual_radius', 'spawn_radius', 'length', 'height', 'speed', 'mu', 'sigma', 'source_coordinates']
log = {}
for attr in attributes: log[attr] = globals()[attr]
np.save(f'{fpt_folder}/log', log)

reach_times = []
for run_n in range(n_runs):
    print(f'Run {run_n}')

    time, success, seed, sim = run_simulation(0)
    reach_times.append(time)

    # sim = run_simulation(0)

    # os.makedirs(f'{fpt_folder}/run{run_n}', exist_ok=True)

    # os.makedirs(f'{coord_folder}/run{run_n}', exist_ok=True)
    # np.save(f'{coord_folder}/run{run_n}/coord_x', sim.swarm.coord_x)
    # np.save(f'{coord_folder}/run{run_n}/coord_y', sim.swarm.coord_y)
    # np.save(f'{coord_folder}/run{run_n}/wt_history', sim.swarm.wt_history)

np.save(f'{fpt_folder}/reach_times', reach_times)
