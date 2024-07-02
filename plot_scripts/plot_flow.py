#this script plots odor field advected by a turbulent flow
#horizontal cross section at the position of the odor source is plotted (perpendicular to the wall normal direction)
#input variable is the snapshot number to be plotted

import numpy as np
import matplotlib.pyplot as plt
import os, sys, random

plot_flow = False

# 0.15, 0.5, 1.0, 1.5
z_coord = 0.15

# time steps to plot (max = 1000)
steps = 500

# length of the simulation box
length = 10

folder = f'flow/re200'

# main folder and file paths
# folder = f'flow/height_{z_coord:.2f}'
odor_path = f'{folder}/odor.npy'
ux_path = f'{folder}/vel_x.npy'
uy_path = f'{folder}/vel_y.npy'

# load the npy files into arrays
odor_frames = np.load(odor_path)

if plot_flow:
    ux_frames = np.load(ux_path)
    uy_frames = np.load(uy_path)

# load first frame
odor = odor_frames[0]
if plot_flow:
    ux = ux_frames[0]
    uy = uy_frames[0]

# extract number of points of the field
npoints_y, npoints_x = odor.shape

# adjust delta_x in order to obtain the desired length
delta_x = length/npoints_x
# delta_x = round(length/npoints_x,2)
delta_y = delta_x

x_values = np.arange(npoints_x)*delta_x
y_values = np.arange(npoints_y)*delta_y
x_max = max(x_values)
y_max = max(y_values)

source_pos = (x_max/10, y_max/2)

fig, ax = plt.subplots(figsize=(10,5))

if plot_flow:
    flow_arrows = ax.quiver(x_values, y_values, ux, uy, scale=5/delta_x, units='xy', 
            headlength=3, headaxislength=3, minshaft=5, alpha=0.5, zorder=2, color='w')

im = ax.imshow(odor, extent=(0,x_max,0,y_max))

plt.scatter(*source_pos, c='red')

# coord = [x_max -10*delta_x, y_max/2]
# point = plt.Circle(coord, delta_x, zorder=2, color='w')
# ax.add_patch(point)

v_x = -2*delta_x

for timestep in range(steps):
    if plot_flow:
        ux = ux_frames[timestep]
        uy = uy_frames[timestep]

    odor = odor_frames[timestep]

    if plot_flow: flow_arrows.set_UVC(ux, uy)
    im.set_data(odor)

    # v_y = 2*(random.random() - 0.5)*delta_x
    # coord[0] += v_x
    # coord[1] += v_y

    plt.title(timestep)
    plt.pause(0.001)

# # plt.savefig(odor_path+str(int(timestep))+".png",dpi=100, bbox_inches='tight')

try: __IPYTHON__; plt.ion()
except NameError: pass
plt.show()
