import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.interpolate import RegularGridInterpolator

# extract matplotlib default colors for plotting purposes
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

class Simulation:
    def __init__(self, time_steps, particle_rate, source_coordinates, flow, swarm, real_time_plot):
        # total time steps of the simulation
        self.time_steps = time_steps

        # position of the odor source
        self.source_coordinates = source_coordinates

        # rate for the odor particle generation
        self.particle_rate = particle_rate

        # source and swarm objects
        self.flow = flow
        self.swarm = swarm

        # flag to enable or disable real time plotting
        self.real_time_plot = real_time_plot

        # pause time between frames during plotting
        self.__pause_time = 0.01

        # initialize empty list for the odor particles
        self.particles = []

        if self.real_time_plot:
            # create figure and axes for plotting
            plt.gca().remove()
            plt.subplot(aspect='equal', adjustable='box', xlim=(0, self.flow.length), ylim=(0, self.flow.heigth), title='time = 0')

            # add arrows for the velocity field
            self.flow_arrows = plt.gca().quiver(self.flow.ux, self.flow.uy, alpha=0.25)
            # plt.streamplot(np.arange(self.flow.length),np.arange(self.flow.heigth),self.flow.ux,self.flow.uy)

            # add source and spawn circle drawings
            plt.plot(*self.source_coordinates, c='b', marker='o')
            spawn_circle = plt.Circle(self.swarm.spawn_center, self.swarm.spawn_radius, fill=False, ls='--', color='k', alpha=0.5)
            plt.gca().add_patch(spawn_circle)

            # add agents points and visual circles
            m=0
            for agent in self.swarm.agents:
                agent_point = plt.Circle(agent.coordinates, 0.25, color=colors[m], label=m)
                visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[m], alpha=0.5)
                plt.gca().add_patch(agent_point)
                plt.gca().add_patch(visual_circle)
                m+=1
            plt.legend(fancybox=False, loc=3)

            plt.pause(self.__pause_time)

    def run(self):
        # initialise counter for the generation of odor partices
        stopwatch = 0
        # get time for the generation of the first particle
        next_time = int(self.__get_next_time())
        for time in range(self.time_steps):
            # if the time for the generation of a particle (since last generation) has passed 
            if stopwatch == next_time:
                # create a new particle at the source position
                self.particles.append(Particle(self.source_coordinates.copy()))
                # and add a patch for plotting
                if self.real_time_plot: plt.gca().add_patch( plt.Circle(self.particles[-1].coordinates, 0.2, color='b') ) 
                # reset the counter
                stopwatch = 0
                # and extract a new time
                next_time = int(self.__get_next_time())
            else:
                # otherwise, increase the counter
                stopwatch += 1

            # update particle positions according to the velocity field
            removed = False
            for particle in self.particles:
                # interpolate the velocity field at the particle position
                # TODO the dt for the particles is the same of the fluctuations (dt)?
                ux_interp, uy_interp = self.flow.interpolate(particle.coordinates)     
                particle.coordinates[0] += ux_interp*1
                particle.coordinates[1] += uy_interp*1
                # if any of the particles is out of the simulation box, remove it
                if (particle.coordinates[0] > self.flow.length-1 or 
                    particle.coordinates[0] < 0 or 
                    particle.coordinates[1] > self.flow.heigth -1 or 
                    particle.coordinates[1] < 0):
                    self.particles.remove(particle)
                    removed = True

            # TODO what do we do with the agents that fly outside the box? remove them?

            # and also remove its patch
            if removed and self.real_time_plot:
                for patch in plt.gca().patches:
                    if (patch.center[0] > self.flow.length-1 or 
                        patch.center[0] < 0 or 
                        patch.center[1] > self.flow.heigth -1 or 
                        patch.center[1] < 0):
                        patch.remove()

            # update the flow
            self.flow.update()

            # update the swarm
            self.swarm.update()

            # # print neighbors info in terminal
            # print(f'\ntime = {time}')
            # for agent in self.swarm.agents:
            #     print(f'neighbors of agent {agent.label}:', end=' ')
            #     for neighbor in agent.neighbors:
            #         print(neighbor.label, end=' ')
            #     print()

            # plot in real time
            if self.real_time_plot:
                plt.title(f'time = {time+1}')
                # update the arrows
                self.flow_arrows.set_UVC(self.flow.ux, self.flow.uy)
                # and redwar the patches
                plt.draw()
                plt.pause(self.__pause_time)

    # sample time for the generation of next particle from an exponential distribution
    def __get_next_time(self):
        return random.expovariate(self.particle_rate)

class Swarm:
    def __init__(self, n_agents, spawn_center, spawn_radius, measure_time, decision_time, 
            agent_speed, olfactory_radius, visual_radius):
        # parameters of the agents and initial spawn conditions
        self.n_agents = n_agents
        self.spawn_center = spawn_center
        self.spawn_radius = spawn_radius
        self.measure_time = measure_time
        self.decision_time = decision_time
        self.agent_speed = agent_speed
        self.olfactory_radius = olfactory_radius
        self.visual_radius = visual_radius

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
        # find neighbors (i.e. other agents within visual_radius) of each agent in the swarm
        self.detect_neighbors()

        # determine behavior of the agents
        for agent in self.agents:
            agent.cast()

    def detect_neighbors(self):
        # count neighbors of each agent
        for agent in self.agents:
            # reset neighbors list
            agent.neighbors = []
            for candidate in self.agents:
                if candidate != agent:
                    x_trasl = candidate.coordinates[0]-agent.coordinates[0]
                    y_trasl = candidate.coordinates[1]-agent.coordinates[1]
                    if x_trasl**2 + y_trasl**2 < agent.visual_radius**2:
                        agent.neighbors.append(candidate)

