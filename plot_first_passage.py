from utils import *
from select_file import *

if final_time == 0:
    coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/wait_for_reach/trust{trust}'
else:
    coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
spawn_center = variables['spawn_center']
spawn_radius = variables['spawn_radius']
n_agents = variables['n_agents']  

source_coordinates = [spawn_center[0] -l_x, spawn_center[1] - h_y]

plt.figure('First passage time')

bound_x = [source_coordinates[0] - margin_x, spawn_center[0] + spawn_radius + 1]
bound_y = [spawn_center[1] + spawn_radius + margin_y, spawn_center[1] - spawn_radius - margin_y]

try:
    # avg_fpt_bins = np.load(f'{coord_folder}/avg_fpt_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)
    avg_fpt_bins = np.load(f'asd', allow_pickle=True)
    print('Average fpt data loaded!')

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

    # Adjust extent to reflect the coordinate shift
    shifted_extent = [bound_x[0] - spawn_center[0], bound_x[1] - spawn_center[0],
                      bound_y[0] - spawn_center[1], bound_y[1] - spawn_center[1]]

    hb = plt.hexbin(flattened_xs, flattened_ys, gridsize=gridsize, extent=shifted_extent, cmap='cividis')

except:
    print('No average fpt data found, computing...')

    fpt_bins_runs = []
    for run_n in range(n_runs):
        print(run_n)
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

        # Adjust extent to reflect the coordinate shift
        shifted_extent = [bound_x[0] - spawn_center[0], bound_x[1] - spawn_center[0],
                          bound_y[0] - spawn_center[1], bound_y[1] - spawn_center[1]]

        # Create the initial hexbin plot (no C parameter for now)
        hb = plt.hexbin(flattened_xs, flattened_ys, gridsize=gridsize, extent=shifted_extent, cmap='cividis')

        if run_n != n_runs-1:
            plt.close()

        # Get the number of bins from the hexbin plot
        bin_coords = hb.get_offsets()  # The coordinates of each hexbin center
        n_bins = len(bin_coords)

        # Initialize first passage time array with inf (for bins that are not visited)
        fpt_bins = np.full(n_bins, np.inf)

        # Loop over timesteps and agents to calculate first passage times
        for t in range(n_timesteps):
            for agent_id in range(n_agents):
                x, y = run_xs[agent_id, t], run_ys[agent_id, t]

                # Calculate the distance to each hexbin center and find the closest bin
                distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
                bin_idx = np.argmin(distances)

                # Store the minimum timestep as the first passage time for the bin
                fpt_bins[bin_idx] = min(fpt_bins[bin_idx], t)

        # Mask bins that were never visited (still have inf as value)
        fpt_bins = np.ma.masked_where(fpt_bins == np.inf, fpt_bins)

        fpt_bins_runs.append(fpt_bins)

    stacked_fpt_bins = np.ma.vstack(fpt_bins_runs)
    avg_fpt_bins = np.ma.mean(stacked_fpt_bins, axis=0)

    # avg_fpt_bins.dump(f'{coord_folder}/avg_fpt_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy')

# Create a mask for bins where the x-coordinate is less than x_threshold
x_threshold = - 40
bin_coords = hb.get_offsets()  
x_edges, y_edges = bin_coords.T
mask_below_threshold = x_edges < x_threshold
avg_fpt_bins = np.ma.masked_where(mask_below_threshold, avg_fpt_bins)

# Update the hexbin plot to show first passage times
hb.set_array(avg_fpt_bins)
plt.colorbar(hb, label='Average first passage time')

# Calculate the distance to each hexbin center and find the closest bin to the source
# x, y = source_coordinates[0], source_coordinates[1]
x, y = -l_x, -h_y
bin_coords = hb.get_offsets()
distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
bin_idx = np.argmin(distances)
fpt_source = avg_fpt_bins[bin_idx]
plt.plot(x, y, '+r')
plt.text(bin_coords[bin_idx,0], bin_coords[bin_idx,1]+1, f'{fpt_source:.1f}', ha='center', va='bottom', c='r')

# Ensure the color limits are set according to first passage time
plt.clim(np.min(avg_fpt_bins), np.max(avg_fpt_bins)) 

plt.title(rf'$\beta={trust}$')
plt.axhline(0, c='r', lw=1, ls='--', alpha=1.0)
plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=False, color='r', ls='--', alpha=1.0) )

arrow_length = 5
hl = 1.5 
dx = arrow_length * np.cos(mu)
dy = arrow_length * np.sin(mu)
plt.arrow(0, 0, dx, dy, head_width=1.5, head_length=hl, width=0.4, fc='w', ec='w', zorder=2)

if sigma > 0:
    import matplotlib.patches as patches
    up = np.degrees(mu) - np.degrees(sigma) / 2 
    dwn = np.degrees(mu) + np.degrees(sigma) / 2 
    wedge = patches.Wedge((0, 0), arrow_length+hl, up, dwn, color='w', alpha=0.3, zorder=1)
    plt.gca().add_patch(wedge)

plt.axis('scaled')
plt.xlim(-60,10)
plt.ylim(-40,40)

show_and_check_ipython()
