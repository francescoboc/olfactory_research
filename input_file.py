from utils import tc
import numpy as np 

# perform a test run without saving data
dry_run = 1

no_odor = 1

# plotting parameters 
real_time_plot = 0
save_frames = 0
save_gif = 0
pause_time = 0.001

# if parallel is true, we scan several values of trust
n_threads = 1
n_samples = 1

private_behavior = 'cast_and_surge'
# private_behavior = 'biased_rw'

# trust parameter aka beta
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
# trust = 0.95
# trust = 0.99
# trust = 1.0

rand_casting_direction = True

rand_casting_steps = 100
# rand_casting_steps = 20
# rand_casting_steps = 0

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 

# visual_radius = 0
# visual_radius = 5*rd
visual_radius = 2*spawn_radius

olfactoy_radius = rd
reach_radius = 1.0

# initial angle
sigma = np.pi/3
# sigma = 0
mus = np.linspace(1, 3/2, 6)*np.pi
mu = mus[0]
 
# initial conditions
shifts = np.linspace(0, 5, 6)*spawn_radius
shift = shifts[0]

# distance from the source
lx_max = 65
lxs = np.linspace(0, 1, 6)[1:]*lx_max
lx = lxs[4]
# lx = 200

# v0
speed = 0.2

# straight_distance = (lx**2 + shift**2)**0.5
# straight_time = straight_distance/speed

# max simulation time 
# (if 0 the simulation will wait for all the agents to arrive or to be past the source)
# final_time = 0
# final_time = 2500
final_time = 500

# measure only fpt or all the reach times
first_passage = True

# olfactory threshold
if no_odor:
    threshold = np.inf
else:
    threshold = 0.0005

# number of agents
n_agents = 100

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
length, height = 5.0*lx, 5.0*lx

# noise on the estimate of the mean wind and on public velocity
sensing_noise = 0.0 # eta
wind_noise = 0.0 

# spawn position and source coordinates 
spawn_center = [length/1.5, height/2 + shift]
source_coordinates = [spawn_center[0]-lx, height/2]

# define folder and filename
root_folder = 'results_cs'
folder = f'mu{mu:.3f}_sigma{sigma:.3f}/lx{lx:.3f}/shift{shift:.3f}'
folder1 = f'vr{visual_radius}_thr{threshold}_N{n_agents}_v{speed}_snoise{sensing_noise}_wnoise{wind_noise}'
full_folder = f'{root_folder}/{folder}/{folder1}'
