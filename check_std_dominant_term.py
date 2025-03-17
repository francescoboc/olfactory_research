from utils import *
from select_file import *

trust = 0.9

coord_folder = f'storage/coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'

com_coord_folder = f'com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'

run_n = 0

coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

n_timesteps = len(coord_x[0]) 

y_std_list = []
y_mean_list = []
y_2_mean_list = []
approx_list = []

for t in range(n_timesteps):

    # # this gives exactly the same result as np.std (obviously)
    # y_mean = np.sum([coord_y[agent_id][t] for agent_id in range(n_agents)])/n_agents
    # sum_t = 0
    # for i in range(n_agents):
    #     sum_t += (coord_y[i][t] - y_mean)**2
    # std_y_2 = sum_t/n_agents

    # x_std = np.std([coord_x[agent_id][t] for agent_id in range(n_agents)])
    y_std = np.var([coord_y[agent_id][t] for agent_id in range(n_agents)])

    y_mean = np.sum([coord_y[agent_id][t] for agent_id in range(n_agents)])/n_agents
    y_2_mean = np.sum([coord_y[agent_id][t]**2 for agent_id in range(n_agents)])/n_agents

    approx = np.sqrt( y_2_mean - y_mean**2 )

    y_std_list.append(y_std)
    y_mean_list.append(y_mean)
    y_2_mean_list.append(y_2_mean)
    approx_list.append(approx)

    # print(y_std - approx)

    # x_mean = np.mean([coord_x[agent_id][t] for agent_id in range(n_agents)])
    # y_mean = np.mean([coord_y[agent_id][t] for agent_id in range(n_agents)])

y_std_list = np.array(y_std_list)
y_mean_list = np.array(y_mean_list)
y_mean_2_list = np.array(y_2_mean_list)
approx_list = np.array(approx_list)

plt.plot(y_std_list, 'k', label=r'$\sigma_y^2$')
plt.plot(y_2_mean_list, label=r'$\langle y_i^2 \rangle$')
plt.plot(y_mean_list**2, label=r'$\langle y_i \rangle ^2$')

plt.xlabel('timestep')
plt.title(rf'$\beta={trust}$')

plt.legend()

show_and_check_ipython()
