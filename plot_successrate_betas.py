from utils import *
from select_file import *

if final_time == 0:
    com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust0.1'
    dicts_folder = f'beta_dicts/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'
else:
    com_coord_folder = f'com_coordinates/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_t{final_time}/trust0.1'
    dicts_folder = f'beta_dicts/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_t{final_time}'

# load the data dict
rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

pr = 0.0

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

add_decorations()

show_and_check_ipython()
