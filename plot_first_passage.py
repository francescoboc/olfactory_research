from utils import *
from select_file import *

dicts_folder = f'beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dict
fpt_betas = np.load(f'{dicts_folder}/fpt_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

avg_fpt = fpt_betas[trust]

normalised = 1

plt.figure()

hb = plt.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='plasma')

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
    # if np.sqrt(x_s**2 + y_s**2) < spawn_radius*3.0:
    if x_s < spawn_radius*2.0:
        avg_fpt[i] = np.ma.masked

avg_fpt = np.ma.masked_where( avg_fpt < 1, avg_fpt)
# avg_fpt[np.where( (avg_fpt.data < 1) & ~avg_fpt.mask )]=1

# TODO gli esagoni troppo vicino alla sorgente soffrono di un problema di normalizzazione:
#     lo straight-line time non è preciso li perchè non so da dove calcolarlo...
#     dal centro dello spawn? dal centro ma sottraendo il raggio?

# # TODO non si capisce bene se plottiamo l'inverse time
# avg_fpt[np.where( (avg_fpt.data <= 1) & ~avg_fpt.mask )]=1
# avg_fpt = 1/avg_fpt

# avg_fpt = np.log(avg_fpt)

# Update the hexbin plot to show first passage times
hb.set_array(avg_fpt)

# Calculate the distance to each hexbin center and find the closest bin to the source
try:
    x, y = l_x, h_y
    bin_coords = hb.get_offsets()
    distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
    bin_idx = np.argmin(distances)
    fpt_source = avg_fpt[bin_idx]
except: pass

try:
    x1, y1 = l_x1, h_y1
    distances = np.sqrt((bin_coords[:, 0] - x1)**2 + (bin_coords[:, 1] - y1)**2)
    bin_idx1 = np.argmin(distances)
    fpt_source1 = avg_fpt[bin_idx1]
except: pass

# plt.clim(np.min(avg_fpt), np.max(avg_fpt)) 
plt.clim(1.0, np.max(avg_fpt)) 

if normalised:
    cbar = plt.colorbar(hb, label=r'Average normalised first passage time $\tau$')

else:
    cbar = plt.colorbar(hb, label=r'Average first passage time $\tau$')

try:
    plt.plot(x, y, 'or')
    plt.text(bin_coords[bin_idx,0], bin_coords[bin_idx,1]+2, f'{fpt_source:.2f}', ha='center', va='bottom', c='r')
except: pass

try:
    plt.plot(x1, y1, 'sr')
    plt.text(bin_coords[bin_idx1,0], bin_coords[bin_idx1,1]+2, f'{fpt_source1:.2f}', ha='center', va='bottom', c='r')
except: pass

# current_ticks = cbar.get_ticks()  # Get existing ticks
# print(current_ticks)
# current_ticks = np.delete(current_ticks, 0)
# current_ticks = np.delete(current_ticks, -1)
# updated_ticks = np.append(current_ticks, 1.0) 
# print(updated_ticks)
# cbar.set_ticks(updated_ticks)  # Set the updated ticks

plt.title(rf'$\beta={trust}$')

add_decorations()

show_and_check_ipython()
