import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.interpolate import RegularGridInterpolator

# extract matplotlib default colors for plotting purposes
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

class Simulation:
    def __init__(self, time_steps, flow, swarm, cloud, real_time_plot, pause_time):
        # total time steps of the simulation
        self.time_steps = time_steps

        # flow, swarm and swarm objects
        self.flow = flow
        self.swarm = swarm
        self.cloud = cloud

        # flag to enable or disable real time plotting
        self.real_time_plot = real_time_plot

        # pause time between frames during plotting
        self.pause_time = pause_time

        if self.real_time_plot:
            # create figure and axes for plotting
            plt.gca().remove()
            self.axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, self.flow.length), ylim=(0, self.flow.heigth), title='time = 0')

            # # add arrows for the velocity field
            # self.flow_arrows = self.axes.quiver(self.flow.ux, self.flow.uy, alpha=0.3)
            # # self.axes.streamplot(np.arange(self.flow.length),np.arange(self.flow.heigth),self.flow.ux,self.flow.uy)

            # add source and spawn circle drawings
            plt.plot(*self.cloud.source_coordinates, c='k', marker='d')
            spawn_circle = plt.Circle(self.swarm.spawn_center, self.swarm.spawn_radius, fill=False, ls='--', color='k', alpha=0.5)
            self.axes.add_patch(spawn_circle)

            # add agents points and visual circles
            m=0
            for agent in self.swarm.agents:
                agent_point = plt.Circle(agent.coordinates, 0.25, color=colors[m], label=m)
                visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[m], alpha=0.5)
                olfactory_circle = plt.Circle(agent.coordinates, agent.olfactory_radius, fill=False, color=colors[m], alpha=0.5, ls='--')
                self.axes.add_patch(agent_point)
                # self.axes.add_patch(visual_circle)
                self.axes.add_patch(olfactory_circle)
                m+=1
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

            # print('-----')

            # if a particle was added to the cloud, add a patch to axes
            if self.real_time_plot and particle_added: 
                self.axes.add_patch( plt.Circle(self.cloud.particles[-1].coordinates, 0.15, color='b') ) 

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

                # # update the flow arrows
                # self.flow_arrows.set_UVC(self.flow.ux, self.flow.uy)

                # and redraw the patches
                plt.draw()
                plt.pause(self.pause_time)

