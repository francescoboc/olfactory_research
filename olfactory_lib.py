import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.ndimage import map_coordinates

# extract matplotlib default colors for plotting purposes
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

# hack to prevent raising KeyboardInterrupt when stopping the script with ctrl-c
# https://stackoverflow.com/questions/7073268/remove-traceback-in-python-on-ctrl-c
import signal, sys
signal.signal(signal.SIGINT, lambda x, y: sys.exit())

# escape sequences to print colors in terminal
class tc:
    purple = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    ul = '\033[4m'
    end = '\033[0m'

def norm(vector):
    return (vector[0]**2 + vector[1]**2)**0.5

def initialise_rng(seed):
    global rng 
    rng = random.Random(seed)

class Simulation:
    def __init__(self, final_time, flow, swarm, cloud, real_time_plot, plot_flow, pause_time, save_frames, elastic):
        self.elastic = elastic
        # final time of the simulation
        self.final_time = final_time

        # flow, swarm and swarm objects
        self.flow = flow
        self.swarm = swarm
        self.cloud = cloud

        # flag to enable or disable real time plotting
        self.real_time_plot = real_time_plot
        self.plot_flow = plot_flow
        self.save_frames = save_frames
        # pause time between frames during plotting
        self.pause_time = pause_time

        if self.real_time_plot:
            # create figure and axes for plotting
            # fig = plt.figure(figsize=(10,5))
            plt.gca().remove()
            # self.axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, self.flow.length-1), ylim=(0, self.flow.heigth-1))
            self.axes = plt.subplot(aspect='equal', adjustable='box',
                    xlim=(self.cloud.source_coordinates[0] - self.swarm.spawn_radius*2, self.swarm.spawn_center[0] + self.swarm.spawn_radius*2), 
                    ylim=(self.swarm.spawn_center[1] - self.swarm.spawn_radius*2.5, self.swarm.spawn_center[1] + self.swarm.spawn_radius*2.5)) 
            # add arrows for the velocity field
            if self.plot_flow: self.flow_arrows = self.axes.quiver(self.flow.ux, self.flow.uy, alpha=0.2)

            # add patches for source and spawn circle 
            # plt.plot(*self.cloud.source_coordinates, c='k', marker='d')
            spawn_circle = plt.Circle(self.swarm.spawn_center, self.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2)
            source_point = plt.Circle(self.cloud.source_coordinates, 0.1, color='k', zorder=2)
            source_circle = plt.Circle(self.cloud.source_coordinates, self.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2)
            self.axes.add_patch(spawn_circle); self.axes.add_patch(source_point); self.axes.add_patch(source_circle)

            # add patches for center of mass
            cmass_point = plt.Circle(self.swarm.center_of_mass, 0.1, color='k', zorder=2)
            cmass_circle = plt.Circle(self.swarm.center_of_mass, self.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2)
            self.axes.add_patch(cmass_point); self.axes.add_patch(cmass_circle)

            # add agents points and visual circles
            index = 0
            for agent in self.swarm.agents:
                color_id = min([len(colors), index%len(colors)]) 
                agent_point = plt.Circle(agent.coordinates, 0.25, color=colors[color_id], label=index)
                visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[color_id], alpha=0.5)
                olfactory_circle = plt.Circle(agent.coordinates, agent.olfactory_radius, fill=False, color=colors[color_id], alpha=0.5, ls='--')
                self.axes.add_patch(agent_point); self.axes.add_patch(visual_circle); self.axes.add_patch(olfactory_circle)
                index += 1
            # plt.legend(fancybox=False, loc=3)

            plt.pause(self.pause_time)

    def run(self):
        # reset flags and timers
        success, agent_removed = False, False
        time_step, time, stopwatch, count = 0, 0, 0, 0
        while time < self.final_time:
            # update the flow
            self.flow.update(time_step)

            # update the cloud
            particle_removed = self.cloud.update()

            # at every decision time, create particles according to rate
            if (time_step*self.cloud.particle_dt) % (self.swarm.decision_time/self.cloud.particle_rate) < 1e-10:
                # particle_added = self.cloud.create()
                self.cloud.particles.append(Particle(self.cloud.source_coordinates.copy()))
                particle_added = True
            else: particle_added = False

            # update the local wind estimate of the agents
            self.swarm.update_wind_estimate()

            for agent in self.swarm.agents: 
                # detect odor particles
                if not agent.sniffed:
                    self.swarm.sniff_particles(agent)

            # at every decision time, update the swarm
            if stopwatch*self.cloud.particle_dt % self.swarm.decision_time < 1e-10:
                if self.elastic: agent_removed, success = self.swarm.update_elastic()
                else: agent_removed, success = self.swarm.update()
                # and advance the time counter
                if self.swarm.activated: time += self.swarm.decision_time

            # update stopwatch for time tracking
            if self.swarm.activated: stopwatch += 1

            # update global time step
            time_step += 1

            # if a particle was added to the cloud, add a patch to axes
            if self.real_time_plot and particle_added: 
                self.axes.add_patch( plt.Circle(self.cloud.particles[-1].coordinates, 0.1, color='b', alpha=0.5) ) 

            # remove patches from axes in case an agent or a particle was removed
            if self.real_time_plot and (particle_removed or agent_removed):
                for patch in self.axes.patches:
                    if (patch.center[0] > self.flow.length-1 or patch.center[0] < 0 or 
                        patch.center[1] > self.flow.heigth -1 or patch.center[1] < 0):
                        patch.remove()
                # plt.legend(fancybox=False, loc=3)

            # plot in real time
            if self.real_time_plot:
                plt.title(rf'$\beta$ = {self.swarm.trust:.2f}, Time = {time}')
                # update the flow arrows
                if self.plot_flow: self.flow_arrows.set_UVC(self.flow.ux, self.flow.uy)
                # and redraw the patches
                plt.draw()
                if self.save_frames: plt.savefig(f'frames/frame{time_step}')
                plt.pause(self.pause_time)

            # if an agent successuffly reached the source, stop
            if success: 
                # count agents within a circle of size spawn_radius around the source
                for candidate in self.swarm.agents:
                    coord_trasl = candidate.coordinates - self.cloud.source_coordinates
                    if norm(coord_trasl) < self.swarm.spawn_radius:
                        count += 1
                print(f'{tc.green}Source reached{tc.end} at time {time:.2f}')
                print(f'Number of agents < Rb: {count}')
                break

            # if all agents are out of the simulation box, stop
            if not self.swarm.agents: 
                print(f'{tc.red}Fail{tc.end}: all agents are out of the box')
                break

        # if the maximum duration of the simulation was reached, stop and return
        if not success and time == self.final_time: print(f'{tc.red}Fail{tc.end}: time is up')
        return(time, count, success)

