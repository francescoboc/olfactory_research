from utils import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random, os, h5py

# hack to prevent raising KeyboardInterrupt when stopping the script with ctrl-c
# https://stackoverflow.com/questions/7073268/remove-traceback-in-python-on-ctrl-c
import signal, sys
signal.signal(signal.SIGINT, lambda x, y: sys.exit())

def initialise_rng(seed):
    global rng 
    rng = random.Random(seed)

class Simulation:
    def __init__(self, 
            final_time, 
            swarm, 
            cloud=None,
            real_time_plot=False, 
            pause_time=0.001, 
            save_frames=False,
            ):

        self.final_time = final_time
        # self.final_x = final_x

        self.swarm = swarm
        self.cloud = cloud

        # flag to enable or disable real time plotting
        self.real_time_plot = real_time_plot
        self.save_frames = save_frames

        # pause time between frames during plotting
        self.pause_time = pause_time

        # calculate total time steps
        self.tot_time_steps = int(self.final_time/self.swarm.dt)

        if self.real_time_plot:
            # create figure and axes for plotting
            if self.save_frames:
                fig = plt.figure(figsize=(13,8))
            else:
                plt.gca().remove()

            if self.cloud is not None:
                self.axes = plt.subplot(aspect='equal', adjustable='box', xlim=(self.cloud.horizontal_shift-margin, 
                    self.cloud.x_max + self.cloud.horizontal_shift+margin), ylim=(self.cloud.vertical_shift-margin, self.cloud.y_max + self.cloud.vertical_shift+margin))
            else:
                self.axes = plt.subplot(aspect='equal', adjustable='box', xlim=(-10, self.swarm.length), ylim=(-self.swarm.height/2, self.swarm.height/2))

            self.axes.add_patch( plt.Circle(self.swarm.spawn_center, self.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2) )
            self.axes.add_patch( plt.Circle(self.swarm.source_coordinates, 0.3, color='k') )

            # add patches for source and spawn circle 
            spawn_circle = plt.Circle(self.swarm.spawn_center, self.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2)

            # image of the odor cloud
            if self.cloud is not None:
                self.odor_image = self.axes.imshow(self.cloud.odor>self.swarm.threshold, extent=(self.cloud.horizontal_shift,
                    self.cloud.x_max+self.cloud.horizontal_shift,self.cloud.vertical_shift,self.cloud.y_max+self.cloud.vertical_shift), cmap=colormap, alpha=0.33, origin='lower')
                # self.odor_image = self.axes.imshow(self.cloud.odor, extent=(self.cloud.horizontal_shift,
                    # self.cloud.x_max+self.cloud.horizontal_shift,self.cloud.vertical_shift,self.cloud.y_max+self.cloud.vertical_shift), cmap='viridis', origin='lower')

            # add agents points and visual circles
            index = 0
            for agent in self.swarm.agents:
                color_id = min([len(colors), index%len(colors)]) 
                # agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[color_id], label=index)
                agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[3], label=index)
                # visual_circle = plt.Circle(agent.coordinates, self.swarm.visual_radius, fill=False, color=colors[color_id], alpha=0.1)
                visual_circle = plt.Circle(agent.coordinates, self.swarm.visual_radius, fill=False, color=colors[3], alpha=0.1)
                self.axes.add_patch(agent_point); self.axes.add_patch(visual_circle)
                index += 1
                if index >= len(colors): index = 0
            plt.axis('off')

    def run(self):
        # reset flags and timers
        success = False
        # agent_removed = False
        time_step = 0
        count = 0

        while True:
            # update the swarm
            self.swarm.update(time_step)
            # agent_removed, success = self.swarm.update(time_step)

            # update the odor cloud
            if self.cloud is not None:
                self.cloud.update()

            # update global time step 
            time_step += 1

            # # remove patches from axes in case an agent was removed
            # if self.real_time_plot and agent_removed:
            #     for patch in self.axes.patches:
            #         if (patch.center[0] > self.swarm.length-1 or patch.center[0] < 0 or 
            #             patch.center[1] > self.swarm.height -1 or patch.center[1] < 0):
            #             patch.remove()

            # plot in real time
            if self.real_time_plot:
                if self.cloud is not None:
                    self.odor_image.set_data(self.cloud.odor>self.swarm.threshold)
                # self.odor_image.set_data(self.cloud.odor)
                plt.title(rf'Time = {np.round(time_step*self.swarm.dt, 2)}')
                # self.axes.plot(self.swarm.center_of_mass[0],self.swarm.center_of_mass[1],'.r',ms=1)
                if self.save_frames: plt.savefig(f'frames/frame{time_step}.png')
                plt.pause(self.pause_time)

            # if an agent successuffly reached the source, stop
            if self.swarm.success: 

                # # count agents within a circle of size spawn_radius around the source
                # for candidate in self.swarm.agents:
                #     coord_trasl = candidate.coordinates - self.swarm.source_coordinates
                #     if norm(coord_trasl) < self.swarm.spawn_radius:
                #         count += 1

                break

            # # BREAK conditions
            # agents_arrived = len(self.swarm.reach_times) 
            # if agents_arrived == self.swarm.n_agents:
            #     print(f'{tc.green}All agents reached the source{tc.end}')
            #     break


            # if final_time is 0, check if the last agent passed the source
            if self.final_time == 0:
                x_coordinates = [agent.coordinates[0] for agent in self.swarm.agents]
                # if min(x_coordinates) >= self.final_x:

                if len(x_coordinates)>0:
                    if min(x_coordinates) >= self.swarm.source_coordinates[0]:
                        break

                # if x_coordinates is an empty sequence, all agents are out
                else:
                    print(f'All agents are out of the box!')
                    break

            # otherwise, check if we reached final_time
            else:
                if time_step == self.tot_time_steps: 
                    break

            # # if all agents are out of the simulation box, stop
            # if not self.swarm.agents: 
            #     print(f'All agents are out of the box')
            #     break

            # # PBC
            # for agent in self.swarm.agents:
            #     if agent.coordinates[0] > self.swarm.length-1:
            #         agent.coordinates[0] -= self.swarm.length
            #     if agent.coordinates[0] < 0:
            #         agent.coordinates[0] += self.swarm.length
            #     if agent.coordinates[1] > self.swarm.height-1:
            #         agent.coordinates[1] -= self.swarm.height
            #     if agent.coordinates[1] < 0:
            #         agent.coordinates[1] += self.swarm.height

        if self.swarm.success:
            return self.swarm.reach_times[0], True
        else:
            return np.inf, False

        # else:
        #     return self.swarm.reach_times, self.swarm.success, count 

