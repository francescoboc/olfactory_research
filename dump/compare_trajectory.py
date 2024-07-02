import numpy as np
import matplotlib.pyplot as plt

# foldername = 'nonuniform10'
foldername = 'j1'

ra = 25*0.2
beta = 0.8

plt.figure()
for i in range(1,101):
    data = np.loadtxt(f'mihir_results/{foldername}/{beta:.2f}/{i}data.txt')
    x = data[:,0]
    y = data[:,1]
    plt.scatter(x[0], y[0], c='k', marker='.')
    plt.plot(x, y, lw=1, zorder=0)
    plt.gca().set_aspect('equal')
source_circle = plt.Circle((0,0), ra, fill=False, color='k', ls='--', alpha=0.2)
plt.gca().add_patch(source_circle)
plt.scatter(0, 0, c='k')
plt.title('mihir')

xlimit = plt.xlim()
ylimit = plt.ylim()

source_coord = [37, 62.5]
plt.figure()
x_coords = np.load(f'coordinates/{foldername}/x_coords.npy', allow_pickle = True)
y_coords = np.load(f'coordinates/{foldername}/y_coords.npy', allow_pickle = True)
for i in range(0,100):
    x = x_coords[i] - source_coord[0]
    y = y_coords[i] - source_coord[1]
    plt.scatter(x[0], y[0], c='k', marker='.')
    plt.plot(x, y, lw=1, zorder=0)
    plt.gca().set_aspect('equal')
source_circle1 = plt.Circle((0,0), ra, fill=False, color='k', ls='--', alpha=0.2)
plt.gca().add_patch(source_circle1)
plt.scatter(0, 0, c='k')
plt.title('francesco')

plt.xlim(xlimit)
plt.ylim(ylimit)

plt.show()
