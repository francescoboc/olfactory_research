import numpy as np
import matplotlib.pyplot as plt

# ns = [10, 40, 100, 400, 1000]

n_agents = 100
biases = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]

discard_till = 2500

# for n_agents in ns:
for bias in biases:

    # folder = f'results/random_walk/{n_agents}'
    # folder = f'results/random_walk/bias_{bias}/{n_agents}'
    folder = f'results/random_walk_noPBC/bias_{bias}/{n_agents}'

    # trusts = np.round(np.arange(0.0, 1.05, 0.05),2)
    trusts = np.append(np.round(np.arange(0.0, 0.85, 0.05),2), np.round(np.arange(0.81, 1.01, 0.01),2))

    ord_params = []
    for trust in trusts:
        path = f'{folder}/{trust}.npy'

        order_param = np.load(path, allow_pickle=True)
        ord_params.append(np.mean(order_param[discard_till:]))

        # plt.plot(range(len(order_param)), order_param, alpha=0.5)
        # plt.axhline(np.mean(order_param), lw=1, color='b')

    # plt.plot(trusts, ord_params, marker='o', lw=1, label=f'{n_agents}')
    plt.plot(trusts, ord_params, marker='o', lw=1, label=f'{bias}')

plt.xlabel('trust')
plt.ylabel('order parameter')

plt.legend()

try: __IPYTHON__; plt.ion()
except NameError: pass
plt.show()

