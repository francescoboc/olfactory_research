import numpy as np
import matplotlib.pyplot as plt

# foldername = 'nonuniform10'
# foldername = 'j1'

# beta = 0.1
# betas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] 
betas = [0.1, 0.3, 0.5, 0.7, 0.9] 

nagents = 2
# nagents = 10

plt.figure()
# plt.title(f'mihir, n={nagents}')

for beta in betas:

    data = np.loadtxt(f'results/mihir_results/casting/n{nagents}/beta{beta}/1data.txt')
    # data = np.loadtxt(f'results/mihir_test/casting/1data.txt')
    x = data[:,0]
    y = data[:,1]
    plt.scatter(x[-1], y[-1], c='k', marker='.')
    plt.plot(x, y, lw=1, zorder=0, label=rf'$\beta = {beta}$')

    data = np.loadtxt(f'results/mihir_results/casting/n{nagents}/beta{beta}/2data.txt')
    # data = np.loadtxt(f'results/mihir_test/casting/1data.txt')
    x1 = data[:,0]
    y1 = data[:,1]
    plt.scatter(x1[-1], y1[-1], c='k', alpha=0.3, marker='.')
    plt.plot(x1, y1, lw=1, c='k', alpha=0.3, zorder=0)


    plt.ylim([-50, 50])
    plt.xlim([-100, 250])

    # # plt.figure()
    # for i in range(1,2+1):
    #     data = np.loadtxt(f'mihir_results/casting/beta{beta}/{i}data.txt')
    #     x = data[:,0]
    #     y = data[:,1]
    #     plt.scatter(x[0], y[0], c='k', marker='.')
    #     plt.plot(x, y, lw=1, zorder=0)
    #     plt.gca().set_aspect('equal')
    # plt.title('mihir')

x = [x[0], 0]
y = [y[0], y[0]]
plt.scatter(x[-1], y[-1], c='k', marker='.')
plt.plot(x, y, lw=1, zorder=-1, label=rf'$\beta = 1.0$')

x1 = [x1[0], 0]
y1 = [y1[0], y1[0]]
plt.scatter(x1[-1], y1[-1], c='k', marker='.')
plt.plot(x1, y1, lw=1, c='k', alpha=0.3, zorder=-1)

plt.gca().set_aspect('equal')
plt.legend()

plt.ion()
plt.show()

# # MIHIR DATA
# foldername = 'nonuniform10'
# # foldername = 'uniform10'
# betas = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
# mean_agents, std_agents = [], []
# mean_time, std_time = [], []
# for beta in betas:
#     Nagents_raw = np.loadtxt(f'mihir_results/{foldername}/{beta:.2f}/Less_than_Rb.txt')
#     time_raw = np.loadtxt(f'mihir_results/{foldername}/{beta:.2f}/reach_time.txt')
#     Nagents = []
#     for entry in Nagents_raw:
#         Nagents.append(entry[1])
#     mean_agents.append(np.mean(Nagents)/len(Nagents))
#     std_agents.append(np.std(Nagents)/len(Nagents))
#     times = []
#     for entry in time_raw:
#         times.append(entry[1])
#     mean_time.append(np.mean(times)/Ts)
#     std_time.append(np.std(times)/Ts)

# plt.figure(1)
# plt.errorbar(betas, mean_time, yerr=std_time, label='mihir', marker=markers[index])
# plt.legend()

# plt.figure(2)
# plt.errorbar(betas, mean_agents, yerr=std_agents, label='mihir', marker=markers[index])
# plt.legend()

