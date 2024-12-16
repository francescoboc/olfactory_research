from scipy.spatial import ConvexHull
from utils import *
from select_file import *
from tqdm import tqdm
import os

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}')

for trust in trusts:
    print(trust)

    if final_time == 0:
        coord_folder = f'../storage/coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        os.makedirs(hexbin_folder, exist_ok=True)
        os.makedirs(com_coord_folder, exist_ok=True)
    else:
        coord_folder = f'../storage/coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        os.makedirs(hexbin_folder, exist_ok=True)
        os.makedirs(com_coord_folder, exist_ok=True)

    variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
    spawn_radius = variables['spawn_radius']
    n_agents = variables['n_agents']  

    try:
        # success_rate = np.load(f'{hexbin_folder}/com_successrate_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)
        success_rate = np.load(f'{hexbin_folder}/successrate_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)

        print('Success rate data already exists!')

    except:
        print('No success rate data found, computing...')

        # INDIVIDUAL AGENTS
        count_sums = []
        for run_n in tqdm(range(n_runs), ascii=' █'):
            coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
            coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

            n_timesteps = len(coord_x[0]) 

            counts = []
            for agent_id in range(n_agents):
                x = coord_x[agent_id]
                y = coord_y[agent_id]
                hb = plt.hexbin(x, y, gridsize=gridsize, extent=[*bound_x, *bound_y])
                plt.close()
                bin_values = hb.get_array()

                # only look for first passage (only count the first visit to the bin)
                bin_values[np.nonzero(bin_values)]=1
                counts.append(bin_values)

            count_sum = np.sum(counts, axis=0)

            # only count for success rate (if at least an agent was in the bin, set it to 1)
            count_sum[np.where(count_sum > 1)] = 1
            count_sums.append(count_sum)

        total_sum = np.sum(count_sums, axis=0)
        success_rate = total_sum/n_runs

        success_rate.dump(f'{hexbin_folder}/successrate_gridsize{gridsize}_offset{offset}.npy')

        # CENTER OF MASS
        count_sums = []
        for run_n in tqdm(range(n_runs), ascii=' █'):
            coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
            coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

            n_timesteps = len(coord_x[0]) 

            com_x, com_y = [], []
            com_x_std, com_y_std = [], []

            # calculate center of mass for each timestep
            for t in range(n_timesteps):
                x_mean = np.mean([coord_x[agent_id][t] for agent_id in range(n_agents)])
                y_mean = np.mean([coord_y[agent_id][t] for agent_id in range(n_agents)])
                com_x.append(x_mean)
                com_y.append(y_mean)

                x_std = np.std([coord_x[agent_id][t] for agent_id in range(n_agents)])
                y_std = np.std([coord_y[agent_id][t] for agent_id in range(n_agents)])
                com_x_std.append(x_std)
                com_y_std.append(y_std)

            hb = plt.hexbin(com_x, com_y, gridsize=gridsize, extent=[*bound_x, *bound_y])

            plt.close()

            bin_values = hb.get_array()
            bin_values[np.nonzero(bin_values)] = 1  # Count each bin only once
            count_sums.append(bin_values)

            # save coordinates and std of center of mass
            os.makedirs(f'{com_coord_folder}/run{run_n}', exist_ok=True)
            np.save(f'{com_coord_folder}/run{run_n}/com_x', com_x)
            np.save(f'{com_coord_folder}/run{run_n}/com_y', com_y)
            np.save(f'{com_coord_folder}/run{run_n}/com_x_std', com_x_std)
            np.save(f'{com_coord_folder}/run{run_n}/com_y_std', com_y_std)

        total_sum = np.sum(count_sums, axis=0)
        success_rate = total_sum/n_runs

        # success_rate.dump(f'{hexbin_folder}/com_successrate_gridsize{gridsize}_offset{offset}.npy')
