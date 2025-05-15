from utils import *
from select_file import *

dicts_folder = f'../beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dict
# if center_of_mass:
    # rate_betas = np.load(f'{dicts_folder}/com_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
# else:
rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

success_rate = rate_betas[trust]

plt.figure()

hb = plt.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='cividis')

# create a mask for bins where the x-coordinate is less than a threshold
x_threshold = final_x
bin_coords = hb.get_offsets()  
x_edges, y_edges = bin_coords.T
mask_below_threshold = x_edges > x_threshold
success_rate[mask_below_threshold] = 0

hb.set_array(success_rate)
hb.set_clim(np.min(success_rate), np.max(success_rate))  

# calculate the distance to each hexbin center and find the closest bin to the source
try:
    x, y = l_x, h_y
    bin_coords = hb.get_offsets()  
    distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
    bin_idx = np.argmin(distances)
    success_rate_source = success_rate[bin_idx]
except: pass

try:
    x1, y1 = l_x1, h_y1
    distances = np.sqrt((bin_coords[:, 0] - x1)**2 + (bin_coords[:, 1] - y1)**2)
    bin_idx1 = np.argmin(distances)
    success_rate_source1 = success_rate[bin_idx1]
except: pass

cb = plt.colorbar(hb, label=r'Average succcess rate $\rho$')

i=0
for pr in rates_list:
    hull, points = get_concave_hull(hb, pr)

    lab = rf'$\rho\geq{rates_list[i]}$'

    # Check if 'hull' has 'geoms' attribute (MultiPolygon case)
    if hasattr(hull, "geoms"):  
        hulls = hull.geoms  # Extract individual polygons
    else:  
        hulls = [hull]  # Treat as a single polygon

    # Iterate over all hulls (handles both single and multi-polygon cases)
    h=0
    for poly in hulls:
        if hasattr(poly, "exterior"):  # Ensure it has an exterior boundary
            exterior_coords = np.array(poly.exterior.coords)  # Get boundary points
            if h==0: plt.plot(exterior_coords[:, 0], exterior_coords[:, 1], c=colors[i], lw=1, label=lab)
            else: plt.plot(exterior_coords[:, 0], exterior_coords[:, 1], c=colors[i], lw=1)

            h+=1

    # # calculate exploration cone width
    # if pr == rate_selected:
    #     min_cone, max_cone = min(points[:,1]), max(points[:,1])
    #     cone_width = max_cone - min_cone
    #     cone_color = i

    # s=0
    # for simplex in hull.simplices:
    #     xs = points[simplex, 0]
    #     ys = points[simplex, 1]

    #     if s==0: 
    #         if rates_list[i] != 1:
    #             plt.plot(xs, ys, c=colors[i], lw=1, label=rf'$\rho\geq{rates_list[i]}$')
    #         else:
    #             plt.plot(xs, ys, c=colors[i], lw=1, label=rf'$\rho={rates_list[i]}$')
    #     else: plt.plot(xs, ys, c=colors[i], lw=1)
    #     s+=1
    i+=1
plt.legend(title='Contour')

# set background (non-explored parts of space) same color as min of colorbar
plt.gca().set_facecolor(cb.cmap(0))

try:
    plt.plot(x, y, 'or', zorder=10)
    plt.text(bin_coords[bin_idx,0], bin_coords[bin_idx,1]+2, f'{success_rate_source:.1f}', ha='center', va='bottom', c='r')
except: pass

try:
    plt.plot(x1, y1, 'sr')
    plt.text(bin_coords[bin_idx1,0], bin_coords[bin_idx1,1]+2, f'{success_rate_source1:.1f}', ha='center', va='bottom', c='r')
except: pass

plt.title(rf'$\beta={trust}$')

add_decorations()

show_and_check_ipython()
