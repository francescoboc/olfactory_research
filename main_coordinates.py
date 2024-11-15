from  mod_olfactory_lib import *
import multiprocessing as mp
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
            rand_casting_steps, rand_casting_direction, dt, memory_time, decision_time, 
            threshold, cloud, method, mu, sigma)
    sim = Simulation(final_time, final_x, swarm, cloud, real_time_plot, pause_time, save_frames, first_passage)

    # # run simulation
    # reach_times, success, count = sim.run()
    # # print(f'sim {n+1}/{n_samples} done!')
    # return reach_times, success, count, seed, sim

    sim.run()
    return sim

# read h5 flow file (on the cluster) or not
if platform.node() == 'swift': read_h5 = False
elif platform.node() == 'e4-seminara.csita.unige.local': read_h5 = True

# print info to the terminal
# print(folder)
# print(folder1)
print(f'Trust = {trust:.2f}')

if final_time == 0:
    coord_folder = f'coordinates/hexbin/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
else:
    coord_folder = f'coordinates/hexbin/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

os.makedirs(coord_folder, exist_ok=True)

# save logfile
attributes = ['final_time', 'final_x', 'memory_time', 'dt', 'rd', 'n_agents', 'visual_radius', 'spawn_radius', 'reach_radius', 'length', 'height', 'speed', 'mu', 'sigma']
log = {}
for attr in attributes: log[attr] = globals()[attr]
np.save(f'{coord_folder}/log', log)

for run_n in range(50):
    print(f'Run {run_n}')

    # reach_times, success, count, seed, sim = run_simulation(0)
    sim = run_simulation(0)

    # # center of mass coordinates
    # x_com = [coord[0] for coord in sim.swarm.com_history]
    # y_com = [coord[1] for coord in sim.swarm.com_history]

    # # calculate velocity of center of mass
    # dt = 1
    # x_t = [(x_com[i+1]-x_com[i])/dt for i in range(len(x_com)-1)]
    # y_t = [(y_com[i+1]-y_com[i])/dt for i in range(len(y_com)-1)]

    # theta_com = []
    # normvs = []
    # for i in range(len(x_t)):
    #     normv = norm([x_t[i], y_t[i]])
    #     normvs.append(normv)
    #     # th = np.arccos(x_t[i]/normv)
    #     th = np.arcsin(y_t[i]/normv)
    #     # th = np.arctan2(y_t[i], x_t[i])
    #     theta_com.append(th)

    # wt = sim.swarm.wt_history.copy()
    # x_wt = [vel[0] for vel in wt]
    # y_wt = [vel[1] for vel in wt]

    # theta_wt = []
    # for i in range(len(x_wt)):
    #     normw = norm([x_wt[i], y_wt[i]])
    #     # th = np.arccos(x_wt[i]/normw)
    #     th = np.arcsin(y_wt[i]/normw)
    #     # th = np.arctan2(y_wt[i], x_wt[i])
    #     theta_wt.append(th)

    # norm_wt = np.array([norm(w) for w in wt])

    # theta = theta_com[0]
    # theta_theo = [theta]
    # for t in range(len(x_t)-1):
    #     theta_dot = ((1-trust)/dt) * norm_wt[t]/speed * np.sin(theta_wt[t] - theta_theo[t])
    #     theta += theta_dot*dt
    #     theta_theo.append(theta)

    # save_path = 'cm_quantities'

    # # calculate traj of center of mass from predicted angle
    # normv_mean_beta = np.load(f'{save_path}/normv_mean_beta.npy', allow_pickle=True).item()
    # normv_std_beta = np.load(f'{save_path}/normv_std_beta.npy', allow_pickle=True).item()
    # normv_mean = normv_mean_beta[trust]

    # x_com_theo, y_com_theo = [x_com[0]], [y_com[0]]
    # new_x, new_y = x_com[0].copy(), y_com[0].copy()
    # for t in range(len(x_t)):
    #     angle = theta_theo[t]
    #     new_x -= normv_mean*np.cos(angle)
    #     new_y += normv_mean*np.sin(angle)
    #     x_com_theo.append(new_x)
    #     y_com_theo.append(new_y)

    # coord_folder = f'coordinates/avg_cm_traj/vr{visual_radius}/sigma{sigma}_randsteps{rand_casting_steps}/trust{trust}'
    # os.makedirs(f'{coord_folder}/run{run_n}', exist_ok=True)
    # np.save(f'{coord_folder}/run{run_n}/x_com', x_com)
    # np.save(f'{coord_folder}/run{run_n}/y_com', y_com)
    # np.save(f'{coord_folder}/run{run_n}/x_com_theo', x_com_theo)
    # np.save(f'{coord_folder}/run{run_n}/y_com_theo', y_com_theo)

    os.makedirs(f'{coord_folder}/run{run_n}', exist_ok=True)
    np.save(f'{coord_folder}/run{run_n}/coord_x', sim.swarm.coord_x)
    np.save(f'{coord_folder}/run{run_n}/coord_y', sim.swarm.coord_y)
