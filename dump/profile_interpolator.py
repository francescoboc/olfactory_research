import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import map_coordinates
from pyinstrument import Profiler

def interp_rgi(ux, xc, yc, position):
    ux_interp = RegularGridInterpolator((xc, yc), ux) 
    return ux_interp(position)

def interp_map(ux, position):
    ux_interp = map_coordinates(ux, [[position[0]], [position[1]]], order=1)
    return ux_interp[0]

length = 50
heigth = 20
position = (31.33, 12.34)

kk = 50000

print('rgi')
prof = Profiler()
prof.start()

xc, yc = np.arange(length), np.arange(heigth)
rng = np.random.default_rng(666)
for k in range(kk):
    ux = rng.random((length,heigth))
    interp = interp_rgi(ux, xc, yc,  position)

prof.stop()
prof.print()


print('map')
prof = Profiler()
prof.start()

xc, yc = np.arange(length), np.arange(heigth)
rng = np.random.default_rng(666)
for k in range(kk):
    ux = rng.random((length,heigth))
    interp = interp_map(ux,  position)

prof.stop()
prof.print()
