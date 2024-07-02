from  olfactory_lib import *
import pandas as pd
import multiprocessing as mp
import os

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *
from input_file import *

# ulimit -Sn unlimited

# pad points to extend the simulation box
pad_points = 100

# plotting parameters 
real_time_plot = True
plot_flow = False
save_frames = True
pause_time = 0.001

# ---------- ---------- ----------

# elastic constant
kelast = 0

sensing_noise = 0.1 # eta
wind_noise = 0.1 # noise on the estimate of the mean wind

# visual radius
radii = [0.1, 0.5, 1, 5, 10]

# trust parameter 
trusts = np.round(np.arange(0.0, 1.1, 0.1),2) 

# number of agents
n_agents = 100 # N

# body radius
spawn_radius = 5 # Rb

# ---------- ---------- ----------

# path of the turbulent flow
if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
else: path = 'flow/re280_small_source'

# set global variables
set_h5_flag(read_h5)
set_pad_points(pad_points)

# read h5 flow file or local npy file
read_h5 = True

# use elastic recall force
elastic = True

# vertical shift of the initial position (in perc of height/2)
shift = 0.0

# radius within which the source is seen by the agents
reach_radius = 0.4

# time parameters
decision_time = 1 # Δt

# smelling threshold
# threshold = 0.0008
threshold = 0.08

# use a stochastic or a turbulent flow
turbulent = True

# use a different beta for informed and uninformed agents
adaptive_beta = False

# these are relevant only if we are using an adaptive beta
trust_uninform = 0.9
trust_inform = 0.1

# decay time used both for beta and for the surging phase
decay_time = 8

Rd = 0.4 # olfactory range
Lx = 70 # distance from the source

# length of the simulation box (height is given by the flow data)
length = 100

# parameters of the agents
speed = 0.2 # v0
olfactory_radius = Rd # Rd 
memory_time = 1/decision_time # inverse of λ

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

final_time = 400

for visual_radius in radii:
    for trust in trusts:
        # name of the output file
        filename = f'ra{visual_radius}_beta{trust}_rs{spawn_radius}_k{kelast}_N{n_agents}_snoise{sensing_noise}_wnoise{wind_noise}'

        # folder where the output file is saved
        folder = 'results/centerofmass_trajectory/'

        folder = folder + f'/k{kelast}_ra{visual_radius}'

        # create folders
        os.makedirs(folder, exist_ok=True)

        # print info to the terminal
        print(f'Filename = {filename}')

        # create flow and odor objects
        flow = Flow_turbulent(path, length)
        cloud = Cloud_turbulent(flow)

        # spawn position and source coordinates 
        source_coordinates = cloud.source_coordinates
        spawn_center = [cloud.source_coordinates[0]+Lx, flow.height/2 + shift*(flow.height/2)]

        # initialise the rng
        # seed = random.randrange(sys.maxsize)
        seed = 2912106185768689831
        initialise_rng(seed)
        print(f'Seed = {seed}')
        # create objects
        swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
                visual_radius, reach_radius, memory_time, sensing_noise, wind_noise, trust, trust_inform, 
                trust_uninform, decay_time, threshold, adaptive_beta, cloud, flow)
        sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
                save_frames, elastic, turbulent)
        # run simulation
        arrival_time, agents_in_Rb, success, traj_centerofmass = sim.run()


        # create figure and axes for plotting
        fig = plt.figure(figsize=(13,8))
        plt.gca().remove()
        sim.axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, sim.flow.length-1), ylim=(0, sim.flow.height-1))

        # add patches for source and spawn circle 
        spawn_circle = plt.Circle(sim.swarm.spawn_center, sim.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2)
        source_point = plt.Circle(sim.cloud.source_coordinates, 0.1, color='k', zorder=2)
        source_circle = plt.Circle(sim.cloud.source_coordinates, sim.swarm.reach_radius, fill=False, color='k', ls='--', alpha=0.2)
        sim.axes.add_patch(spawn_circle); sim.axes.add_patch(source_point); sim.axes.add_patch(source_circle)

        # add agents points and visual circles
        index = 0
        for agent in sim.swarm.agents:
            color_id = min([len(colors), index%len(colors)]) 
            agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[color_id], label=index)
            visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[color_id], alpha=0.1)
            olfactory_circle = plt.Circle(agent.coordinates, agent.olfactory_radius, fill=False, color=colors[color_id], alpha=0.2, ls='--')
            sim.axes.add_patch(agent_point); sim.axes.add_patch(visual_circle); sim.axes.add_patch(olfactory_circle)
            index += 1

        plt.title( f'ra={visual_radius}, beta={trust}, rs={spawn_radius}, k={kelast}, N={n_agents}, sens_noise={sensing_noise}, wind_noise={wind_noise}' )
        plt.scatter([coord[0] for coord in traj_centerofmass], [coord[1] for coord in traj_centerofmass], c='k', s=1)

        plt.savefig(f'{folder}/{filename}.png')
        plt.close()
