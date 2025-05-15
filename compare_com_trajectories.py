from utils import *
from select_file import *
from tqdm import tqdm

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}')
print(f'trust = {trust:.2f}')

if final_time == 0:
    com_coord_folder = f'com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
else:
    com_coord_folder = f'com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

dt = 1

sim_x_list, sim_y_list = [], []
theo_x_list, theo_y_list = [], []
# for run_n in range(n_runs):
for run_n in tqdm(range(n_runs), ascii=' █'):
    com_x = np.load(f'{com_coord_folder}/run{run_n}/com_x.npy', allow_pickle=True)
    com_y = np.load(f'{com_coord_folder}/run{run_n}/com_y.npy', allow_pickle=True)
    # com_x_std = np.load(f'{com_coord_folder}/run{run_n}/com_x_std.npy', allow_pickle=True)
    # com_y_std = np.load(f'{com_coord_folder}/run{run_n}/com_y_std.npy', allow_pickle=True)
    wt = np.load(f'{com_coord_folder}/run{run_n}/wt_history.npy', allow_pickle=True)

    # calculate velocity of center of mass
    x_t = [(com_x[i+1]-com_x[i])/dt for i in range(len(com_x)-1)]
    y_t = [(com_y[i+1]-com_y[i])/dt for i in range(len(com_y)-1)]

    theta_com = []
    normvs = []
    for i in range(len(x_t)):
        normv = norm([x_t[i], y_t[i]])
        normvs.append(normv)
        # th = np.arccos(x_t[i]/normv)
        th = np.arcsin(y_t[i]/normv)
        # th = np.arctan2(y_t[i], x_t[i])
        theta_com.append(th)

    # normv_mean = np.mean(normvs)
    normv_mean = trust*speed

    # normv_std = np.std(normvs)

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

    # normv_mean = speed

    com_x_theo, com_y_theo = [com_x[0]], [com_y[0]]
    new_x, new_y = com_x[0].copy(), com_y[0].copy()
    for t in range(len(x_t)):
        angle = theta_theo[t]
        new_x += normvs[t]*np.cos(angle)
        new_y += normvs[t]*np.sin(angle)
        # new_x += normv_mean*np.cos(angle)
        # new_y += normv_mean*np.sin(angle)
        com_x_theo.append(new_x)
        com_y_theo.append(new_y)

    sim_x_list.append(com_x)
    sim_y_list.append(com_y)
    theo_x_list.append(com_x_theo)
    theo_y_list.append(com_y_theo) 

    # save theoretical coordinates in run folder
    np.save(f'{com_coord_folder}/run{run_n}/com_x_theo.npy', com_x_theo)
    np.save(f'{com_coord_folder}/run{run_n}/com_y_theo.npy', com_y_theo)

    # # plot traj of center of mass from simulation
    # if run_n==0:
    #     plt.plot(com_x, com_y, 'r-', label='simulation')
    #     plt.plot(com_x_theo, com_y_theo, 'b--', label='theoretical')
    # else:
    #     plt.plot(com_x, com_y, 'r-')
    #     plt.plot(com_x_theo, com_y_theo, 'b--')

# calculate average trajectories and their standard deviations
mean_x_sim = np.mean(truncate_and_stack(sim_x_list),axis=0)
mean_y_sim = np.mean(truncate_and_stack(sim_y_list),axis=0)
std_x_sim = np.std(truncate_and_stack(sim_x_list),axis=0)
std_y_sim = np.std(truncate_and_stack(sim_y_list),axis=0)

shaded_errorbar(mean_x_sim, mean_y_sim, std_y_sim, lab='simulation', c='b', ls='--', m='')

mean_x_theo = np.mean(truncate_and_stack(theo_x_list),axis=0)
mean_y_theo = np.mean(truncate_and_stack(theo_y_list),axis=0)
std_x_theo = np.std(truncate_and_stack(theo_x_list),axis=0)
std_y_theo = np.std(truncate_and_stack(theo_y_list),axis=0)

shaded_errorbar(mean_x_theo, mean_y_theo, std_y_theo, lab='theory', c='k', ls='-', m='')

# plt.plot(np.gradient(mean_x_sim))
# plt.plot(com_x)

plt.title(fr'Average trajectory, $\beta = {trust}$')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
# plt.axis('equal')

# add_decorations()

show_and_check_ipython()
