from scipy.spatial import ConvexHull
from utils import *
from select_file import *

pr = 0.0

trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

fig, ax = plt.subplots()
fig1, ax1 = plt.subplots()

i=0
for trust in trusts:
    if final_time == 0:
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    else:
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

    success_rate = np.load(f'{hexbin_folder}/successrate_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)

    coord_x = np.load(f'{com_coord_folder}/run0/coord_x.npy', allow_pickle=True).item()
    coord_y = np.load(f'{com_coord_folder}/run0/coord_y.npy', allow_pickle=True).item()

    x = coord_x[0]
    y = coord_y[0]

    hb = ax1.hexbin(x, y, gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='viridis')

    # Create a mask for bins where the x-coordinate is less than a threshold
    x_threshold = final_x
    bin_coords = hb.get_offsets()  
    x_edges, y_edges = bin_coords.T
    mask_below_threshold = x_edges > x_threshold
    success_rate[mask_below_threshold] = 0

    hb.set_array(success_rate)
    # hb.set_clim(np.min(success_rate), np.max(success_rate))  

    plt.close(fig1)

    hull, points = get_convexhull(hb, pr)

    s=0
    for simplex in hull.simplices:
        xs = points[simplex, 0]
        ys = points[simplex, 1]

        if s==0: ax.plot(xs, ys, c=colors[i], lw=1, label=trust)
        else: ax.plot(xs, ys, c=colors[i], lw=1)

        s+=1
    i+=1

ax.legend(title=r'Trust parameter $\beta$', ncol=2)

ax.set_title(rf'Contour: $P \geq {pr}$, Fixed final time')

ax.axhline(0, c='r', lw=1, ls='--', alpha=1.0)
ax.add_patch( plt.Circle((0,0), spawn_radius, fill=False, color='r', ls='--', alpha=1.0, lw=1) )

arrow_length = 5
hl = 1.5 
dx = arrow_length * np.cos(mu)
dy = arrow_length * np.sin(mu)
ax.arrow(0, 0, dx, dy, head_width=1.5, head_length=hl, width=0.4, fc='k', ec='k', zorder=2)

if sigma > 0:
    import matplotlib.patches as patches
    up = np.degrees(mu) - np.degrees(sigma) / 2 
    dwn = np.degrees(mu) + np.degrees(sigma) / 2 
    wedge = patches.Wedge((0, 0), arrow_length+hl, up, dwn, color='k', alpha=0.3, zorder=1)
    ax.add_patch(wedge)

ax.axis('equal')

# plt.gca().invert_xaxis()

show_and_check_ipython()
