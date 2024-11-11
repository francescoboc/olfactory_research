from scipy.spatial import ConvexHull
from utils import *
from tqdm import tqdm

def get_convexhull(hb, pr):
    probs = hb.get_array()
    bin_centers = hb.get_offsets()

    hulls, points = [], []

    # find indices of bins above threshold
    selected_bins = probs > pr

    # filter x_coords to only include non-zero bins
    selected_xs = bin_centers[selected_bins, 0]
    selected_ys = bin_centers[selected_bins, 1]

    # use ConvexHull to find the outermost boundary around the non-zero bins
    points = np.column_stack([selected_xs, selected_ys])

    hull = ConvexHull(points)

    return hull, points

# trust parameter aka beta
# trust = 0.0

# trust = 0.1
# trust = 0.2
# trust = 0.3
# trust = 0.4
# trust = 0.5
trust = 0.6
# trust = 0.7
# trust = 0.8
# trust = 0.9

# trust = 0.95
# trust = 0.99

# trust = 1.0

# check the trajectories of all the agents or only the center of mass
center_of_mass = 0

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

n_runs = 50
# n_runs = 10

final_time = 500
# final_time = 0

if final_time == 0:
    coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/sigma{sigma:.2f}_randsteps{rand_casting_steps}/wait_for_reach/trust{trust}'
else:
    coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
spawn_center = variables['spawn_center']
spawn_radius = variables['spawn_radius']
lx = variables['lx']
source_coordinates = variables['source_coordinates']
n_agents = variables['n_agents']  
n_timesteps = variables['final_time'] + 1  

gridsize = 200
margin_x = 40
margin_y = 40
bound_x = [source_coordinates[0]-margin_x, spawn_center[0]+spawn_radius+1]
bound_y = [spawn_center[1]+spawn_radius+margin_y, spawn_center[1]-spawn_radius-margin_y]

try:
    if center_of_mass:
        probability = np.load(f'{coord_folder}/com_probability_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)
    else:
        probability = np.load(f'{coord_folder}/probability_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)
    print('Passage counts data loaded!')

except:

    print('No passage counts data found, computing...')
    if center_of_mass:
        count_sums = []
        for run_n in tqdm(range(n_runs), ascii=' █'):
            coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
            coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

            n_timesteps = len(coord_x[0]) 

            centers_of_mass_x = []
            centers_of_mass_y = []

            # Calculate center of mass for each timestep
            for t in range(n_timesteps):
                com_x = np.mean([coord_x[agent_id][t] for agent_id in range(n_agents)])
                com_y = np.mean([coord_y[agent_id][t] for agent_id in range(n_agents)])
                centers_of_mass_x.append(com_x)
                centers_of_mass_y.append(com_y)

            # # Calculate hexbin for the center of mass trajectory
            hb = plt.hexbin(centers_of_mass_x, centers_of_mass_y, gridsize=gridsize, extent=[*bound_x, *bound_y])

            plt.close()

            bin_values = hb.get_array()
            bin_values[np.nonzero(bin_values)] = 1  # Count each bin only once
            count_sums.append(bin_values)

        total_sum = np.sum(count_sums, axis=0)
        probability = total_sum/n_runs

        probability.dump(f'{coord_folder}/com_probability_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy')

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
                bin_values[np.nonzero(bin_values)]=1
                counts.append(bin_values)
            count_sums.append(np.sum(counts, axis=0))

        total_sum = np.sum(count_sums, axis=0)
        probability = total_sum/(n_agents*n_runs)

        probability.dump(f'{coord_folder}/probability_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy')

run_n = 0
coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()
x = coord_x[0]
y = coord_y[0]
hb = plt.hexbin(x, y, gridsize=gridsize, extent=[*bound_x, *bound_y])

hb.set_array(probability)
hb.set_clim(min(hb.get_array()), max(hb.get_array()))  

cb = plt.colorbar(hb, orientation='horizontal')

centerline = spawn_center[1]

# prob_list = [0, 0.01]
prob_list = [0]

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

        if s==0: plt.plot(xs, ys, c=colors[i], lw=1, label=prob_list[i])
        else: plt.plot(xs, ys, c=colors[i], lw=1)

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

    plt.axhline(max_nonzero_y, c='w', lw=1, alpha=0.7)
    plt.axhline(min_nonzero_y, c='w', lw=1, alpha=0.7)

    exploration_area = max_nonzero_y - min_nonzero_y
    plt.text(min_nonzero_x, max_nonzero_y, f'{exploration_area:.1f}', ha='left', va='bottom', c='w', alpha=0.7)
    plt.text(spawn_center[0], spawn_center[1]+spawn_radius, f'{spawn_radius*2:.1f}', ha='left', va='bottom', c='w', alpha=0.7)

else:
    plt.axhline(max_y, c='w', lw=1, alpha=0.7)
    plt.axhline(min_y, c='w', lw=1, alpha=0.7)

    exploration_area = max_y - min_y
    plt.text(source_coordinates[0], max_y, f'{exploration_area:.1f}', ha='left', va='bottom', c='w', alpha=0.7)
    plt.text(spawn_center[0], spawn_center[1]+spawn_radius, f'{spawn_radius*2:.1f}', ha='left', va='bottom', c='w', alpha=0.7)

plt.legend()

# set background (non-explored parts of space) same color as min of colorbar
plt.gca().set_facecolor(cb.cmap(0))

plt.title(rf'$\beta={trust}$')
plt.plot(*source_coordinates, 'or', alpha=0.5)
plt.axhline(centerline, c='w', lw=1, ls='--', alpha=0.7)
plt.gca().add_patch( plt.Circle(spawn_center, spawn_radius, fill=False, color='w', ls='--', alpha=0.7) )

plt.axis('equal')

show_and_check_ipython()
