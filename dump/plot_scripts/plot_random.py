import numpy as np
import matplotlib.pyplot as plt

# ns = [10, 40, 100, 400, 1000]

n_agents = 100
biases = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]

discard_till = 2000

# trusts = np.round(np.arange(0.0, 1.05, 0.05),2)
trusts = np.append(np.round(np.arange(0.0, 0.85, 0.05),2), np.round(np.arange(0.81, 1.01, 0.01),2))

nruns = 5

for bias in biases:
    mean_param_trust = []
    for trust in trusts:

        mean_param_temp = []
        for nr in range(nruns):
            # build folder path
            folder = f'results/random_walk_noPBC/bias_{bias}/{n_agents}/run{nr}'
            path = f'{folder}/{trust}.npy'

            # load file
            order_param = np.load(path, allow_pickle=True)

            # take temporal mean discurding initial dynamics
            mean_param_temp.append(np.mean(order_param[discard_till:]))

        # take mean over runs and append result to list
        mean_param_trust.append(np.mean(mean_param_temp))

    plt.figure(1)
    plt.plot(trusts, mean_param_trust, mfc='none', marker='o', lw=1, label=f'{bias}')

    # plt.figure(2)
    # plt.plot(trusts, np.gradient(np.gradient(mean_param_trust)), mfc='none', marker='o', lw=1, label=f'{bias}')

plt.xlabel('trust')
plt.ylabel('order parameter')

plt.legend()

try: __IPYTHON__; plt.ion()
except NameError: pass
plt.show()

# folder = f'results/random_walk/{n_agents}'
# folder = f'results/random_walk/bias_{bias}/{n_agents}'
# for n_agents in ns:
# plt.plot(range(len(order_param)), order_param, alpha=0.5)
# plt.axhline(np.mean(order_param), lw=1, color='b')
# plt.plot(trusts, op_timeavg, marker='o', lw=1, label=f'{n_agents}')

