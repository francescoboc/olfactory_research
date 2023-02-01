import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.interpolate import RegularGridInterpolator

# extract matplotlib default colors for plotting purposes
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

class Simulation:
    def __init__(self, time_steps, flow, swarm, cloud, real_time_plot, plot_flow, pause_time):
        # total time steps of the simulation
        self.time_steps = time_steps

        # flow, swarm and swarm objects
        self.flow = flow
        self.swarm = swarm
        self.cloud = cloud

        # flag to enable or disable real time plotting
        self.real_time_plot = real_time_plot
        self.plot_flow = plot_flow
        # pause time between frames during plotting
        self.pause_time = pause_time

        if self.real_time_plot:
            # create figure and axes for plotting
            plt.gca().remove()
            self.axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, self.flow.length), ylim=(0, self.flow.heigth), title='time = 0')

            # add arrows for the velocity field
            if self.plot_flow: self.flow_arrows = self.axes.quiver(self.flow.ux, self.flow.uy, alpha=0.2)

            # add source and spawn circle drawings
            plt.plot(*self.cloud.source_coordinates, c='k', marker='d')
            spawn_circle = plt.Circle(self.swarm.spawn_center, self.swarm.spawn_radius, fill=False, color='k', alpha=0.2)
            self.axes.add_patch(spawn_circle)

            # add agents points and visual circles
            index=0
            for agent in self.swarm.agents:
                color_id = min([len(colors), index%len(colors)]) 
                agent_point = plt.Circle(agent.coordinates, 0.25, color=colors[color_id], label=index)
                visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[color_id], alpha=0.5)
                olfactory_circle = plt.Circle(agent.coordinates, agent.olfactory_radius, fill=False, color=colors[color_id], alpha=0.5, ls='--')
                self.axes.add_patch(agent_point)
                self.axes.add_patch(visual_circle)
                self.axes.add_patch(olfactory_circle)
                index+=1
            # plt.legend(fancybox=False, loc=3)

            plt.pause(self.pause_time)

    def run(self):
        for time in range(self.time_steps):
            # update the flow
            self.flow.update()
            # update the cloud
            particle_removed, particle_added = self.cloud.update()
            # update the swarm
            agent_removed = self.swarm.update()
            # if a particle was added to the cloud, add a patch to axes
            if self.real_time_plot and particle_added: 
                self.axes.add_patch( plt.Circle(self.cloud.particles[-1].coordinates, 0.1, color='b') ) 

            # remove patches from axes in case an agent or a particle was removed
            if self.real_time_plot and (particle_removed or agent_removed):
                for patch in self.axes.patches:
                    if (patch.center[0] > self.flow.length-1 or patch.center[0] < 0 or 
                        patch.center[1] > self.flow.heigth -1 or patch.center[1] < 0):
                        patch.remove()
                # plt.legend(fancybox=False, loc=3)

            # plot in real time
            if self.real_time_plot:
                plt.title(f'time = {time+1}')
                # update the flow arrows
                if self.plot_flow: self.flow_arrows.set_UVC(self.flow.ux, self.flow.uy)
                # and redraw the patches
                plt.draw()
                plt.pause(self.pause_time)

            # if all agents are out of the simulation box, stop
            if not self.swarm.agents: break

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
        # initialize empty list for the swarm of agents
        self.agents = []

        # constants for the update of the exp. disc. running average for the wind estimate
        self.c_exp = np.exp( -(1/self.memory_time)*self.cloud.particle_dt )
        self.c_exp2 = 1 - self.c_exp

        # extract uniformly random points within the initial spawn circle
        # https://stackoverflow.com/questions/5837572/generate-a-random-point-within-a-circle-uniformly
        for n_ag in range(self.n_agents):
            radius = self.spawn_radius*np.sqrt(np.random.rand())
            theta = np.random.rand()*2*np.pi
            # spawn each agent randomly in the circle
            coordinates = [self.spawn_center[0]+radius*np.cos(theta), self.spawn_center[1]+radius*np.sin(theta)]
            # initialise the wind estimate with the istantaneous local wind
            initial_wind_estimate = self.flow.interpolate(coordinates)
            new_agent = Moth(n_ag, coordinates, self.speed, self.decision_time, 
                    self.olfactory_radius, self.visual_radius, initial_wind_estimate)
            self.agents.append(new_agent)

    def update(self):
        removed = False
        # determine behavior of the agents
        for agent in self.agents:
            # detect odor particles
            self.sniff_particles(agent)

            # find neighbors (i.e. other agents within visual_radius) of the agent
            self.detect_neighbors(agent)

            # start behaving only at the sniff of the first particle
            if agent.sniffed_particles and not agent.go: agent.go = True
            if agent.go:
                # update the local wind estimate of the agent
                self.update_wind_estimate(agent)

                # update private velocity according to the cast and surge program
                if agent.sniffed_particles:
                    agent.surge()
                else:
                    agent.cast()

                # update public velocity
                self.update_public_velocity(agent)

                # add noise to public velocity (random rotation)
                random_angle = random.uniform(-self.sensing_noise*3.141592653589793, self.sensing_noise*3.141592653589793)
                random_rot_matrix = [[np.cos(random_angle), -np.sin(random_angle)], 
                        [np.sin(random_angle), np.cos(random_angle)]]
                agent.velocity_pub = np.matmul(random_rot_matrix, agent.velocity_pub) 

                # update coordinates according to velocity_comb (linear comb. of priv. and pul.)
                agent.velocity_comb = (1-self.trust)*agent.velocity_priv + self.trust*agent.velocity_pub
                agent.coordinates += agent.speed*agent.decision_time*agent.velocity_comb/np.linalg.norm(agent.velocity_comb)

            # if an agent is out of the simulation box, remove it
            if (agent.coordinates[0] > self.flow.length-1 or agent.coordinates[0] < 0 or 
                agent.coordinates[1] > self.flow.heigth-1 or agent.coordinates[1] < 0):
                self.agents.remove(agent)
                removed = True

        # return the removed flag
        return removed

    # detect other agents within the visual_radius
    def detect_neighbors(self, agent):
        # reset neighbors list
        agent.neighbors = []
        for candidate in self.agents:
            if candidate != agent:
                x_trasl = candidate.coordinates[0]-agent.coordinates[0]
                y_trasl = candidate.coordinates[1]-agent.coordinates[1]
                if x_trasl**2 + y_trasl**2 < agent.visual_radius**2:
                    agent.neighbors.append(candidate)

                    # activate an agent is any of its neighbours are activated
                    if not agent.go:
                        if candidate.go: 
                            agent.go = True

    # detect odor particles within the olfactoy_radius
    def sniff_particles(self, agent):
        # reset particles list
        agent.sniffed_particles = []
        for candidate in self.cloud.particles:
            x_trasl = candidate.coordinates[0]-agent.coordinates[0]
            y_trasl = candidate.coordinates[1]-agent.coordinates[1]
            if x_trasl**2 + y_trasl**2 < agent.olfactory_radius**2:
                agent.sniffed_particles.append(candidate)

    # update the wind estimate of an agent (i.e. private cues)
    def update_wind_estimate(self, agent):
        # interpolate the flow field to obtain the estimate of the local wind speed
        inst_wind_estimate = self.flow.interpolate(agent.coordinates)
        # incremental update rule for the ex. disc. running average
        agent.wind_estimate = self.c_exp*agent.wind_estimate + self.c_exp2*inst_wind_estimate

    # update the agent perception of the mean velocity of its neighbors (i.e. public cues)
    def update_public_velocity(self, agent):
        # reset sum
        sum_vel = np.array([0, 0])
        for neighbor in agent.neighbors:
            sum_vel = sum_vel + neighbor.velocity_comb
        # update public velocity
        if np.linalg.norm(sum_vel)>0:
            agent.velocity_pub = agent.speed*sum_vel/np.linalg.norm(sum_vel)

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
        self.__rot_matrix_45 = [[-2**(-0.5), 2**(-0.5)], [2**(-0.5), 2**(-0.5)]]
        self.__rot_matrix_neg45 = [[-2**(-0.5), 2**(-0.5)], [-2**(-0.5), -2**(-0.5)]]
        self.__rot_matrix_90 = [[0, -1], [1, 0]]

        # these attributes are updated by the Swarm() class:
        # estimate of the local wind velocity 
        self.wind_estimate = initial_wind_estimate
        # list of the particles within the olfactory_radius
        self.sniffed_particles = []
        # list of other agents within the visual_radius
        self.neighbors = []
        # flag to determine when to start the behavior of the agents
        self.go = False
        # private and public velocity of the agent
        self.velocity_priv = np.array([0, 0])
        self.velocity_pub = np.array([0, 0])
        # linear combination of the two
        self.velocity_comb = np.array([0, 0])

    # cast and surge behavior 
    # NB here and in cast() we only update the private velocity, we do NOT update the coordinates yet!
    def surge(self):
        # divide the wind estimate by its norm to obtain a unit vector
        norm_wind_estimate = self.wind_estimate/np.linalg.norm(self.wind_estimate)
        # update value of private velocity to move upwind
        self.velocity_priv = -norm_wind_estimate*self.speed
        # reset surging counters
        self.t_prime = 0; self.clock = 0

    def cast(self):
        # divide the wind estimate by its norm to obtain a unit vector
        norm_wind_estimate = self.wind_estimate/np.linalg.norm(self.wind_estimate)
        # move 45 degrees
        if self.clock == self.t_prime:
            if self.flip_dir: direction_45 = np.matmul(self.__rot_matrix_45, norm_wind_estimate)
            else: direction_45 = np.matmul(self.__rot_matrix_neg45, norm_wind_estimate)
            self.velocity_priv = direction_45*self.speed
            self.clock = 0
            self.t_prime += 2*self.decision_time
            self.flip_dir = not self.flip_dir
        # move crosswind
        else:
            if self.flip_dir: direction_crosswind = np.matmul(self.__rot_matrix_90, norm_wind_estimate)
            else: direction_crosswind = -np.matmul(self.__rot_matrix_90, norm_wind_estimate)
            # update value of private velocity to move crosswind
            self.velocity_priv = direction_crosswind*self.speed
            self.clock += self.decision_time

