import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

plt.rcParams['font.size'] = 17 

# plt.rcParams['legend.fontsize'] = 17 
# plt.rcParams['legend.handlelength'] = 1
# plt.rcParams['legend.handletextpad'] = 0.5
# plt.rcParams['legend.title_fontsize'] = 'small'

plt.rc('text', usetex=True)
# plt.rc('text.latex', preamble=r'\usepackage{bm}')
plt.rc('savefig', format='pdf')
plt.rc('savefig', directory='/mnt/c/Users/franc/Dropbox/papero_1_olfactory/img')

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