class Swarm:
    def __init__(self, n_agents, spawn_center, spawn_radius, decision_time, speed,
            olfactory_radius, visual_radius, memory_time, trust, sensing_noise, cloud, flow):
        # parameters of the agents and initial spawn conditions
        self.n_agents = n_agents
        self.spawn_center = spawn_center
        self.spawn_radius = spawn_radius
        self.decision_time = decision_time
        self.speed = speed
        self.olfactory_radius = olfactory_radius
        self.visual_radius = visual_radius
        self.memory_time = memory_time
        self.trust = trust
        self.sensing_noise = sensing_noise

        # we also need the cloud object, to sniff the particles
        self.cloud = cloud
        # and the flow, to estimate the wind velocity
        self.flow = flow
        # initialise empty list for the swarm of agents
        self.agents = []

        # flag to account for the activation of the swarm (i.e.if any of the agents started moving)
        self.activated: bool = False

        # constants for the update of the exp. disc. running average for the wind estimate
        self.c_exp = np.exp( -(1/self.memory_time)*self.cloud.particle_dt )
        self.c_exp2 = 1 - self.c_exp

        # extract uniformly random points within the initial spawn circle
        # https://stackoverflow.com/questions/5837572/generate-a-random-point-within-a-circle-uniformly
        for n_ag in range(self.n_agents):
            # spawn each agent randomly in the circle
            radius = self.spawn_radius*np.sqrt(rng.random())
            theta = rng.random()*2*np.pi
            rand_x = self.spawn_center[0]+radius*np.cos(theta)
            rand_y = self.spawn_center[1]+radius*np.sin(theta)

            # initialise the wind estimate with the istantaneous local wind
            ux_interp, uy_interp = self.flow.interpolate([rand_x], [rand_y])
            initial_wind_estimate = np.array([ux_interp[0], uy_interp[0]])
            new_agent = Moth(n_ag, [rand_x, rand_y], self.speed, self.decision_time, 
                    self.olfactory_radius, self.visual_radius, initial_wind_estimate)
            self.agents.append(new_agent)

        # initialise position of center of mass
        pos_x = [agent.coordinates[0] for agent in self.agents]
        pos_y = [agent.coordinates[1] for agent in self.agents]
        self.center_of_mass = np.array([np.mean(pos_x), np.mean(pos_y)])

    def update_elastic(self):
        removed, success = False, False
        # determine future coordinates of the agents
        future_x, future_y = [], []
        for agent in self.agents:
            # start behaving only at the sniff of the first particle
            if agent.sniffed and not agent.go: agent.go = True

            # update public velocity
            self.update_public_velocity(agent)

            if agent.go:
                # turn on the flag
                if not self.activated: self.activated = True

                # update private velocity according to the cast and surge program
                if agent.sniffed:
                    agent.surge()
                else:
                    agent.cast()

                # add noise to public velocity (random rotation)
                random_angle = rng.uniform(-self.sensing_noise*3.141592653589793, self.sensing_noise*3.141592653589793)
                random_rot_matrix = [[np.cos(random_angle), -np.sin(random_angle)], 
                        [np.sin(random_angle), np.cos(random_angle)]]
                agent.velocity_pub = np.matmul(random_rot_matrix, agent.velocity_pub) 

                # check if the odor source is within the visual radius of any of the agents
                if agent.coordinates[0] < self.cloud.source_coordinates[0] + agent.visual_radius:
                    coord_trasl = self.cloud.source_coordinates - agent.coordinates
                    # if it is, the agent moves directly towards the source
                    if norm(coord_trasl) < agent.visual_radius:
                        agent.velocity_comb = coord_trasl/norm(coord_trasl)*agent.speed

                # otherwise, calculate velocity_comb (linear comb. of priv. and publ. cues)
                else: agent.velocity_comb = (1-self.trust)*agent.velocity_priv + self.trust*agent.velocity_pub

                # calculate future coordinates of the agent
                future_coord = agent.coordinates + agent.speed*agent.decision_time*agent.velocity_comb/norm(agent.velocity_comb)
                future_x.append(future_coord[0]); future_y.append(future_coord[1])

                # TODO normalise?
                # calculate instantaneous velocity of the agent as a finite difference
                agent.inst_velocity = (future_coord - agent.coordinates)/agent.decision_time

                # reset sniffed flag for the next iteration
                agent.sniffed = False

            else:
                agent.velocity_comb = np.array([0, 0])
                future_coord = agent.coordinates 
                future_x.append(future_coord[0]); future_y.append(future_coord[1])
                agent.inst_velocity = np.array([0, 0])

        # calculate predicted future position of the center of mass
        if self.activated:
            self.center_of_mass[0] = np.mean(future_x); self.center_of_mass[1] = np.mean(future_y)

        # direction = ( pos(t) - pos_cdm(t) ) / ||pos(t) - pos_cdm(t)|| 
        # acc(t) = -G * [H * (||pos(t) - pos_cdm(t)|| - Rb) * direction + (vel(t) - v_comb(t))]
        # vel(t+dt) = vel(t) + acc(t)*dt
        # pos(t+dt) = pos(t) + vel(t+dt)*dt
        # H is the heavyside function: H = 0 if pos <= Rb
        # vel(t) is calculated with finite difference

        # calculate acceleration
        for agent in self.agents:
            if agent.go:
                coord_trasl = agent.coordinates - self.center_of_mass 
                if norm(coord_trasl) < self.spawn_radius: heavyside = 0
                else: heavyside = 1
                magnitude = norm(agent.coordinates-self.center_of_mass) 
                agent.acceleration = -1 * ( heavyside*(magnitude - self.spawn_radius) * coord_trasl/magnitude 
                        + agent.inst_velocity - agent.velocity_comb )

                # update velocity and position
                agent.inst_velocity += agent.acceleration*agent.decision_time
                agent.coordinates += agent.inst_velocity*agent.decision_time

                # check if the agent has reached the source
                coord_trasl = self.cloud.source_coordinates - agent.coordinates
                if norm(coord_trasl) <= agent.speed*agent.decision_time:
                    success = True

                # if an agent is out of the simulation box, remove it
                if (agent.coordinates[0] > self.flow.length-1 or agent.coordinates[0] < 0 or 
                    agent.coordinates[1] > self.flow.heigth-1 or agent.coordinates[1] < 0):
                    self.agents.remove(agent)
                    removed = True

        # return success flag
        return removed, success

    def update(self):
        removed, success = False, False
        # determine behavior of the agents
        for agent in self.agents:
            # start behaving only at the sniff of the first particle
            if agent.sniffed and not agent.go: agent.go = True

            # update public velocity
            self.update_public_velocity(agent)

            if agent.go:
                # turn on the flag
                if not self.activated: self.activated = True

                # update private velocity according to the cast and surge program
                if agent.sniffed:
                    agent.surge()
                else:
                    agent.cast()

                # add noise to public velocity (random rotation)
                random_angle = rng.uniform(-self.sensing_noise*3.141592653589793, self.sensing_noise*3.141592653589793)
                random_rot_matrix = [[np.cos(random_angle), -np.sin(random_angle)], 
                        [np.sin(random_angle), np.cos(random_angle)]]
                agent.velocity_pub = np.matmul(random_rot_matrix, agent.velocity_pub) 

                # check if the odor source is within the visual radius of any of the agents
                if agent.coordinates[0] < self.cloud.source_coordinates[0] + agent.visual_radius:
                    coord_trasl = self.cloud.source_coordinates - agent.coordinates
                    # if it is, the agent moves directly towards the source
                    if norm(coord_trasl) < agent.visual_radius:
                        agent.velocity_comb = coord_trasl/norm(coord_trasl)
                        # check if the agent has reached the source
                        if norm(coord_trasl) <= agent.speed*agent.decision_time:
                            success = True

                # otherwise, calculate velocity_comb (linear comb. of priv. and publ. cues)
                else: agent.velocity_comb = (1-self.trust)*agent.velocity_priv + self.trust*agent.velocity_pub

                # update agent's coordinates
                agent.coordinates += agent.speed*agent.decision_time*agent.velocity_comb/norm(agent.velocity_comb)

                # reset sniffed flag for the next iteration
                agent.sniffed = False

                # if an agent is out of the simulation box, remove it
                if (agent.coordinates[0] > self.flow.length-1 or agent.coordinates[0] < 0 or 
                    agent.coordinates[1] > self.flow.heigth-1 or agent.coordinates[1] < 0):
                    self.agents.remove(agent)
                    removed = True

        # return the removed and success flags
        return removed, success

    # detect odor particles within the olfactoy_radius
    def sniff_particles(self, agent):
        for candidate in self.cloud.particles:
            coord_trasl = candidate.coordinates - agent.coordinates
            if norm(coord_trasl) < agent.olfactory_radius:
                agent.sniffed = True

    # update the wind estimate of agents (i.e. private cues)
    def update_wind_estimate(self):
        pos_x = [agent.coordinates[0] for agent in self.agents]
        pos_y = [agent.coordinates[1] for agent in self.agents]
        # interpolate the velocity field at all the agent positions
        ux_interp, uy_interp = self.flow.interpolate(pos_x, pos_y)     
        for aid in range(len(self.agents)):
            agent = self.agents[aid]
            # update agent coordinates
            inst_wind_estimate = np.array([ux_interp[aid], uy_interp[aid]])
            # incremental update rule for the exp. disc. running average
            agent.wind_estimate = self.c_exp*agent.wind_estimate + self.c_exp2*inst_wind_estimate

    # update the agent perception of the mean velocity of its neighbors (i.e. public cues)
    def update_public_velocity(self, agent):
        # find neighbors (i.e. other agents within visual_radius) of the agent
        self.detect_neighbors(agent)
        # reset sum
        sum_vel = np.array([0, 0])
        for neighbor in agent.neighbors:
            sum_vel = sum_vel + neighbor.velocity_comb
        # update public velocity
        if norm(sum_vel)>0:
            agent.velocity_pub = agent.speed*sum_vel/norm(sum_vel)

    # detect other agents within the visual_radius
    def detect_neighbors(self, agent):
        # reset neighbors list
        agent.neighbors = []
        for candidate in self.agents:
            coord_trasl = candidate.coordinates - agent.coordinates
            if (candidate != agent) and (norm(coord_trasl) < agent.visual_radius):
                agent.neighbors.append(candidate)
                # activate an agent if any of its neighbours are activated
                if not agent.go:
                    if candidate.go: agent.go = True

