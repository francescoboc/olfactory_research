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
        probability_gridsize = np.load(f'{hexbin_folder}/probability_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)
        print('Probability data already exists!')

    except:
        print('No probability data found, computing...')

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
            count_sums.append(count_sum)

        total_sum = np.sum(count_sums, axis=0)
        probability = total_sum/(n_agents*n_runs)

        probability.dump(f'{hexbin_folder}/probability_gridsize{gridsize}_offset{offset}.npy')
