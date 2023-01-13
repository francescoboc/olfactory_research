from olfactory_lib import *

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *

# INITIALISE
# parameters of the simulation 
length, heigth = 50, 25
time_steps = 10

# parameters of the swarm
n_agents = 5
spawn_center, spawn_radius = [length-10, heigth/2], 7.5
measure_time, decision_time = 1, 2
agent_speed = 0.5
olfactory_radius, visual_radius = 2, 5

# parameters of the source
source_pos = [1, heigth/2]

# create objects
source = Source(source_pos)
swarm = Swarm(length, heigth, n_agents, spawn_center, spawn_radius, measure_time, decision_time, 
        agent_speed, olfactory_radius, visual_radius)
sim = Simulation(length, heigth, time_steps, source, swarm)

# spawn the agents
swarm.spawn()

# PLOT STUFF
# create figure and axes for plotting
plt.gca().remove()
plt.subplot(aspect='equal', adjustable='box', xlim=(0, length), ylim=(0, heigth), title='time = 0')

# add source and spawn circle drawings
plt.plot(*source_pos, c='b', marker='o')
spawn_circle = plt.Circle(spawn_center, spawn_radius, fill=False, ls='--', color='k', alpha=0.5)
plt.gca().add_patch(spawn_circle)

# add agents points and visual circles
m=0
for agent in swarm.agents:
    agent_point = plt.Circle(agent.coordinates, 0.25, color=colors[m], label=m)
    visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[m], alpha=0.5)
    plt.gca().add_patch(agent_point)
    plt.gca().add_patch(visual_circle)
    m+=1
plt.legend(fancybox=False)

# RUN SIMULATION
sim.run()

plt.ion()
plt.show()
