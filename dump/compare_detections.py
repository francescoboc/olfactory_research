import numpy as np
import matplotlib.pyplot as plt

foldername = 'detections'

ra = 25*0.2
beta = 0.8

det_fra, det_mihir = [], []
for nrun in range(100):

    detections_raw = np.loadtxt(f'mihir_results/{foldername}/{beta:.2f}/number_of_detections{nrun}.txt')
    detections_mihir = detections_raw[:,1]
    avg_mihir = np.mean(detections_mihir)
    det_mihir.append(avg_mihir)
    # print(f'Detections Mihir: {avg_mihir}')

    detections_fra = np.load(f'detections/detections{nrun}.npy', allow_pickle = True)
    avg_fra = np.mean(detections_fra)
    det_fra.append(avg_fra)
    # print(f'Detections Fra: {avg_fra}')

