from  olfactory_lib import *
import pandas as pd
import multiprocessing as mp
import os

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
from olfactory_lib import *

bias = 0.0
print(bias)

def beta_run(trust):
    print(f'β = {trust:.2f}')
    # create objects
    if turbulent:
        flow = Flow_turbulent(z_coord, length)
        cloud = Cloud_turbulent(threshold, flow)
        # spawn_center = [length/2, height/4]
    else:
        flow = Flow_stochastic(length, height, npoints_x, npoints_y, flow_dt, flow_lengthscale, 
                flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
        cloud = Cloud_of_particles(particle_dt, particle_rate, source_coordinates, flow)
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, memory_time, sensing_noise, trust, trust_inform, trust_uninform, 
            decay_time, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)

    order_param = sim.run_random(bias)
    # np.save(f'results/random_walk/{n_agents}/{trust}.npy', order_param)
    # np.save(f'results/random_walk/bias_{bias}/{n_agents}/{trust}.npy', order_param)
    np.save(f'results/random_walk_noPBC/bias_{bias}/{n_agents}/run{nrun}/{trust}.npy', order_param)
    return 

nrun = 0

# plotting parameters 
real_time_plot = True
plot_flow = False
save_frames = False
pause_time = 0.001

# name of the output results file
filename = 'random_transition'

# do more runs at the same time
parallel = True
n_threads = 2 # number of threads used for parallelisation

# use elastic recall force
elastic = False

# use a different beta for informed and uninformed agents
adaptive_beta = False

# use a stochastic or a turbulent flow
turbulent = False

# parameters of the turbulent flow
# available heights = 0.15, 0.5, 1.0, 1.5
z_coord = 1
# smelling threshold
threshold = 0.02

# trust parameter (β) values to check in a parallel run
# trusts = np.round(np.arange(0.05, 1, 0.05),2) 
# trusts = np.round(np.arange(0.0, 1.05, 0.05),2)

trusts = np.append(np.round(np.arange(0.0, 0.85, 0.05),2), np.round(np.arange(0.81, 1.01, 0.01),2))

# # trust parameter (β) values to check if using an adaptive beta
# trusts_inf = np.round(np.arange(0.0, 1, 0.1),2) 
# trusts_uninf = np.round(np.arange(0.8, 1, 0.02),2) 

# constant trust parameter
# trust = 0.0 # β
trust = 1.0 # β

# these are relevant only if we are using an adaptive beta
trust_uninform = 0.9
trust_inform = 0.1

# decay time used both for beta and for the surging phase
decay_time = 4

Rd = 0.2 # olfactory range
# Lx = 250*Rd # distance from the source
Lx: int = 50 # distance from the source

# size of the simulation box
length: int = 50
height: int = 50

# # size of the simulation box
# length = int(2*Lx) 
# # length = 150
# height = int(length/2)

# number of grid points for the stochastic flow
npoints_x = length
npoints_y = height

# time parameters
decision_time: int = 1 # Δt

# 40, 100, 400, 4000
# parameters of the agents
n_agents: int = 100 # N
speed = 0.2 # v0
olfactory_radius = Rd # Rd 
visual_radius = 5*Rd # Ra
memory_time = 1/decision_time # inverse of λ
sensing_noise = 0.0 # eta
spawn_radius = 25*Rd # Rb

# parameters of the particle cloud
particle_dt = decision_time/10 # δt
particle_rate: int = 10 # J
flow_dt = particle_dt

# parameters of the stochastic flow
fluct_intensity = 0.42
flow_lengthscale: int = 10
flow_corr_time: int = 5
mean_wind = [1, 0]
loop_cycles: int = 10

# max duration of the simulation
Ts = Lx/speed # straight-path time
# final_time = 10*Ts 
final_time: int = 5000

# spawn position and source coordinates 
source_coordinates = [int(length/2 - Lx/2), height/2]
spawn_center = [length/2, height/2]

# check if we are using too many CPUs
if parallel and os.cpu_count() < n_threads:
    raise Warning(f'Too many threads!')

# print info to the terminal
print(f'Filename = {filename}')
print(f'Turbulent = {turbulent}, Elastic = {elastic}')
print(f'Ts = {Ts:.2f}, N = {n_agents}')

# create folders
os.makedirs('results', exist_ok=True); os.makedirs('frames', exist_ok=True)
# os.makedirs(f'results/random_walk/{n_agents}', exist_ok=True)
# os.makedirs(f'results/random_walk/bias_{bias}/{n_agents}', exist_ok=True)
os.makedirs(f'results/random_walk_noPBC/bias_{bias}/run{nrun}/{n_agents}', exist_ok=True)

# initialise the rng
seed = random.randrange(sys.maxsize)
initialise_rng(seed)
print(f'Seed = {seed}')

if not parallel:
    # create objects
    if turbulent:
        flow = Flow_turbulent(z_coord, length)
        cloud = Cloud_turbulent(threshold, flow)
        spawn_center = [length/2, height/4]
    else:
        flow = Flow_stochastic(length, height, npoints_x, npoints_y, flow_dt, flow_lengthscale, 
                flow_corr_time, mean_wind, fluct_intensity, loop_cycles)
        cloud = Cloud_of_particles(particle_dt, particle_rate, source_coordinates, flow)

    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, memory_time, sensing_noise, trust, trust_inform, trust_uninform, 
            decay_time, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)
    # run simulation
    order_param  = sim.run_random()

else:
    real_time_plot = False
    # create and run a pool of parallel workers
    pool = mp.Pool(processes = n_threads)
    pool.map(beta_run, trusts)
    # close the pool of workers
    pool.close(); pool.join()

# plotting functions
if real_time_plot: 
    plt.ion(); plt.show()
    if save_frames:
        import os
        os.system(f"ffmpeg -framerate 60 -start_number 1 -i 'frames/frame%d.png' -c:v libx264 {filename}.mp4")
