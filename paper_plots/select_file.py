import numpy as np

# trust parameter
# trust = 0.0

# trust = 0.1
# trust = 0.2
# trust = 0.3
trust = 0.4
# trust = 0.5
# trust = 0.6
# trust = 0.7
# trust = 0.8
# trust = 0.9

# trust = 1.0

trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# trusts = [0.1, 0.3, 0.5, 0.7, 0.9]

# set the thresholds for the success rate and presence probability
rate_threshold = 0.95
prob_threshold = 0.04

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

# standard deviation of initial distribution of angles
sigma = 0
# sigma = np.pi/4
# sigma = np.pi/2

# sigma = np.pi

# number of agents
n_agents = 100
# n_agents = 20
# n_agents = 10

# number of realisations
n_runs = 50
# n_runs = 2

# final_time = 500
final_time = 0

final_x = 100

# # distance from source and shift from centerline
# l_x = 50
# h_y = 0 

# # secondary source
# l_x1 = 70
# h_y1 = 10 

# hexbin parameters
gridsize = 200
# gridsize = 300
offset = 100

# list of rates to plot contours of success rate
rates_list = [0.1, 0.5, 0.9]

# selected probability threshold to plot exploration cone width
rate_selected = rates_list[-1]

# list of probabilitis to plot contours of probability of presence
prob_list = [0.0, 0.01, 0.1]

# calculate hexbin related variables (don't change this)
traj_center = final_x/2
bound_x = [traj_center - offset, traj_center + offset]
bound_y = [-offset, offset]

width = bound_x[1] - bound_x[0]
hex_radius = width / (gridsize * np.sqrt(3))

# agent's speed
speed = 0.2
