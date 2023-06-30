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
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, memory_time, sensing_noise, trust, trust_inform, trust_uninform, 
            decay_time, threshold, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)

    # run simulation
    arrival_time, agents_in_Rb, success = sim.run()

    return arrival_time, agents_in_Rb, success, seed

# plotting parameters 
real_time_plot = True
plot_flow = False
save_frames = True
pause_time = 0.001

# visual_radius = 0.1 # Ra
# visual_radius = 0.3 # Ra
# visual_radius = 0.6 # Ra
visual_radius = 1 # Ra
# visual_radius = 5 # Ra
# visual_radius = 10 # Ra

# time parameters
decision_time = 1 # Δt

# smelling threshold
threshold = 0.001

# elastic constant
kelast = 1

# vertical shift of the initial position (in perc of height/2)
shift = 0.5

# number of agents
n_agents = 100 # N

# do more runs at the same time
parallel = False
n_threads = 12 # number of threads used for parallelisation
 
# number of successful episodes to sample
n_samples = 50

# max number simulations to run to reach the sampling limit
limit = int(n_samples*50)

# use elastic recall force
elastic = True

# use a stochastic or a turbulent flow
turbulent = True

# use a different beta for informed and uninformed agents
adaptive_beta = False

# path of the turbulent flow
if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
else: path = 'flow/re280_small_source'

# trust parameter (β) values to check in a parallel run
trusts = np.round(np.arange(0.0, 1.1, 0.1),2) 

# constant trust parameter
trust = 0.85 # β

# these are relevant only if we are using an adaptive beta
trust_uninform = 0.9
trust_inform = 0.1

# decay time used both for beta and for the surging phase
decay_time = 8

Rd = 0.2 # olfactory range
Lx = 30 # distance from the source

# length of the simulation box (height is given by the flow data)
length = int(2*Lx) 

# parameters of the agents
speed = 0.2 # v0
olfactory_radius = Rd # Rd 
memory_time = 1/decision_time # inverse of λ
sensing_noise = 0.1 # eta
spawn_radius = 5 # Rb

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

# name of the output results file
filename = f'r280_ra{visual_radius}_dt{decision_time}_thr{threshold}_k{kelast}_shift{shift}_N{n_agents}'

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

# create flow and odor objects
flow = Flow_turbulent(path, length)
cloud = Cloud_turbulent(flow)

# delete old frames
if save_frames:
    import os
    os.system(f"rm -f frames/frame*.png")

# spawn position and source coordinates 
source_coordinates = cloud.source_coordinates
spawn_center = [cloud.source_coordinates[0]+Lx, flow.height/2 + shift*(flow.height/2)]

# do multiple runs in parallel
if parallel:
    # do not plot if we are doing parallel runs!
    real_time_plot = False

    # create empty dataframe to store results
    results = pd.DataFrame(index=trusts, columns=['times', 'n_agents', 'fails', 'seeds'])

    for trust in trusts:
        print(f'\nβ = {trust:.2f}')

        # initialise counters and lists
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
    attributes = ['Rd', 'Lx', 'length', 'decay_time', 'decision_time', 'n_agents', 'speed', 'olfactory_radius', 
            'visual_radius', 'memory_time', 'sensing_noise', 'final_time', 'spawn_radius', 
            'spawn_center', 'path', 'threshold', 'elastic', 'adaptive_beta', 'turbulent']
    # add metadata to dataframe
    for attr in attributes: results.attrs[attr] = locals()[attr]

    # save to disk
    results.to_pickle(f'results/{filename}.pkl')

# do just one test run
else:
    # initialise the rng
    # seed = random.randrange(sys.maxsize)
    seed = 98712391
    initialise_rng(seed)
    print(f'Seed = {seed}')
    # create objects
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, memory_time, sensing_noise, trust, trust_inform, trust_uninform, 
            decay_time, threshold, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)
    # run simulation
    arrival_time, agents_in_Rb, success = sim.run()

# plotting stuff
if real_time_plot: 
    plt.ion(); plt.show()
    if save_frames:
        os.system(f"ffmpeg -framerate 60 -start_number 1 -i 'frames/frame%d.png' -c:v libx264 {filename}.mp4")
