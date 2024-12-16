from scipy.spatial import ConvexHull
from utils import *
from select_file import *
from tqdm import tqdm
import os
import matplotlib.patches as mpatches

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}')

for trust in trusts:
    print(trust)

    if final_time == 0:
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        os.makedirs(hexbin_folder, exist_ok=True)
        os.makedirs(com_coord_folder, exist_ok=True)
    else:
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        os.makedirs(hexbin_folder, exist_ok=True)
        os.makedirs(com_coord_folder, exist_ok=True)

    # variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
    # spawn_radius = variables['spawn_radius']
    # n_agents = variables['n_agents']  

    # CENTER OF MASS
    count_sums = []
    for run_n in tqdm(range(n_runs), ascii=' █'):
    # for run_n in range(1):
        com_x = np.load(f'{com_coord_folder}/run{run_n}/com_x.npy', allow_pickle=True)
        com_y = np.load(f'{com_coord_folder}/run{run_n}/com_y.npy', allow_pickle=True)
        com_x_std = np.load(f'{com_coord_folder}/run{run_n}/com_x_std.npy', allow_pickle=True)
        com_y_std = np.load(f'{com_coord_folder}/run{run_n}/com_y_std.npy', allow_pickle=True)

        # create an empty hexbin to get grid structure
        hb = plt.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y])
        hex_centers_x = hb.get_offsets()[:, 0]
        hex_centers_y = hb.get_offsets()[:, 1]
        plt.close()

        # initialize an array to accumulate counts
        bin_values = np.zeros(len(hex_centers_x))

        # loop through each timestep to build ellipses
        for t in range(len(com_x)):
            # parameters of the ellipse
            x0, y0 = com_x[t], com_y[t]
            a, b = com_x_std[t]*2, com_y_std[t]*2

            # check which hexbin centers fall within the ellipse
            inside_ellipse = ((hex_centers_x - x0) / a) ** 2 + ((hex_centers_y - y0) / b) ** 2 <= 1
            bin_values[inside_ellipse] = 1  # assign count = 1 to the bins inside the ellipse

            # # visualise the ellipse and the selected centers (for debugging)
            # if run_n == 0 and t == 0:
            #     fig, ax = plt.subplots()
            #     add_decorations()
            #     ax.scatter(hex_centers_x, hex_centers_y, color='lightgrey')
            #     ax.scatter(hex_centers_x[inside_ellipse], hex_centers_y[inside_ellipse], color='red', s=20)
            #     ellipse = mpatches.Ellipse((x0, y0), 2*a, 2*b, edgecolor='blue', facecolor='none')
            #     ax.add_patch(ellipse)

        count_sums.append(bin_values)

    total_sum = np.sum(count_sums, axis=0)
    success_rate = total_sum/n_runs

    success_rate.dump(f'{hexbin_folder}/com_successrate_gridsize{gridsize}_offset{offset}.npy')

    show_and_check_ipython()
