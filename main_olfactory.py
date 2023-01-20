from olfactory_lib import *

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *

# general parameters of the simulation 
length, heigth = 50, 25
time_steps = 100
# TODO 5 or 1/5?
particle_rate = 5
source_pos = [1, heigth/2]
real_time_plot = True

# parameters of the swarm
n_agents = 5
spawn_center, spawn_radius = [length-5, heigth/2], 3
measure_time, decision_time = 1, 2
agent_speed = 0.5
olfactory_radius, visual_radius = 2, 3

# parameters of the flow
dt = 0.1 # timestep
fluct_intensity = 0.42
flow_lengthscale = 10
flow_corr_time = 5
mean_wind = [1, 0]

# create objects
swarm = Swarm(n_agents, spawn_center, spawn_radius, measure_time, decision_time, agent_speed, olfactory_radius, visual_radius)
flow = Flow(length, heigth, dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity)
sim = Simulation(time_steps, particle_rate, source_pos, flow, swarm, real_time_plot)

# run simulation
sim.run()

# plotting functions
if real_time_plot:
    plt.ion()
    plt.show()