class Swarm:
    def __init__(self, n_agents, spawn_center, spawn_radius, measure_time,
            decision_time, agent_speed, olfactory_radius, visual_radius, cloud, flow):
        # parameters of the agents and initial spawn conditions
        self.n_agents = n_agents
        self.spawn_center = spawn_center
        self.spawn_radius = spawn_radius
        self.measure_time = measure_time
        self.decision_time = decision_time
        self.agent_speed = agent_speed
        self.olfactory_radius = olfactory_radius
        self.visual_radius = visual_radius

        # we also need the cloud object, to sniff the particles
        self.cloud = cloud

        # and the flow, to estimate the wind velocity
        self.flow = flow

        # initialize empty list for the swarm of agents
        self.agents = []

        # extract uniformly random points within the initial spawn circle
        # https://stackoverflow.com/questions/5837572/generate-a-random-point-within-a-circle-uniformly
        for nn in range(self.n_agents):
            radius = self.spawn_radius*np.sqrt(np.random.rand())
            theta = np.random.rand()*2*np.pi
            coordinates = [self.spawn_center[0]+radius*np.cos(theta), self.spawn_center[1]+radius*np.sin(theta)]
            # spawn each agent randomly in the circle and give it a label
            self.agents.append(Moth(nn, coordinates, self.agent_speed, self.measure_time, self.olfactory_radius, self.visual_radius))

    def update(self):
        removed = False
        # determine behavior of the agents
        for agent in self.agents:
            # find neighbors (i.e. other agents within visual_radius) of each agent in the swarm
            neighbors = self.detect_neighbors(agent)

            # detect odor particles
            sniffed_particles = self.sniff_particles(agent)

            # SURGE
            # 1. If the agent has detected at least one flow particle in the time interval Delta_t (measure time), it moves
            # upwind by v_0*Delta_t units, v_0 being the speed of the agent. This phase is called "surging".  The agent 
            # remains in the surging phase as long as it detects flow particles within every Delta_t time and after taking 
            # every step in the surging phase the agent sets t'=0, a number that the agent keeps track of.

            # TODO add measure_time interval!
            if len(sniffed_particles)>0:
                self.update_wind_estimate(agent)
                agent.surge()

            # # print neighbors info in terminal
            # if len(neighbors)>0:
            #     print(f'neighbors of agent {agent.label}:', end=' ')
            #     for neighbor in neighbors:
            #         print(neighbor.label, end=' ')
            #     print()

            # if an agent is out of the simulation box, remove it
            if (agent.coordinates[0] > self.flow.length-1 or agent.coordinates[0] < 0 or 
                agent.coordinates[1] > self.flow.heigth-1 or agent.coordinates[1] < 0):
                self.agents.remove(agent)
                removed = True
        # return the removed flag
        return removed

    # function to detect other agents within the visual_radius
    def detect_neighbors(self, agent):
        # reset neighbors list
        neighbors = []
        for candidate in self.agents:
            if candidate != agent:
                x_trasl = candidate.coordinates[0]-agent.coordinates[0]
                y_trasl = candidate.coordinates[1]-agent.coordinates[1]
                if x_trasl**2 + y_trasl**2 < agent.visual_radius**2:
                    neighbors.append(candidate)
        return neighbors

    # function to detect odor particles within the olfactoy_radius
    def sniff_particles(self, agent):
        # find neighboring particles of each agent
        sniffed_particles = []
        for candidate in self.cloud.particles:
            x_trasl = candidate.coordinates[0]-agent.coordinates[0]
            y_trasl = candidate.coordinates[1]-agent.coordinates[1]
            if x_trasl**2 + y_trasl**2 < agent.olfactory_radius**2:
                sniffed_particles.append(candidate)
                # print(f'agent {agent.label} sniffed a particle!')
        return sniffed_particles

    # TODO this will be a discounted running average
    def update_wind_estimate(self, agent):
        agent.wind_estimate[0], agent.wind_estimate[1] = self.flow.interpolate(agent.coordinates)