class Flow:
    def __init__(self, length, heigth, flow_dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity):
        # dimensions of the simulation box
        self.length = length
        self.heigth = heigth

        # time step
        self.flow_dt = flow_dt

        # parameters of the stochastic flow
        self.constL = flow_lengthscale
        self.tau = flow_corr_time
        self.mean_wind = mean_wind
        self.fluct_intensity = fluct_intensity

        # calculate useful constants
        urms = self.fluct_intensity*(self.mean_wind[0]**2 + self.mean_wind[1]**2)**0.5
        ks = 2*np.pi/self.constL
        self.__sqrtdt = self.flow_dt**0.5

        # calculate wavevectors
        K1x = [ks, 0, -ks, 0]
        K1y = [0, ks, 0, -ks]
        K2x = [ks, ks, -ks, -ks]
        K2y = [ks, -ks, -ks, ks]

        K1, K2 = [], []
        for ki in range(len(K1x)):
            K1.append([K1x[ki], K1y[ki]])
            K2.append([K2x[ki], K2y[ki]])

        self.Kall = K1 + K2

        # precalculate diffusion constant for different values of k
        self.diff_const = []
        for kvec in self.Kall:
            if kvec in K1:
                self.diff_const.append( (urms / (3**0.5 * ks)) * (2 / self.tau)**0.5 )
            elif kvec in K2:
                self.diff_const.append( 0.5* (urms / (3**0.5 * ks)) * (2 / self.tau)**0.5 )

        # precalculate all dotproducts
        self.dotprod = np.zeros([self.heigth,self.length,len(self.Kall)])
        for y in range(self.heigth):
            for x in range(self.length):
                for k in range(len(self.Kall)):
                    kvec = self.Kall[k]
                    self.dotprod[y][x][k] = kvec[0]*x + kvec[1]*y

        # initialise array for Fourier amplitudes
        self.amp = np.zeros(len(self.Kall))
        # self.amp = np.random.rand(len(self.Kall))

        # create arrays of coordinates for the interpolation of the velocity field
        self.__xc, self.__yc = np.arange(self.length), np.arange(self.heigth)

        # run a single timestep in order to initialise the velocity field (ux, uy)
        self.update()

    def update(self):
        # calculate increment of Fourier amplitudes
        for k in range(len(self.Kall)):
            kvec = self.Kall[k]
            self.amp[k] = self.amp[k] -self.amp[k]*self.flow_dt/self.tau + self.diff_const[k]*self.__get_deltaW()

        # compute velocity field
        vx, vy = np.zeros([self.heigth,self.length]), np.zeros([self.heigth,self.length])
        for y in range(self.heigth):
            for x in range(self.length):
                for k in range(len(self.Kall)):
                    kvec = self.Kall[k]
                    vx[y][x] += 2*self.amp[k] * np.sin(self.dotprod[y][x][k]) * kvec[1]
                    vy[y][x] += -2*self.amp[k] * np.sin(self.dotprod[y][x][k]) * kvec[0]

        # velocity field is mean wind + noise
        self.ux = self.mean_wind[0] + vx
        self.uy = self.mean_wind[1] + vy

    # sample a Wiener increment
    def __get_deltaW(self):
        # return np.random.normal(0.0, 1.0)*self.__sqrtdt
        return random.gauss(0.0, 1.0)*self.__sqrtdt

    # interpolate the velocity field at a given position
    def interpolate(self, position):
        ux_interp = RegularGridInterpolator((self.__xc, self.__yc), self.ux.T) 
        uy_interp = RegularGridInterpolator((self.__xc, self.__yc), self.uy.T) 
        return np.array([ux_interp(position)[0], uy_interp(position)[0]])

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
        self.next_time = int(self.__get_next_time())
        # initialise empty list for the odor particles
        self.particles = []

    def update(self):
        # update particle positions according to the velocity field 
        removed = False
        for particle in self.particles:
            # interpolate the velocity field at the particle position
            u_interp = self.flow.interpolate(particle.coordinates)     
            # and update its coordinates accordingly
            particle.coordinates += u_interp*self.particle_dt
            # if any of the particles is out of the simulation box, remove it
            if (particle.coordinates[0] > self.flow.length-1 or 
                particle.coordinates[0] < 0 or 
                particle.coordinates[1] > self.flow.heigth-1 or 
                particle.coordinates[1] < 0):
                self.particles.remove(particle)
                removed = True

        # create new particle
        added = False
        # if the time for the generation of a particle (since last generation) has passed 
        if self.stopwatch == self.next_time:
            # create a new particle at the source position
            self.particles.append(Particle(self.source_coordinates.copy()))
            # reset the counter
            self.stopwatch = 0
            # and extract a new time
            self.next_time = int(self.__get_next_time())
            added = True
        else:
            # otherwise, increase the counter
            # TODO +1 or +dt?
            self.stopwatch += 1
        # return flags about removal or creation of new particles
        return removed, added

    # sample time for the generation of next particle from an exponential distribution
    def __get_next_time(self):
        return random.expovariate(self.particle_rate)

class Particle:
    def __init__(self, coordinates):
        self.coordinates = coordinates
