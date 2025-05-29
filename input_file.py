from utils import tc
import numpy as np 

# plotting parameters 
real_time_plot = 0
save_frames = 0
save_gif = 0
pause_time = 0.001

# perform a test run without saving data
dry_run = 0

# simulation without odor
no_odor = 1

private_behavior = 'cast_and_surge'
# private_behavior = 'biased_rw'

# trust parameter
# trust = 0.0
# trust = 0.01

# trust = 0.1
# trust = 0.2
# trust = 0.3
# trust = 0.4
# trust = 0.5
# trust = 0.6
# trust = 0.7
trust = 0.8
# trust = 0.9

# trust = 0.99
# trust = 1.0

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 

# visual_radius = 0
# visual_radius = 5*rd
visual_radius = 100*spawn_radius

olfactoy_radius = rd

# random initial casting clock
rand_casting_steps = 100
# rand_casting_steps = 10
# rand_casting_steps = 0

rand_casting_direction = 1

# average of initial distribution of angles
mu = 0
# mu = np.pi/4

# mu = np.pi/2

# std of initial distribution of angles
# sigma = 0
sigma = np.pi/2

# sigma = np.pi/4
# sigma = np.pi

# number of agents
# n_agents = 10
n_agents = 100
# n_agents = 1000
# n_agents = 2000

# number of realisations
n_runs = 50

# max simulation time 
# (if 0 the simulation will wait for all the agents to reach final_x)
final_time = 0
# final_time = 1000
# final_time = 5000

final_x = 100

# agent's speed
speed = 0.2

# olfactory threshold
if no_odor:
    threshold = np.inf
else:
    threshold = 0.0005

# delta t
decision_time = 1

# tau
memory_time = 1.0 *decision_time

# space bin for the odor field
odor_delta_x = 0.1

# use the memory kernel for the public velocity or not
# method = 'kernel'; dt = 0.01
method = 'no_kernel'; dt = decision_time

# simulation box size
length, height = 500, 500

# noise on the estimate of the mean wind and on public velocity
sensing_noise = 0.0 # eta
wind_noise = 0.0 

source_coordinates = [75, 0]
# source_coordinates = [50, 0]
reach_radius = visual_radius
