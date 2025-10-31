from  olfactory_lib_firstpassage import *
from utils import *
from select_file import *
import os
from scipy.stats import Normal
from perf_infiniterange import get_success_rate_source
plt.close()

plt.rcParams['font.size'] = 16
# plt.rcParams['legend.fontsize'] = 14 
plt.rcParams['figure.constrained_layout.use'] = True

trusts = np.arange(0.01, 1, 0.02)
# trusts = [0.5]

tsteps = int(1e5)
tclock = 100

# swarm parameters
rd = 0.2
spawn_radius = 25*rd 
speed = 0.2
reach_radius = 5*rd

h_ys = [0, 10, 16, 20]
l_x = 75


 # ----------- calculate a reference casting trajectory -----------
private_behavior = 'cast_and_surge'
rd = 0.2
olfactoy_radius = rd
rand_casting_steps = 0
rand_casting_direction = False
sensing_noise = 0.0 # eta
length, height = 500, 500
source_coordinates = [75, 0]
threshold = np.inf
method = 'no_kernel' 
decision_time = 1
dt = decision_time
memory_time = 1.0 *decision_time
wind_noise = 0.0 
cloud = None
seed = random.randrange(sys.maxsize)
initialise_rng(seed)
swarm = Swarm(private_behavior, n_agents, spawn_radius, speed, visual_radius, 
        olfactoy_radius, sensing_noise, wind_noise, trust, length, height, 
        source_coordinates, reach_radius, 
        rand_casting_steps, rand_casting_direction, dt, memory_time, decision_time, 
        threshold, cloud, method, mu, sigma)

agent = swarm.agents[0]
x_cs, y_cs = 0, 0
x_cs_hist, y_cs_hist = [x_cs], [y_cs]
for t in range(tsteps+tclock):
    agent.cast(t)

    v_x = agent.private_velocity[0]
    x_cs += v_x*dt
    v_y = agent.private_velocity[1]
    y_cs += v_y*dt

    x_cs_hist.append(x_cs)
    y_cs_hist.append(y_cs)
 # ----------- ----------- ----------- ----------- -----------

# TODO
# calcola time window all'interno della quale calcolare la media/il max
# t compreso tra (L-rs)/(beta v0) e (L+rs)/(beta v0)
# calcola max (o forse media?)

# TODO per ogni beta:
# calcola t_star = l_x/(trust*speed)
# calcola l'integrale in t = t_star
# calcola sigma_y_2: se è > H allora rho=1, altrimenti rho=0
# appendi il risultato a una lista: ecco rho(beta)

c=0
for h_y in h_ys:
# for h_y in [h_ys[2]]:
    rho_beta = []

    for trust in trusts:

        # t_star = int(l_x/(trust*speed))

        t_star_min = int((l_x - spawn_radius)/(trust*speed))
        t_star_max = int((l_x + spawn_radius)/(trust*speed))

        y_cs_2 = []
        for t in range(t_star_min, t_star_max, dt):
            int_s = 0
            for tau in range(tclock):
                int_s += (y_cs_hist[t+tau] - y_cs_hist[tau])**2
            y_cs_2.append(int_s)

        y_cs_2 = np.array(y_cs_2)/tclock
        y_cs_2 *= (1 + 2*trust*(1-trust))*(1-trust)**2
        y_cs_2 += (spawn_radius/2)**2

        y_cs = np.sqrt(y_cs_2)

        # # check binario
        # if max(2*y_cs) >= h_y: 
        #     rho = 1
        # else:
        #     rho = 0

        # proviamo a metterci una gaussiana per smoothare il risultato
        sigma_y = max(y_cs)
        stat_y = Normal(mu=0, sigma=sigma_y)
        est_dx = h_y + reach_radius/trust
        est_sx = h_y - reach_radius/trust
        rho = 1- (1 - (stat_y.cdf(est_dx) - stat_y.cdf(est_sx)))**n_agents

        # prob_h = 1/(np.sqrt(np.pi*sigma_y))*np.exp(-(h_y**2/sigma_y**2))

        # rho = 1-(1-2*reach_radius*prob_h)**n_agents
        # rho = 1-(1-2*reach_radius*prob_h/trust)**n_agents

        rho_beta.append(rho)

    # plt.plot(trusts, rho_beta, ls='-', color=colors[c], marker=markers[c], label=rf'${h_y}$')
    # plt.plot(trusts, rho_beta, ls='-', color=colors[c], marker=None, label=rf'${h_y}$')
    plt.plot(trusts, rho_beta, ls='-', color=colors[c], marker=None)
    c+=1


        # # THEORY:
        # y_cs_2 = []
        # for t in tqdm(range(tsteps)):
        #     int_s = 0
        #     for tau in range(tclock):
        #         int_s += (y_cs_hist[t+tau] - y_cs_hist[tau])**2
        #     y_cs_2.append(int_s)

        # y_cs_2 = np.array(y_cs_2)/tclock
        # y_cs_2 *= (1 + 2*trust*(1-trust))*(1-trust)**2
        # y_cs_2 += (spawn_radius/2)**2

    # y_cs = np.sqrt(y_cs_2)
    # plt.plot(y_cs, c='k', label='theory')

    # plt.legend()
    # plt.xlabel('timestep')
    # plt.ylabel(r'$\sigma_y$')

    # plt.title(rf'$\beta={trust}$')

ax = plt.gca()
fig = plt.gcf()

fig.set_size_inches(4.5, 4.5)

# leg = ax.legend(title=r'Shift $H$', loc='center right')
# ax.add_artist(leg)

plt.xlabel(r'Trust $\beta$')
plt.ylabel(r'Success rate $\rho$')

plt.xlim(0.05,0.95)
# plt.xticks([0.25, 0.5, 0.75])


# add simulation data
variable = 'shift'
filename = rf'perf_{variable}_infiniterange.pdf'
visual_radius = 100*spawn_radius
trusts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

# plt.xticks(trusts)

iterable = [0, 10, 16, 20]
l_x = 75
mu = 0
sigma = 0
labels = [rf'${h}$' for h in iterable]

dummy_fig, dummy_ax = plt.subplots()
hb = dummy_ax.hexbin([], [], gridsize=gridsize, extent=[*bound_x, *bound_y])
plt.close(dummy_fig)
bin_coords = hb.get_offsets()  

c=0
for item in iterable:
    h_y = item
    dicts_folder = f'../beta_dicts/n_agents{n_agents}/vr{visual_radius}/mu{mu:.2f}_sigma{sigma:.2f}_randsteps{rand_casting_steps}/final_x{final_x}'

    rates = []
    for trust in trusts:
        success_rate_source = get_success_rate_source(trust, l_x, h_y)
        rates.append(success_rate_source)

    rates = np.array(rates)

    # plt.plot(trusts, rates, '--', color='grey', marker=markers[c], label=labels[c], zorder=-10)
    plt.plot(trusts, rates, '--', color=colors[c], marker=markers[c], zorder=-10, label=rf'${h_y}$')

    c+=1

leg = ax.legend(title=r'Shift $H$', loc='center right')
ax.add_artist(leg)

# title = 'Theory'
# title = 'Simulation'
# plt.title(title)

# custom legend
from matplotlib.lines import Line2D
custom_lines = [
    Line2D([0], [0], color='grey', ls='-', label=r'Theory'),
    Line2D([0], [0], color='grey', ls='--', label=r'Simul.') ]

# Add the custom legend
ax.legend(
    handles=custom_lines,
    loc='center right',
    bbox_to_anchor=(1, 0.8),  # x = 1 (bordo destro), y > 0.5 per salire
    fontsize=14
)

show_and_check_ipython()
