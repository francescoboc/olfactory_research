import matplotlib.pyplot as plt
import numpy as np
import olfactory_lib as ol
import pandas as pd

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
import olfactory_lib as ol

# plotting parameters
real_time_plot = True
plot_flow = False
pause_time = 0.01

Rd = 0.2 # olfactory range
Lx = 250*Rd # distance from the source

# size of the simulation box
length = int(2.5*Lx)
heigth = length

# time parameters
decision_time = 1 # Δt
particle_dt = decision_time/10 # δt
particle_rate = 1 # J
flow_dt = particle_dt

# parameters of the agents
n_agents = 100 # N
trust = 0.85 # β
speed = 2.5*Rd/decision_time # v0
olfactory_radius = Rd # Rd 
visual_radius = 5*Rd # Ra
memory_time = 1 # inverse of λ
sensing_noise = 0.1 # eta
spawn_radius = 25*Rd # Rb

# parameters of the flow
fluct_intensity = 0.42
flow_lengthscale = 10
flow_corr_time = 5
loop_cycles = 10
mean_wind = [1, 0]

# max duration of the simulation
Ts = Lx/speed # straight-path time
final_time = 10*Ts 

# spawn position and source coordinates 
source_coordinates = [int(length/2 - Lx/2), heigth/2]
spawn_center = [source_coordinates[0]+Lx, heigth/2]

# TODO reflection boundary conditions
# TODO save figures and make a video
# TODO beta=1 doesn't make sense (?) -> it does if we initialise the velocities (e.g. random)

print(f'Ts = {Ts:.2f}, N = {n_agents}')
print(f'β = {trust:.2f}')
# create objects
flow = ol.Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
cloud = ol.Cloud(particle_dt, particle_rate, source_coordinates, flow)
swarm = ol.Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
        olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow)
sim = ol.Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time)
# run simulation
arrival_time, agents_in_Rb, success = sim.run()

# # trust parameter (beta) values to check
# # betas = np.round(np.arange(0.05, 1, 0.05),2) 
# betas = np.round(np.arange(0.1, 1, 0.1),2) 
# # number of successful episodes to sample
# n_samples = 10
# print(f'Ts = {Ts:.2f}, N = {n_agents}')
# # empty dataframe to store results
# results = pd.DataFrame(index=betas, columns=['times', 'n_agents'])
# for trust in betas:
#     print(f'β = {trust:.2f}')
#     # create empty lists
#     arrival_times, arrival_agents = [], []
#     # counter to count the successes
#     success_counter = 0
#     while success_counter < n_samples:
#         # create objects
#         flow = ol.Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
#         cloud = ol.Cloud(particle_dt, particle_rate, source_coordinates, flow)
#         swarm = ol.Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
#                 olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow)
#         sim = ol.Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time)
#         # run simulation
#         arrival_time, agents_in_Rb, success = sim.run()
#         if success:
#             # save results
#             arrival_times.append(arrival_time)
#             arrival_agents.append(agents_in_Rb)
#             # increase success_counter
#             success_counter += 1
#     # add results to dataframe
#     results.loc[trust]['times'] = arrival_times
#     results.loc[trust]['n_agents'] = arrival_agents
#     print('--------')
# # attributes to save in results metadata
# attributes = ['Rd', 'Lx', 'heigth', 'decision_time', 'particle_dt', 'particle_rate', 'flow_dt', 'n_agents', 'speed', 
#         'olfactory_radius', 'visual_radius', 'memory_time', 'sensing_noise', 'final_time', 'spawn_radius', 'source_coordinates', 
#         'spawn_center', 'length', 'fluct_intensity', 'flow_lengthscale', 'flow_corr_time', 'mean_wind', 'loop_cycles']
# # add metadata to dataframe
# for attr in attributes: results.attrs[attr] = locals()[attr]
# # save to disk
# results.to_pickle(f'square_results_dt{particle_dt:.2f}.pkl')

# plotting functions
if real_time_plot: plt.ion(); plt.show()
