import numpy as np 

folder = 'turbulent/maxt_100ts'

# plotting parameters 
real_time_plot = True
plot_flow = False
save_frames = False
pause_time = 0.001

# read h5 flow file or local npy file
read_h5 = False

# visual_radius = 0.1 # Ra
visual_radius = 0.5 # Ra
# visual_radius = 1 # Ra
# visual_radius = 5 # Ra
# visual_radius = 10 # Ra

# vertical shift of the initial position (in perc of height/2)
shift = 0.0

reach_radius = 0.4

# time parameters
decision_time = 1 # Δt

# smelling threshold
threshold = 0.0008

# elastic constant
kelast = 1

# number of agents
n_agents = 100 # N

# do more runs at the same time
parallel = False
n_threads = 6 # number of threads used for parallelisation
 
# number of successful episodes to sample
n_samples = 50

# constant trust parameter
trust = 0.85 # β

# max number simulations to run to reach the sampling limit
limit = int(n_samples*10)

# use elastic recall force
elastic = True

# use a stochastic or a turbulent flow
turbulent = True

# use a different beta for informed and uninformed agents
adaptive_beta = False

# trust parameter (β) values to check in a parallel run
trusts = np.round(np.arange(0.0, 1.1, 0.1),2) 

# these are relevant only if we are using an adaptive beta
trust_uninform = 0.9
trust_inform = 0.1

# decay time used both for beta and for the surging phase
decay_time = 8

Rd = 0.4 # olfactory range
Lx = 50 # distance from the source

# length of the simulation box (height is given by the flow data)
length = 100

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

# path of the turbulent flow
if read_h5: path = '/storage/boccardo/odor_data_re280_small_source/r280_small_source.h5'
else: path = 'flow/re280_small_source'

