from scipy.spatial import ConvexHull
from utils import *
from tqdm import tqdm
from select_file import *

# prob_list = [0, 0.5, 1]
prob_list = [1.0]

def get_convexhull(hb, pr):
    probs = hb.get_array()
    bin_centers = hb.get_offsets()

    hulls, points = [], []

    # find indices of bins above threshold
    if pr==1:
        selected_bins = probs >= pr
    else:
        selected_bins = probs > pr

    # filter x_coords to only include non-zero bins
    selected_xs = bin_centers[selected_bins, 0]
    selected_ys = bin_centers[selected_bins, 1]

    # use ConvexHull to find the outermost boundary around the non-zero bins
    points = np.column_stack([selected_xs, selected_ys])

    hull = ConvexHull(points)

    return hull, points

if final_time == 0:
    coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/wait_for_reach/trust{trust}'
else:
    coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
spawn_center = variables['spawn_center']
spawn_radius = variables['spawn_radius']
lx = variables['lx']
source_coordinates = variables['source_coordinates']
n_agents = variables['n_agents']  
n_timesteps = variables['final_time'] + 1  

source_coordinates = [spawn_center[0] -l_x, spawn_center[1] - h_y]

bound_x = [source_coordinates[0]-margin_x, spawn_center[0]+spawn_radius+1]
bound_y = [spawn_center[1]+spawn_radius+margin_y, spawn_center[1]-spawn_radius-margin_y]

