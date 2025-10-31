import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
import platform
import alphashape
from tqdm import tqdm as base_tqdm

square_figsize = (6,4.8)
square_figsize_reduced = (6,4.28)

# detect if running on cluster or laptop
if platform.node() == 'swift': on_cluster = False
elif platform.node() == 'e4-seminara.csita.unige.local': on_cluster = True

# extract matplotlib default colors and markers
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
# markers = list(plt.Line2D.markers.keys())[2:]
markers = ['o', 'v', 's', 'd', '^', '<', '>']

# update matplotlib parameters globally
plt.rcParams['lines.markerfacecolor'] = 'none'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['errorbar.capsize'] = 2
plt.rcParams['legend.fancybox'] = False
plt.rcParams['figure.constrained_layout.use'] = True

plt.rcParams['legend.fontsize'] = 15 
plt.rcParams['legend.title_fontsize'] = 12

plt.rcParams['legend.handlelength'] = 1.25
plt.rcParams['legend.handletextpad'] = 0.5

plt.rc('text', usetex=True)
plt.rcParams['font.size'] = 16

save_directory = '/mnt/c/Users/franc/Dropbox/papero_1_olfactory/img/'

# plt.rc('text.latex', preamble=r'\usepackage{bm}')
# plt.rc('text.latex', preamble=r'\usepackage{amsmath}')
plt.rc('text.latex', preamble=r'\usepackage{bm} \usepackage{amsmath}')
plt.rc('savefig', format='pdf')
plt.rc('savefig', directory='/mnt/c/Users/franc/Dropbox/papero_1_olfactory/img')

# parameters for plotting the cloud
margin = 10
colormap='GnBu'

def print_attributes(dataframe):
    for key in dataframe.attrs.keys():
        print(f'{key} = {dataframe.attrs[key]}')

def show_and_check_ipython():
    try: __IPYTHON__; plt.ion()
    except NameError: pass
    plt.show()

def shaded_errorbar(x, y, yerr=None, label=None, color=None, ls='-', marker='o', alpha=0.1, ax=None):
    if ax is None: ax=plt.gca()
    if yerr is not None:
        if is_1d(yerr):
            below = np.array(y)-np.array(yerr)
            above = np.array(y)+np.array(yerr)
        else:
            below = np.array(y)-np.array(yerr[0])
            above = np.array(y)+np.array(yerr[1])
    if color is not None:
        ax.plot(x, y, marker=marker, color=color, ls=ls, label=label)
        if yerr is not None:
            ax.fill_between(x, below, above, color=color, alpha=alpha)
    else:
        ax.plot(x, y, marker=marker, ls=ls, label=label)
        if yerr is not None:
            ax.fill_between(x, below, above, alpha=alpha)

def is_1d(data):
    """Returns True if `data` is a 1D list, tuple, or NumPy array, otherwise False."""

    # If it's a NumPy array, check its number of dimensions directly
    if isinstance(data, np.ndarray):
        return data.ndim == 1  # A 1D array has only one axis

    # If it's a list or tuple, check if it contains only numbers (or non-list elements)
    if isinstance(data, (list, tuple)):
        for item in data:
            if isinstance(item, (list, tuple, np.ndarray)):  # If we find a list/tuple/array inside, it's 2D
                return False
        return True  # If we never found a list inside, it's 1D

    return False  # If it's something else, we assume it's not 1D

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

def get_hull(hb, pr, alpha=0.5, max_alpha=5.0, step=0.5, convex=True, prob=True):
    probs = hb.get_array()
    bin_centers = hb.get_offsets()

    # convert masked fpts in infinity
    if not prob: probs = probs.filled(np.inf)

    # find indices of bins above threshold
    if prob:
        if pr==1: selected_bins = probs >= pr
        else: selected_bins = probs > pr

    # find indices of bins below threshold
    else:
        selected_bins = probs <= pr

    # filter x_coords to only include non-zero bins
    selected_xs = bin_centers[selected_bins, 0]
    selected_ys = bin_centers[selected_bins, 1]

    points = np.column_stack([selected_xs, selected_ys])

    if len(points) < 3:
        return None # Not enough points to form a shape

    if convex:
        chull = ConvexHull(points)
        hull_points = points[chull.vertices]
        # Chiudi il contorno se necessario
        if not np.allclose(hull_points[0], hull_points[-1]):
            hull_points = np.vstack([hull_points, hull_points[0]])
        return [hull_points]

    else:
        hull = alphashape.alphashape(points, alpha)
        while (hull is None or hull.is_empty) and alpha <= max_alpha:
            alpha += step
            hull = alphashape.alphashape(points, alpha)
        if hull is None or hull.is_empty:
            return None
        # Estrai i punti dal contorno
        if hasattr(hull, "geoms"):  # MultiPolygon
            hull_points = []
            for geom in hull.geoms:
                coords = np.array(geom.exterior.coords)
                if not np.allclose(coords[0], coords[-1]):
                    coords = np.vstack([coords, coords[0]])
                hull_points.append(coords)
        else:  # Polygon
            coords = np.array(hull.exterior.coords)
            if not np.allclose(coords[0], coords[-1]):
                coords = np.vstack([coords, coords[0]])
            hull_points = [coords]

        print(alpha)
        return hull_points

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


