import numpy as np 

# plotting parameters 
real_time_plot = True
save_frames = False
save_gif = False
pause_time = 0.001
# pause_time = 0.5

# if parallel is true, we scan several values of trust
parallel = False
n_threads = 10
n_samples = 10

# constrain the swarm 
constrained = False

# max simulation time
final_time = int(2e6)

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 

# visual_radius = rd
# visual_radius = 2*rd
# visual_radius = 5*rd
# visual_radius = 10*rd
# visual_radius = 25*rd
visual_radius = 50*rd

olfactoy_radius = rd
reach_radius = 1.0

# initial conditions
shifts = np.linspace(0, 3, 6)*spawn_radius
shift = shifts[0]

sigma = np.pi/20
# sigma = np.pi/3
mus = np.linspace(1, 3/2, 6)*np.pi
mu = mus[0]
 
# beta (only for parallel = False option)
trust = 0.9

# olfactory threshold
# threshold = 0.0005
threshold = 1.0

# number of agents
n_agents = 100
# n_agents = 1

# trust values to check in the parallel run
trust_init = 0.9
trust_final = 0.99
trust_step = 0.01
trusts = np.round(np.arange(trust_init, trust_final + trust_step, trust_step),2) 

# max number of simulations to do to try reaching n_samples
# limit = int(n_samples*10)
# limit = 10

# delta t
decision_time = 1

# tau
memory_time = 1.0 *decision_time

# space bin for the odor field
odor_delta_x = 0.1

# use the memory kernel for the public velocity or not
# method = 'kernel'; dt = 0.01
# method = 'no_kernel'; dt = decision_time
method = 'no_kernel'
dt = 0.5

# distance from the source
lx = 50

# simulation box size
length, height = 125, 125

# noise on the estimate of the mean wind and on public velocity
sensing_noise = 0.0 # eta
wind_noise = 0.0 

# v0
speed = 0.2 
# speed = 1.0 

# spawn position and source coordinates 
spawn_center = [length/1.5, height/2 + shift]
source_coordinates = [spawn_center[0]-lx, height/2]

# define folder and filename
folder = f'results/thr{threshold}/vr{visual_radius}_N{n_agents}_sr{spawn_radius}'
filename = f'dt{dt}'
