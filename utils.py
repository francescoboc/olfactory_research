import matplotlib.pyplot as plt
import numpy as np

# extract matplotlib default colors and markers
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
markers = list(plt.Line2D.markers.keys())[2:]
# markers = ['o', 's', 'd', 'v', '^', '<', '>']

# update matplotlib parameters globally
plt.rcParams['lines.markerfacecolor'] = 'none'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['errorbar.capsize'] = 2
plt.rcParams['legend.fancybox'] = False
plt.rcParams['figure.constrained_layout.use'] = True

# plt.rcParams['legend.fontsize'] = 14 
# plt.rcParams['legend.title_fontsize'] = 'small'
# plt.rcParams['legend.handlelength'] = 1
# plt.rcParams['legend.handletextpad'] = 0.5

# plt.rc('text', usetex=True)
# plt.rcParams['font.size'] = 17 

# plt.rc('text.latex', preamble=r'\usepackage{bm}')
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

def shaded_errorbar(x, y, yerr, label=None, c=None, ls='-', m='o', alpha=0.1):
    below = np.array(y)-np.array(yerr)
    above = np.array(y)+np.array(yerr)
    if c is not None:
        plt.plot(x, y, marker=m, color=c, ls=ls, label=label)
        plt.fill_between(x, below, above, color=c, alpha=alpha)
    else:
        plt.plot(x, y, marker=m, ls=ls, label=label)
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

def show_and_check_ipython():
    try: __IPYTHON__; plt.ion()
    except NameError: pass
    plt.show()

def norm(vector):
    return (vector[0]**2 + vector[1]**2)**0.5

def normalised(vector):
    norm = (vector[0]**2 + vector[1]**2)**0.5
    if norm != 0: return vector/norm
    else: return vector

