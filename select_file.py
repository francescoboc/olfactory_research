import numpy as np

# trust parameter
# trust = 0.0

# trust = 0.1
# trust = 0.2
# trust = 0.3
# trust = 0.4
# trust = 0.5
# trust = 0.6
# trust = 0.7
# trust = 0.8
trust = 0.9

# trust = 1.0

# check only center of mass or consider all the agents
center_of_mass = 0

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 

# visual_radius = 0
# visual_radius = 5*rd
visual_radius = 100*spawn_radius

# random initial casting clock
rand_casting_steps = 100
# rand_casting_steps = 20
# rand_casting_steps = 0

# average of initial distribution of angles
mu = 0
# mu = np.pi/4
# mu = np.pi/2

# std of initial distribution of angles
# sigma = 0
# sigma = np.pi/2
sigma = np.pi

# number of realisations
n_runs = 50
# n_runs = 2

# final_time = 500
final_time = 0

final_x = 100

# distance from source and shift from centerline
l_x = 50
h_y = 0 

# hexbin parameters
gridsize = 200
# gridsize = 300
offset = 100

# list of probabilities to plot contours of success rate
prob_list = [1.0, 0.5, 0.0]

# selected probability threshold to plot exploration cone width
prob_selected = prob_list[-1]

# calculate hexbin related variables (don't change this)
traj_center = final_x/2
bound_x = [traj_center - offset, traj_center + offset]
bound_y = [-offset, offset]

width = bound_x[1] - bound_x[0]
hex_radius = width / (gridsize * np.sqrt(3))

n_agents = 100
