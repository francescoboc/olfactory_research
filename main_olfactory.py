from  olfactory_lib import *
import pandas as pd
import multiprocessing as mp

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from  olfactory_lib import *

def single_run(n):
    # create objects
    flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
    cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
            olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, save_frames)
    # run simulation
    arrival_time, agents_in_Rb, success = sim.run()
    return arrival_time, agents_in_Rb, success

def beta_run(trust):
    print(f'β = {trust:.2f}')
    # create empty lists
    arrival_times, arrival_agents = [], []
    # counter to count the successes
    success_counter = 0
    while success_counter < n_samples:
        # create objects
        flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
        cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
        swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
                olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow)
        sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, save_frames)
        # run simulation
        arrival_time, agents_in_Rb, success = sim.run()
        if success:
            # save results
            arrival_times.append(arrival_time)
            arrival_agents.append(agents_in_Rb)
            # increase success_counter
            success_counter += 1
    return trust, arrival_times, arrival_agents

# TODO BUG sometimes we get number of agents < Rb = 0
# TODO make all the swarm activate at once (?)
# TODO initial amplitudes of noise?
# TODO reflection boundary conditions
# TODO beta=1 doesn't make sense (?) -> it does if we initialise the velocities (e.g. random)
# TODO save number of unsuccessful runs

# plotting parameters 
real_time_plot = True
plot_flow = False
save_frames = False
pause_time = 0.01

# do more runs at the same time
parallel = False
n_threads = 50 # number of parallel threads
 
# prefix name of the output results file
name = 'elastic_vj'

# trust parameter (beta) values to check
betas = np.round(np.arange(0.05, 1, 0.05),2) 
# betas = np.round(np.arange(0.1, 1, 0.1),2) 

Rd = 0.2 # olfactory range
# Lx = 250*Rd # distance from the source
Lx = 150*Rd # distance from the source

# number of successful episodes to sample
n_samples = 50

# size of the simulation box
length = int(2.5*Lx)
heigth = length

# time parameters
decision_time = 1 # Δt
particle_dt = decision_time/10 # δt
particle_rate = 10 # J
flow_dt = particle_dt

# parameters of the agents
n_agents = 100 # N
trust = 0.85 # β
speed = 2.5*Rd/decision_time # v0
olfactory_radius = Rd # Rd 
visual_radius = 5*Rd # Ra
memory_time = 1/decision_time # inverse of λ
sensing_noise = 0.1 # eta
spawn_radius = 25*Rd # Rb

# parameters of the flow
fluct_intensity = 0.42
flow_lengthscale = 10
flow_corr_time = 5
mean_wind = [1, 0]
loop_cycles = 10

# max duration of the simulation
Ts = Lx/speed # straight-path time
final_time = 10*Ts 

# spawn position and source coordinates 
source_coordinates = [int(length/2 - Lx/2), heigth/2]
spawn_center = [source_coordinates[0]+Lx, heigth/2]

# print info to the terminal
print(f'Seed = {seed}')
print(f'Ts = {Ts:.2f}, N = {n_agents}')

# betas = [trust]
# ns = np.arange(n_samples)
# results = pd.DataFrame(index=betas, columns=['times', 'n_agents'])
# # create and run a pool of parallel workers
# pool = mp.Pool(processes = n_threads)
# arrival_agents, arrival_times = [], []
# for res in pool.map(single_run, ns):
#     # split result 
#     arrival_time, agents_in_Rb, success = res[0], res[1], res[2]
#     if success:
#         # and save it into the dataframe
#         arrival_times.append(arrival_time)
#         arrival_agents.append(agents_in_Rb)
# results.loc[trust]['times'] = arrival_times
# results.loc[trust]['n_agents'] = arrival_agents
# # close the pool of workers
# pool.close(); pool.join()
# # attributes to save in results metadata
# attributes = ['seed', 'Rd', 'Lx', 'heigth', 'decision_time', 'particle_dt', 'particle_rate', 'flow_dt', 'n_agents', 'speed', 
#         'olfactory_radius', 'visual_radius', 'memory_time', 'sensing_noise', 'final_time', 'spawn_radius', 'source_coordinates', 
#         'spawn_center', 'length', 'fluct_intensity', 'flow_lengthscale', 'flow_corr_time', 'mean_wind', 'loop_cycles']
# # add metadata to dataframe
# for attr in attributes: results.attrs[attr] = locals()[attr]
# # save to disk
# results.to_pickle(f'{name}_results_dt{particle_dt:.2f}.pkl')

# do a single run
if not parallel:
    print(f'β = {trust:.2f}')
    # create objects
    flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
    cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
            olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, save_frames)
    # run simulation
    # for agent in swarm.agents: agent.go = 1
    arrival_time, agents_in_Rb, success = sim.run()
    # arrival_time, agents_in_Rb, success, wind_estimates = sim.run()
# do more runs at the same time
else:
    # do not plot if we are doing parallel runs!
    real_time_plot = False
    # empty dataframe to store results
    results = pd.DataFrame(index=betas, columns=['times', 'n_agents'])
    # create and run a pool of parallel workers
    pool = mp.Pool(processes = n_threads)
    for res in pool.map(beta_run, betas):
        # split result 
        trust, arrival_times, arrival_agents = res[0], res[1], res[2]
        # and save it into the dataframe
        results.loc[trust]['times'] = arrival_times
        results.loc[trust]['n_agents'] = arrival_agents
    # close the pool of workers
    pool.close(); pool.join()
    # attributes to save in results metadata
    attributes = ['seed', 'Rd', 'Lx', 'heigth', 'decision_time', 'particle_dt', 'particle_rate', 'flow_dt', 'n_agents', 'speed', 
            'olfactory_radius', 'visual_radius', 'memory_time', 'sensing_noise', 'final_time', 'spawn_radius', 'source_coordinates', 
            'spawn_center', 'length', 'fluct_intensity', 'flow_lengthscale', 'flow_corr_time', 'mean_wind', 'loop_cycles']
    # add metadata to dataframe
    for attr in attributes: results.attrs[attr] = locals()[attr]
    # save to disk
    results.to_pickle(f'{name}_results_dt{particle_dt:.2f}.pkl')

# plotting functions
if real_time_plot: 
    plt.ion(); plt.show()
    if save_frames:
        import os
        os.system("ffmpeg -framerate 30 -start_number 1 -i 'frames/frame%d.png' -c:v libx264 out.mp4")
