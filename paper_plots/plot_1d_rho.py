from utils import *
from select_file import *

fix_L = 60

# filename = rf'performance_maps/map_rho_angle{mu:.2f}_std{sigma:.2f}_beta{trust}.png'
# savefig = True

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

plt.axvline(fix_L, c='k', ls='--')

# hb.set_clim(np.min(success_rate), np.max(success_rate))  
hb.set_clim(0,1)  

# set background (non-explored parts of space) same color as min of colorbar
cb = plt.colorbar(hb, label=r'Average succcess rate $\rho$')
plt.gca().set_facecolor(cb.cmap(0))

plt.title(rf'$\beta={trust}$')

add_decorations(30)

# # empty ticks
# ax = plt.gca()
# ax.set_yticks([])
# ax.set_xticks([])

# if savefig: plt.gcf().savefig(save_directory + filename, dpi=300)

limits = plt.ylim()

bins_L = np.where(np.abs(x_edges - 60)<1e-5)
rho_H = success_rate[bins_L]
Hs = y_edges[bins_L]

plt.figure()
plt.plot(Hs, rho_H)

plt.xlim(limits)
plt.title(rf'$\beta={trust}, L={fix_L}$')
plt.xlabel('Shift H')
plt.ylabel(r'Average success rate $\rho$')


show_and_check_ipython()
