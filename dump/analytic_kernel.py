import matplotlib.pyplot as plt
import numpy as np

beta = 0.2

nsteps = 3

# NO KERNEL
ratio_nk_list = []
for n in range(nsteps):
    ratio_nk = (1-beta**(n+1)) / beta**n
    ratio_nk_list.append(ratio_nk)

plt.plot(range(nsteps), ratio_nk_list, label=rf'No kernel')

# plt.xlabel('nsteps')
# plt.ylabel('A/B')
# plt.legend()

# KERNEL
tau = 1
dt = 0.01

msteps = nsteps

ratio_k_list = []
for m in range(msteps):
    A = (1-beta)*(1+m*beta*dt/tau)
    B = beta*(1-m*dt/tau + beta*m*dt/tau)
    ratio_k = A/B
    ratio_k_list.append(ratio_k)

plt.plot(range(msteps), ratio_k_list, label=rf'With kernel')
plt.xlabel('nsteps')
plt.ylabel('A/B')
plt.legend()




# c1 = np.exp(-dt/tau)
# c2 = 1-c1

# exp_list = []
# for t in range(10):
#     exp_list.append(np.exp(-t/tau))

# plt.plot(range(10), exp_list)
# plt.axvline(tau, lw=1, c='k')

# print( (1-beta)*(1-beta*c2) / beta*(c1+beta*c2) )
# print( (1-beta)*(1+beta*c1*c2+beta*c2-(beta*c2)**2) / beta*(c1**2+2*beta*c1*c2+(beta*c2)**2 ) )
# print( (1-beta)*(1+beta*c1*c2-(beta*c2)**2+2*beta*c2+beta*c2*c1**2) / beta*(c1**2+2*beta*c1*c2+(beta*c2)**2+c1**3+2*beta*c2*c1**2+(beta*c2)**2*c1 ) )
# print( (1-beta)*(1+beta*c2*(c1**3+c1**2+c1+1) +(beta*c2)**2*(2*c1+2)-(beta*c2)**3*(c1+1)+(beta*c1*c2)**2) / beta*(c1**4+4*beta*c2*c1**3 + 5*(beta*c2*c1)**2 + beta**3*c1*c2**3 + beta*c2*c1**2 + 2*beta**2*c1*c2**2 + beta**3*c2**3*(1+c1)) )

plt.ion(); plt.show()
