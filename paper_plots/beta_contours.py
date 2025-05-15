from utils import *
from select_file import *

if final_time == 0:
    dicts_folder = f'../beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'
    mode = 'fixedtime'
else:
    dicts_folder = f'../beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_t{final_time}'
    mode = 'fixedposition'

filename = rf'betacontour_angle{mu:.2f}_std{sigma:.2f}_{mode}.pdf'
savefig = True

# load the data dict
rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

pr = rate_threshold

fig, ax = plt.subplots()
fig1, ax1 = plt.subplots()

i=0
for trust in trusts:
    success_rate = rate_betas[trust]

    hb = ax1.hexbin([0], [0], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='viridis')

    # Create a mask for bins where the x-coordinate is less than a threshold
    x_threshold = final_x
    bin_coords = hb.get_offsets()  
    x_edges, y_edges = bin_coords.T
    mask_below_threshold = x_edges > x_threshold
    success_rate[mask_below_threshold] = 0

    hb.set_array(success_rate)

    plt.close(fig1)

    hull, points = get_concave_hull(hb, pr)

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
            if h==0: ax.plot(exterior_coords[:, 0], exterior_coords[:, 1], c=colors[i], lw=1, label=trust)
            else: ax.plot(exterior_coords[:, 0], exterior_coords[:, 1], c=colors[i], lw=1)

    i+=1

ax.legend(title=r'Trust parameter $\beta$', ncol=2)

if final_time == 0:
    title = fr'Contour: $\rho \geq {pr}$, Fixed final position'
else:
    title = fr'Contour: $\rho \geq {pr}$, Fixed final time'

ax.set_title(title)

add_decorations(reduce_bounds = 40)

show_and_check_ipython()

if savefig: fig.savefig(save_directory + filename)
