from utils import *
from select_file import *
import os

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}, n_ag={n_agents}')
print()

for trust in trusts:
    if final_time == 0:
        coord_folder = f'../storage/coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
        com_coord_folder = f'com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    else:
        coord_folder = f'../storage/coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'
        com_coord_folder = f'com_coordinates/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

    all_good = True
    for run_n in range(n_runs):
        try: np.load(f'{com_coord_folder}/run{run_n}/wt_history.npy')
        except: all_good = False

    if all_good and not OVERWRITE: 
        print(f'{trust} wt_history in com_coord_folder already exists for all runs!')

    else:
        for run_n in range(n_runs):
            try:
                # copy wt_history into com_coord_folder (will be used for theoretical traj)
                wt_history = np.load(f'{coord_folder}/run{run_n}/wt_history.npy', allow_pickle=True)
                os.makedirs(f'{com_coord_folder}/run{run_n}', exist_ok=True)
                np.save(f'{com_coord_folder}/run{run_n}/wt_history', wt_history)
            except:
                print(f'wt_history in coord_folder does not exist!')
                print(f'coord_folder: {coord_folder}')
                exit()
        print(f'{trust} wt_history copied from coord_folder to com_coord_folder for all runs!')
