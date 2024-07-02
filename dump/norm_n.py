from input_file import *
from  olfactory_lib import *
import pandas as pd
import multiprocessing as mp
import os

set_h5_flag(read_h5)

# create flow and odor objects
flow = Flow_turbulent(path, length)
cloud = Cloud_turbulent(flow)

# spawn position and source coordinates 
source_coordinates = cloud.source_coordinates
spawn_center = [cloud.source_coordinates[0]+Lx, flow.height/2 + shift*(flow.height/2)]

threshold = 0.0008

olfactory_radius = 5.0 # Rd 

# trust = 0.2 # β

visual_radius = 1000 # Ra

speed = 1

n_agents = 100

# max duration of the simulation
Ts = Lx/speed # straight-path time
final_time = 50*Ts 

mean_norms, std_norms, ns = [], [], []
# for n_agents in np.arange(1,85,5):
for trust in np.arange(0,1.01,0.01):
# for olfactory_radius in np.arange(0,10.1,0.1):
    # print(n_agents)
    print(trust)
    # print(olfactory_radius)

    #initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)
    # print(f'Seed = {seed}')
    # create objects
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, reach_radius, memory_time, sensing_noise, trust, trust_inform, trust_uninform, 
            decay_time, threshold, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)
    # run simulation
    arrival_time, agents_in_Rb, success = sim.run()

    mean_norms.append(np.mean(swarm.norms))
    std_norms.append(np.std(swarm.norms))

    # ns.append(n_agents)
    ns.append(trust)
    # ns.append(olfactory_radius)

plt.scatter(ns, mean_norms)
# plt.xlabel(r'$N$ agents')
plt.xlabel(r'$\beta$')
# plt.xlabel(r'$R_o$')
plt.ylabel(r'$<||\sum v_j ||$>')
p = np.polyfit(ns, mean_norms, deg=1)
plt.plot(np.arange(0, max(ns), 0.01), p[1] + p[0]*np.arange(0, max(ns), 0.01), ls='--', color='k', lw=1) 
plt.title(f'fit: $y={p[1]:.2f} + {p[0]:.2f}x$')
# plt.savefig(f'results/norm_n_mean_fit_speed{speed}_thr{threshold}_ro{olfactory_radius}_beta{trust}.png', dpi=300)
plt.savefig(f'results/norm_beta_mean_fit_speed{speed}_thr{threshold}_ro{olfactory_radius}_n{n_agents}.png', dpi=300)
# plt.savefig(f'results/norm_ro_mean_fit_speed{speed}_thr{threshold}_beta{trust}_n{n_agents}.png', dpi=300)
plt.close()

plt.scatter(ns, std_norms)
# plt.xlabel(r'$N$ agents')
plt.xlabel(r'$\beta$')
# plt.xlabel(r'$R_o$')
plt.ylabel(r'$std(|\sum v_j ||)$')
# plt.savefig(f'results/norm_n_mean_fit_speed{speed}_thr{threshold}_ro{olfactory_radius}_beta{trust}.png', dpi=300)
plt.savefig(f'results/norm_beta_std_speed{speed}_thr{threshold}_ro{olfactory_radius}_n{n_agents}.png', dpi=300)
# plt.savefig(f'results/norm_ro_std_speed{speed}_thr{threshold}_beta{trust}_n{n_agents}.png', dpi=300)
plt.close()
