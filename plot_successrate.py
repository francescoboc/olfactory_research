from utils import *
from select_file import *

com_coord_folder = f'com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'

dicts_folder = f'beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dict
if center_of_mass:
    rate_betas = np.load(f'{dicts_folder}/com_rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()
else:
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

cb = plt.colorbar(hb, label='Average succcess rate')

i=0
for pr in rates_list:
    hull, points = get_convexhull(hb, pr)

    # calculate exploration cone width
    if pr == rate_selected:
        min_cone, max_cone = min(points[:,1]), max(points[:,1])
        cone_width = max_cone - min_cone
        cone_color = i

    s=0
    for simplex in hull.simplices:
        xs = points[simplex, 0]
        ys = points[simplex, 1]

        if s==0: plt.plot(xs, ys, c=colors[i], lw=1, label=rf'$\rho\geq{rates_list[i]}$')
        else: plt.plot(xs, ys, c=colors[i], lw=1)
        s+=1
    i+=1
plt.legend(title='Contour')

# plt.text(final_x+2, max_cone, f'Width: {cone_width:.1f}', ha='left', va='bottom', c=colors[cone_color])
# plt.text(-spawn_radius, spawn_radius, f'{spawn_radius*2:.1f}', ha='right', va='bottom', c=colors[cone_color])

# if center_of_mass:

#     std_x, std_y = [], []
#     mean_x, mean_y = [], []

#     for run_n in range(n_runs):

#         com_x = np.load(f'{com_coord_folder}/run{run_n}/com_x.npy')
#         com_y = np.load(f'{com_coord_folder}/run{run_n}/com_y.npy')
#         com_x_std = np.load(f'{com_coord_folder}/run{run_n}/com_x_std.npy')
#         com_y_std = np.load(f'{com_coord_folder}/run{run_n}/com_y_std.npy')

#         n_timesteps = len(com_x) 

#         for t in range(n_timesteps):

#             # calculate l(t)
#             try:
#                 std_x[t].append(com_x_std[t])
#                 std_y[t].append(com_y_std[t])
#             except:
#                 std_x.append([com_x_std[t]])
#                 std_y.append([com_y_std[t]])

#             try:
#                 mean_x[t].append(com_x[t])
#                 mean_y[t].append(com_y[t])
#             except:
#                 mean_x.append([com_x[t]])
#                 mean_y.append([com_y[t]])

#     # calculate L(t)
#     total_std_x_avg = []
#     for entry in std_x:
#         total_std_x_avg.append(np.mean(entry))
#     total_std_y_avg = []
#     for entry in std_y:
#         total_std_y_avg.append(np.mean(entry))

#     total_com_x_avg = []
#     total_com_x_std = []
#     for entry in mean_x:
#         total_com_x_avg.append(np.mean(entry))
#         total_com_x_std.append(np.std(entry))
#     total_com_y_avg = []
#     total_com_y_std = []
#     for entry in mean_y:
#         total_com_y_avg.append(np.mean(entry))
#         total_com_y_std.append(np.std(entry))

#     TOT_STD_Y = np.array(total_com_y_std) + np.array(total_std_y_avg)*2

#     # cut anything that is above final_x
#     if final_time == 0:
#         cut = min(np.flatnonzero(np.array(total_com_x_avg)>final_x))
#         total_com_x_avg = total_com_x_avg[:cut]
#         total_com_y_avg = total_com_y_avg[:cut]
#         TOT_STD_Y = TOT_STD_Y[:cut]

#     shaded_errorbar(total_com_x_avg, total_com_y_avg, yerr=TOT_STD_Y, lab='std', m='', c='w', alpha=0.3)

#     cone_width_com = 2*max(TOT_STD_Y)

#     plt.text(final_x+2, -cone_width_com/2, f'Width: {cone_width_com:.2f}', ha='left', va='top', c='w', alpha=0.5)

#     # plt.plot(com_x, com_y, '-k')


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
plt.axhline(0, c='r', lw=1, ls='--', alpha=0.7)
plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=False, color='r', ls='--', alpha=0.7, lw=1) )

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