class Moth:
    def __init__(self, label, coordinates, agent_speed, measure_time, olfactory_radius, visual_radius):
        self.label = label
        self.coordinates = coordinates
        self.agent_speed = agent_speed
        self.measure_time = measure_time
        self.olfactory_radius = olfactory_radius
        self.visual_radius = visual_radius

        # initialize empty list that will be used to track the neighbors
        self.neighbors = []

        # SURGE
        # 1. If the agent has detected at least one flow particle in the time interval Delta_t (measure time), it moves
        # upwind by v_0*Delta_t units, v_0 being the speed of the agent. This phase is called "surging".  The agent 
        # remains in the surging phase as long as it detects flow particles within every Delta_t time and after taking 
        # every step in the surging phase the agent sets t'=0, a number that the agent keeps track of.

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

    def surge(self):
        pass

    def cast(self):
        self.coordinates[0] -= self.agent_speed*self.measure_time 
        self.coordinates[1] += 2*(np.random.rand()-0.5)

class Flow:
    def __init__(self, length, heigth, dt, flow_lengthscale, flow_corr_time, mean_wind, fluct_intensity):
        # dimensions of the simulation box
        self.length = length
        self.heigth = heigth

        # time step
        self.dt = dt

        # parameters of the stochastic flow
        self.constL = flow_lengthscale
        self.tau = flow_corr_time
        self.mean_wind = mean_wind
        self.fluct_intensity = fluct_intensity

        # calculate useful constants
        urms = self.fluct_intensity*(self.mean_wind[0]**2 + self.mean_wind[1]**2)**0.5
        ks = 2*np.pi/self.constL
        self.__sqrtdt = self.dt**0.5

        # calculate wavevectors
        K1x = [ks, 0, -ks, 0]
        K1y = [0, ks, 0, -ks]
        K2x = [ks, ks, -ks, -ks]
        K2y = [ks, -ks, -ks, ks]

        K1, K2 = [], []
        for ki in range(len(K1x)):
            K1.append([K1x[ki], K1y[ki]])
            K2.append([K2x[ki], K2y[ki]])

        self.__Kall = K1 + K2

        # precalculate diffusion constant for different values of k
        self.__diff_const = []
        for kvec in self.__Kall:
            if kvec in K1:
                self.__diff_const.append( (urms / (3**0.5 * ks)) * (2 / self.tau)**0.5 )
            elif kvec in K2:
                self.__diff_const.append( 0.5* (urms / (3**0.5 * ks)) * (2 / self.tau)**0.5 )

        # precalculate all dotproducts
        self.__dotprod = np.zeros([self.heigth,self.length])
        for y in range(self.heigth):
            for x in range(self.length):
                for kvec in self.__Kall:
                    self.__dotprod[y][x] = kvec[0]*x + kvec[1]*y

        # initialise array for Fourier amplitudes
        self.__amp = np.random.rand(len(self.__Kall))
        # self.__amp = np.zeros(len(self.__Kall))

        # create arrays of coordinates for the interpolation of the velocity field
        self.__xc, self.__yc = np.arange(self.length), np.arange(self.heigth)

        # run a single timestep in order to initialise the velocity field (ux, uy)
        self.update()

    def update(self):
        # # calculate increment of Fourier amplitudes
        # for ki in range(len(__Kall)):
        #     kvec = __Kall[ki]
        #     __amp[ki] = __amp[ki] -__amp[ki]*dt/self.tau + self.__diff_const[ki]*self.__get_deltaW()

        # self.psi = np.zeros([self.heigth,self.length])

        # compute velocity field
        vx, vy = np.zeros([self.heigth,self.length]), np.zeros([self.heigth,self.length])
        for y in range(self.heigth):
            for x in range(self.length):
                for ki in range(len(self.__Kall)):
                    kvec = self.__Kall[ki]
                    # TODO qui o prima? (direi qui! altrimenti c'è periodicità perfetta)
                    self.__amp[ki] = self.__amp[ki] - self.__amp[ki]*self.dt/self.tau + self.__diff_const[ki]*self.__get_deltaW()
                    vx[y][x] += 2*self.__amp[ki] * np.sin(self.__dotprod[y][x]) * kvec[1]
                    vy[y][x] += -2*self.__amp[ki] * np.sin(self.__dotprod[y][x]) * kvec[0]
                    # the two forms are equivalent
                    # self.psi[y][x] += __amp[ki] * ( np.exp(1j*(kvec[0]*x+kvec[1]*y)) + np.exp(-1j*(kvec[0]*x+kvec[1]*y)) )
                    # self.psi[y][x] += self.__amp[ki] * 2*np.cos(kvec[0]*x + kvec[1]*y)

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

class Particle:
    def __init__(self, coordinates):
        self.coordinates = coordinates