class Moth:
    def __init__(self, label, coordinates, agent_speed, measure_time, olfactory_radius, visual_radius):
        # parameters of the moth
        self.label = label
        self.coordinates = coordinates
        self.agent_speed = agent_speed
        self.measure_time = measure_time
        self.olfactory_radius = olfactory_radius
        self.visual_radius = visual_radius

        # moth estimate of the wind velocity along x and y
        self.wind_estimate = [0, 0]

    # TODO the speed of movement should be self.agent_speed!
    def surge(self):
        self.coordinates[0] += -self.wind_estimate[0]*self.measure_time
        self.coordinates[1] += -self.wind_estimate[1]*self.measure_time

    # CAST
    # 2. In absence of any odors, the agent moves by v0*Delta_t units in a direction that forms an angle of +45◦ with 
    # respect to the locally estimated upwind direction.
    # 3. The agent updates t' as t' ← t'+2*Delta_t and then moves in the crosswind direction for time period t' with
    # speed v_0.
    # 4. The agent moves by v_0*Delta_t units in the direction that forms an angle of −45◦ with respect to the locally
    # estimated upwind direction.
    # 5. The agent updates t' ← t'+2*Delta_t and then moves with speed v_0 in the crosswind direction (opposite to the 
    # one taken in step 3) for time period t' and resumes further from step 2.
    # Steps 2-5 describe the "casting" phase, which is terminated as soon as the agent detects an flow particle. Then 
    # the agent sets t' = 0 and starts the surging phase (step 1) from the next decision time.

    def cast(self):
        pass

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
        # self.amp = np.random.rand(len(self.Kall))
        self.amp = np.zeros(len(self.Kall))

        # create arrays of coordinates for the interpolation of the velocity field
        self.__xc, self.__yc = np.arange(self.length), np.arange(self.heigth)

        # run a single timestep in order to initialise the velocity field (ux, uy)
        self.update()

    def update(self):
        # # calculate increment of Fourier amplitudes
        # for ki in range(len(Kall)):
        #     kvec = Kall[ki]
        #     amp[ki] = amp[ki] -amp[ki]*dt/self.tau + self.diff_const[ki]*self.__get_deltaW()

        # self.psi = np.zeros([self.heigth,self.length])

        # compute velocity field
        vx, vy = np.zeros([self.heigth,self.length]), np.zeros([self.heigth,self.length])
        for y in range(self.heigth):
            for x in range(self.length):
                for k in range(len(self.Kall)):
                    kvec = self.Kall[k]
                    # TODO qui o prima? (direi qui! altrimenti c'è periodicità perfetta)
                    self.amp[k] = self.amp[k] - self.amp[k]*self.flow_dt/self.tau + self.diff_const[k]*self.__get_deltaW()
                    vx[y][x] += 2*self.amp[k] * np.sin(self.dotprod[y][x][k]) * kvec[1]
                    vy[y][x] += -2*self.amp[k] * np.sin(self.dotprod[y][x][k]) * kvec[0]
                    # the two forms are equivalent
                    # self.psi[y][x] += amp[ki] * ( np.exp(1j*(kvec[0]*x+kvec[1]*y)) + np.exp(-1j*(kvec[0]*x+kvec[1]*y)) )
                    # self.psi[y][x] += self.amp[ki] * 2*np.cos(kvec[0]*x + kvec[1]*y)

        # print(self.dotprod[5][0])
        # print()

        # velocity field is mean wind + noise
        self.ux = self.mean_wind[0] + vx
        self.uy = self.mean_wind[1] + vy

    # internal function to sample a Wiener increment
    def __get_deltaW(self):
        # return np.random.normal(0.0, 1.0)*self.__sqrtdt
        return random.gauss(0.0, 1.0)*self.__sqrtdt

    # function to interpolate the velocity field at a given position
    def interpolate(self, position):
        ux_interp = RegularGridInterpolator((self.__xc, self.__yc), self.ux.T) 
        uy_interp = RegularGridInterpolator((self.__xc, self.__yc), self.uy.T) 
        return ux_interp(position)[0], uy_interp(position)[0] 

class Cloud:
    def __init__(self, particle_dt, particle_rate, source_coordinates, flow):
        # time step
        self.particle_dt = particle_dt
        # position of the odor source
        self.source_coordinates = source_coordinates
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
            self.stopwatch += 1

        removed = False
        # update particle positions according to the velocity field 
        for particle in self.particles:
            # interpolate the velocity field at the particle position
            # TODO the dt for the particles is the same of the fluctuations (dt)?
            ux_interp, uy_interp = self.flow.interpolate(particle.coordinates)     
            particle.coordinates[0] += ux_interp*self.particle_dt
            particle.coordinates[1] += uy_interp*self.particle_dt
            # if any of the particles is out of the simulation box, remove it
            if (particle.coordinates[0] > self.flow.length-1 or 
                particle.coordinates[0] < 0 or 
                particle.coordinates[1] > self.flow.heigth-1 or 
                particle.coordinates[1] < 0):
                self.particles.remove(particle)
                removed = True
        # return flags
        return removed, added

    # sample time for the generation of next particle from an exponential distribution
    def __get_next_time(self):
        return random.expovariate(self.particle_rate)

class Particle:
    def __init__(self, coordinates):
        self.coordinates = coordinates
