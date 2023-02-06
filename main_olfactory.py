from olfactory_lib import *
import pandas as pd

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *

# plotting parameters
real_time_plot = False
plot_flow = False
pause_time = 0.01

# olfactory range
Rd = 0.2
# distance from the source
Lx = 250*Rd
# heigth of the simulation box
heigth = 20

# time parameters
decision_time = 1
particle_dt = decision_time/10
particle_rate = 1
flow_dt = particle_dt

# parameters of the agents
n_agents = 2
# trust = 0.85 # beta
trust = 1 # beta
speed = 2.5*Rd/decision_time
olfactory_radius = Rd # Rd 
visual_radius = 5*Rd # Ra
memory_time = 1 # inverse of lambda
sensing_noise = 0.1 # eta

# straight-path time (i.e. minimum time to reach the target)
Ts = Lx/speed
# max duration of the simulation
final_time = 3*Ts

# other parameters
spawn_radius = 25*Rd # Rb
source_coordinates = [spawn_radius, heigth/2]
spawn_center = [source_coordinates[0]+Lx, heigth/2]
length = int(Lx+2*spawn_radius)
fluct_intensity = 0.42
flow_lengthscale = 10
flow_corr_time = 5
mean_wind = [1, 0]

# number of time steps to perform
time_steps = final_time/particle_dt

# TODO bottleneck?
# TODO beta=1 doesn't make sense (?)
# TODO set fixed particle rate or create at exp. distributed times?
# TODO save figures and make a video
# TODO loop the wind field
# TODO reflection boundary conditions (?)

print(f'Ts={Ts:.2f}, N={n_agents}')
print(f'Beta={trust:.2f}')

# create objects
flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity)
cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
        olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow)
sim = Simulation(time_steps, flow, swarm, cloud, real_time_plot, plot_flow, pause_time)
# run simulation
arrival_time, agents_in_Rb, success = sim.run()

# trust parameter (beta) values to check
betas = np.round(np.arange(0.0, 1, 0.05),2) 

n_samples = 10

# empty dataframe to store results
results = pd.DataFrame(index=betas, columns=['times', 'n_agents'])
for trust in betas:
    print(f'Beta={trust:.2f}')
    # create empty lists
    arrival_times, arrival_agents = [], []
    # counter to count the successes
    success_counter = 0
    while success_counter < n_samples:
        # create objects
        flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity)
        cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
        swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
                olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow)
        sim = Simulation(time_steps, flow, swarm, cloud, real_time_plot, plot_flow, pause_time)
        # run simulation
        arrival_time, agents_in_Rb, success = sim.run()
        if success:
            # save results
            arrival_times.append(arrival_time)
            arrival_agents.append(agents_in_Rb)
            # increase success_counter
            success_counter += 1
    # add results to dataframe
    results.loc[trust]['times'] = arrival_times
    results.loc[trust]['n_agents'] = arrival_agents
    print('-----')
# attributes to save in results metadata
attributes = ['Rd', 'Lx', 'heigth', 'decision_time', 'particle_dt', 'particle_rate', 'flow_dt', 'n_agents', 
        'speed', 'olfactory_radius', 'visual_radius', 'memory_time', 'sensing_noise', 'final_time', 'spawn_radius', 
        'source_coordinates', 'spawn_center', 'length', 'fluct_intensity', 'flow_lengthscale', 'flow_corr_time', 'mean_wind']
# add metadata to dataframe
for attr in attributes: results.attrs[attr] = globals()[attr]
# save to disk
results.to_pickle(f'results_dt{particle_dt:.2f}.pkl')

# arrival_times_list = np.load('arrival_times_list.npy', allow_pickle=True)
# times_avg, times_std = [], []
# for at in arrival_times_list:
#     times_filt = [i for i in at if i is not None]
#     times_avg.append(np.mean(times_filt))
#     times_std.append(np.std(times_filt)) 
# times_avg_norm = np.array(times_avg)/Ts
# times_std_norm = np.array(times_std)/Ts
# plt.errorbar(betas, times_avg_norm, times_std_norm, lw=1, capsize=2, marker='o', mfc='none')
# plt.xlabel(r'Trust parameter $\beta$')
# plt.ylabel(r'$T/T_s$')
# plt.ion(); plt.show()

# plotting functions
if real_time_plot: plt.ion(); plt.show()
