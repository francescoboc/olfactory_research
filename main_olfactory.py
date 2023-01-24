from olfactory_lib import *

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *

# space and time parameters of the simulation 
length, heigth = 30, 20
time_steps = 100

# parameters of the air flow
flow_dt = 1 
fluct_intensity = 0.42
flow_lengthscale = 10
flow_corr_time = 5
mean_wind = [1, 0]

# parameters of the olfactory particle cloud
particle_dt = 1
# TODO rate is 5 or 1/5?
particle_rate = 5
source_coordinates = [1, heigth/2]

# parameters of the swarm of agents
n_agents = 3
olfactory_radius, visual_radius = 3, 3
spawn_radius = 4
spawn_center = [length-spawn_radius-1, heigth/2]
measure_time, decision_time = 1, 2
agent_speed = 1

# plotting parameters
real_time_plot = True
pause_time = 0.01

# create objects
flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity)
cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
swarm = Swarm(n_agents, spawn_center, spawn_radius, measure_time, decision_time, 
        agent_speed, olfactory_radius, visual_radius, cloud, flow)
sim = Simulation(time_steps, flow, swarm, cloud, real_time_plot, pause_time)

# run simulation
sim.run()

# plotting functions
if real_time_plot:
    plt.ion()
    plt.show()
