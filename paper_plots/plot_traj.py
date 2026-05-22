from utils import *
from select_file import *

com_coord_folder = f'../com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'

# run_n = 11
for run_n in range(50):
    # x_fulltheo = np.load(f'{com_coord_folder}/run{run_n}/com_x_theo_betav0.npy')
    # y_fulltheo = np.load(f'{com_coord_folder}/run{run_n}/com_y_theo_betav0.npy')

    # x_theo = np.load(f'{com_coord_folder}/run{run_n}/com_x_theo.npy')
    # y_theo = np.load(f'{com_coord_folder}/run{run_n}/com_y_theo.npy')

    x_sim = np.load(f'{com_coord_folder}/run{run_n}/com_x.npy')
    y_sim = np.load(f'{com_coord_folder}/run{run_n}/com_y.npy')

    # plt.plot(x_fulltheo, y_fulltheo-1, label=r'theory $\beta v_0$')
    # plt.plot(x_theo, y_theo, label='theo')
    plt.plot(x_sim, y_sim, label='simulation')
    # plt.legend()
add_decorations()

show_and_check_ipython()
