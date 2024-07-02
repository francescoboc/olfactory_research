from  olfactory_lib import *
import os

import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *


# ------------

final_time = 100

shift = 0.0

decision_time = 1

trust = 0.8

rd = 0.2

# number of agents
n_agents = 2 

visual_radius = 25*rd

# body radius
spawn_radius = 25*rd # Rb

reach_radius = rd

lx = 250*rd

b = 5
length, height = b*lx, b*lx

# noise on the estimate of the mean wind and on public vel
sensing_noise = 0.0 # eta
wind_noise = 0.0 

# speed of the agents
# speed = 0.2 
speed = 1

# spawn position and source coordinates 
spawn_center = [length/1.5, height/2 + shift]
source_coordinates = [spawn_center[0]-lx, height/2]

olfactory_radius = 0

# memory_time = 0.1
# memory_time = 0.5
memory_time = 1.0
# memory_time = 2.0
# memory_time = 5.0

# ------------


# pad points to extend the simulation box
pad_points = 200

# plotting parameters 
real_time_plot = False
plot_flow = False
save_frames = False
pause_time = 0.001

# read h5 flow file or local npy file
read_h5 = False

# smelling threshold
# threshold = 0.0008
threshold = 0.8

# elastic constant
kelast = 1

# use elastic recall force
elastic = False

# use a stochastic or a turbulent flow
turbulent = True

# use a different beta for informed and uninformed agents
adaptive_beta = False

# these are relevant only if we are using an adaptive beta
trust_uninform = 0.9
trust_inform = 0.1

# decay time used both for beta and for the surging phase
decay_time = 8

# parameters of the agents

# sensing_noise = 0.1 # eta
sensing_noise = 0.0 # eta
# wind_noise = 0.1 # noise on the estimate of the mean wind
wind_noise = 0.0 # noise on the estimate of the mean wind


# parameters of the particle cloud
particle_dt = decision_time/10 # δt
particle_rate = 10 # J
flow_dt = particle_dt

# parameters of the stochastic flow
fluct_intensity = 0.42
flow_lengthscale = 10
flow_corr_time = 5
mean_wind = [1, 0]
loop_cycles = 10

# path of the turbulent flow
if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
else: path = 'flow/re280_small_source'

# set global variables
set_h5_flag(read_h5)
set_pad_points(pad_points)

# create flow and odor objects
flow = Flow_turbulent(path, length)
cloud = Cloud_turbulent(flow)

# initialise the rng
# seed = random.randrange(sys.maxsize)
seed = 66
initialise_rng(seed)
print(f'Seed = {seed}')
# create objects
swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
        visual_radius, reach_radius, memory_time, sensing_noise, wind_noise, trust, trust_inform, 
        trust_uninform, decay_time, threshold, adaptive_beta, cloud, flow)
sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
        save_frames, elastic, turbulent)
# run simulation
arrival_time, agents_in_Rb, success = sim.run()

# ----------------------------------------

vel_x = np.array([vel[0] for vel in sim.swarm.vel_t])
vel_y = np.array([vel[1] for vel in sim.swarm.vel_t])
coord_x = np.array([coord[0] for coord in sim.swarm.traj])
coord_y = np.array([coord[1] for coord in sim.swarm.traj])

# attributes to save in logfile
attributes = ['final_time', 'memory_time', 'dt', 'rd', 'n_agents', 'visual_radius', 'spawn_radius', 
        'reach_radius', 'lx', 'length', 'height', 'speed', 'spawn_center', 'source_coordinates']

# folder = f'results/casting/geometric/lx{lx:.3f}_shift{shift:.3f}/memory_time{memory_time:.3f}/dt{dt:.3f}_dec_time{decision_time:.3f}/trust{trust:.3f}'
# os.makedirs(f'{folder}', exist_ok=True)
# np.save(f'{folder}/vel_x', vel_x)
# np.save(f'{folder}/vel_y', vel_y)
# np.save(f'{folder}/coord_x', coord_x)
# np.save(f'{folder}/coord_y', coord_y)
# # save logfile
# log = {}
# for attr in attributes: log[attr] = locals()[attr]
# np.save(f'{folder}/log', log)

plt.figure(0)
# create axes for plotting
# axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, length), ylim=(0, height))
axes = plt.subplot(aspect='equal', adjustable='box')
# add patches for source and spawn circle 
axes.add_patch( plt.Circle(sim.swarm.spawn_center, sim.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2) )
axes.add_patch( plt.Circle(source_coordinates, 0.2, color='k') )

axes.axhline( source_coordinates[1], lw=1, ls='--', c='k', alpha=.2 )

# # add agents points and visual circles
# index = 0
# for agent in sim.swarm.agents:
#     color_id = min([len(colors), index%len(colors)]) 
#     agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[color_id], label=index)
#     visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[color_id], alpha=0.1)
#     # visual_circle = plt.Circle(agent.coordinates, reach_radius, fill=False, color=colors[color_id], alpha=0.1)
#     axes.add_patch(agent_point); axes.add_patch(visual_circle)
#     index += 1

axes.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1)
# axes.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1, marker='o', mfc='none', ms=3)

# sign_changes = np.where(vel_y[:-1] * vel_y[1:] < 0 )[0] + 1 
# max_x = coord_x[sign_changes]
# max_y = coord_y[sign_changes]
# axes.plot(max_x, max_y, c='r', marker='o', mfc='none', ls='')

# t_star = int(final_time/2)+1
t_star = 1
time_steps = np.arange(0, final_time-t_star)
plt.figure(1)
plt.plot(time_steps, -vel_x[t_star:], label='NO kernel')

norm_cumprod = np.cumprod(sim.swarm.norms[t_star:])
proj_an = []
for n in time_steps:
    projection = trust**(n+1)/norm_cumprod[n]
    proj_an.append(projection)
plt.plot(time_steps, proj_an, label='analytic')

# plt.xlabel(r'$t-t^*$')
plt.xlabel(r'$n$')
plt.ylabel(r'$-v_x$')
# plt.xscale('log')
plt.legend()


plt.ion()
plt.show()