class Swarm:
    def __init__(self,
            private_behavior,
            n_agents, 
            spawn_radius, 
            speed, 
            visual_radius, 
            olfactory_radius,
            sensing_noise, 
            wind_noise, 
            trust, 
            length, 
            height,
            source_coordinates, 
            reach_radius, 
            rand_casting_steps,
            rand_casting_direction,
            dt, 
            memory_time,
            decision_time,
            threshold,
            cloud,
            method,
            mu,
            sigma):

        # parameters of the agents and initial spawn conditions
        self.n_agents = n_agents
        self.spawn_radius = spawn_radius
        self.speed = speed
        self.visual_radius = visual_radius
        self.olfactory_radius = olfactory_radius
        self.sensing_noise = sensing_noise
        self.wind_noise = wind_noise
        self.cloud = cloud
        self.method = method

        # spawn center fixed at the origin
        self.spawn_center = (0, 0)

        self.trust = trust

        self.length = length
        self.height = height

        self.source_coordinates = source_coordinates
        self.reach_radius = reach_radius

        self.rand_casting_steps = rand_casting_steps
        self.rand_casting_direction = rand_casting_direction
        self.dt = dt
        self.memory_time = memory_time
        self.decision_time = decision_time
        self.threshold = threshold

        # initialise empty list for the swarm of agents
        self.agents = []

        # constants for the update of the exp. disc. running average of the public velocity
        self.c_exp = np.exp(-(self.dt/self.memory_time))
        self.c_exp2 = 1 - self.c_exp

        self.mu = mu
        self.sigma = sigma

        # self.norm_sum_vels_avg = []
        # self.norm_sum_vels_std = []
        # self.max_diff = []

        # determine private behavior of the agents
        if private_behavior == 'cast_and_surge':
            self.update_private_velocity = self.cast_and_surge
        elif private_behavior == 'biased_rw':
            self.update_private_velocity = self.biased_rw
        else:
            raise Exception('Unsupported private behavior')

        # create empty lists for the reach times
        self.reach_times = []
        self.success = False

        # extract uniformly random points within the initial spawn circle
        # https://stackoverflow.com/questions/5837572/generate-a-random-point-within-a-circle-uniformly
        self.coord_x, self.coord_y = {}, {}
        for n_ag in range(self.n_agents):
            # spawn each agent randomly in the circle
            radius = self.spawn_radius*np.sqrt(rng.random())
            theta = rng.random()*2*np.pi
            rand_x = self.spawn_center[0]+radius*np.cos(theta)
            rand_y = self.spawn_center[1]+radius*np.sin(theta)
            new_agent = Agent(n_ag, [rand_x, rand_y], self.speed, self.trust, self.wind_noise, self.decision_time, self.rand_casting_steps, self.rand_casting_direction, self.dt, self.mu, self.sigma)
            self.agents.append(new_agent)
            self.coord_x[n_ag] = [rand_x]
            self.coord_y[n_ag] = [rand_y]

        # # place agents on a circle
        # self.coord_x, self.coord_y = {}, {}
        # for n_ag in range(self.n_agents):
        #     radius = self.spawn_radius
        #     theta = (n_ag)*2*np.pi/(n_agents)
        #     pos_x = self.spawn_center[0]+radius*np.cos(theta)
        #     pos_y = self.spawn_center[1]+radius*np.sin(theta)
        #     new_agent = Agent(n_ag, [pos_x, pos_y], self.speed, self.trust, self.wind_noise, self.decision_time, self.rand_casting_steps, self.rand_casting_direction, self.dt, self.mu, self.sigma)
        #     self.agents.append(new_agent)
        #     self.coord_x[n_ag] = [pos_x]
        #     self.coord_y[n_ag] = [pos_y]

        # initialize public velocity of each agent
        for agent in self.agents:
            # find neighbors (i.e. other agents within visual_radius) of the agent
            self.detect_neighbors(agent)
            # if there are neighbors:
            alone = False
            if agent.neighbors:
                # reset sum
                sum_vel = np.array([0, 0])
                for neighbor in agent.neighbors:
                    sum_vel = sum_vel + neighbor.combined_velocity
                # calculate instantaneous public velocity
                instant_public_velocity = agent.speed*normalised(sum_vel)
            # otherwise, set alone flag to True
            else:
                alone = True
                instant_public_velocity = np.array([0, 0])
            agent.public_velocity = instant_public_velocity.copy() 
            agent.alone = alone

        # # initialise position of center of mass
        # pos_x = [agent.coordinates[0] for agent in self.agents]
        # pos_y = [agent.coordinates[1] for agent in self.agents]
        # self.center_of_mass = np.array([np.mean(pos_x), np.mean(pos_y)])
        # self.com_history = [self.center_of_mass.copy()]

        # sum_vel = np.array([0, 0])
        # for agent in self.agents:
            # self.update_private_velocity(agent, 0)
            # sum_vel = sum_vel + agent.private_velocity
        # self.wt_history = [sum_vel/self.n_agents]
        self.wt_history = []

    def update(self, time_step):
        # removed = False

        # TODO with odor, the agent should decide if change from casting to surging only at every decision_time!
        # norm_sum_vels = []
        for agent in self.agents:
            # sniff odor field
            if self.cloud is not None:
                self.sniff_odor(agent)

            # update private and public velocity of the agent
            self.update_private_velocity(agent, time_step)

            # self.update_public_velocity(agent)
            sum_vel = self.update_public_velocity(agent)
            # norm_sum_vels.append(norm(sum_vel)/agent.speed)

        maximum = 0
        for agent in self.agents:
            # calculate combined velocity (linear comb. of priv. and publ. cues)
            if not agent.alone:
                agent.combined_velocity = (1-agent.trust)*agent.private_velocity + agent.trust*agent.public_velocity
            else:
                agent.combined_velocity = agent.private_velocity

            max_agent = 0
            for agent_j in self.agents:
                if agent != agent_j:
                    candidate = norm(agent.combined_velocity - agent_j.combined_velocity)
                    if candidate > max_agent:
                        max_agent = candidate

            if max_agent > maximum:
                maximum = max_agent

            # update agent's coordinates
            agent.coordinates += agent.speed*agent.dt*normalised(agent.combined_velocity)
            self.coord_x[agent.label].append(agent.coordinates[0])
            self.coord_y[agent.label].append(agent.coordinates[1])

            # check if agent reached the target
            if self.check_reach(agent):
                self.reach_times.append(time_step*self.dt)
                self.success = True

        # self.max_diff.append(maximum)

        # self.norm_sum_vels_avg.append(np.mean(norm_sum_vels))
        # self.norm_sum_vels_std.append(np.std(norm_sum_vels))

        # pos_x = [agent.coordinates[0] for agent in self.agents]
        # pos_y = [agent.coordinates[1] for agent in self.agents]
        # self.center_of_mass = np.array([np.mean(pos_x), np.mean(pos_y)])
        # self.com_history.append(self.center_of_mass.copy())

        # sum_vel = np.array([0, 0])
        # for agent in self.agents:
        #     sum_vel = sum_vel + agent.private_velocity
        # self.wt_history.append(sum_vel/self.n_agents)

        # if an agent is out of the simulation box, remove it
        if (agent.coordinates[1] > self.height or agent.coordinates[1] < -self.height):
            self.agents.remove(agent)
            # removed = True

    # update the agents perception of the mean velocity of neighborrs (i.e. public cues)
    def update_public_velocity(self, agent):
    # def update_public_velocity(self, agent, time_step):
        # find neighbors (i.e. other agents within visual_radius) of the agent
        self.detect_neighbors(agent)
        # if there are neighbors:
        alone = False
        if agent.neighbors:
            # reset sum
            sum_vel = np.array([0, 0])
            for neighbor in agent.neighbors:
                sum_vel = sum_vel + neighbor.combined_velocity
            # calculate instantaneous public velocity
            instant_public_velocity = agent.speed*normalised(sum_vel)
        # otherwise, set alone flag to True
        else:
            alone = True
            instant_public_velocity = np.array([0, 0])
            sum_vel = np.array([0, 0])

        if self.method == 'no_kernel':
            agent.public_velocity = instant_public_velocity.copy() 

        # # with the memory kernel (riemann sum)
        # agent.public_velocity_observations_sum += instant_public_velocity*np.exp(time_step*self.dt/self.memory_time)
        # agent.public_velocity = self.dt/self.memory_time * np.exp(-time_step*self.dt/self.memory_time) * agent.public_velocity_observations_sum

        # with the memory kernel (incremental approximation)
        elif self.method == 'kernel':
            agent.public_velocity = self.c_exp*agent.public_velocity + self.c_exp2*instant_public_velocity

        # add noise to public velocity (random rotation)
        if self.sensing_noise != 0:
            random_angle = rng.uniform(-self.sensing_noise*np.pi, self.sensing_noise*np.pi)
            random_rot_matrix = [[np.cos(random_angle), -np.sin(random_angle)], [np.sin(random_angle), np.cos(random_angle)]]
            agent.public_velocity = np.matmul(random_rot_matrix, agent.public_velocity) 

        # set agent's alone flag
        agent.alone = alone

        return sum_vel

    def cast_and_surge(self, agent, time_step):
        # update private velocity according to the cast and surge program
        if agent.sniffed: 
            agent.surge()
        else: 
            agent.cast(time_step)

    def biased_rw(self, agent, time_step):
        pass

    # detect other agents within the visual_radius
    def detect_neighbors(self, agent):
        # reset neighbors list
        agent.neighbors = []
        for candidate in self.agents:
            coord_trasl = candidate.coordinates - agent.coordinates
            if (candidate != agent) and (norm(coord_trasl) < self.visual_radius):
                agent.neighbors.append(candidate)

    # detect odor field within the olfactory_radius
    def sniff_odor(self, agent):
        agent.sniffed = False
        # check if we are inside the window of the odor field
        if agent.coordinates[1] <= self.cloud.y_max + self.cloud.vertical_shift and agent.coordinates[1] >= self.cloud.vertical_shift:
            # find pixels that are within the olfactory circle and create a mask
            x_trasl = self.cloud.x_values + self.cloud.horizontal_shift - agent.coordinates[0] 
            y_trasl = self.cloud.y_values + self.cloud.vertical_shift - agent.coordinates[1]
            mask = norm([x_trasl, np.atleast_2d(y_trasl).T]) <= self.olfactory_radius
            if np.any(self.cloud.odor[mask]>self.threshold):
                agent.sniffed = True

    def check_reach(self, agent):
        reached = False
        # check if the odor source is within the reach radius of any of the agents
        if agent.coordinates[0] < self.source_coordinates[0] + self.reach_radius:
            coord_trasl = self.source_coordinates - agent.coordinates
            if norm(coord_trasl) < self.reach_radius:
                reached = True
        return reached

