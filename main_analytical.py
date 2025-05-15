from  olfactory_lib_analytical import *
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
print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}')
print(f'trust = {trust:.2f}')

if final_time == 0:
    coord_folder = f'analytical/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
else:
    coord_folder = f'analytical/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
os.makedirs(coord_folder, exist_ok=True)

# # save logfile
# attributes = ['final_time', 'final_x', 'memory_time', 'dt', 'rd', 'n_agents', 'visual_radius', 'spawn_radius', 'length', 'height', 'speed', 'mu', 'sigma']
# log = {}
# for attr in attributes: log[attr] = globals()[attr]
# np.save(f'{coord_folder}/log', log)

run_n = 0

sim = run_simulation(run_n)
# os.makedirs(f'{coord_folder}/run{run_n}', exist_ok=True)
# np.save(f'{coord_folder}/run{run_n}/com_history', sim.swarm.com_history)

# com_history = np.load(f'{coord_folder}/run{run_n}/com_history.npy')

# plt.figure()
# timesteps = len(sim.swarm.com_history)
timesteps = len(sim.swarm.com_history)
v_x_b = [sim.swarm.com_history[t][0] for t in range(timesteps)]
plt.plot(range(timesteps), np.gradient(v_x_b))
plt.axhline(trust*speed, c='k', ls='--')
# plt.axis('equal')

show_and_check_ipython()

# fig_xi, ax_xi = plt.subplots()
# # fig_alpha, ax_alpha = plt.subplots()

# ax_xi.axhline(speed, c='k', ls='--')
# # ax_alpha.axhline(n_agents*speed, c='k', ls='--')

# # plt.axhline(n_agents*speed, c='k', ls='--')

# # plt.axhline(trust*n_agents*speed +(1-trust)*np.sqrt(n_agents)*speed, ls='-')

# for i in range(3):
#     xi_t = [norm(sim.swarm.xi_history[i][t]) for t in range(final_time)]
#     x_comp_t = [sim.swarm.xi_history[i][t][0] for t in range(final_time)]

#     ax_xi.plot(range(final_time), xi_t)
#     # ax_xi.plot(range(final_time), x_comp_t)

#     # alpha_t = sim.swarm.alpha_history[i]
#     # ax_alpha.plot(range(final_time), alpha_t)

#     # plt.plot(range(final_time), alpha_t, label=trust)

#     # plt.plot(range(final_time), alpha_t, label=trust)

# x_avg_t = []
# x_comp_avg_t = []

# for t in range(final_time):
#     xi_list=[]
#     x_comp_list=[]
#     for i in range(n_agents):
#         xi_t = norm(sim.swarm.xi_history[i][t])
#         xi_list.append(xi_t)

#         x_comp_t = sim.swarm.xi_history[i][t][0]
#         x_comp_list.append(x_comp_t)

#     x_avg_t.append(np.mean(xi_list))
#     x_comp_avg_t.append(np.mean(x_comp_list))
    
# ax_xi.axhline(speed*np.sqrt(1+2*trust**2-2*trust), c='r', ls=':', lw=2)

# ax_xi.plot(range(final_time), x_avg_t, c='k', lw=2)
# # ax_xi.plot(range(final_time), x_comp_avg_t, c='k', lw='2')

# ax_xi.set_title(rf'$\beta = {trust}$, $N={n_agents}$')
# ax_xi.set_xlabel('timestep')

# ax_xi.set_ylabel(r'$\xi_i(\beta,N)$')
# # ax_xi.set_ylabel(r'componente x')

# # ax_alpha.set_title(rf'$\beta = {trust}$, $N={n_agents}$')
# # ax_alpha.set_xlabel('timestep')
# # ax_alpha.set_ylabel(r'$\alpha_i(\beta,N)$')

# ax_xi.set_ylim([0-0.01,speed+0.01])
# show_and_check_ipython()

# # for run_n in range(50):
# #     print(f'Run {run_n}')
# #     # reach_times, success, count, seed, sim = run_simulation(0)
# #     sim = run_simulation(0)
# #     os.makedirs(f'{coord_folder}/run{run_n}', exist_ok=True)
# # #     np.save(f'{coord_folder}/run{run_n}/coord_x', sim.swarm.coord_x)
# # #     np.save(f'{coord_folder}/run{run_n}/coord_y', sim.swarm.coord_y)
# # #     np.save(f'{coord_folder}/run{run_n}/wt_history', sim.swarm.wt_history)

