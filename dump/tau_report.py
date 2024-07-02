from olfactory_plot_utils import *

beta = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
tau =  [1,   2.0, 2.5, 3.1, 3.4, 2.1, 1.3, 1.2, 1.2, 1.2, 1] 

plt.figure()
plt.plot(beta, tau, marker='o')
plt.xlabel(r'$\beta$')
plt.ylabel(r'$\tau / \Delta t$')

show_and_check_ipython()
