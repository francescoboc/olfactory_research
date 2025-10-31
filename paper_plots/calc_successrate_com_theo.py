from scipy.spatial import ConvexHull
from utils import *
from tqdm import tqdm
import os
import matplotlib.patches as mpatches

from  olfactory_lib_coordinates import *
# from input_file import *

from select_file import *

dt = 1

data_missing = False
for trust in trusts:
    if final_time == 0:
        hexbin_folder = f'../hexbins/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        com_coord_folder = f'../com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    else:
        hexbin_folder = f'../hexbins/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        com_coord_folder = f'../com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

    try:
        # success_rate = np.load(f'{hexbin_folder}/com_fulltheo_successrate_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)
        success_rate = np.load(f'{hexbin_folder}/com_fulltheo_betav0_successrate_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)

        print(f'{trust} COM success rate data already exists!')

    except:
        print(f'{trust} No COM success rate data found, computing...')
        data_missing = True

    if data_missing or OVERWRITE:
        os.makedirs(hexbin_folder, exist_ok=True)
        os.makedirs(com_coord_folder, exist_ok=True)

        # CENTER OF MASS
        count_sums = []
        sim_x_list, sim_y_list = [], []
        theo_x_list, theo_y_list = [], []
        for run_n in tqdm(range(n_runs), ascii=' █'):
        # for run_n in range(n_runs):

            ## TODO questo serve solo se vogliamo la media delle v_cm, se invece usiamo beta*v0 non serve!
            # try:
            #     # com_x_theo = np.load(f'{com_coord_folder}/run{run_n}/com_x_the.npy', allow_pickle=True)
            #     # com_y_theo = np.load(f'{com_coord_folder}/run{run_n}/com_y_theo.npy', allow_pickle=True)
            #     com_x_theo = np.load(f'{com_coord_folder}/run{run_n}/com_x_theo_betav0.npy', allow_pickle=True)
            #     com_y_theo = np.load(f'{com_coord_folder}/run{run_n}/com_y_theo_betav0.npy', allow_pickle=True)
            # except:
            #     print('No theo COM coordinates found, computing...')

            #     com_x = np.load(f'{com_coord_folder}/run{run_n}/com_x.npy', allow_pickle=True)
            #     com_y = np.load(f'{com_coord_folder}/run{run_n}/com_y.npy', allow_pickle=True)
            #     wt = np.load(f'{com_coord_folder}/run{run_n}/wt_history.npy', allow_pickle=True)

            #     # calculate velocity of center of mass
            #     x_t = [(com_x[i+1]-com_x[i])/dt for i in range(len(com_x)-1)]
            #     y_t = [(com_y[i+1]-com_y[i])/dt for i in range(len(com_y)-1)]

            #     theta_com = []
            #     normvs = []
            #     for i in range(len(x_t)):
            #         normv = norm([x_t[i], y_t[i]])
            #         normvs.append(normv)
            #         # th = np.arccos(x_t[i]/normv)
            #         th = np.arcsin(y_t[i]/normv)
            #         # th = np.arctan2(y_t[i], x_t[i])
            #         theta_com.append(th)

            #     # normv_mean = np.mean(normvs)
            #     normv_mean = trust*speed

            #     # normv_std = np.std(normvs)

            ##TODO proviamo a simulare una wt_history nuova, senza usare quella delle simulazioni (troppo corte)

            #steps = 10000

            #seed = random.randrange(sys.maxsize)
            #initialise_rng(seed)
            #cloud = None
            #swarm = Swarm(private_behavior, n_agents, spawn_radius, speed, visual_radius, 
            #        olfactoy_radius, sensing_noise, wind_noise, trust, length, height, 
            #        rand_casting_steps, rand_casting_direction, dt, memory_time, decision_time, 
            #        threshold, cloud, method, mu, sigma)

            #pos_x = [agent.coordinates[0] for agent in swarm.agents]
            #pos_y = [agent.coordinates[1] for agent in swarm.agents]
            #com_x = [np.mean(pos_x)]
            #com_y = [np.mean(pos_y)]

            #wt = []
            #for tstep in range(steps):
            #    swarm.update(tstep)

            #    pos_x = [agent.coordinates[0] for agent in swarm.agents]
            #    pos_y = [agent.coordinates[1] for agent in swarm.agents]
            #    com_x.append(np.mean(pos_x))
            #    com_y.append(np.mean(pos_y))


            #x_t = [(com_x[i+1]-com_x[i])/dt for i in range(len(com_x)-1)]
            #y_t = [(com_y[i+1]-com_y[i])/dt for i in range(len(com_y)-1)]

            #wt = swarm.wt_history
            #x_wt = [vel[0] for vel in wt]
            #y_wt = [vel[1] for vel in wt]

            #theta_wt = []
            #for i in range(len(x_wt)):
            #    normw = norm([x_wt[i], y_wt[i]])
            #    # th = np.arccos(x_wt[i]/normw)
            #    th = np.arcsin(y_wt[i]/normw)
            #    # th = np.arctan2(y_wt[i], x_wt[i])
            #    theta_wt.append(th)

            #norm_wt = np.array([norm(w) for w in wt])

            #normv_mean = speed*trust

            ## theta_com = []
            ## # normvs = []
            ## for i in range(steps):
            ##     # normv = norm([x_t[i], y_t[i]])
            ##     # normvs.append(normv)
            ##     # th = np.arccos(x_t[i]/normv)
            ##     th = np.arcsin(y_t[i]/normv_mean)
            ##     # th = np.arctan2(y_t[i], x_t[i])
            ##     theta_com.append(th)


            #theta = np.arcsin(y_t[0]/normv_mean)
            ## theta = theta_com[0]
            #theta_theo = [theta]
            #for t in range(steps-1):
            #    theta_dot = ((1-trust)/dt) * norm_wt[t]/speed * np.sin(theta_wt[t] - theta_theo[t])
            #    theta += theta_dot*dt
            #    theta_theo.append(theta)

            #com_x_theo, com_y_theo = [com_x[0]], [com_y[0]]
            #new_x, new_y = com_x_theo[0].copy(), com_y_theo[0].copy()
            #for t in range(steps):
            #    angle = theta_theo[t]
            #    new_x += normv_mean*np.cos(angle)
            #    new_y += normv_mean*np.sin(angle)
            #    com_x_theo.append(new_x)
            #    com_y_theo.append(new_y)

            ## sim_x_list.append(com_x)
            ## sim_y_list.append(com_y)
            ## theo_x_list.append(com_x_theo)
            ## theo_y_list.append(com_y_theo) 

            ## save theoretical coordinates in run folder
            ## np.save(f'{com_coord_folder}/run{run_n}/com_x_theo.npy', com_x_theo)
            ## np.save(f'{com_coord_folder}/run{run_n}/com_y_theo.npy', com_y_theo)
            #np.save(f'{com_coord_folder}/run{run_n}/com_x_theo_betav0.npy', com_x_theo)
            #np.save(f'{com_coord_folder}/run{run_n}/com_y_theo_betav0.npy', com_y_theo)




            com_x_theo = np.load(f'{com_coord_folder}/run{run_n}/com_x_theo_betav0.npy')
            com_y_theo = np.load(f'{com_coord_folder}/run{run_n}/com_y_theo_betav0.npy')

            # some simulations failed (dunno why) so we have to filter them out...
            if not np.isnan(com_x_theo[1]):

                # # NB if these are not available, just run calc_successrate_com first!
                # com_x_std = np.load(f'{com_coord_folder}/run{run_n}/com_x_std.npy', allow_pickle=True)
                # com_y_std = np.load(f'{com_coord_folder}/run{run_n}/com_y_std.npy', allow_pickle=True)

                # use theoretical std
                com_y_std = np.load(f'{com_coord_folder}/com_y_std_teho.npy', allow_pickle=True)
                com_x_std = spawn_radius/2

                # create an empty hexbin to get grid structure
                hb = plt.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y])
                hex_centers_x = hb.get_offsets()[:, 0]
                hex_centers_y = hb.get_offsets()[:, 1]
                plt.close()

                # initialize an array to accumulate counts
                bin_values = np.zeros(len(hex_centers_x))

                # loop through each timestep to build ellipses
                # min_tsteps = min(len(com_y_std), len(com_x_theo))
                for t in range(len(com_x_theo)):
                # for t in range(len(com_y_std)):
                # for t in range(min_tsteps):
                    # parameters of the ellipse
                    x0, y0 = com_x_theo[t], com_y_theo[t]
                    # a, b = com_x_std[t]*2, com_y_std[t]*2
                    a, b = com_x_std*2, com_y_std[t]*2

                    # check which hexbin centers fall within the ellipse
                    inside_ellipse = ((hex_centers_x - x0) / a) ** 2 + ((hex_centers_y - y0) / b) ** 2 <= 1
                    bin_values[inside_ellipse] = 1  # assign count = 1 to the bins inside the ellipse

                    # # visualise the ellipse and the selected centers (for debugging)
                    # if run_n == 0 and t == 0:
                    #     fig, ax = plt.subplots()
                    #     add_decorations()
                    #     ax.scatter(hex_centers_x, hex_centers_y, color='lightgrey')
                    #     ax.scatter(hex_centers_x[inside_ellipse], hex_centers_y[inside_ellipse], color='red', s=20)
                    #     ellipse = mpatches.Ellipse((x0, y0), 2*a, 2*b, edgecolor='blue', facecolor='none')
                    #     ax.add_patch(ellipse)

                count_sums.append(bin_values)

            else:
                print(f'simulation {run_n} failed')

            total_sum = np.sum(count_sums, axis=0)
            success_rate = total_sum/len(count_sums)

        # success_rate.dump(f'{hexbin_folder}/com_fulltheo_successrate_gridsize{gridsize}_offset{offset}.npy')
        success_rate.dump(f'{hexbin_folder}/com_fulltheo_betav0_successrate_gridsize{gridsize}_offset{offset}.npy')

        # plt.figure()
        # hb = plt.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y], cmap='plasma')
        # # create a mask for bins where the x-coordinate is less than a threshold
        # x_threshold = final_x
        # bin_coords = hb.get_offsets()  
        # x_edges, y_edges = bin_coords.T
        # mask_below_threshold = x_edges > x_threshold
        # success_rate[mask_below_threshold] = 0
        # hb.set_array(success_rate)
        # # hb.set_clim(np.min(success_rate), np.max(success_rate))  
        # hb.set_clim(0,1)  
        # # set background (non-explored parts of space) same color as min of colorbar
        # cb = plt.colorbar(hb, label=r'Average succcess rate $\rho$')
        # plt.gca().set_facecolor(cb.cmap(0))
        # plt.title(rf'$\beta={trust}$')
        # show_and_check_ipython()

