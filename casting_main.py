from  test_lib import *
from olfactory_plot_utils import *

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['test_lib'])
from  test_lib import *

def run_simulation():
    # initialise the rng
    # seed = random.randrange(sys.maxsize)
    seed = 667
    initialise_rng(seed)
    # create objects
    swarm = Swarm(n_agents, spawn_center, spawn_radius, speed, visual_radius, sensing_noise, wind_noise, trust, length, height, source_coordinates, reach_radius, dt, memory_time)
    sim = Simulation(final_time, swarm, real_time_plot, pause_time, save_frames)
    # run simulation
    arrival_time, count, success = sim.run()
    return arrival_time, count, success, sim 

# plotting parameters 
real_time_plot = False
save_frames = False
# pause_time = 0.001
pause_time = 1/2

final_time = 150

memory_time = 1

# dt = 1
# dt = 0.1
# dt = 0.05
# dt = 0.01
# dt = 0.005
dt = 0.001

# dt = 1
# dt = 0.5
# dt = 0.25
# dt = 0.2
# dt = 0.1
# dt = 0.05
# dt = 0.01
# dt = 0.005
# dt = 0.001
# dt = 0.0001

# trust parameter 
# trust = float(sys.argv[1])
trust = 0.5
# trust = 0.8

rd = 0.2

# if dt == 1: trust = 0.5
# elif dt == 0.5: trust = 0.6405
# elif dt == 0.25: trust = 0.78
# elif dt == 0.2: trust = 0.816
# elif dt == 0.1: trust = 0.8995

# if dt == 1: trust = 0.85
# elif dt == 0.5: trust = 0.918
# elif dt == 0.25: trust = 0.957
# elif dt == 0.2: trust = 0.9655
# elif dt == 0.1: trust = 0.9824

# number of agents
# n_agents = 100 
# n_agents = 10 
n_agents = 2 

# visual_radius = 5*rd
visual_radius = 25*rd

# body radius
spawn_radius = 25*rd # Rb

reach_radius = rd

lx = 250*rd

b = 2.5
length, height = b*lx, b*lx

# noise on the estimate of the mean wind and on public vel
sensing_noise = 0.0 # eta
wind_noise = 0.0 

# speed of the agents
speed = 0.2 

# spawn position and source coordinates 
spawn_center = [length/1.5, height/2]
source_coordinates = [spawn_center[0]-lx, height/2]
 
# -------------------------------------------------------------------------------------

# plt.figure()
# plt.clf()
# fig = plt.figure(figsize=(12,7))
arrival_time, count, success, sim  = run_simulation()
# if not real_time_plot:
    # clear current figure
    # plt.clf()
    # create axes for plotting
    # axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, length), ylim=(0, height))
    # axes = plt.subplot(aspect='equal', adjustable='box')
    # add patches for source and spawn circle 
    # axes.add_patch( plt.Circle(sim.swarm.spawn_center, sim.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2) )
    # axes.add_patch( plt.Circle(source_coordinates, 0.5, color='k') )

    # # add agents points and visual circles
    # index = 0
    # for agent in sim.swarm.agents:
    #     color_id = min([len(colors), index%len(colors)]) 
    #     # agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[color_id], label=index)
    #     agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[color_id])
    #     visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[color_id], alpha=0.1)
    #     axes.add_patch(agent_point); axes.add_patch(visual_circle)
    #     index += 1

# plt.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], c='k', lw=1)
# plt.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1, label=rf'$dt={dt}, \beta={trust}$')
# plt.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], c='k', lw=1, marker='o', mfc='none', ms=3)
# plt.scatter([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], c='k', s=1)
# plt.legend()

# plt.figure()
# plt.subplot(aspect='equal', adjustable='box')
# plt.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1, marker=' ', ms=3, label=f'riemann sum, dt={dt}')
plt.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1, marker=' ', ms=3, label=f'incremental update, dt={dt}')

# plt.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], c='r', lw=1, marker=' ', ms=3, label=f'incremental update, dt={dt}')
# plt.title(f'dt={dt}')
plt.legend()

# # add the analytical result
# t_star = int(final_time/2)
# u1 = speed*np.array([-np.sqrt(2), -np.sqrt(2)])/2
# u2 = speed*np.array([-np.sqrt(2), +np.sqrt(2)])/2
# position = np.array([86.10609261150304, 60.57261908026775])
# trajectory = []
# trajectory.append(position.copy())
# tot_time_steps = int(final_time/dt)
# for time_step in range(tot_time_steps):
#     time = dt*time_step
#     if time <= t_star:
#         priv_vel = speed*np.array([-np.sqrt(2), -np.sqrt(2)])/2 
#         publ_vel = u1*(1-np.exp(-time/memory_time))
#     else:
#         priv_vel = speed*np.array([-np.sqrt(2), np.sqrt(2)])/2 
#         publ_vel = u1*(np.exp(-time/memory_time)*(np.exp(t_star/memory_time)-1)) + u2*(1-np.exp((t_star-time)/memory_time))
#     vel = (1-trust)*priv_vel + trust*publ_vel
#     vel = speed*vel/norm(vel)
#     position += vel*dt
#     trajectory.append(position.copy())
# plt.plot([coord[0] for coord in trajectory], [coord[1] for coord in trajectory], c='r', lw=1, label='analytic')
# # plt.plot([coord[0] for coord in trajectory], [coord[1] for coord in trajectory], c='r', lw=1, marker='o', mfc='none', ms=3)
# plt.title(f'dt={dt}')
# plt.legend()

show_and_check_ipython()
# -------------------------------------------------------------------------------------

# folder = 'casting_res/dt%.2f/'%dt
# os.makedirs(f'{folder}', exist_ok=True)
# times = []
# counts = []
# successes = []
# samples = 100
# print('trust =', trust)
# for sample in np.arange(samples):
#     print(sample)
#     arrival_time, count, success, sim = run_simulation()
#     times.append(arrival_time)
#     counts.append(count)
#     successes.append(success)
# np.save('%s/n%i_times_%.2f.npy'%(folder,n_agents,trust), times)
# np.save('%s/n%i_counts_%.2f.npy'%(folder,n_agents,trust), counts)
# np.save('%s/n%i_successes_%.2f.npy'%(folder,n_agents,trust), successes)

