from  olfactory_lib_coordinates import *
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
    sim = Simulation(final_time, final_x, swarm, cloud, real_time_plot, pause_time, save_frames)

    sim.run()
    return sim

# read h5 flow file (on the cluster) or not
if platform.node() == 'swift': read_h5 = False
elif platform.node() == 'e4-seminara.csita.unige.local': read_h5 = True

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}')
print(f'trust = {trust:.2f}')

# run simulation
sim = run_simulation(0)

# calculate traj of center of mass
coord_x = sim.swarm.coord_x
coord_y = sim.swarm.coord_y

n_timesteps = len(coord_x[0]) 

com_x, com_y = [], []
com_x_std, com_y_std = [], []

for t in range(n_timesteps):
    x_mean = np.mean([coord_x[agent_id][t] for agent_id in range(n_agents)])
    y_mean = np.mean([coord_y[agent_id][t] for agent_id in range(n_agents)])
    com_x.append(x_mean)
    com_y.append(y_mean)

    # x_std = np.std([coord_x[agent_id][t] for agent_id in range(n_agents)])
    # y_std = np.std([coord_y[agent_id][t] for agent_id in range(n_agents)])
    # com_x_std.append(x_std)
    # com_y_std.append(y_std)

# calculate velocity of center of mass
dt = 1
x_t = [(com_x[i+1]-com_x[i])/dt for i in range(len(com_x)-1)]
y_t = [(com_y[i+1]-com_y[i])/dt for i in range(len(com_y)-1)]

theta_com = []
normvs = []
for i in range(len(x_t)):
    normv = norm([x_t[i], y_t[i]])
    # normvs.append(normv)

    # th = np.arccos(x_t[i]/normv)
    th = np.arcsin(y_t[i]/normv)
    # th = np.arctan2(y_t[i], x_t[i])
    theta_com.append(th)

# normv_mean = np.mean(normvs)

# normv_std = np.std(normvs)

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

# plt.figure()
# plt.plot(theta_com, label='simulation')
# plt.plot(theta_theo, label='theoretical')
# plt.title('angle')
# plt.xlabel('time step')
# plt.ylabel(r'$\theta_{CM}$')
# plt.legend()

normv_mean = speed

com_x_theo, com_y_theo = [com_x[0]], [com_y[0]]
new_x, new_y = com_x[0].copy(), com_y[0].copy()
for t in range(len(x_t)):
    angle = theta_theo[t]
    new_x += normv_mean*np.cos(angle)
    new_y += normv_mean*np.sin(angle)
    com_x_theo.append(new_x)
    com_y_theo.append(new_y)

# plot traj of center of mass from simulation
plt.figure()
plt.plot(com_x, com_y, '-', label='simulation')
plt.plot(com_x_theo, com_y_theo, '--', label='theoretical')
plt.title(fr'$\beta = {trust}$')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()

# plt.figure()
# plt.plot(normvs)
# plt.xlabel('t')
# plt.ylabel(r'$<v_{cm}>(t)$')

show_and_check_ipython()
