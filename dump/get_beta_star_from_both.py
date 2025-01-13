import matplotlib.pyplot as plt
from utils import *
from tqdm import tqdm
from get_beta_star_from_firstpassage import get_beta_star_from_fpt

# from get_beta_star_from_probability import get_beta_star_from_hull
from get_beta_star_from_successrate import get_beta_star_from_hull

# source position
# l_x = 10

# probability treshold
pr = 0.0

dists = [6,8,10]
shifts = [5,7,9]

# use the center of mass trajectory or all the agents
center_of_mass = 1

fig, ax = plt.subplots()

for l_x in dists:
    beta_probs, beta_fpts = [], []
    for h_y in tqdm(shifts, ascii=' █'):
        beta_prob = get_beta_star_from_hull(l_x, h_y, pr, center_of_mass)
        beta_fpt = get_beta_star_from_fpt(l_x, h_y)
        beta_probs.append(beta_prob)
        beta_fpts.append(beta_fpt)

    for s in range(len(shifts)):
        x = beta_probs[s]*(1+np.random.uniform(-0.05,0.05))
        y = beta_fpts[s]*(1+np.random.uniform(-0.05,0.05))
        ax.errorbar(x, y, yerr=0.05, xerr=0.05)
        ax.scatter(x, y, label=f'{(l_x/shifts[s]):.2f}')
    # plt.show()

x = np.arange(0,11)
y = x
ax.plot(x, y, 'k--', lw=1, zorder=-10)

# ax.set_xlabel(r'$\beta*$ from probability ($P_0$) convex hull')
ax.set_xlabel(r'$\beta*$ from success rate ($R_0$) convex hull')
ax.set_ylabel(r'$\beta*$ from first passage time map')
# ax.set_title(rf'$P_0$={pr}')
ax.set_title(rf'$R_0$={pr}')

ax.legend(title='L/H', ncols=2)
ax.axis('square')

ax.set_xlim(0,1)
ax.set_ylim(0,1)

plt.show()
# show_and_check_ipython()
