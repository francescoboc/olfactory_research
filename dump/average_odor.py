import matplotlib.pyplot as plt
import numpy as np

path = 'flow/re280_small_source'

threshold = 0.0005

odor_path = f'{path}/odor.npy'
odor_frames = np.load(odor_path)
n_frames = len(odor_frames) 

for n in range(n_frames):
    odor = np.array(odor_frames[n])
    odor[odor>threshold] = 0

    if n == 0:
        avg_odor = odor.copy()
    else:
        avg_odor += odor

# avg_odor /= n_frames

# plt.imshow(avg_odor>threshold)
plt.imshow(avg_odor)

plt.ion()
plt.show()
