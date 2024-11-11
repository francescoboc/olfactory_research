from scipy.spatial import ConvexHull
import matplotlib.path as mpltPath
from utils import *

# # source position
# l_x = 50
# h_y = 8.5

# success_rate treshold
pr = 0.0

def get_beta_star_from_hull(l_x, h_y, pr, center_of_mass):

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

    def in_hull(point, hb, pr):
        hull, points = get_convexhull(hb, pr)

        centerline = spawn_center[1]
        all_x, all_y = [], []
        for simplex in hull.simplices:

            # SHIFT points
            xs = points[simplex, 0]
            ys = points[simplex, 1]

            if center_of_mass:
                for j in range(len(ys)):
                    if ys[j] > centerline: ys[j]+=spawn_radius
                    else: ys[j]-=spawn_radius

            # plt.plot(xs, ys, c='k', lw=1)
            all_x.append(xs[0])
            all_x.append(xs[1])
            all_y.append(ys[0])
            all_y.append(ys[1])

        plt.scatter(all_x, all_y, c='k', lw=1)
        plt.scatter(source_coordinates[0], source_coordinates[1])

        p = [[x,y] for x,y in zip(all_x, all_y)]
        p = np.array(p)
        mean = np.mean(p, axis=0)
        d = p-mean
        s = np.arctan2(d[:,0], d[:,1])

        ordered_p = p[np.argsort(s),:]

        poly = plt.Polygon(ordered_p, alpha=0.2, zorder=-10)
        plt.gca().add_patch(poly)

        path = mpltPath.Path(ordered_p)

        inside = path.contains_point(point)

        # print(inside)
        return inside

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

        if center_of_mass:
            success_rate = np.load(f'{coord_folder}/com_successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)
        else:
            success_rate = np.load(f'{coord_folder}/successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)

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

        hb.set_array(success_rate)
        hb.set_clim(min(hb.get_array()), max(hb.get_array()))  

        in_convexhull_list.append(in_hull(source_coordinates, hb, pr))

    # extract beta star from list
    for i in range(len(in_convexhull_list)):
        # if the value is False it means that the source was out the convex hull
        if in_convexhull_list[i]==False:
            break

    beta_star = trusts[i-1]

    return beta_star

# print(get_beta_star_from_hull(10,8.5,0.0))
# plt.show()
