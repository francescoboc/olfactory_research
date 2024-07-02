from olfactory_plot_utils import *
import matplotlib.pyplot as plt
import numpy as np

def norm(vector):
    return (vector[0]**2 + vector[1]**2)**0.5

rd = 0.2
vis_radii = [i*rd for i in [0,1,2,5,10,25,50]] 

spawn_radius = 25*rd 

# trust = 0.99
# trust = 0.95
trust = 0.9
# trust = 0.85
# trust = 0.8
# trust = 0.75
# trust = 0.7

n_agents = 100

spawn_radius = 25*rd 

avg_std = []
std_std = []

for visual_radius in vis_radii:
    folder = f'results/trust{trust}/vr{visual_radius}'
    filename = f'N{n_agents}_sr{spawn_radius}'
    full_folder = f'{folder}/{filename}'

    velocities = np.load(f'{full_folder}/velocities.npy')

    angles = []
    stds = []
    for vel_agents in velocities:
        ang_agents = []
        for v in vel_agents:
            theta = np.arccos(abs(v[0])/norm(v))
            ang_agents.append(theta)
        stds.append(np.std(ang_agents))
        angles.append(ang_agents)

    avg_std.append(np.mean(stds[50:]))
    std_std.append(np.std(stds[50:]))

    plt.plot(stds, label=f'{visual_radius}')

plt.ylabel(fr'std($\theta$)')
plt.xlabel('time')
plt.legend(title='visual r')
plt.title(f'trust={trust}')
plt.figure()

shaded_errorbar(vis_radii, avg_std, std_std, lab=f'{trust}')
plt.ylabel(fr'average std($\theta$)')
plt.xlabel('visual radius')
plt.legend(title='trust')
plt.ion()
plt.show()
