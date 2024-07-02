from input_file import *
from  olfactory_lib import *
import pandas as pd
import multiprocessing as mp
import os

# ulimit -Sn unlimited

# in case we need to reload the library
import sys
from importlib import reload
reload(sys.modules['olfactory_lib'])
reload(sys.modules['input_file'])
from olfactory_lib import *
from input_file import *

def parallel_run(n):
    print(f'Running sim. {n+1}', end='\r')
    sys.stdout.write("\033[K")

    # initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)

    # create objects
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, reach_radius, memory_time, sensing_noise, wind_noise, trust, trust_inform, 
            trust_uninform, decay_time, threshold, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)

    # run simulation
    arrival_time, agents_in_Rb, success = sim.run()

    return arrival_time, agents_in_Rb, success, seed

# set global variables
set_h5_flag(read_h5)
set_pad_points(pad_points)

# check if file already exists
if parallel and os.path.isfile(f'results/{folder}/{filename}.pkl'):
    raise Warning(f'File {filename}.pkl already exists!')

# check if we are using too many CPUs
if parallel and os.cpu_count() < n_threads:
    raise Warning(f'Too many threads!')

# print info to the terminal
print(f'Filename = {filename}')
print(f'Turbulent = {turbulent}, Elastic = {elastic}')
print(f'Ts = {Ts:.2f}, N = {n_agents}, Shift = {shift}')

# create folders
os.makedirs(f'{folder}', exist_ok=True)

# create flow and odor objects
flow = Flow_turbulent(path, length)
cloud = Cloud_turbulent(flow)

# delete old frames
if save_frames and not parallel:
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
    results.to_pickle(f'{folder}/{filename}.pkl')

# do just one test run
else:
    # initialise the rng
    seed = random.randrange(sys.maxsize)
    initialise_rng(seed)
    print(f'Seed = {seed}')
    # create objects
    swarm = Swarm(n_agents, spawn_center, spawn_radius, decision_time, speed, olfactory_radius, 
            visual_radius, reach_radius, memory_time, sensing_noise, wind_noise, trust, trust_inform, 
            trust_uninform, decay_time, threshold, adaptive_beta, cloud, flow)
    sim = Simulation(final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, 
            save_frames, elastic, turbulent)
    # run simulation
    arrival_time, agents_in_Rb, success = sim.run()

# plotting stuff
if real_time_plot: 
    plt.ion(); plt.show()
    if save_frames:
        os.system(f"ffmpeg -hide_banner -loglevel error -framerate 30 -start_number 1 -i 'frames/frame%d.png' -c:v libx264 results/videos/{filename}.mp4")
        print(f'Movie saved as results/videos/{filename}.mp4')




# ----------------------------------------

vel_x = np.array([vel[0] for vel in sim.swarm.vel_t])
vel_y = np.array([vel[1] for vel in sim.swarm.vel_t])
coord_x = np.array([coord[0] for coord in sim.swarm.traj])
coord_y = np.array([coord[1] for coord in sim.swarm.traj])

# attributes to save in logfile
attributes = ['final_time', 'memory_time', 'dt', 'rd', 'n_agents', 'visual_radius', 'spawn_radius', 
        'reach_radius', 'lx', 'length', 'height', 'speed', 'spawn_center', 'source_coordinates']

# folder = f'results/casting/geometric/lx{lx:.3f}_shift{shift:.3f}/memory_time{memory_time:.3f}/dt{dt:.3f}_dec_time{decision_time:.3f}/trust{trust:.3f}'
# os.makedirs(f'{folder}', exist_ok=True)
# np.save(f'{folder}/vel_x', vel_x)
# np.save(f'{folder}/vel_y', vel_y)
# np.save(f'{folder}/coord_x', coord_x)
# np.save(f'{folder}/coord_y', coord_y)
# # save logfile
# log = {}
# for attr in attributes: log[attr] = locals()[attr]
# np.save(f'{folder}/log', log)

plt.clf()
# plt.figure()
if not real_time_plot and not parallel:
    # create axes for plotting
    # axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, length), ylim=(0, height))
    axes = plt.subplot(aspect='equal', adjustable='box')
    # add patches for source and spawn circle 
    axes.add_patch( plt.Circle(sim.swarm.spawn_center, sim.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2) )
    axes.add_patch( plt.Circle(source_coordinates, 0.2, color='k') )

    axes.axhline( source_coordinates[1], lw=1, ls='--', c='k', alpha=.2 )

    # add agents points and visual circles
    index = 0
    for agent in sim.swarm.agents:
        color_id = min([len(colors), index%len(colors)]) 
        agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[color_id], label=index)

        visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[color_id], alpha=0.1)
        # visual_circle = plt.Circle(agent.coordinates, reach_radius, fill=False, color=colors[color_id], alpha=0.1)
        axes.add_patch(agent_point); axes.add_patch(visual_circle)
        index += 1

    axes.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], lw=1)
    # axes.plot([coord[0] for coord in sim.swarm.traj], [coord[1] for coord in sim.swarm.traj], c='k', lw=1, marker='o', mfc='none', ms=3)

    # sign_changes = np.where(vel_y[:-1] * vel_y[1:] < 0 )[0] + 1 
    # max_x = coord_x[sign_changes]
    # max_y = coord_y[sign_changes]
    # axes.plot(max_x, max_y, c='r', marker='o', mfc='none', ls='')

plt.show()
