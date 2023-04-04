from  olfactory_lib import *
import pandas as pd
import multiprocessing as mp
import os

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from  olfactory_lib import *

def parallel_run(n):
    print(f'Running sim. {n+1}', end='\r')
    sys.stdout.write("\033[K")
    # initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)
    # create objects
    flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
    cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
            olfactory_radius, visual_radius, memory_time, sensing_noise, trust_inform, trust_uninform, trust_decay, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, save_frames, elastic)
    # run simulation
    # arrival_time, agents_in_Rb, success = sim.run()
    arrival_time, agents_in_Rb, success, x_coords, y_coords, detections = sim.run()
    return arrival_time, agents_in_Rb, success, seed
    # return arrival_time, agents_in_Rb, success, seed, x_coords, y_coords, detections

# TODO make all the swarm activate at once (?)
# TODO initial amplitudes of noise?
# TODO reflection boundary conditions (or better not?)
# TODO beta=1 doesn't make sense (?) -> it does if we initialise the velocities (e.g. random)!
# TODO save data periodically (just in case) 

# TODO fai andare ancora un po' la sim con elastic=True per far si che tutti gli agenti arrivino a destinazione
# TODO john hopkins turbulence dataset

# plotting parameters 
real_time_plot = False
plot_flow = True
save_frames = True
pause_time = 0.001

# name of the output results file
filename = 'adaptive_beta_elastic_refined'
elastic = True

# do more runs at the same time
parallel = True
n_threads = 50 # number of threads used for parallelisation
 
# number of successful episodes to sample
n_samples = 100

# trust parameter (beta) values to check in a parallel run
# betas = np.round(np.arange(0.05, 1, 0.05),2) 

betas_inf = np.round(np.arange(0.0, 1, 0.1),2) 
betas_uninf = np.round(np.arange(0.8, 1, 0.02),2) 

# radii = [1,2,3,4,5,6,7,8,9,10]
# radii = [5]

Rd = 0.2 # olfactory range
Lx = 250*Rd # distance from the source

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
# trust = 0.85 # β
# speed = 2.5*Rd/decision_time # v0
speed = 0.2
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

# trust_inform = 0.1
# trust_uninform = 0.9
# trust_decay = 0.1

# trust_inform = trust
# trust_uninform = trust
# trust_decay = 0.1

# max duration of the simulation
Ts = Lx/speed # straight-path time
final_time = 10*Ts 

# spawn position and source coordinates 
source_coordinates = [int(length/2 - Lx/2), heigth/2]
spawn_center = [source_coordinates[0]+Lx, heigth/2]

# check if file already exists
if os.path.isfile(f'results/{filename}.pkl'):
    raise Warning(f'File {filename}.pkl already exists!')

# check if we are using too many CPUs
if parallel and os.cpu_count() < n_threads:
    raise Warning(f'Too many threads!')

# print info to the terminal
print(f'Filename = {filename}, Elastic = {elastic}')
print(f'Ts = {Ts:.2f}, N = {n_agents}')

# create folders
os.makedirs('results', exist_ok=True); os.makedirs('frames', exist_ok=True)

if parallel:
    multiindex = pd.MultiIndex.from_product([betas_uninf, betas_inf], names=['trust_uninf', 'trust_inf'])
    results = pd.DataFrame(index=multiindex, columns=['times', 'n_agents', 'fails', 'seeds'])
    # results = pd.DataFrame(index=betas, columns=['times', 'n_agents', 'fails', 'seeds'])
    # results = pd.DataFrame(index=radii, columns=['times', 'n_agents', 'fails', 'seeds'])
    # do not plot if we are doing parallel runs!
    real_time_plot = False
    # for trust in betas:
    # for spawn_radius in radii:
    for trust_uninform in betas_uninf:
        for trust_inform in betas_inf:
            print(f'\nβ_u = {trust_uninform:.2f}, β_i = {trust_inform:.2f}')
            arrival_times, arrival_agents, seeds = [], [], []
            fail_counter, success_counter = 0, 0

            # create and run a pool of parallel workers
            pool = mp.Pool(processes = n_threads)
            limit = 5000 # max number simulations to run to reach the sampling limit
            for arrival_time, agents_in_Rb, success, seed in pool.imap_unordered(parallel_run, range(limit)):
                # if the run was successfull, save results into the dataframe
                if success:
                    arrival_times.append(arrival_time)
                    arrival_agents.append(agents_in_Rb)
                    seeds.append(seed)
                    success_counter += 1
                # otherwise, increase fail cunter
                else:
                    fail_counter += 1
                # if we reached the desired number of samples, stop
                if success_counter == n_samples:
                    break
                # terminate the pool of workersadaptive_beta  
            pool.terminate(); pool.join() 

            results.loc[(trust_uninform, trust_inform)]['times'] = arrival_times
            results.loc[(trust_uninform, trust_inform)]['n_agents'] = arrival_agents
            results.loc[(trust_uninform, trust_inform)]['fails'] = fail_counter
            results.loc[(trust_uninform, trust_inform)]['seeds'] = seeds

        # results.loc[spawn_radius]['times'] = arrival_times
        # results.loc[spawn_radius]['n_agents'] = arrival_agents
        # results.loc[spawn_radius]['fails'] = fail_counter
        # results.loc[spawn_radius]['seeds'] = seeds

        # results.loc[trust]['times'] = arrival_times
        # results.loc[trust]['n_agents'] = arrival_agents
        # results.loc[trust]['fails'] = fail_counter
        # results.loc[trust]['seeds'] = seeds

        # attributes to save in results metadata
        attributes = ['Rd', 'Lx', 'heigth', 'decision_time', 'particle_dt', 'particle_rate', 'flow_dt', 'n_agents', 'speed', 
                'olfactory_radius', 'visual_radius', 'memory_time', 'sensing_noise', 'final_time', 'spawn_radius', 'source_coordinates', 
                'spawn_center', 'length', 'fluct_intensity', 'flow_lengthscale', 'flow_corr_time', 'mean_wind', 'loop_cycles']
        # add metadata to dataframe
        for attr in attributes: results.attrs[attr] = locals()[attr]
        # save to disk
        results.to_pickle(f'results/{filename}.pkl')
else:
    # initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)
    print(f'Seed = {seed}')
    # create objects
    flow = Flow(length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
    cloud = Cloud(particle_dt, particle_rate, source_coordinates, flow)
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed,
            olfactory_radius, visual_radius, memory_time, sensing_noise, trust_inform, trust_uninform, trust_decay, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, save_frames, elastic)
    # run simulation
    # arrival_time, agents_in_Rb, success = sim.run()
    arrival_time, agents_in_Rb, success, x_coords, y_coords, detections = sim.run()
    np.save('x_coords', x_coords)
    np.save('y_coords', y_coords)
    np.save('detections', detections)

# plotting functions
if real_time_plot: 
    plt.ion(); plt.show()
    if save_frames:
        import os
        os.system(f"ffmpeg -framerate 60 -start_number 1 -i 'frames085/frame%d.png' -c:v libx264 {filename}.mp4")
