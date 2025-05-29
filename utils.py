import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
import platform
import alphashape

# detect if running on cluster or laptop
if platform.node() == 'swift': on_cluster = False
elif platform.node() == 'e4-seminara.csita.unige.local': on_cluster = True

# extract matplotlib default colors and markers
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
markers = list(plt.Line2D.markers.keys())[2:]
# markers = ['o', 's', 'd', 'v', '^', '<', '>']

# update matplotlib parameters globally
plt.rcParams['lines.markerfacecolor'] = 'none'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['errorbar.capsize'] = 2
plt.rcParams['legend.fancybox'] = False
# plt.rcParams['figure.constrained_layout.use'] = True

# plt.rcParams['legend.fontsize'] = 14 
# plt.rcParams['legend.title_fontsize'] = 'small'

# plt.rcParams['legend.handlelength'] = 1
# plt.rcParams['legend.handletextpad'] = 0.5

# plt.rc('text', usetex=True)
# plt.rcParams['font.size'] = 17 

# plt.rc('text.latex', preamble=r'\usepackage{bm}')
# plt.rc('text.latex', preamble=r'\usepackage{amsmath}')
plt.rc('text.latex', preamble=r'\usepackage{bm} \usepackage{amsmath}')
plt.rc('savefig', format='pdf')
plt.rc('savefig', directory='/mnt/c/Users/franc/Dropbox/papero_1_olfactory/img')

# parameters for plotting the cloud
margin = 15
colormap='GnBu'

def print_attributes(dataframe):
    for key in dataframe.attrs.keys():
        print(f'{key} = {dataframe.attrs[key]}')

def show_and_check_ipython():
    try: __IPYTHON__; plt.ion()
    except NameError: pass
    plt.show()

def shaded_errorbar(x, y, yerr, lab=None, c=None, ls='-', m='o', alpha=0.1):
    below = np.array(y)-np.array(yerr)
    above = np.array(y)+np.array(yerr)
    if c is not None:
        plt.plot(x, y, marker=m, color=c, ls=ls, label=lab)
        plt.fill_between(x, below, above, color=c, alpha=alpha)
    else:
        plt.plot(x, y, marker=m, ls=ls, label=lab)
        plt.fill_between(x, below, above, alpha=alpha)

# escape sequences to print colors in terminal
class tc:
    purple = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    ul = '\033[4m'
    end = '\033[0m'

def norm(vector):
    return (vector[0]**2 + vector[1]**2)**0.5

def normalised(vector):
    norm = (vector[0]**2 + vector[1]**2)**0.5
    if norm != 0: return vector/norm
    else: return vector

def get_concave_hull(hb, pr, alpha=0.5, max_alpha=5.0, step=0.5):
    probs = hb.get_array()
    bin_centers = hb.get_offsets()

    # find indices of bins above threshold
    if pr==1: selected_bins = probs >= pr
    else: selected_bins = probs > pr

    # filter x_coords to only include non-zero bins
    selected_xs = bin_centers[selected_bins, 0]
    selected_ys = bin_centers[selected_bins, 1]

    # use ConvexHull to find the outermost boundary around the non-zero bins
    points = np.column_stack([selected_xs, selected_ys])

    # hull = ConvexHull(points)

    if len(points) < 3:
        return None, points  # Not enough points to form a shape

    # Try to find a valid concave hull by adjusting alpha
    hull = alphashape.alphashape(points, alpha)
    
    while (hull is None or hull.is_empty) and alpha <= max_alpha:
        alpha += step
        hull = alphashape.alphashape(points, alpha)
    
    # If all attempts fail, return convex hull
    if hull is None or hull.is_empty:
        hull = alphashape.alphashape(points, alpha=None)  # Convex hull fallback

    print(alpha)
    return hull, points

def get_closest_bin(bin_coords, l_x, h_y):
    # Calculate the distance to each hexbin center and find the closest bin to the source
    x, y = l_x, h_y
    distances = np.sqrt((bin_coords[:, 0] - x)**2 + (bin_coords[:, 1] - y)**2)
    bin_idx = np.argmin(distances)
    return bin_idx


def get_straight_line_times(bin_coords, spawn_radius, speed):
    straight_line_times = []
    for i in range(len(bin_coords)):
        x_s, y_s = bin_coords[i][0], bin_coords[i][1]
        straight_line_times.append(np.sqrt((x_s-spawn_radius)**2 + y_s**2)/speed)
    return straight_line_times

def add_decorations():
    from select_file import spawn_radius, mu, sigma, bound_x, bound_y
    plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=True, color='w', ls='', alpha=1, lw=0, zorder=2) )
    plt.axhline(0, c='r', lw=1, ls='--', alpha=0.7, zorder=3)
    plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=False, color='r', ls='--', alpha=0.7, lw=1, zorder=3) )

    arrow_length = 5
    hl = 3 
    hw = 3
    w = 0.6
    dx = arrow_length * np.cos(mu)
    dy = arrow_length * np.sin(mu)
    plt.arrow(0, 0, dx, dy, head_width=hw, head_length=hl, width=w, fc='k', ec='k', zorder=4)

    if sigma > 0:
        import matplotlib.patches as patches
        up = np.degrees(mu) - np.degrees(sigma) / 2 
        dwn = np.degrees(mu) + np.degrees(sigma) / 2 
        wedge = patches.Wedge((0, 0), arrow_length+hl, up, dwn, color='k', alpha=0.3, zorder=3)
        plt.gca().add_patch(wedge)

    plt.axis('scaled')
    plt.xlim(*bound_x)
    plt.ylim(*bound_y)

def truncate_and_stack(array_list):
    # Find the length of the shortest array
    min_length = min(len(arr) for arr in array_list)
    
    # Truncate all arrays to the shortest length and stack
    return np.stack([arr[:min_length] for arr in array_list])
