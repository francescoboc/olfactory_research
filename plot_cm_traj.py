from  mod_olfactory_lib import *
import multiprocessing as mp
from input_file import *
import platform

# in case we need to reload the libraries
import sys
from importlib import reload
reload(sys.modules['mod_olfactory_lib'])
reload(sys.modules['input_file'])
from mod_olfactory_lib import *
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
            reach_radius, rand_casting_steps, rand_casting_direction, dt, memory_time, decision_time, 
            threshold, cloud, method, mu, sigma)
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
    assert real_time_plot == False, 'real time plot only available with 1 thread!'
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

# coord_folder = f'coordinates/detection_cone/vr{visual_radius}/trust{trust}'
# os.makedirs(f'{coord_folder}/run{run_n}', exist_ok=True)
# np.save(f'{coord_folder}/run{run_n}/coord_x', sim.swarm.coord_x)
# np.save(f'{coord_folder}/run{run_n}/coord_y', sim.swarm.coord_y)

# eta = np.array(sim.swarm.norm_sum_vels_avg) -2
# diff = np.array(sim.swarm.max_diff) 
# x_val = range(1,len(diff))
# plt.plot(x_val, diff[1:], label=r'max$||v_i - v_j||$') 
# plt.plot(x_val, 3*(1-trust)*speed*(1+eta[1:])/(eta[1:]), label=r'$3(1-\beta)v_0\frac{1+\eta(t)}{\eta(t)}$') 
# plt.title(fr'$\beta=${trust}, $r_v=${visual_radius}')
# plt.xlabel('time step')
# plt.legend()

# center of mass coordinates
x_com = [coord[0] for coord in sim.swarm.com_history]
y_com = [coord[1] for coord in sim.swarm.com_history]

# calculate velocity of center of mass
dt = 1
x_t = [(x_com[i+1]-x_com[i])/dt for i in range(len(x_com)-1)]
y_t = [(y_com[i+1]-y_com[i])/dt for i in range(len(y_com)-1)]

theta_com = []
normvs = []
for i in range(len(x_t)):
    normv = norm([x_t[i], y_t[i]])
    normvs.append(normv)
    # th = np.arccos(x_t[i]/normv)
    th = np.arcsin(y_t[i]/normv)
    # th = np.arctan2(y_t[i], x_t[i])
    theta_com.append(th)

save_path = 'cm_quantities'

# try: 
#     normv_mean_beta = np.load(f'{save_path}/normv_mean_beta.npy', allow_pickle=True).item()
#     normv_std_beta = np.load(f'{save_path}/normv_std_beta.npy', allow_pickle=True).item()
# except: 
#     normv_mean_beta = {}
#     normv_std_beta = {}

# normv_mean_beta[trust] = np.mean(normvs)
# normv_std_beta[trust] = np.std(normvs)

# np.save(f'{save_path}/normv_mean_beta', normv_mean_beta) 
# np.save(f'{save_path}/normv_std_beta', normv_std_beta) 

wt = sim.swarm.wt_history.copy()
x_wt = [vel[0] for vel in wt]
y_wt = [vel[1] for vel in wt]

theta_wt = []
for i in range(len(x_wt)):
    normw = norm([x_wt[i], y_wt[i]])
    # th = np.arccos(x_wt[i]/normw)
    th = np.arcsin(y_wt[i]/normw)
    # th = np.arctan2(y_wt[i], x_wt[i])
    theta_wt.append(th)

norm_wt = np.array([norm(w) for w in wt])

theta = theta_com[0]
theta_theo = [theta]
for t in range(len(x_t)-1):
    theta_dot = ((1-trust)/dt) * norm_wt[t]/speed * np.sin(theta_wt[t] - theta_theo[t])
    theta += theta_dot*dt

    theta_theo.append(theta)

# plt.figure(0)
# plt.plot(theta_com, label='simulation')
# plt.plot(theta_theo, label='theoretical')
# plt.title('angle')
# plt.xlabel('time step')
# plt.ylabel(r'$\theta_{CM}$')
# plt.legend()

# calculate traj of center of mass from predicted angle
normv_mean_beta = np.load(f'{save_path}/normv_mean_beta.npy', allow_pickle=True).item()
normv_std_beta = np.load(f'{save_path}/normv_std_beta.npy', allow_pickle=True).item()
normv_mean = normv_mean_beta[trust]

# normv = speed

x_com_theo, y_com_theo = [x_com[0]], [y_com[0]]
new_x, new_y = x_com[0].copy(), y_com[0].copy()
for t in range(len(x_t)):
    angle = theta_theo[t]
    new_x -= normv_mean*np.cos(angle)
    new_y += normv_mean*np.sin(angle)
    x_com_theo.append(new_x)
    y_com_theo.append(new_y)

# plot traj of center of mass from simulation
plt.figure(1)
plt.plot(x_com, y_com, '-', label='simulation')
plt.plot(x_com_theo, y_com_theo, '-', label='theoretical')
plt.plot(source_coordinates[0], source_coordinates[1], 'ok')
plt.title('trajectory')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()

plt.figure(2)
plt.plot(normvs)
plt.xlabel('t')
plt.ylabel(r'$<v_{cm}>(t)$')

# TODO once we have the coordinates of the center of mass, we can calculate beta star for a fixed initial condition, i.e. shift/distance from source and initial angle

# filename = f'video_centerofmass_trust{trust}'

# if real_time_plot and save_frames:
#     os.system(f"rm -f frames/frame*.png")
#     if save_gif:
#         os.system(f"ffmpeg -hide_banner -loglevel error -i 'frames/frame%d.png' -vf palettegen frames/palette.png")
#         os.system(f"ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 -i 'frames/frame%d.png' -i frames/palette.png -lavfi paletteuse videos/{filename}.gif")
#     else:
#         # os.system(f"ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 -i 'frames/frame%d.png' -c:v libx264 videos/{filename}.mp4")

#         # per il maledettissimo powerpoint
#         os.system(f"ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 -i 'frames/frame%d.png' -c:v mpeg2video -pix_fmt yuv420p -me_method epzs -threads 4 -r 30.000030 -g 45 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -b 2500k -bt 300k -async 1 -y videos/{filename}.mkv")
