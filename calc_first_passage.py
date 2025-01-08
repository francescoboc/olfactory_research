from utils import *
from select_file import *
from tqdm import tqdm
import os
from matplotlib.patches import RegularPolygon
from scipy.spatial import cKDTree  # Fast spatial indexing

# Function to check if a point is inside a hexagon
def is_point_in_hexagon(x, y, hex_center):
    hexagon = RegularPolygon(hex_center, numVertices=6, radius=hex_radius, orientation=np.radians(30))
    return hexagon.contains_point((x, y))

# print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}, n_ag={n_agents}')

for trust in trusts:
    if final_time == 0:
        coord_folder = f'../storage/coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        hexbin_folder = f'hexbins/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        os.makedirs(hexbin_folder, exist_ok=True)
    else:
        coord_folder = f'../storage/coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        hexbin_folder = f'hexbins/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        os.makedirs(hexbin_folder, exist_ok=True)

    try:
        avg_fpt = np.load(f'{hexbin_folder}/avg_fpt_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)

        print(f'{trust} FPT data already exists!')

    except:
        print(f'{trust} No FPT data found, computing...')

        fpt_bins_runs = []
        # for run_n in tqdm(range(n_runs), ascii=' █'):
        for run_n in range(n_runs):
            coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
            coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

            n_timesteps = len(coord_x[0])  

            # Initialize arrays to store the coordinates
            run_xs = np.zeros((n_agents, n_timesteps))
            run_ys = np.zeros((n_agents, n_timesteps))

            # Collect data for this run, agent by agent
            for agent_id in range(n_agents):
                run_xs[agent_id, :] = coord_x[agent_id]
                run_ys[agent_id, :] = coord_y[agent_id]

            # Flatten the arrays for hexbin processing
            flattened_xs = run_xs.flatten()
            flattened_ys = run_ys.flatten()

            # Create the initial hexbin plot (no C parameter for now)
            hb = plt.hexbin(flattened_xs, flattened_ys, gridsize=gridsize, extent=[*bound_x, *bound_y])

            plt.close()

            # Get the number of bins from the hexbin plot
            bin_coords = hb.get_offsets()  # The coordinates of each hexbin center
            n_bins = len(bin_coords)

            # Build a KDTree for fast nearest-neighbor search
            kdtree = cKDTree(bin_coords)

            # Initialize first passage time array with inf (for bins that are not visited)
            fpt_bins = np.full(n_bins, np.inf)

            # Loop over timesteps and agents to calculate first passage times
            for t in range(n_timesteps):
                for agent_id in range(n_agents):
                    x, y = run_xs[agent_id, t], run_ys[agent_id, t]

                    # Use KDTree to find nearby bins within the hex radius
                    nearby_bins = kdtree.query_ball_point((x, y), hex_radius)

                    # Perform the geometric check only for nearby bins
                    for bin_idx in nearby_bins:
                       hex_center = bin_coords[bin_idx]
                       if is_point_in_hexagon(x, y, hex_center):
                           fpt_bins[bin_idx] = min(fpt_bins[bin_idx], t)

                    # # Calculate the distance to each hexbin center and find the closest bin
                    # distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
                    # bin_idx = np.argmin(distances)

                    # Store the minimum timestep as the first passage time for the bin
                    fpt_bins[bin_idx] = min(fpt_bins[bin_idx], t)

            # Mask bins that were never visited (still have inf as value)
            fpt_bins = np.ma.masked_where(fpt_bins == np.inf, fpt_bins)

            fpt_bins_runs.append(fpt_bins)

        stacked_fpt_bins = np.ma.vstack(fpt_bins_runs)
        avg_fpt = np.ma.mean(stacked_fpt_bins, axis=0)

        avg_fpt.dump(f'{hexbin_folder}/avg_fpt_gridsize{gridsize}_offset{offset}.npy')
