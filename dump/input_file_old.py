import numpy as np 

# folder where the output file is saved
# folder = 'results/turbulent/no_noise'
folder = 'results/turbulent/decision_time'

# pad points to extend the simulation box
pad_points = 200

# plotting parameters 
real_time_plot = False
plot_flow = False
save_frames = False
pause_time = 0.001

# read h5 flow file or local npy file
read_h5 = False

Rd = 0.2 # olfactory range
Lx = 50 # distance from the source

visual_radius = 5*Rd # Ra

# vertical shift of the initial position (in perc of height/2)
shift = 0.0

# radius within which the source is seen by the agents
reach_radius = 0.4

# time parameters
# decision_time = 0.2 # Δt
decision_time = 1 # Δt

# smelling threshold
# threshold = 0.0008
threshold = 0.8

# elastic constant
kelast = 1

# number of agents
# n_agents = 100 # N
n_agents = 10 # N

# do more runs at the same time
parallel = False
n_threads = 10 # number of threads used for parallelisation
 
# number of successful episodes to sample
n_samples = 10

# constant trust parameter
# trust = 0.85 # β
trust = 0.1 # β

# max number simulations to run to reach the sampling limit
limit = int(n_samples*10)

# use elastic recall force
elastic = False

# use a stochastic or a turbulent flow
turbulent = True

# use a different beta for informed and uninformed agents
adaptive_beta = False

# trust parameter (β) values to check in a parallel run
# trusts = np.round(np.arange(0.0, 1.1, 0.1),2) 
trusts = np.round(np.arange(0.5, 1.0, 0.01),2) 

# these are relevant only if we are using an adaptive beta
trust_uninform = 0.9
trust_inform = 0.1

# decay time used both for beta and for the surging phase
decay_time = 8

# length of the simulation box (height is given by the flow data)
length = 100

# parameters of the agents
speed = 0.2 # v0
olfactory_radius = Rd # Rd 
memory_time = 1/decision_time # inverse of λ
# sensing_noise = 0.1 # eta
sensing_noise = 0.0 # eta
# wind_noise = 0.1 # noise on the estimate of the mean wind
wind_noise = 0.0 # noise on the estimate of the mean wind
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
# final_time = 100*Ts 
final_time = 100 

# name of the output results file
# filename = f'r280_ra{visual_radius}_dt{decision_time}_thr{threshold}_k{kelast}_shift{shift}_N{n_agents}'
filename = f'r280_ra{visual_radius}_dt{decision_time}_thr{threshold}_k{kelast}_shift{shift}_N{n_agents}_snoise{sensing_noise}_wnoise{wind_noise}'
# filename = f'free_ra{visual_radius}_dt{decision_time}_thr{threshold}_k{kelast}_shift{shift}_N{n_agents}_snoise{sensing_noise}_wnoise{wind_noise}'

# path of the turbulent flow
if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
else: path = 'flow/re280_small_source'

