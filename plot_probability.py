from scipy.spatial import ConvexHull
from utils import *

def get_convexhulls(hb, prob_list):
    probs = hb.get_array()
    bin_centers = hb.get_offsets()

    hulls, points = [], []
    for pr in prob_list:
        # find indices of bins above threshold
        selected_bins = probs > pr

        # filter x_coords to only include non-zero bins
        selected_xs = bin_centers[selected_bins, 0]
        selected_ys = bin_centers[selected_bins, 1]

        # use ConvexHull to find the outermost boundary around the non-zero bins
        po = np.column_stack([selected_xs, selected_ys])
        hulls.append(ConvexHull(po))
        points.append(po)

    return hulls, points

# trust parameter aka beta
# trust = 0.0

# trust = 0.1
# trust = 0.2
# trust = 0.3
# trust = 0.4
# trust = 0.5
# trust = 0.6
# trust = 0.7
# trust = 0.8
trust = 0.9

# trust = 0.95
# trust = 0.99

# trust = 1.0

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

if trust==0.1:
    n_runs = 10
else:
    n_runs = 50

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

# # OLD COORDINATES
# coord_folder = f'coordinates/detection_cone/old/vr{visual_radius}/trust{trust}'

if final_time == 0:
    # Lists to store the coordinates for all runs (since timesteps vary)
    all_xs = []
    all_ys = []
else:
    # Pre-allocate arrays for all runs
    all_xs = np.zeros((n_runs, n_agents, n_timesteps))
    all_ys = np.zeros((n_runs, n_agents, n_timesteps))

for run_n in range(n_runs):
    coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
    coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

    if final_time == 0:
        n_timesteps = len(coord_x[0]) # Assume each agent has the same number of timesteps

        # Collect data for this run, agent by agent
        run_xs = np.zeros((n_agents, n_timesteps))
        run_ys = np.zeros((n_agents, n_timesteps))

        for agent_id in range(n_agents):
            run_xs[agent_id, :] = coord_x[agent_id]
            run_ys[agent_id, :] = coord_y[agent_id]

        # Append to the main list (one list entry per run)
        all_xs.append(run_xs)
        all_ys.append(run_ys)

    else:
        for agent_id in range(n_agents):
            all_xs[run_n, agent_id, :] = coord_x[agent_id]
            all_ys[run_n, agent_id, :] = coord_y[agent_id]

    # # calculate center of mass trajectory
    # x_com = []
    # y_com = []
    # for t in range(timesteps):
    #     xs = []
    #     ys = []
    #     for agent in agents:
    #         xs.append(coord_x[agent][t])
    #         ys.append(coord_y[agent][t])
    #     x_com.append(np.mean(xs))
    #     y_com.append(np.mean(ys))
    # x_coms.append(x_com)
    # y_coms.append(y_com)

    # for step in timesteps:
        # plt.plot(all_x, all_y, '.w', alpha=0.3)
        # plt.pause(0.001)

if final_time == 0:
    # After collecting data for all runs, concatenate the arrays along the timestep axis
    # This results in one large array of (all_timesteps_across_all_runs, agents)
    all_xs = np.concatenate([run_x.T for run_x in all_xs], axis=0)
    all_ys = np.concatenate([run_y.T for run_y in all_ys], axis=0)

# flatten the arrays to obtain a 1D list of all values
flattened_xs = all_xs.flatten()
flattened_ys = all_ys.flatten()

gridsize = 200
margin_x = 40
margin_y = 40
bound_x = [source_coordinates[0]-margin_x, spawn_center[0]+spawn_radius+1]
bound_y = [spawn_center[1]+spawn_radius+margin_y, spawn_center[1]-spawn_radius-margin_y]

plt.figure()

norm = len(flattened_xs)
hb = plt.hexbin(flattened_xs, flattened_ys, gridsize=gridsize, 
        C=np.ones_like(flattened_ys)/norm,
        reduce_C_function=np.sum,
        bins='log',
        extent=[*bound_x, *bound_y], cmap='cividis')

cb = plt.colorbar(orientation='horizontal')

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

prob_list = [0, 1e-4, 2e-4]
hulls, points = get_convexhulls(hb, prob_list)

# plot convexhulls relative to the probability thresholds in prob_list
i=0
for hull, points in zip(hulls, points):
    s=0
    for simplex in hull.simplices:
        if s==0:
            plt.plot(points[simplex, 0], points[simplex, 1], c=colors[i], lw=1, label=prob_list[i])  
        else:
            plt.plot(points[simplex, 0], points[simplex, 1], c=colors[i], lw=1)  
        s+=1
    i+=1

plt.legend()

# set background (non-explored parts of space) same color as min of colorbar
plt.gca().set_facecolor(cb.cmap(0))

plt.title(rf'$\beta={trust}$')
plt.plot(*source_coordinates, 'or', alpha=0.5)
plt.axhline(source_coordinates[1], c='w', lw=1, ls='--', alpha=0.7)
plt.gca().add_patch( plt.Circle(spawn_center, spawn_radius, fill=False, color='w', ls='--', alpha=0.7) )

# x_coms_avg = np.mean(x_coms, axis=0)
# x_coms_std = np.std(x_coms, axis=0)
# y_coms_avg = np.mean(y_coms, axis=0)
# y_coms_std = np.std(y_coms, axis=0)
# plt.errorbar(x_coms_avg, y_coms_avg, yerr=y_coms_std, xerr=x_coms_std)
# # shaded_errorbar(x_coms_avg, y_coms_avg, yerr=y_coms_std, m='', alpha=0.2, lab=trust)
# plt.legend()

plt.axis('equal')

show_and_check_ipython()
