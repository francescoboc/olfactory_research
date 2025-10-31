from  olfactory_lib_firstpassage import *
from utils import *
from select_file import *
from tqdm import tqdm
import os

col = 0
visual_radius = 100*spawn_radius

for trust in trusts:

    # SIMULATION:
    # for trust in trusts:
    # for trust in [0.7]:

    com_y_std_list = []
    for run_n in range(n_runs):
        if final_time == 0:
            com_coord_folder = f'../com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        else:
            com_coord_folder = f'../com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

        # com_x_std = np.load(f'{com_coord_folder}/run{run_n}/com_x_std.npy', allow_pickle=True)
        com_y_std = np.load(f'{com_coord_folder}/run{run_n}/com_y_std.npy', allow_pickle=True)

        com_y_std_list.append(com_y_std)

    # if trust == 0.1: timesteps = len(com_x_std)
    # timesteps = len(com_y_std)

    mean_com_y_std = np.mean(truncate_and_stack(com_y_std_list),axis=0)
    std_com_y_std = np.std(truncate_and_stack(com_y_std_list),axis=0)

    # timesteps = len(mean_com_y_std)
    timesteps = 100000


    # THEORY:
     # ----------- calculate a reference casting trajectory -----------
    y_cs_theo_list = []
    for run_n in range(n_runs):
        private_behavior = 'cast_and_surge'
        olfactoy_radius = rd
        rand_casting_direction = False
        sensing_noise = 0.0 # eta
        length, height = 500, 500
        source_coordinates = [75, 0]
        reach_radius = visual_radius
        threshold = np.inf
        method = 'no_kernel' 
        decision_time = 1
        dt = decision_time
        memory_time = 1.0 *decision_time
        wind_noise = 0.0 
        cloud = None
        seed = random.randrange(sys.maxsize)
        initialise_rng(seed)
        swarm = Swarm(private_behavior, n_agents, spawn_radius, speed, visual_radius, 
                olfactoy_radius, sensing_noise, wind_noise, trust, length, height, 
                source_coordinates, reach_radius, 
                rand_casting_steps, rand_casting_direction, dt, memory_time, decision_time, 
                threshold, cloud, method, mu, sigma)

        agent = swarm.agents[0]
        x_cs, y_cs = 0, 0
        x_cs_hist, y_cs_hist = [x_cs], [y_cs]

        for t in range(timesteps+rand_casting_steps):
            agent.cast(t)

            v_x = agent.private_velocity[0]
            x_cs += v_x*dt
            v_y = agent.private_velocity[1]
            y_cs += v_y*dt

            x_cs_hist.append(x_cs)
            y_cs_hist.append(y_cs)
        com_y_std_list.append(y_cs_hist)

        y_cs_2 = []
        for t in range(timesteps):
            int_s = 0
            for tau in range(rand_casting_steps):
                int_s += (y_cs_hist[t+tau] - y_cs_hist[tau])**2
            y_cs_2.append(int_s)
        y_cs_2 = np.array(y_cs_2)/rand_casting_steps

        # y_cs_2 *= (1-trust)**2/(trust**2+(1-trust)**2)
        y_cs_2 *= (1 + 2*trust*(1-trust))*(1-trust)**2
        # y_cs_2 *= (1 + 2*trust*(1-trust) + trust**2*(1-trust)**2)*(1-trust)**2

        y_cs_2 += (spawn_radius/2)**2

        y_cs_theo = np.sqrt(y_cs_2)

        y_cs_theo_list.append(y_cs_theo)

    mean_y_cs_theo= np.mean(truncate_and_stack(y_cs_theo_list),axis=0)
    std_y_cs_theo = np.std(truncate_and_stack(y_cs_theo_list),axis=0)

    np.save(f'{com_coord_folder}/com_y_std_teho', y_cs_theo)
    print(com_coord_folder)

     # ----------- ----------- ----------- ----------- -----------

    # shaded_errorbar(range(len(mean_com_y_std)), mean_com_y_std, yerr=std_com_y_std, label=fr'Simulation', color='b', marker='')

    # shaded_errorbar(range(len(mean_y_cs_theo)), mean_y_cs_theo, yerr=std_y_cs_theo, label=fr'Theory', color='k', marker='', ls='--')

    # # plt.plot(mean_y_cs_theo, label=fr'$\beta={trust}$, theory', ls='--')

    # col += 1


    # # y_cs_2 = []
    # # for T in range(timesteps - 100):
    # #     int_s = 0
    # #     for s in range(T,T+100):
    # #         int_s += y_cs_hist[s]**2
    # #     int_tau = 0
    # #     for tau in range(100): 
    # #         int_tau += y_cs_hist[T+tau]*y_cs_hist[tau]
    # #     y_cs_2.append(int_s/100 - int_tau/50)
    # # y_cs_2 = np.array(y_cs_2)

    # # # take square root of variance to get standard deviation
    # # y_cs_2 = np.sqrt(np.abs(y_cs_2))

    # # # add std at time 0 (uniformly random distributed points in a circle)
    # # # y_cs_2 += spawn_radius/2
    # # y_cs_2 += (spawn_radius/2)**2

    # # plt.plot(y_cs_2, c='k', label='theory')

    # plt.legend()
    # plt.xlabel('$t$')
    # plt.ylabel(r'$\sigma_y$ (average over 50 runs)')

    # plt.title(rf'$\beta={trust}$')

    # show_and_check_ipython()
