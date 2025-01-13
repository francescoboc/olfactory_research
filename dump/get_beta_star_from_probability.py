from scipy.spatial import Delaunay
from utils import *

# # source position
# l_x = 50
# h_y = 8.5

# probability treshold
pr = 0.0

def get_beta_star_from_hull(l_x, h_y, pr):
    def in_hull(p, hull):
        """
        Test if points in `p` are in `hull`

        `p` should be a `NxK` coordinates of `N` points in `K` dimensions
        `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
        coordinates of `M` points in `K`dimensions for which Delaunay triangulation
        will be computed
        """
        if not isinstance(hull,Delaunay):
            hull = Delaunay(hull)

        return hull.find_simplex(p)>=0

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

    in_convexhull_list = []
    for trust in trusts:

        coord_folder = f'coordinates/first_passage_grid/vr{visual_radius}/sigma{sigma:.2f}_randsteps{rand_casting_steps}/wait_for_reach/trust{trust}'
        probability = np.load(f'{coord_folder}/probability_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)

        variables = np.load(f'{coord_folder}/log.npy', allow_pickle=True).item()
        spawn_center = variables['spawn_center']
        spawn_radius = variables['spawn_radius']
        n_agents = variables['n_agents']  

        source_coordinates = [spawn_center[0] -l_x, spawn_center[1] - h_y]

        bound_x = [source_coordinates[0]-margin_x, spawn_center[0]+spawn_radius+1]
        bound_y = [spawn_center[1]+spawn_radius+margin_y, spawn_center[1]-spawn_radius-margin_y]

        run_n = 0
        coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
        coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()
        x = coord_x[0]
        y = coord_y[0]
        fig2, ax2 = plt.subplots()
        hb = ax2.hexbin(x, y, gridsize=gridsize, extent=[*bound_x, *bound_y])
        plt.close(fig2)

        hb.set_array(probability)
        hb.set_clim(min(hb.get_array()), max(hb.get_array()))  

        probs = hb.get_array()
        bin_centers = hb.get_offsets()

        # find indices of bins above threshold
        selected_bins = probability > pr

        # filter x_coords to only include non-zero bins
        selected_xs = bin_centers[selected_bins, 0]
        selected_ys = bin_centers[selected_bins, 1]

        # use ConvexHull to find the outermost boundary around the non-zero bins
        points = np.column_stack([selected_xs, selected_ys])

        # # plot convexhulls relative to the probability thresholds in prob_list
        # hull = ConvexHull(points)
        # for simplex in hull.simplices:
        #     plt.plot(points[simplex, 0], points[simplex, 1], c='r', lw=1)  

        in_convexhull_list.append(in_hull(source_coordinates, points))

    # extract beta star from list
    for i in range(len(in_convexhull_list)):
        # if the value is False it means that the source was out the convex hull
        if in_convexhull_list[i]==False:
            break

    beta_star = trusts[i-1]

    return beta_star
