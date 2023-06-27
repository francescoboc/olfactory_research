from  olfactory_lib import *
import pandas as pd
import multiprocessing as mp
import os

# ulimit -Sn unlimited

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *

def parallel_run(n):
    print(f'Running sim. {n+1}', end='\r')
    sys.stdout.write("\033[K")
    # initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)

    # create objects
    if turbulent:
        flow = Flow_turbulent(path, length)
        cloud = Cloud_turbulent(flow)
        # spawn_center = [cloud.source_coordinates[0]+Lx, flow.height/2]
    else:
        flow = Flow_stochastic(length, height, npoints_x, npoints_y, flow_dt, flow_lengthscale, 
                flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
        cloud = Cloud_of_particles(particle_dt, particle_rate, source_coordinates, flow)

    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, memory_time, sensing_noise, trust, trust_inform, trust_uninform, 
            decay_time, threshold, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)

    # run simulation
    arrival_time, agents_in_Rb, success = sim.run()

    return arrival_time, agents_in_Rb, success, seed

# TODO reflection boundary conditions (or better not?)
# TODO initial amplitudes of noise? -> not needed for the trubulent flow
# TODO beta=1 doesn't make sense (?) -> it does if we initialise the velocities (e.g. random)!
# TODO save data periodically (just in case) 
# TODO fai andare ancora un po' la sim con elastic=True per far si che tutti gli agenti arrivino a destinazione -> just remove this parameter from evaluation (?)
# TODO vary eta and Lx

# plotting parameters 
real_time_plot = True
plot_flow = False
save_frames = False
pause_time = 0.001

visual_radius = 5 # Ra

# time parameters
decision_time = 1 # Δt

shift = 0.0

# smelling threshold
threshold = 0.001

# name of the output results file
# filename = f'r280_ra{visual_radius}_dt{decision_time}_thr{threshold}_k1'
filename = f'testshift'

# do more runs at the same time
parallel = False
n_threads = 10 # number of threads used for parallelisation
 
# number of successful episodes to sample
n_samples = 10

# use elastic recall force
elastic = True

# use a stochastic or a turbulent flow
turbulent = True

# use a different beta for informed and uninformed agents
adaptive_beta = False

# parameters of the turbulent flow
# path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
path = 'flow/re280_small_source'

# trust parameter (β) values to check in a parallel run
trusts = np.round(np.arange(0.05, 1.05, 0.05),2) 

# # trust parameter (β) values to check if using an adaptive beta
# trusts_inf = np.round(np.arange(0.0, 1, 0.1),2) 
# trusts_uninf = np.round(np.arange(0.0, 1, 0.1),2) 
# # trusts_uninf = np.round(np.arange(0.8, 1, 0.02),2) 

# constant trust parameter
# trust = 0.85 # β
trust = 0.5 # β

# these are relevant only if we are using an adaptive beta
trust_uninform = 0.9
trust_inform = 0.1

# decay time used both for beta and for the surging phase
decay_time = 8

Rd = 0.2 # olfactory range
Lx = 250*Rd # distance from the source

# size of the simulation box
length = int(2*Lx) 
# length = 150
height = int(length/2)

# number of grid points for the stochastic flow
npoints_x = int(length)
npoints_y = int(height)

# parameters of the agents
n_agents = 10 # N
speed = 0.2 # v0
olfactory_radius = Rd # Rd 
# visual_radius = 5*Rd # Ra
memory_time = 1/decision_time # inverse of λ
sensing_noise = 0.1 # eta
spawn_radius = 25*Rd # Rb

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

# max duration of the simulation
Ts = Lx/speed # straight-path time
final_time = 10*Ts 

# spawn position and source coordinates 
source_coordinates = [int(length/2 - Lx/2), height/2]
spawn_center = [source_coordinates[0]+Lx, height/2 + shift*(height/2)]

# check if file already exists
if parallel and os.path.isfile(f'results/{filename}.pkl'):
    raise Warning(f'File {filename}.pkl already exists!')

# check if we are using too many CPUs
if parallel and os.cpu_count() < n_threads:
    raise Warning(f'Too many threads!')

# print info to the terminal
print(f'Filename = {filename}')
print(f'Turbulent = {turbulent}, Elastic = {elastic}')
print(f'Ts = {Ts:.2f}, N = {n_agents}')

# create folders
os.makedirs('results', exist_ok=True); os.makedirs('frames', exist_ok=True)

