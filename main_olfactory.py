from olfactory_lib import *

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *

Rd = 0.2
Lx = 250*Rd

# space and time parameters of the simulation 
length, heigth = int(Lx+30*Rd), int(Lx/2)
time_steps = 300

# plotting parameters
real_time_plot = True
plot_flow = False
pause_time = 0.01

# parameters of the air flow
flow_dt = 1
fluct_intensity = 0.42
flow_lengthscale = 10
flow_corr_time = 5
mean_wind = [1, 0]

# parameters of the olfactory particle cloud
particle_dt = 1 # TODO the dt for the particles is the same of the flow?
particle_rate = 1 # TODO rate is 5 or 1/5?
source_coordinates = [1, heigth/2]

# parameters of the swarm of agents
n_agents = 100
decision_time = 1
speed = 2.5*Rd/decision_time
olfactory_radius = Rd # Rd 
visual_radius = 5*Rd # Ra
memory_time = 1 # inverse of lambda
trust = 0.85 # beta
sensing_noise = 0.1 # eta
spawn_radius = 25*Rd # Rb
spawn_center = [Lx, heigth/2]

# create objects
flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity)
cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
        olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow)
sim = Simulation(time_steps, flow, swarm, cloud, real_time_plot, plot_flow, pause_time)

# run simulation
sim.run()

# TODO add function to check how many agents reach the target and in how long

# plotting functions
if real_time_plot: plt.ion(); plt.show()
