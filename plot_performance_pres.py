from utils import *
from select_file import *
from plot_first_passage import plot_first_passage
from plot_successrate import plot_successrate
import os

trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

straight_line_time = np.sqrt(l_x**2 + h_y**2)

print(f'mu={mu:.2f}, sigma={sigma:.2f}, final_t={final_time}, r_v={visual_radius}')

# fpts, rates = [], []
# for trust in trusts:
#     fpt_source, fpt_found = plot_first_passage(trust, l_x, h_y, False)
#     success_rate_source, rate_found = plot_successrate(trust, l_x, h_y, False)
#     if fpt_found and rate_found:
#         fpts.append(fpt_source)
#         rates.append(success_rate_source)
#     else:
#         print(f'Trust {trust}: FPT={fpt_found}, RATE={rate_found}')
# os.makedirs(f'pres_data/mu{mu:.2f}_sigma{sigma:.2f}_h{h_y}/', exist_ok=True)
# np.save(f'pres_data/mu{mu:.2f}_sigma{sigma:.2f}_h{h_y}/fpts',fpts)
# np.save(f'pres_data/mu{mu:.2f}_sigma{sigma:.2f}_h{h_y}/rates',rates)

fpts = np.load(f'pres_data/mu{mu:.2f}_sigma{sigma:.2f}_h{h_y}/fpts.npy')
rates = np.load(f'pres_data/mu{mu:.2f}_sigma{sigma:.2f}_h{h_y}/rates.npy')

# convert lists into numpy arrays for easier manipulation
fpts = np.array(fpts)
rates = np.array(rates)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

# fpt_plot = ax1.plot(trusts, fpts/straight_line_time, 'o-', color=colors[0], label=r'$\tau$')
# rate_plot = ax2.plot(trusts, rates, 'o-', color=colors[1], label=r'$\rho$')

# fpt_plot = ax1.plot(trusts, fpts, 'o-', color=colors[0], label=r'FPT')
# rate_plot = ax2.plot(trusts, rates, 'o-', color=colors[1], label=r'Success rate')

fpt_plot = ax1.plot(trusts, fpts/straight_line_time, 'o-', color=colors[0], label=f'{h_y}')
rate_plot = ax2.plot(trusts, rates, 's--', color=colors[0])

# all_plots = fpt_plot + rate_plot
# labels = [p.get_label() for p in all_plots]
# plt.legend(all_plots, labels)

# ax1.set_ylabel(r'Normalized first passage time $\tau$')
ax1.set_ylabel(r'Average first passage time $\tau$')
ax2.set_ylabel(r'Average success rate $\rho$')
ax2.set_ylim(-0.02, 1.02)

ax1.set_xlabel(r'Trust $\beta$')

# plt.title(rf'$\mu={mu:.2f}, \sigma={sigma:.2f}, L={l_x}, H={h_y}, r_v={visual_radius}$')
# plt.title(rf'Source position B')
plt.title(rf'Varying initial angle')

show_and_check_ipython()
