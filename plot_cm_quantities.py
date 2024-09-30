from utils import *


save_path = 'cm_quantities'

normv_mean_beta = np.load(f'{save_path}/normv_mean_beta.npy', allow_pickle=True).item()
normv_std_beta = np.load(f'{save_path}/normv_std_beta.npy', allow_pickle=True).item()

betas = []
normv_means, normv_stds = [], []
for beta in normv_mean_beta.keys():
    betas.append(beta)
    normv_means.append(normv_mean_beta[beta])
    normv_stds.append(normv_std_beta[beta])

speed = 0.2
shaded_errorbar(betas, np.array(normv_means)/speed, np.array(normv_stds)/speed)

plt.xlabel('trust')
plt.ylabel(r'$<|v_{cm}|>/v_0$')

show_and_check_ipython()
