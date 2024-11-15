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

# source position
l_x = 50
h_y = 8.5

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 

# visual_radius = 0
# visual_radius = 5*rd
visual_radius = 2*spawn_radius

# sigma = 0
# sigma = np.pi
sigma = np.pi/2
# sigma = np.pi/3

mu = 3.141
# mu = 4.712

rand_casting_steps = 100
# rand_casting_steps = 20
# rand_casting_steps = 0

final_time = 500
# final_time = 0

gridsize = 200
margin_x = 40
margin_y = 40

prob = 0.0
prob_list = [prob]

trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

fig, ax = plt.subplots()
fig1, ax1 = plt.subplots()

i=0
for trust in trusts:
    if final_time == 0:
        coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/wait_for_reach/trust{trust}'
    else:
        coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

    variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
    spawn_center = variables['spawn_center']
    spawn_radius = variables['spawn_radius']
    n_agents = variables['n_agents']  
    source_coordinates = [spawn_center[0] -l_x, spawn_center[1] - h_y]

    bound_x = [source_coordinates[0]-margin_x, spawn_center[0]+spawn_radius+1]
    bound_y = [spawn_center[1]+spawn_radius+margin_y, spawn_center[1]-spawn_radius-margin_y]

    success_rate = np.load(f'{coord_folder}/successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)

    run_n = 0
    coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
    coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()
    x = coord_x[0]
    y = coord_y[0]
    hb = ax1.hexbin(x, y, gridsize=gridsize, extent=[*bound_x, *bound_y])
    plt.close(fig1)

    hb.set_array(success_rate)

    # hb.set_clim(min(hb.get_array()), max(hb.get_array()))  
    # cb = plt.colorbar(hb, orientation='horizontal')

    # add axploration area vlines
    bin_values = hb.get_array()
    bin_centers = hb.get_offsets()

    # Find indices of non-zero bins (where the count is > 0)
    nonzero_bins = bin_values > 0

    # # Filter x_coords to only include non-zero bins
    # nonzero_xs = bin_centers[nonzero_bins, 0]
    # nonzero_ys = bin_centers[nonzero_bins, 1]
    # min_nonzero_x = min(nonzero_xs)
    # max_nonzero_y = max(nonzero_ys)
    # min_nonzero_y = min(nonzero_ys)
    # plt.axhline(max_nonzero_y, c='w', lw=1, alpha=0.7)
    # plt.axhline(min_nonzero_y, c='w', lw=1, alpha=0.7)

    # exploration_area = max_nonzero_y - min_nonzero_y
    # plt.text(min_nonzero_x, max_nonzero_y, f'{exploration_area:.1f}', ha='left', va='bottom', c='w', alpha=0.7)
    # plt.text(spawn_center[0], spawn_center[1]+spawn_radius, f'{spawn_radius*2:.1f}', ha='left', va='bottom', c='w', alpha=0.7)

    hulls, points = get_convexhulls(hb, prob_list)

    # plot convexhulls relative to the success_rate thresholds in prob_list
    for hull, points in zip(hulls, points):
        s=0
        for simplex in hull.simplices:
            if s==0:
                ax.plot(points[simplex, 0], points[simplex, 1], c=colors[i], lw=1, label=trust)  
            else:
                ax.plot(points[simplex, 0], points[simplex, 1], c=colors[i], lw=1)  
            s+=1
    i+=1

ax.legend(title=r'$\beta$', ncol=2)

ax.set_title(rf'$P_0={prob}$')
# ax.plot(*source_coordinates, '+r')
ax.axhline(spawn_center[1], c='k', lw=1, ls='--')
ax.add_patch( plt.Circle(spawn_center, spawn_radius, fill=False, color='k', ls='--') )

ax.axis('equal')

show_and_check_ipython()
