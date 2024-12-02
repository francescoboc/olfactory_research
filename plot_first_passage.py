from utils import *
from select_file import *

def plot_first_passage(trust, l_x, h_y, plot=True):
    if final_time == 0:
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    else:
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

    try:
        avg_fpt = np.load(f'{hexbin_folder}/avg_fpt_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)
        data_found = True

    except:
        data_found = False

    if data_found:
        if plot: plt.figure()

        coord_x = np.load(f'{com_coord_folder}/run0/coord_x.npy', allow_pickle=True).item()
        coord_y = np.load(f'{com_coord_folder}/run0/coord_y.npy', allow_pickle=True).item()

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

        hb = plt.hexbin(flattened_xs, flattened_ys, gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='cividis')

        if not plot: plt.close()

        # Create a mask for bins where the x-coordinate is less than x_threshold
        x_threshold = final_x
        bin_coords = hb.get_offsets()  
        x_edges, y_edges = bin_coords.T
        mask_below_threshold = x_edges > x_threshold
        avg_fpt = np.ma.masked_where(mask_below_threshold, avg_fpt)

        # noralize the fpts by the straight line path
        for i in range(len(bin_coords)):
            x_s, y_s = bin_coords[i][0], bin_coords[i][1]
            straight_line_time = np.sqrt((x_s-spawn_radius)**2 + y_s**2)/speed
            avg_fpt[i] /= straight_line_time

        # Update the hexbin plot to show first passage times
        hb.set_array(avg_fpt)

        # Calculate the distance to each hexbin center and find the closest bin to the source
        x, y = l_x, h_y
        bin_coords = hb.get_offsets()
        distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
        bin_idx = np.argmin(distances)
        fpt_source = avg_fpt[bin_idx]

        x1, y1 = 70, 7
        distances = np.sqrt((bin_coords[:, 0] - x1)**2 + (bin_coords[:, 1] - y1)**2)
        bin_idx1 = np.argmin(distances)
        fpt_source1 = avg_fpt[bin_idx1]

        if plot:
            plt.colorbar(hb, label='Normalised average first passage time')

            plt.plot(x, y, 'or')
            plt.text(bin_coords[bin_idx,0], bin_coords[bin_idx,1]+2, f'{fpt_source:.2f}', ha='center', va='bottom', c='r')

            plt.plot(x1, y1, 'sr')
            plt.text(bin_coords[bin_idx1,0], bin_coords[bin_idx1,1]+2, f'{fpt_source1:.2f}', ha='center', va='bottom', c='r')

            # Ensure the color limits are set according to first passage time
            plt.clim(np.min(avg_fpt), np.max(avg_fpt)) 

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

            plt.xlim(*bound_x)
            plt.ylim(*bound_y)

            # plt.gca().invert_xaxis()
            # plt.savefig(f'beta{trust}.png')

            show_and_check_ipython()
    else:
        fpt_source = np.nan

    return fpt_source, data_found

if __name__ == '__main__':
    fpt_source, data_found = plot_first_passage(trust, l_x, h_y)
