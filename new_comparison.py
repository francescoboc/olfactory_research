from  olfactory_lib_firstpassage import *
from utils import *
from select_file import *
from tqdm import tqdm
import os

trust = 0.9

if final_time == 0:
    com_coord_folder = f'com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
else:
    com_coord_folder = f'com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

com_y_std_list, com_y_list = [], []

# for run_n in range(n_runs):
run_n = 0

com_x_std = np.load(f'{com_coord_folder}/run{run_n}/com_x_std.npy', allow_pickle=True)
com_y_std = np.load(f'{com_coord_folder}/run{run_n}/com_y_std.npy', allow_pickle=True)

com_x = np.load(f'{com_coord_folder}/run{run_n}/com_x.npy', allow_pickle=True)
com_y = np.load(f'{com_coord_folder}/run{run_n}/com_y.npy', allow_pickle=True)
wt = np.load(f'{com_coord_folder}/run{run_n}/wt_history.npy', allow_pickle=True)

# theoretical
com_y_std_theo = np.load(f'{com_coord_folder}/com_y_std_teho.npy', allow_pickle=True)


timesteps = len(com_x_std) +100

# com_y_std_list.append(com_y_std**2) 
# com_y_list.append(com_y**2)

plt.plot(com_y_std**2, 
        label=r'$\sigma_y^2 $ ')

# plt.plot(np.mean(truncate_and_stack(com_y_std_list), axis=0) + np.mean(truncate_and_stack(com_y_list), axis=0), 
#         label=r'$\sigma_y^2 + \langle y_i(t) \rangle^2 $ (avg on 50 sim)')



 # ----------- calculate a reference casting trajectory -----------
private_behavior = 'cast_and_surge'
rd = 0.2
olfactoy_radius = rd
rand_casting_steps = 0
rand_casting_direction = False
sensing_noise = 0.0 # eta
length, height = 500, 500
source_coordinates = [75, 0]
reach_radius = visual_radius
threshold = np.inf
method = 'no_kernel' 
decision_time = 1
dt = decision_time
memory_time = 1.0 *decision_time
wind_noise = 0.0 
cloud = None
seed = random.randrange(sys.maxsize)
initialise_rng(seed)
swarm = Swarm(private_behavior, n_agents, spawn_radius, speed, visual_radius, 
        olfactoy_radius, sensing_noise, wind_noise, trust, length, height, 
        source_coordinates, reach_radius, 
        rand_casting_steps, rand_casting_direction, dt, memory_time, decision_time, 
        threshold, cloud, method, mu, sigma)

agent = swarm.agents[0]
x_cs, y_cs = 0, 0
x_cs_hist, y_cs_hist = [x_cs], [y_cs]
for t in range(timesteps):
    agent.cast(t)

    v_x = agent.private_velocity[0]
    x_cs += v_x*dt
    v_y = agent.private_velocity[1]
    y_cs += v_y*dt

    x_cs_hist.append(x_cs)
    y_cs_hist.append(y_cs)
 # ----------- ----------- ----------- ----------- -----------


# x_an, y_an = [0], [0]
# for T in range(1,timesteps-101):
#     x_an.append(trust*speed*T)
#     y_an.append(y_an[T-1] + dt*(1-trust)*wt[T][1])

# plt.plot( com_x, com_y, label=r'simulation')
# plt.plot( x_an, y_an, label=r'theory')
# plt.ylabel('y')
# plt.xlabel('x')

# # plt.plot( com_x, label=r'simulation')
# # plt.plot( x_an, label=r'theory')
# # plt.xlabel('t')
# # plt.ylabel('x')



y_cs_2 = []
for T in range(timesteps - 100):

    int_s = 0
    for s in range(T,T+100):
        int_s += y_cs_hist[s]**2

    int_tau = 0
    for tau in range(100): 
        int_tau += y_cs_hist[T+tau]*y_cs_hist[tau]

    y_cs_2.append(int_s/100 - int_tau/50)

y_cs_2 = np.array(y_cs_2)

# # take square root of variance to get standard deviation
# y_cs_2 = np.sqrt(np.abs(y_cs_2))

# add std at time 0 (uniformly random distributed points in a circle)
# y_cs_2 += spawn_radius/2
y_cs_2 += (spawn_radius/2)**2

# plt.plot(y_cs_2 - com_y**2, 
#         c='k', label=r'$\langle y_{CS}^2 \rangle - \langle y_i(t) \rangle^2 $')

# plt.plot( com_y**2, 
#         label=r'$ \langle y_i(t) \rangle^2 $')

plt.legend()
# plt.xlabel('timestep')
# plt.ylabel(r'$\sigma_y^2$')
plt.title(rf'$\beta={trust}$')

show_and_check_ipython()