if not parallel:
    # initialise the rng
    # seed = random.randrange(sys.maxsize)
    seed = 8771123456127782765
    initialise_rng(seed)
    print(f'Seed = {seed}')
    # create objects
    if turbulent:
        flow = Flow_turbulent(path, length)
        cloud = Cloud_turbulent(flow)
        spawn_center = [cloud.source_coordinates[0]+Lx, flow.height/2 + shift*(flow.height/2)]
    else:
        flow = Flow_stochastic(length, height, npoints_x, npoints_y, flow_dt, flow_lengthscale, 
                flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
        cloud = Cloud_of_particles(particle_dt, particle_rate, source_coordinates, flow)

    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, memory_time, sensing_noise, trust, trust_inform, trust_uninform, 
            decay_time, threshold, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)
    # run simulation
    arrival_time, agents_in_Rb, success = sim.run()

else:
    # max number simulations to run to reach the sampling limit
    limit = int(n_samples*50) 
    # do not plot if we are doing parallel runs!
    real_time_plot = False
    if adaptive_beta:
        multiindex = pd.MultiIndex.from_product([trusts_uninf, trusts_inf], names=['trust_uninf', 'trust_inf'])
        results = pd.DataFrame(index=multiindex, columns=['times', 'n_agents', 'fails', 'seeds'])
        for trust_uninform in trusts_uninf:
            for trust_inform in trusts_inf:
                print(f'\nβ_u = {trust_uninform:.2f}, β_i = {trust_inform:.2f}')
                arrival_times, arrival_agents, seeds = [], [], []
                fail_counter, success_counter = 0, 0

                # create and run a pool of parallel workers
                pool = mp.Pool(processes = n_threads)
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

    else:
        results = pd.DataFrame(index=trusts, columns=['times', 'n_agents', 'fails', 'seeds'])
        for trust in trusts:
            print(f'\nβ = {trust:.2f}')
            arrival_times, arrival_agents, seeds = [], [], []
            fail_counter, success_counter = 0, 0

            # create and run a pool of parallel workers
            pool = mp.Pool(processes = n_threads)
            for arrival_time, agents_in_Rb, success, seed in pool.imap_unordered(parallel_run, range(limit)):
                # save seed of the rng
                seeds.append(seed)

                # if the run was successfull, save results into the dataframe
                if success:
                    arrival_times.append(arrival_time)
                    arrival_agents.append(agents_in_Rb)
                    success_counter += 1
                # otherwise, increase fail cunter
                else:
                    fail_counter += 1

                # if we reached the desired number of samples, stop
                if success_counter == n_samples:
                    break

            # terminate the pool of workers
            pool.terminate(); pool.join() 

            # save results in dataframe
            results.loc[trust]['times'] = arrival_times
            results.loc[trust]['n_agents'] = arrival_agents
            results.loc[trust]['fails'] = fail_counter
            results.loc[trust]['seeds'] = seeds

    # attributes to save in results metadata
    if turbulent:
        attributes = ['Rd', 'Lx', 'length', 'decay_time', 'decision_time', 'n_agents', 'speed', 'olfactory_radius', 
                'visual_radius', 'memory_time', 'sensing_noise', 'final_time', 'spawn_radius', 'source_coordinates', 
                'spawn_center', 'path', 'threshold', 'elastic', 'adaptive_beta', 'turbulent']
    else:
        attributes = ['Rd', 'Lx', 'length', 'height', 'npoints_x', 'npoints_y', 'decay_time', 'decision_time', 'particle_dt', 
                'particle_rate', 'flow_dt', 'n_agents', 'speed', 'olfactory_radius', 'visual_radius', 'memory_time', 'sensing_noise', 
                'final_time', 'spawn_radius', 'source_coordinates', 'spawn_center', 'fluct_intensity', 'flow_lengthscale', 
                'flow_corr_time', 'mean_wind', 'loop_cycles', 'elastic', 'adaptive_beta', 'turbulent']
    # add metadata to dataframe
    for attr in attributes: results.attrs[attr] = locals()[attr]
    # save to disk
    results.to_pickle(f'results/{filename}.pkl')

# plotting functions
if real_time_plot: 
    plt.ion(); plt.show()
    if save_frames:
        import os
        os.system(f"rm -f frames/frame*.png'")
        os.system(f"ffmpeg -framerate 60 -start_number 1 -i 'frames/frame%d.png' -c:v libx264 {filename}.mp4")