class Moth:
    def __init__(self, label, coordinates, speed, decision_time, olfactory_radius, visual_radius, initial_wind_estimate):
        # parameters of the moth
        self.label = label
        self.coordinates = np.array(coordinates)
        self.speed = speed
        self.decision_time = decision_time
        self.olfactory_radius = olfactory_radius
        self.visual_radius = visual_radius

        # counters and flags for the surging phase
        self.t_prime, self.clock, self.flip_dir = 0, 0, False

        # rotation matrices for 45deg 90deg rotations
        self._rot_matrix_45 = [[-2**(-0.5), 2**(-0.5)], [2**(-0.5), 2**(-0.5)]]
        self._rot_matrix_neg45 = [[-2**(-0.5), 2**(-0.5)], [-2**(-0.5), -2**(-0.5)]]
        self._rot_matrix_90 = [[0, -1], [1, 0]]

        # these attributes are updated by the Swarm() class:
        # estimate of the local wind velocity 
        self.wind_estimate = initial_wind_estimate
        # list of other agents within the visual_radius
        self.neighbors = []
        # flag to determine if a particle was sniffed
        self.sniffed = False
        # private and public velocity of the agent
        self.velocity_priv = np.array([0, 0])
        self.velocity_pub = np.array([0, 0])
        # linear combination of the two
        self.velocity_comb = np.array([0, 0])
        # instantaneous velocity
        self.inst_velocity = np.array([0, 0])

        # flag to determine when to start moving the agent
        self.go = False

    # cast and surge behavior 
    # NB here and in cast() we only update the private velocity, we do NOT update the coordinates yet!
    def surge(self):
        # divide the wind estimate by its norm to obtain a unit vector
        norm_wind_estimate = self.wind_estimate/norm(self.wind_estimate)
        # update value of private velocity to move upwind
        self.velocity_priv = -norm_wind_estimate*self.speed
        # reset surging counters
        self.t_prime = 0; self.clock = 0

    def cast(self):
        # divide the wind estimate by its norm to obtain a unit vector
        norm_wind_estimate = self.wind_estimate/norm(self.wind_estimate)
        # move 45 degrees
        if self.clock == self.t_prime:
            if self.flip_dir: direction_45 = np.matmul(self._rot_matrix_45, norm_wind_estimate)
            else: direction_45 = np.matmul(self._rot_matrix_neg45, norm_wind_estimate)
            self.velocity_priv = direction_45*self.speed
            self.clock = 0
            self.t_prime += 2*self.decision_time
            self.flip_dir = not self.flip_dir
        # move crosswind
        else:
            if self.flip_dir: direction_crosswind = np.matmul(self._rot_matrix_90, norm_wind_estimate)
            else: direction_crosswind = -np.matmul(self._rot_matrix_90, norm_wind_estimate)
            # update value of private velocity to move crosswind
            self.velocity_priv = direction_crosswind*self.speed
            self.clock += self.decision_time