class Agent:
    def __init__(self, 
            label, 
            coordinates, 
            speed, 
            trust, 
            wind_noise, 
            decision_time, 
            rand_casting_steps,
            rand_casting_direction,
            dt,
            mu,
            sigma):

        self.label = label
        self.coordinates = np.array(coordinates)
        self.speed = speed
        self.trust = trust
        self.wind_noise = wind_noise
        self.decision_time = decision_time
        self.rand_casting_steps = rand_casting_steps
        self.rand_casting_direction = rand_casting_direction
        self.dt = dt

        self.alone = False

        # counters and flags for the surging phase
        self.t_prime: int = 0
        self.clock: int = 0
        self.flip_dir: bool = False

        # rotation matrices for 45deg and 90deg rotations
        self._rot_matrix_45 = np.array([[-2**(-0.5), 2**(-0.5)], [2**(-0.5), 2**(-0.5)]])
        self._rot_matrix_neg45 = np.array([[-2**(-0.5), 2**(-0.5)], [-2**(-0.5), -2**(-0.5)]])
        self._rot_matrix_90 = np.array([[0, -1], [1, 0]])

        # these attributes are updated by the Swarm() class:
        # estimate of the local wind velocity 
        self.wind_estimate = -np.array([1.0, 0.0])
        # list of other agents within the visual_radius
        self.neighbors = []
        # flag to determine if a particle was sniffed
        self.sniffed: bool = False

        # # initial velocity of the agent
        # self.private_velocity = self.speed*np.array([-np.sqrt(2)/2, -np.sqrt(2)/2]) 
        # self.public_velocity = self.speed*np.array([-np.sqrt(2)/2, -np.sqrt(2)/2]) 
        # self.combined_velocity = self.speed*np.array([-np.sqrt(2)/2, -np.sqrt(2)/2]) 
        # self.private_velocity = np.array([-1.0, 0.0])
        # self.public_velocity = np.array([-1.0, 0.0])
        # self.combined_velocity = np.array([-1.0, 0.0])

        # self.public_velocity = np.array([0.0, 0.0])
        self.mu = mu
        self.sigma = sigma
        random_angle = rng.gauss(mu, sigma)
        self.combined_velocity = np.array([np.cos(random_angle), np.sin(random_angle)])

        # mean wind
        self.mean_wind = -np.array([1.0,0.0])

        # calculate how many steps in une casting unit
        self.cast_steps = int(self.decision_time/self.dt)

        # initial counters and flags for casting
        self.diagonal_clock: int = 1
        self.move_diagonal: bool = True
        self.crosswind_multi: int = 0
        self.crosswind_clock: int = 1

        if self.rand_casting_direction:
            self.flip_dir = rng.choice([True, False])
        else:
            self.flip_dir = False

        for i in range(rng.randint(0, self.rand_casting_steps)):
            self.cast(i)

        # # random initial counters and flags for casting
        # self.diagonal_clock: int = 1
        # self.flip_dir = rng.choice([True, False])
        # if rng.random()<0.1:
        #     self.move_diagonal: bool = True
        #     self.crosswind_multi: int = 0
        #     self.crosswind_clock: int = 1
        # else:
        #     self.move_diagonal: bool = False
        #     self.crosswind_multi = rng.randint(1,4) * 2
        #     self.crosswind_clock = rng.randint(1, self.crosswind_multi)

    def extract_random_wind_estimate(self):
        # compute wind estimate as mean wind + noise
        self.wind_estimate[0] = self.mean_wind[0] + (2*rng.random()-1)*self.wind_noise
        self.wind_estimate[1] = self.mean_wind[1] + (2*rng.random()-1)*self.wind_noise
        # divide the wind estimate by its norm to obtain a unit vector
        self.wind_estimate = self.wind_estimate/norm(self.wind_estimate)

    # cast and surge behavior 
    # NB here and in cast() we only update the private velocity, we do NOT update the coordinates yet!
    def surge(self):
        if self.wind_noise != 0: self.extract_random_wind_estimate()

        # update value of private velocity to move upwind
        self.private_velocity = -self.wind_estimate*self.speed

        # reset counters
        self.move_diagonal: bool = True
        self.diagonal_clock: int = 1
        self.crosswind_clock: int = 1
        self.crosswind_multi: int = 0

    def cast(self, time_step):
        if self.wind_noise != 0:
            self.extract_random_wind_estimate()

        # move diagonally for casting_steps
        if self.move_diagonal:
            if self.flip_dir: direction_45 = np.matmul(self._rot_matrix_45, self.wind_estimate)
            else: direction_45 = np.matmul(self._rot_matrix_neg45, self.wind_estimate)
            # assign value to private velocity
            self.private_velocity = direction_45*self.speed
            if self.diagonal_clock == self.cast_steps:
                # reset the clock for moving diagonally
                self.diagonal_clock = 0
                # set flag to move diagonally to False (now we want to go crosswind)
                self.move_diagonal = False
                # increase the multiplier for the crosswind movement
                self.crosswind_multi += 2
                # flip the direction for the next movement
                self.flip_dir = not self.flip_dir
            # increase counter for diagonal movement
            self.diagonal_clock += 1
        # move crosswind for crosswind_multi*casting_steps
        else:
            if self.flip_dir: direction_crosswind = np.matmul(self._rot_matrix_90, self.wind_estimate)
            else: direction_crosswind = -np.matmul(self._rot_matrix_90, self.wind_estimate)
            # assign value to private velocity
            self.private_velocity = direction_crosswind*self.speed
            if self.crosswind_clock == self.crosswind_multi*self.cast_steps:
                # reset the clock for moving crosswind
                self.crosswind_clock = 0
                # set flag to move diagonally to False (now we want to go diagonal)
                self.move_diagonal = True
            # increase counter for crosswind movement
            self.crosswind_clock += 1

