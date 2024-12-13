from utils import *
from select_file import *
import os

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, v_r={visual_radius}')

if final_time == 0:
    dicts_folder = f'beta_dicts/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'
else:
    dicts_folder = f'beta_dicts/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_t{final_time}'

os.makedirs(dicts_folder, exist_ok=True)

prob_betas, rate_betas, fpt_betas = {}, {}, {}
for trust in trusts:
    if final_time == 0:
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}/trust{trust}'
    else:
        hexbin_folder = f'hexbins/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_time{final_time}/trust{trust}'

    data_found = True
    try:
        probability = np.load(f'{hexbin_folder}/probability_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)
    except:
        data_found = False
        print(f'Probability missing for trust {trust}')
        break

    try:
        success_rate = np.load(f'{hexbin_folder}/successrate_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)
    except:
        data_found = False
        print(f'Success rate missing for trust {trust}')
        break

    try:
        avg_fpt = np.load(f'{hexbin_folder}/avg_fpt_gridsize{gridsize}_offset{offset}.npy', allow_pickle=True)
    except:
        data_found = False
        print(f'FPT missing for trust {trust}')
        break

    if data_found:
        prob_betas[trust] = probability
        rate_betas[trust] = success_rate
        fpt_betas[trust] = avg_fpt

if data_found:
    np.save(f'{dicts_folder}/prob_betas_gridsize{gridsize}_offset{offset}', prob_betas)
    np.save(f'{dicts_folder}/rate_betas_gridsize{gridsize}_offset{offset}', rate_betas)
    np.save(f'{dicts_folder}/fpt_betas_gridsize{gridsize}_offset{offset}', fpt_betas)
    print('Lists saved!')
