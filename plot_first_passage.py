from utils import *
from select_file import *

dicts_folder = f'beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

# load the data dict
fpt_betas = np.load(f'{dicts_folder}/fpt_betas_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True).item()

avg_fpt = fpt_betas[trust]

plt.figure()

hb = plt.hexbin([0], [0], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='cividis')

# Create a mask for bins where the x-coordinate is less than x_threshold
x_threshold = final_x
bin_coords = hb.get_offsets()  
x_edges, y_edges = bin_coords.T
mask_below_threshold = x_edges > x_threshold
avg_fpt = np.ma.masked_where(mask_below_threshold, avg_fpt)

# noralize the fpts by the straight line path
for i in range(len(bin_coords)):
    x_s, y_s = bin_coords[i][0], bin_coords[i][1]
    straight_line_time = np.sqrt((x_s-spawn_radius)**2 + y_s**2)/speed
    avg_fpt[i] /= straight_line_time

# Update the hexbin plot to show first passage times
hb.set_array(avg_fpt)

# Calculate the distance to each hexbin center and find the closest bin to the source
x, y = l_x, h_y
bin_coords = hb.get_offsets()
distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
bin_idx = np.argmin(distances)
fpt_source = avg_fpt[bin_idx]

try:
    x1, y1 = l_x1, h_y1
    distances = np.sqrt((bin_coords[:, 0] - x1)**2 + (bin_coords[:, 1] - y1)**2)
    bin_idx1 = np.argmin(distances)
    fpt_source1 = avg_fpt[bin_idx1]
except: pass

plt.colorbar(hb, label='Normalised average first passage time')

plt.plot(x, y, 'or')
plt.text(bin_coords[bin_idx,0], bin_coords[bin_idx,1]+2, f'{fpt_source:.2f}', ha='center', va='bottom', c='r')

try:
    plt.plot(x1, y1, 'sr')
    plt.text(bin_coords[bin_idx1,0], bin_coords[bin_idx1,1]+2, f'{fpt_source1:.2f}', ha='center', va='bottom', c='r')
except: pass

# Ensure the color limits are set according to first passage time
plt.clim(np.min(avg_fpt), np.max(avg_fpt)) 

plt.title(rf'$\beta={trust}$')
plt.axhline(0, c='r', lw=1, ls='--', alpha=1.0)
plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=False, color='r', ls='--', alpha=1.0) )

arrow_length = 5
hl = 1.5 
dx = arrow_length * np.cos(mu)
dy = arrow_length * np.sin(mu)
plt.arrow(0, 0, dx, dy, head_width=1.5, head_length=hl, width=0.4, fc='w', ec='w', zorder=2)

if sigma > 0:
    import matplotlib.patches as patches
    up = np.degrees(mu) - np.degrees(sigma) / 2 
    dwn = np.degrees(mu) + np.degrees(sigma) / 2 
    wedge = patches.Wedge((0, 0), arrow_length+hl, up, dwn, color='w', alpha=0.3, zorder=1)
    plt.gca().add_patch(wedge)

plt.axis('scaled')

plt.xlim(*bound_x)
plt.ylim(*bound_y)

# plt.gca().invert_xaxis()
# plt.savefig(f'beta{trust}.png')

show_and_check_ipython()
