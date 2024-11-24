from utils import *
from select_file import *
from plot_first_passage import plot_first_passage
from plot_successrate import plot_successrate

trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

straight_line_time = np.sqrt(l_x**2 + h_y**2)

fpts, rates = [], []
for trust in trusts:
    fpts.append(plot_first_passage(trust, l_x, h_y, False, False))
    rates.append(plot_successrate(trust, l_x, h_y, False, False))

# convert lists into numpy arrays for easier manipulation
fpts = np.array(fpts)
rates = np.array(rates)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

fpt_plot = ax1.plot(trusts, fpts/straight_line_time, color=colors[0], label='FPT')
rate_plot = ax2.plot(trusts, rates, color=colors[1], label='Success rate')

all_plots = fpt_plot + rate_plot
labels = [p.get_label() for p in all_plots]
plt.legend(all_plots, labels)

ax1.set_ylabel('First passage time')
ax2.set_ylabel('Success rate')
ax2.set_ylim(-0.02, 1.02)

ax1.set_xlabel('Trust')

show_and_check_ipython()
