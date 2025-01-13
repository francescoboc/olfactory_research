from utils import *

# source position
l_x = 50
h_y = 8.5

def get_beta_star_from_fpt(l_x, h_y):
    def calculate_fpt_source(coord_folder, l_x, h_y):
        variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
        spawn_center = variables['spawn_center']
        spawn_radius = variables['spawn_radius']
        n_agents = variables['n_agents']  

        source_coordinates = [spawn_center[0] -l_x, spawn_center[1] - h_y]

        bound_x = [source_coordinates[0] - margin_x, spawn_center[0] + spawn_radius + 1]
        bound_y = [spawn_center[1] + spawn_radius + margin_y, spawn_center[1] - spawn_radius - margin_y]

        try:
            avg_fpt_bins = np.load(f'{coord_folder}/avg_fpt_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)

        except:
            print(f'No average fpt data found for beta={trust}, gridsize={gridsize}')
            return

        run_n = 0
        coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
        coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

        n_timesteps = len(coord_x[0])  # Assume each agent has the same number of timesteps

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

        # Step 1: Create the initial hexbin plot (no C parameter for now)
        fig1, ax1 = plt.subplots()
        hb = ax1.hexbin(flattened_xs, flattened_ys, gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='viridis')
        plt.close(fig1)

        # Create a mask for bins where the x-coordinate is less than x_threshold
        x_threshold = source_coordinates[0] - 2  
        bin_coords = hb.get_offsets()  # The coordinates of each hexbin center
        x_edges, y_edges = bin_coords.T
        mask_below_threshold = x_edges < x_threshold
        avg_fpt_bins = np.ma.masked_where(mask_below_threshold, avg_fpt_bins)

        # Step 4: Update the hexbin plot to show first passage times
        hb.set_array(avg_fpt_bins)  # Update the color data for the bins

        # Calculate the distance to each hexbin center and find the closest bin to the source
        x, y = source_coordinates[0], source_coordinates[1]
        bin_coords = hb.get_offsets()  
        distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
        bin_idx = np.argmin(distances)
        fpt_source = avg_fpt_bins[bin_idx]

        return fpt_source

    # swarm parameters
    rd = 0.2
    spawn_radius = 25*rd 

    # visual_radius = 0
    # visual_radius = 5*rd
    visual_radius = 2*spawn_radius

    sigma = 0
    # sigma = np.pi/3

    rand_casting_steps = 100
    # rand_casting_steps = 20
    # rand_casting_steps = 0

    final_time = 0

    # trusts = [0.10, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]

    # Define extent and gridsize for hexbin plot
    gridsize = 200
    margin_x = 40
    margin_y = 40

    fpt_source_list = []
    for trust in trusts:
        coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/sigma{sigma:.2f}_randsteps{rand_casting_steps}/wait_for_reach/trust{trust}'

        fpt_source = calculate_fpt_source(coord_folder, l_x, h_y)

        fpt_source_list.append(fpt_source)

    # extract beta star from list
    for i in range(len(fpt_source_list)):
        # if the value is masked it means that it was never reached
        if np.ma.is_masked(fpt_source_list[i]):
            break

    beta_star = trusts[i-1]

    return beta_star