class Cloud_turbulent:
    def __init__(self, path, read_h5, source_coordinates, delta_x):
        self.read_h5 = read_h5
        self.path = path

        # initialise the field
        if self.read_h5:
            self.data = h5py.File(f'{self.path}')
        else:
            # build path for npy files containing odor frames
            odor_path = f'{self.path}/odor.npy'
            # load the npy file into an array
            self._odor_frames = np.load(odor_path)

        # extract number of frames
        if read_h5: self.total_frames = len(list(self.data.items())[0][1].keys()) 
        else: self.total_frames = len(self._odor_frames) 

        # initialise the first frame randomly
        self.current_frame_id = rng.randint(0, self.total_frames-1) 
        # self.current_frame_id = 0

        if read_h5: self.odor = np.array(self.data['odor'][str(self.current_frame_id)])
        else: self.odor = self._odor_frames[self.current_frame_id]

        # flippa tutto il campo rispetto all'asse verticale
        self.odor = np.flip(self.odor, axis=1)

        # extract number of points of the field
        self.npoints_y, self.npoints_x = self.odor.shape

        # scale dimensions of the box according to delta_x
        # self.delta_x = length/self.npoints_x 
        self.delta_x = delta_x
        self.delta_y = delta_x
        self.x_max = self.npoints_x*self.delta_x
        self.y_max = self.npoints_y*self.delta_y
        self.x_values = np.arange(self.npoints_x)*self.delta_x
        self.y_values = np.arange(self.npoints_y)*self.delta_y

        # calculate the shifts to match the box dimensions and source position
        original_source_coordinates = (self.x_max/7, self.y_max/2) #hardcoded

        # self.horizontal_shift = source_coordinates[0] - original_source_coordinates[0]
        self.horizontal_shift = -original_source_coordinates[0]

        self.vertical_shift = source_coordinates[1] - original_source_coordinates[1]

        # for n in range(self.total_frames):
        #     odor = np.array(self._odor_frames[n])
        #     odor[odor>0.0005] = 0
        #     if n == 0: self.avg_odor = odor.copy()
        #     else: self.avg_odor += odor
        # self.odor = self.avg_odor

    def update(self):
        # loop through the lists of frames
        if self.read_h5:
            self.odor = np.array(self.data['odor'][str(self.current_frame_id)])
        else:
            self.odor = self._odor_frames[self.current_frame_id]
            # self.odor = self.avg_odor

        # flippa tutto il campo rispetto all'asse verticale
        self.odor = np.flip(self.odor, axis=1)

        if self.current_frame_id < self.total_frames-1: self.current_frame_id += 1
        else: self.current_frame_id = 0