class Flow:
    def __init__(self, length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity, loop_cycles):
        # dimensions of the simulation box
        self.length = length+1
        self.heigth = heigth+1

        # time step
        self.flow_dt = flow_dt

        # parameters of the stochastic flow
        self.constL = flow_lengthscale
        self.tau = flow_corr_time
        self.mean_wind = mean_wind
        self.fluct_intensity = fluct_intensity
        self.loop_cycles = loop_cycles

        # calculate useful constants
        urms = self.fluct_intensity*(self.mean_wind[0]**2 + self.mean_wind[1]**2)**0.5
        ks = 2*np.pi/self.constL
        self._sqrt_dt = self.flow_dt**0.5

        # calculate wavevectors
        K1x = [ks, 0, -ks, 0]
        K1y = [0, ks, 0, -ks]
        K2x = [ks, ks, -ks, -ks]
        K2y = [ks, -ks, -ks, ks]

        K1, K2 = [], []
        for ki in range(len(K1x)):
            K1.append([K1x[ki], K1y[ki]])
            K2.append([K2x[ki], K2y[ki]])

        self._Kall = K1 + K2

        # precalculate diffusion constant for different values of k
        self._diff_const = []
        for kvec in self._Kall:
            if kvec in K1:
                self._diff_const.append( (urms / (3**0.5 * ks)) * (2 / self.tau)**0.5 )
            elif kvec in K2:
                self._diff_const.append( 0.5* (urms / (3**0.5 * ks)) * (2 / self.tau)**0.5 )

        # precalculate all dotproducts
        self._dotprod = np.zeros([self.heigth,self.length,len(self._Kall)])
        for y in range(self.heigth):
            for x in range(self.length):
                for k in range(len(self._Kall)):
                    kvec = self._Kall[k]
                    self._dotprod[y][x][k] = kvec[0]*x + kvec[1]*y

        # initialise array for Fourier amplitudes
        self._amp = np.zeros(len(self._Kall))
        # self._amp = np.random.rand(len(self._Kall))

        # create arrays of coordinates for the interpolation of the velocity field
        self._xc, self._yc = np.arange(self.length), np.arange(self.heigth)

        # initialise the velocity field (ux, uy)
        self.initialise()

        # auxiliary variables to store the evolution of the field
        self._ux_frames, self._uy_frames = [], []
        self._f_id: int = 0
        self._first_call = True

    # initialise the velocity field
    def initialise(self):
        # evolve Fourier amplitudes
        for k in range(len(self._Kall)):
            kvec = self._Kall[k]
            self._amp[k] = self._amp[k] -self._amp[k]*self.flow_dt/self.tau + self._diff_const[k]*self._get_deltaW()

        # compute velocity field
        vx, vy = np.zeros([self.heigth,self.length]), np.zeros([self.heigth,self.length])
        for y in range(self.heigth):
            for x in range(self.length):
                for k in range(len(self._Kall)):
                    kvec = self._Kall[k]
                    vx[y][x] += 2*self._amp[k] * np.sin(self._dotprod[y][x][k]) * kvec[1]
                    vy[y][x] += -2*self._amp[k] * np.sin(self._dotprod[y][x][k]) * kvec[0]

        # compute the velocity field as mean wind + noise
        self.ux = self.mean_wind[0] + vx
        self.uy = self.mean_wind[1] + vy

    # update the flow: either evolve the dynamics and save frames or loop through saved frames 
    def update(self, time_step):
        # evolve
        if time_step*self.flow_dt < self.loop_cycles*self.tau:
            # evolve Fourier amplitudes
            for k in range(len(self._Kall)):
                kvec = self._Kall[k]
                self._amp[k] = self._amp[k] -self._amp[k]*self.flow_dt/self.tau + self._diff_const[k]*self._get_deltaW()

            # compute noise
            vx, vy = np.zeros([self.heigth,self.length]), np.zeros([self.heigth,self.length])
            for y in range(self.heigth):
                for x in range(self.length):
                    for k in range(len(self._Kall)):
                        kvec = self._Kall[k]
                        vx[y][x] += 2*self._amp[k] * np.sin(self._dotprod[y][x][k]) * kvec[1]
                        vy[y][x] += -2*self._amp[k] * np.sin(self._dotprod[y][x][k]) * kvec[0]

            # compute the velocity field as mean wind + noise
            self.ux = self.mean_wind[0] + vx
            self.uy = self.mean_wind[1] + vy

            # save current frame of the evolution in lists
            self._ux_frames.append(self.ux)
            self._uy_frames.append(self.uy)

        # loop through the lists of frames
        else:
            if self._first_call: print('Looping velocity field'); self._first_call = False
            self.ux = self._ux_frames[self._f_id]
            self.uy = self._uy_frames[self._f_id]
            if self._f_id < len(self._ux_frames)-1: self._f_id += 1
            else: self._f_id = 0

    # sample a Wiener increment
    def _get_deltaW(self):
        # return np.random.normal(0.0, 1.0)*self._sqrt_dt
        return rng.gauss(0.0, 1.0)*self._sqrt_dt

    # interpolate the velocity field at a given position
    def interpolate(self, pos_x, pos_y):
        ux_interp = map_coordinates(self.ux.T, [pos_x, pos_y], mode='grid-wrap', order=1)
        uy_interp = map_coordinates(self.uy.T, [pos_x, pos_y], mode='grid-wrap', order=1)
        return ux_interp, uy_interp