try:
    if center_of_mass:
        success_rate = np.load(f'{coord_folder}/com_successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)
    else:
        success_rate = np.load(f'{coord_folder}/successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)

    print('Passage counts data loaded!')

except:
    print('No passage counts data found, computing...')

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

        success_rate.dump(f'{coord_folder}/com_successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy')

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

        success_rate.dump(f'{coord_folder}/successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy')

run_n = 0
coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()
x = coord_x[0]
y = coord_y[0]

# Adjust extent to reflect the coordinate shift
shifted_extent = [bound_x[0] - spawn_center[0], bound_x[1] - spawn_center[0],
                  bound_y[0] - spawn_center[1], bound_y[1] - spawn_center[1]]

plt.figure('Success rate')
hb = plt.hexbin(x, y, gridsize=gridsize, extent=shifted_extent)
# hb = plt.hexbin(x, y, gridsize=gridsize, extent=[*bound_x, *bound_y])

# Create a mask for bins where the x-coordinate is less than x_threshold
x_threshold = - 40
bin_coords = hb.get_offsets()  
x_edges, y_edges = bin_coords.T
mask_below_threshold = x_edges < x_threshold
# success_rate = np.ma.masked_where(mask_below_threshold, success_rate)
success_rate[mask_below_threshold] = 0

hb.set_array(success_rate)
hb.set_clim(np.min(success_rate), np.max(success_rate))  

cb = plt.colorbar(hb, label='Average succcess rate')

# centerline = spawn_center[1]
centerline = 0

i=0
max_y, min_y = centerline, centerline
for pr in prob_list:
    hull, points = get_convexhull(hb, pr)

    s=0
    for simplex in hull.simplices:

        # SHIFT points
        xs = points[simplex, 0]
        ys = points[simplex, 1]

        if center_of_mass:
            for j in range(len(ys)):
                if ys[j] > centerline: ys[j]+=spawn_radius
                else: ys[j]-=spawn_radius

                # find max and min
                if ys[j] > max_y: max_y = ys[j]
                if ys[j] < min_y: min_y = ys[j]

        if s==0: plt.plot(xs, ys, c=colors[i+1], lw=1, label=prob_list[i])
        else: plt.plot(xs, ys, c=colors[i+1], lw=1)
        # if s==0: plt.plot(xs, ys, c='w', lw=1, label=prob_list[i])
        # else: plt.plot(xs, ys, c='w', lw=1)

        s+=1
    i+=1

if not center_of_mass:
    # add axploration area vlines
    bin_values = hb.get_array()
    bin_centers = hb.get_offsets()

    # Find indices of non-zero bins (where the count is > 0)
    nonzero_bins = bin_values > 0

    # Filter x_coords to only include non-zero bins
    nonzero_xs = bin_centers[nonzero_bins, 0]
    nonzero_ys = bin_centers[nonzero_bins, 1]

    min_nonzero_x = min(nonzero_xs)

    max_nonzero_y = max(nonzero_ys)
    min_nonzero_y = min(nonzero_ys)

    # plt.axhline(max_nonzero_y, c='w', lw=1, alpha=0.7)
    # plt.axhline(min_nonzero_y, c='w', lw=1, alpha=0.7)
    # exploration_area = max_nonzero_y - min_nonzero_y
    # plt.text(min_nonzero_x, max_nonzero_y, f'{exploration_area:.1f}', ha='left', va='bottom', c='w', alpha=0.7)
    # plt.text(spawn_center[0], spawn_center[1]+spawn_radius, f'{spawn_radius*2:.1f}', ha='left', va='bottom', c='w', alpha=0.7)

else:
    plt.axhline(max_y, c='w', lw=1, alpha=0.7)
    plt.axhline(min_y, c='w', lw=1, alpha=0.7)

    exploration_area = max_y - min_y
    plt.text(source_coordinates[0], max_y, f'{exploration_area:.1f}', ha='left', va='bottom', c='w', alpha=0.7)
    plt.text(spawn_center[0], spawn_center[1]+spawn_radius, f'{spawn_radius*2:.1f}', ha='left', va='bottom', c='w', alpha=0.7)

    # calculate L(t)
    std_x_avg = []
    for entry in std_x:
        std_x_avg.append(np.mean(entry))
    std_y_avg = []
    for entry in std_y:
        std_y_avg.append(np.mean(entry))

    com_x_avg = []
    com_x_std = []
    for entry in mean_x:
        com_x_avg.append(np.mean(entry))
        com_x_std.append(np.std(entry))
    com_y_avg = []
    com_y_std = []
    for entry in mean_y:
        com_y_avg.append(np.mean(entry))
        com_y_std.append(np.std(entry))

    total_std_y = np.array(com_y_std) + 2*np.array(std_y_avg)

    shaded_errorbar(com_x_avg, com_y_avg, yerr=total_std_y, lab='std', m='', c='w', alpha=0.3)

    # shaded_errorbar(com_x_avg, com_y_avg, yerr=spawn_radius, lab='std', m='', c='w', alpha=0.3)

plt.legend()

# set background (non-explored parts of space) same color as min of colorbar
plt.gca().set_facecolor(cb.cmap(0))

# Calculate the distance to each hexbin center and find the closest bin to the source
# x, y = source_coordinates[0], source_coordinates[1]
x, y = -l_x, -h_y
bin_coords = hb.get_offsets()  
distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
bin_idx = np.argmin(distances)
success_rate_source = success_rate[bin_idx]
plt.plot(x, y, '+r')
plt.text(bin_coords[bin_idx,0], bin_coords[bin_idx,1]+1, f'{success_rate_source:.1f}', ha='center', va='bottom', c='r')

plt.title(rf'$\beta={trust}$')
# plt.plot(*source_coordinates, 'or', alpha=0.5)
plt.axhline(0, c='r', lw=1, ls='--', alpha=1.0)
plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=False, color='r', ls='--', alpha=1.0, lw=1) )
# plt.axhline(spawn_center[1], c='r', lw=1, ls='--', alpha=1.0)
# plt.gca().add_patch( plt.Circle((spawn_center[0],spawn_center[1]), spawn_radius, fill=False, color='r', ls='--', alpha=1.0, lw=1) )

arrow_length = 5
hl = 1.5 
dx = arrow_length * np.cos(mu)
dy = arrow_length * np.sin(mu)
plt.arrow(0, 0, dx, dy, head_width=1.5, head_length=hl, width=0.4, fc='k', ec='k', zorder=2)

if sigma > 0:
    import matplotlib.patches as patches
    up = np.degrees(mu) - np.degrees(sigma) / 2 
    dwn = np.degrees(mu) + np.degrees(sigma) / 2 
    wedge = patches.Wedge((0, 0), arrow_length+hl, up, dwn, color='k', alpha=0.3, zorder=1)
    plt.gca().add_patch(wedge)

plt.axis('scaled')
plt.xlim(-60,10)
plt.ylim(-40,40)

show_and_check_ipython()
