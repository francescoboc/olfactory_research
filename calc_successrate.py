from scipy.spatial import ConvexHull
from utils import *
from tqdm import tqdm
from select_file import *

if final_time == 0:
    coord_folder = f'coordinates/hexbin/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    os.makedirs(hexbin_folder, exist_ok=True)
else:
    coord_folder = f'coordinates/hexbin/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
    hexbin_folder = f'hexbins/hexbin/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
    os.makedirs(hexbin_folder, exist_ok=True)

variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
spawn_radius = variables['spawn_radius']
n_agents = variables['n_agents']  
n_timesteps = variables['final_time'] + 1  

traj_center = final_x/2
bound_x = [traj_center - offset, traj_center + offset]
bound_y = [-offset, offset]

try:
    if center_of_mass:
        success_rate = np.load(f'{coord_folder}/com_successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)
    else:
        success_rate = np.load(f'{coord_folder}/successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)

    print('Hexbin data already exists!')

except:
    print('No hexbin data found, computing...')

    std_x, std_y = [], []
    mean_x, mean_y = [], []
    if center_of_mass:
        count_sums = []
        for run_n in tqdm(range(n_runs), ascii=' █'):
            coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
            coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

            n_timesteps = len(coord_x[0]) 

            com_x, com_y = [], []

            # calculate center of mass for each timestep
            for t in range(n_timesteps):
                x_mean = np.mean([coord_x[agent_id][t] for agent_id in range(n_agents)])
                y_mean = np.mean([coord_y[agent_id][t] for agent_id in range(n_agents)])
                com_x.append(x_mean)
                com_y.append(y_mean)

                xstd = np.std([coord_x[agent_id][t] for agent_id in range(n_agents)])
                ystd = np.std([coord_y[agent_id][t] for agent_id in range(n_agents)])

                # calculate l(t)
                try:
                    std_x[t].append(xstd)
                    std_y[t].append(ystd)
                except:
                    std_x.append([xstd])
                    std_y.append([ystd])

                try:
                    mean_x[t].append(x_mean)
                    mean_y[t].append(y_mean)
                except:
                    mean_x.append([x_mean])
                    mean_y.append([y_mean])

            hb = plt.hexbin(com_x, com_y, gridsize=gridsize, extent=[*bound_x, *bound_y])

            plt.close()

            bin_values = hb.get_array()
            bin_values[np.nonzero(bin_values)] = 1  # Count each bin only once
            count_sums.append(bin_values)

        total_sum = np.sum(count_sums, axis=0)
        success_rate = total_sum/n_runs

        success_rate.dump(f'{hexbin_folder}/com_successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy')

    else:
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

        success_rate.dump(f'{hexbin_folder}/successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy')

