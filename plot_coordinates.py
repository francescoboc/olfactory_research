from utils import *

rd = 0.2
spawn_radius = 25*rd 

# visual_radius = 5*rd
visual_radius = 2*spawn_radius

# trust parameter aka beta
# trust = 0.4
# trust = 0.5
trust = 0.6
# trust = 0.7
# trust = 0.8
# trust = 0.9
# trust = 1.0

n_sim = 10
n_ag = 100
max_t = 1000

plt.figure()
# for run_n in range(n_sim):
for run_n in range(1):
    coord_folder = f'coordinates/detection_cone/vr{visual_radius}/trust{trust}'
    coord_x = np.load(f'{coord_folder}/run{run_n}/coord_x.npy', allow_pickle=True).item()
    coord_y = np.load(f'{coord_folder}/run{run_n}/coord_y.npy', allow_pickle=True).item()

    for n in range(n_ag):
        plt.plot(coord_x[n], coord_y[n], color=colors[run_n], alpha=0.3)

    # calculate coordinates of center of mass
    com_x, com_y = [], []
    for t in range(max_t+1):
        com_x.append(np.mean([coord_x[n][t] for n in range(n_ag)]))
        com_y.append(np.mean([coord_y[n][t] for n in range(n_ag)]))

    # plt.plot(com_x, com_y, color='k', zorder=3)
    # plt.plot(com_x, com_y, color=colors[run_n], alpha=0.3, zorder=3)

plt.title(fr'$\beta=${trust}, $r_v=${visual_radius}')
plt.gca().set_aspect('equal')
plt.ylim(735, 810)
plt.xlim(800, 1015)

show_and_check_ipython()
