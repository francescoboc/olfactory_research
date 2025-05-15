from utils import *
from select_file import *

filename = rf'performance_maps/map_rho_angle{mu:.2f}_std{sigma:.2f}_beta{trust}.png'
savefig = True

dicts_folder = f'../beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dict
rate_betas = np.load(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

success_rate = rate_betas[trust]

plt.figure()

hb = plt.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='plasma')

# create a mask for bins where the x-coordinate is less than a threshold
x_threshold = final_x
bin_coords = hb.get_offsets()  
x_edges, y_edges = bin_coords.T
mask_below_threshold = x_edges > x_threshold
success_rate[mask_below_threshold] = 0

hb.set_array(success_rate)

# hb.set_clim(np.min(success_rate), np.max(success_rate))  
hb.set_clim(0,1)  

# set background (non-explored parts of space) same color as min of colorbar
cb = plt.colorbar(hb, label=r'Average succcess rate $\rho$')
plt.gca().set_facecolor(cb.cmap(0))

plt.title(rf'$\beta={trust}$')

# # calculate the distance to each hexbin center and find the closest bin to the source
# try:
#     x, y = l_x, h_y
#     bin_coords = hb.get_offsets()  
#     distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
#     bin_idx = np.argmin(distances)
#     success_rate_source = success_rate[bin_idx]
# except: pass

# try:
#     x1, y1 = l_x1, h_y1
#     distances = np.sqrt((bin_coords[:, 0] - x1)**2 + (bin_coords[:, 1] - y1)**2)
#     bin_idx1 = np.argmin(distances)
#     success_rate_source1 = success_rate[bin_idx1]
# except: pass

# try:
#     plt.plot(x, y, 'or', zorder=10)
#     plt.text(bin_coords[bin_idx,0], bin_coords[bin_idx,1]+2, f'{success_rate_source:.1f}', ha='center', va='bottom', c='r')
# except: pass

# try:
#     plt.plot(x1, y1, 'sr')
#     plt.text(bin_coords[bin_idx1,0], bin_coords[bin_idx1,1]+2, f'{success_rate_source1:.1f}', ha='center', va='bottom', c='r')
# except: pass

## ADD FPT CONTOURS ##

# load the data dict
fpt_betas = np.load(f'{dicts_folder}/fpt_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

avg_fpt = fpt_betas[trust]

normalised = True

dummy_fig, dummy_ax = plt.subplots()
hb1 = dummy_ax.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='cividis')

# Create a mask for bins where the x-coordinate is less than x_threshold
x_threshold = final_x
bin_coords = hb.get_offsets()  
x_edges, y_edges = bin_coords.T
mask_below_threshold = x_edges > x_threshold
avg_fpt = np.ma.masked_where(mask_below_threshold, avg_fpt)

# noralize the fpts by the straight line path
for i in range(len(bin_coords)):
    x_s, y_s = bin_coords[i][0], bin_coords[i][1]
    straight_line_time = (np.sqrt(x_s**2 + y_s**2)-spawn_radius)/speed
    # straight_line_time = (np.sqrt(x_s**2 + y_s**2))/speed
    if normalised:
        avg_fpt[i] /= straight_line_time

    # mask the bins that are too close to the starting point
    if np.sqrt(x_s**2 + y_s**2) < spawn_radius*2.5:
        avg_fpt[i] = np.ma.masked

    # # if x_s < spawn_radius*2.0:
    # if x_s > 15:
    #     avg_fpt[i] = np.ma.masked

# avg_fpt = np.ma.masked_where( avg_fpt < 1, avg_fpt)
# avg_fpt[np.where( (avg_fpt.data < 1) & ~avg_fpt.mask )]=1

min_fpt, max_fpt = np.min(avg_fpt), np.max(avg_fpt) 

hb1.set_array(avg_fpt)
hb1.set_clim(1.0, max_fpt) 
cbar = plt.colorbar(hb1, ax = dummy_ax)

plt.close(dummy_fig)

# taus_list = np.linspace(min_fpt, max_fpt, 4)[1:]
taus_list = cbar.get_ticks()[1:-1]
# taus_list = [int(v) for v in taus_list]

# manually overwrite the taus_list with a custom one
if trust == 0.1:
    taus_list = [20, 60, 120]
elif trust == 0.7:
        taus_list = [1.2, 1.4, 1.6]
elif trust == 0.9:
        taus_list = [1.1, 1.2, 1.4]

for i, tr in enumerate(taus_list):
    lab = rf'$\tau\leq{taus_list[i]:.1f}$'
    # lab = rf'$\tau\leq{taus_list[i]}$'

    if mu != 0 and trust > 0.5:
        hulls = get_hull(hb1, tr, alpha=0.01, convex=False, prob=False)
    else:
        hulls = get_hull(hb1, tr, convex=True, prob=False)

    # Skip if no hull is returned
    if hulls is None:
        continue  

    for h, coords in enumerate(hulls):
        if coords is None or len(coords) == 0:
            continue
        if h == 0:
            plt.plot(coords[:, 0], coords[:, 1], c=colors[i], lw=1, label=lab)
        else:
            plt.plot(coords[:, 0], coords[:, 1], c=colors[i], lw=1)

# plt.legend(title=r'FPT')
plt.legend(fontsize=15)

if mu == 0 and sigma == 0:
    l_y = [0,10,16,20]
else:
    l_y = [0]

l_x = [75 for y in l_y]

for i in range(len(l_x)):
    plt.plot(l_x[i], l_y[i], color='k', marker=markers[i])

add_decorations(30)

# # Set y-ticks to match the number of x-ticks
# ax = plt.gca()
# x_ticks = ax.get_xticks()
# ax.set_yticks(np.linspace(ax.get_ylim()[0], ax.get_ylim()[1], len(x_ticks)))

# empty ticks
ax = plt.gca()
ax.set_yticks([])
ax.set_xticks([])

if savefig: plt.gcf().savefig(save_directory + filename, dpi=300)

show_and_check_ipython()
