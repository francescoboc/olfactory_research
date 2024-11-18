from scipy.spatial import ConvexHull
from utils import *
from tqdm import tqdm
from select_file import *


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

prob_list = [1.0]

if final_time == 0:
    coord_folder = f'coordinates/hexbin/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    os.makedirs(hexbin_folder, exist_ok=True)
else:
    coord_folder = f'coordinates/hexbin/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
    hexbin_folder = f'hexbins/hexbin/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
    os.makedirs(hexbin_folder, exist_ok=True)

try:
    if center_of_mass:
        success_rate = np.load(f'{hexbin_folder}/com_successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)
    else:
        success_rate = np.load(f'{hexbin_folder}/successrate_gridsize{gridsize}_margx{margin_x}_margy{margin_y}.npy', allow_pickle=True)

    print('Hexbin data loaded!')

except:
    print('No hexbin data found!')

run_n = 0
coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()
x = coord_x[0]
y = coord_y[0]

plt.figure('Success rate')
hb = plt.hexbin(x, y, gridsize=gridsize, extent=[*bound_x, *bound_y])

# Create a mask for bins where the x-coordinate is less than a threshold
x_threshold = final_x
bin_coords = hb.get_offsets()  
x_edges, y_edges = bin_coords.T
mask_below_threshold = x_edges > x_threshold
success_rate[mask_below_threshold] = 0

hb.set_array(success_rate)
hb.set_clim(np.min(success_rate), np.max(success_rate))  

cb = plt.colorbar(hb, label='Average succcess rate')

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

        s+=1
    i+=1

# if not center_of_mass:
#     # add axploration area vlines
#     bin_values = hb.get_array()
#     bin_centers = hb.get_offsets()

#     # Find indices of non-zero bins (where the count is > 0)
#     nonzero_bins = bin_values > 0

#     # Filter x_coords to only include non-zero bins
#     nonzero_xs = bin_centers[nonzero_bins, 0]
#     nonzero_ys = bin_centers[nonzero_bins, 1]

#     min_nonzero_x = min(nonzero_xs)

#     max_nonzero_y = max(nonzero_ys)
#     min_nonzero_y = min(nonzero_ys)

# else:
#     plt.axhline(max_y, c='w', lw=1, alpha=0.7)
#     plt.axhline(min_y, c='w', lw=1, alpha=0.7)

#     exploration_area = max_y - min_y
#     # plt.text(source_coordinates[0], max_y, f'{exploration_area:.1f}', ha='left', va='bottom', c='w', alpha=0.7)
#     # plt.text(spawn_center[0], spawn_center[1]+spawn_radius, f'{spawn_radius*2:.1f}', ha='left', va='bottom', c='w', alpha=0.7)

#     # calculate L(t)
#     std_x_avg = []
#     for entry in std_x:
#         std_x_avg.append(np.mean(entry))
#     std_y_avg = []
#     for entry in std_y:
#         std_y_avg.append(np.mean(entry))

#     com_x_avg = []
#     com_x_std = []
#     for entry in mean_x:
#         com_x_avg.append(np.mean(entry))
#         com_x_std.append(np.std(entry))
#     com_y_avg = []
#     com_y_std = []
#     for entry in mean_y:
#         com_y_avg.append(np.mean(entry))
#         com_y_std.append(np.std(entry))

#     total_std_y = np.array(com_y_std) + 2*np.array(std_y_avg)

#     shaded_errorbar(com_x_avg, com_y_avg, yerr=total_std_y, lab='std', m='', c='w', alpha=0.3)

#     # shaded_errorbar(com_x_avg, com_y_avg, yerr=spawn_radius, lab='std', m='', c='w', alpha=0.3)

plt.legend()

# set background (non-explored parts of space) same color as min of colorbar
plt.gca().set_facecolor(cb.cmap(0))

# Calculate the distance to each hexbin center and find the closest bin to the source
x, y = l_x, h_y
bin_coords = hb.get_offsets()  
distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
bin_idx = np.argmin(distances)
success_rate_source = success_rate[bin_idx]
plt.plot(x, y, '+r')
plt.text(bin_coords[bin_idx,0], bin_coords[bin_idx,1]+1, f'{success_rate_source:.1f}', ha='center', va='bottom', c='r')

plt.title(rf'$\beta={trust}$')
plt.axhline(0, c='r', lw=1, ls='--', alpha=1.0)
plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=False, color='r', ls='--', alpha=1.0, lw=1) )

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

plt.xlim(*bound_x)
plt.ylim(*bound_y)

show_and_check_ipython()