def add_decorations(reduce_bounds=0.0, white_circle=True, color='r', ax=None, arrow_length = 5, hl = 3, hw = 3, w = 0.6):
    from select_file import spawn_radius, mu, sigma, bound_x, bound_y
    import matplotlib.patches as patches

    if ax is None:
        ax = plt.gca()

    if white_circle:
        ax.add_patch(patches.Circle((0, 0), spawn_radius, fill=True, color='w',
                                    ls='', alpha=1, lw=0, zorder=2))

    ax.axhline(0, c=color, lw=1, ls='--', alpha=0.7, zorder=3)
    ax.add_patch(patches.Circle((0, 0), spawn_radius, fill=False, color=color,
                                ls='--', alpha=0.7, lw=1, zorder=3))

    dx = arrow_length * np.cos(mu)
    dy = arrow_length * np.sin(mu)
    ax.arrow(0, 0, dx, dy, head_width=hw, head_length=hl, width=w,
             fc='k', ec='k', zorder=4)

    if sigma > 0:
        up = np.degrees(mu) - np.degrees(sigma) 
        dwn = np.degrees(mu) + np.degrees(sigma) 
        wedge = patches.Wedge((0, 0), arrow_length + hl, up, dwn,
                              color='k', alpha=0.3, zorder=3)
        ax.add_patch(wedge)

    ax.set_aspect('equal', adjustable='box')

    bx = np.array(bound_x) + [reduce_bounds, -reduce_bounds]
    by = np.array(bound_y) + [reduce_bounds, -reduce_bounds]
    ax.set_xlim(*bx)
    ax.set_ylim(*by)


# def add_decorations(reduce_bounds = 0.0, white_circle=True, color='r'):
#     from select_file import spawn_radius, mu, sigma, bound_x, bound_y
#     if white_circle:
#         plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=True, color='w', ls='', alpha=1, lw=0, zorder=2) )
#     plt.axhline(0, c=color, lw=1, ls='--', alpha=0.7, zorder=3)
#     plt.gca().add_patch( plt.Circle((0,0), spawn_radius, fill=False, color=color, ls='--', alpha=0.7, lw=1, zorder=3) )

#     arrow_length = 5
#     hl = 3 
#     hw = 3
#     w = 0.6
#     dx = arrow_length * np.cos(mu)
#     dy = arrow_length * np.sin(mu)
#     plt.arrow(0, 0, dx, dy, head_width=hw, head_length=hl, width=w, fc='k', ec='k', zorder=4)

#     if sigma > 0:
#         import matplotlib.patches as patches
#         up = np.degrees(mu) - np.degrees(sigma) / 2 
#         dwn = np.degrees(mu) + np.degrees(sigma) / 2 
#         wedge = patches.Wedge((0, 0), arrow_length+hl, up, dwn, color='k', alpha=0.3, zorder=3)
#         plt.gca().add_patch(wedge)

#     plt.axis('scaled')

#     bound_x = np.array(bound_x) + [reduce_bounds, -reduce_bounds]
#     bound_y = np.array(bound_y) + [reduce_bounds, -reduce_bounds]
#     plt.gca().set_xlim(*bound_x)
#     plt.gca().set_ylim(*bound_y)

def truncate_and_stack(array_list):
    # Find the length of the shortest array
    min_length = min(len(arr) for arr in array_list)
    
    # Truncate all arrays to the shortest length and stack
    return np.stack([arr[:min_length] for arr in array_list])

def tqdm(iterable=None, *args, **kwargs):
    kwargs.setdefault('ascii', ' █')
    return base_tqdm(iterable, *args, **kwargs)