class Cloud:
    def __init__(self, particle_dt, particle_rate, source_coordinates, flow):
        # time step
        self.particle_dt = particle_dt
        # position of the odor source
        self.source_coordinates = np.array(source_coordinates)
        # rate for the odor particle generation
        self.particle_rate = particle_rate
        # we need to access the flow object, to calculate velocities
        self.flow = flow

        # initialise counter for the generation of odor partices
        self.stopwatch = 0
        # initialise time for the generation of the first particle
        self.next_time = int(self._get_next_time())
        # initialise empty list for the odor particles
        self.particles = []

    def update(self):
        # update particle positions according to the velocity field 
        removed = False
        # build lists of x and y particle coordinates
        pos_x = [particle.coordinates[0] for particle in self.particles]
        pos_y = [particle.coordinates[1] for particle in self.particles]
        # interpolate the velocity field at all the particle positions
        ux_interp, uy_interp = self.flow.interpolate(pos_x, pos_y)     
        to_be_removed = []
        for pid in range(len(self.particles)):
            particle = self.particles[pid]
            # update particle coordinates
            particle.coordinates[0] += ux_interp[pid]*self.particle_dt
            particle.coordinates[1] += uy_interp[pid]*self.particle_dt
            # if any of the particles is out of the simulation box, remove it
            if (particle.coordinates[0] > self.flow.length-1 or 
                particle.coordinates[0] < 0 or 
                particle.coordinates[1] > self.flow.heigth-1 or 
                particle.coordinates[1] < 0):
                to_be_removed.append(particle)
        if to_be_removed:
            for particle in to_be_removed: self.particles.remove(particle)
            removed = True
        return removed

    # create a particle according to exponentially distributed times
    def create(self):
        # create new particle
        added = False
        # if the time for the creation of a particle (since last generation) has passed 
        if self.stopwatch == self.next_time:
            # create a new particle at the source position
            self.particles.append(Particle(self.source_coordinates.copy()))
            # reset the counter
            self.stopwatch = 0
            # and extract a new time
            self.next_time = int(self._get_next_time())
            added = True
        else:
            # otherwise, increase the counter
            self.stopwatch += 1
        # return flags about removal or creation of new particles
        return added

    # sample time for the generation of next particle from an exponential distribution
    def _get_next_time(self):
        return rng.expovariate(self.particle_rate)

class Particle:
    def __init__(self, coordinates):
        self.coordinates = coordinates
