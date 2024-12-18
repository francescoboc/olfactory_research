from utils import *
from select_file import *

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}')
print(f'trust = {trust:.2f}')

if final_time == 0:
    com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
else:
    com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

std_x_list, std_y_list = [], []
for run_n in range(n_runs):
    # com_x = np.load(f'{com_coord_folder}/run{run_n}/com_x.npy', allow_pickle=True)
    # com_y = np.load(f'{com_coord_folder}/run{run_n}/com_y.npy', allow_pickle=True)
    com_x_std = np.load(f'{com_coord_folder}/run{run_n}/com_x_std.npy', allow_pickle=True)
    com_y_std = np.load(f'{com_coord_folder}/run{run_n}/com_y_std.npy', allow_pickle=True)
    # wt = np.load(f'{com_coord_folder}/run{run_n}/wt_history.npy', allow_pickle=True)

    std_x_list.append(com_x_std)
    std_y_list.append(com_y_std)

# calculate average 
mean_std_x = np.mean(truncate_and_stack(std_x_list),axis=0)
mean_std_y = np.mean(truncate_and_stack(std_y_list),axis=0)

# plt.figure()
# plt.plot(mean_std_x, 'b--', label='x')
# plt.plot(mean_std_y, 'r', label='y')

plt.title(fr'std x')
plt.plot(mean_std_x, '--', label=fr'$\beta = {trust}$')

# plt.title(fr'std y')
# plt.plot(mean_std_y, label=fr'$\beta = {trust}$')

# plt.plot(std_x_list[0], 'b--', label='x')
# plt.plot(std_y_list[0], 'r', label='y')

# plt.title(fr'$\beta = {trust}$')
plt.xlabel('Timestep')
plt.ylabel('Average std over 50 simulations')
plt.legend()

show_and_check_ipython()

