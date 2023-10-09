import matplotlib.pyplot as plt
import numpy as np
import random
import os

# hack to prevent raising KeyboardInterrupt when stopping the script with ctrl-c
# https://stackoverflow.com/questions/7073268/remove-traceback-in-python-on-ctrl-c
import signal, sys
signal.signal(signal.SIGINT, lambda x, y: sys.exit())

# extract matplotlib default colors and markers
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
markers = list(plt.Line2D.markers.keys())[2:]

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
    def __init__(self, final_time, swarm, real_time_plot, pause_time, save_frames):
        self.swarm = swarm

        # final time of the simulation
        self.final_time = final_time

        # flag to enable or disable real time plotting
        self.real_time_plot = real_time_plot
        self.save_frames = save_frames
        # pause time between frames during plotting
        self.pause_time = pause_time

        # total time steps
        self.tot_time_steps = int(self.final_time/self.swarm.dt)

        if self.real_time_plot:
            # create figure and axes for plotting
            # fig = plt.figure(figsize=(13,8))
            plt.gca().remove()
            self.axes = plt.subplot(aspect='equal', adjustable='box', xlim=(0, self.swarm.length), ylim=(0, self.swarm.height))

            # add patches for source and spawn circle 
            spawn_circle = plt.Circle(self.swarm.spawn_center, self.swarm.spawn_radius, fill=False, color='k', ls='--', alpha=0.2)

            # add agents points and visual circles
            index = 0
            for agent in self.swarm.agents:
                color_id = min([len(colors), index%len(colors)]) 
                agent_point = plt.Circle(agent.coordinates, 0.1, color=colors[color_id], label=index)
                visual_circle = plt.Circle(agent.coordinates, agent.visual_radius, fill=False, color=colors[color_id], alpha=0.1)
                self.axes.add_patch(agent_point); self.axes.add_patch(visual_circle)
                index += 1

            # cmass_point = plt.Circle(self.swarm.center_of_mass, 0.1, color='k', zorder=2)
            # self.axes.add_patch(cmass_point)

    def run(self):
        # reset flags and timers
        success, agent_removed = False, False
        time_step = 0
        count = 0

        while time_step <= self.tot_time_steps:

            # update the swarm
            agent_removed, success = self.swarm.update(time_step)

            # update global time step 
            time_step += 1

            # plot in real time
            if self.real_time_plot:
                plt.title(rf'Time = {time_step*self.swarm.dt}')
                if self.save_frames: plt.savefig(f'frames/frame{time_step}')
                plt.pause(self.pause_time)

            # if an agent successuffly reached the source, stop
            if success: 
                # count agents within a circle of size spawn_radius around the source
                for candidate in self.swarm.agents:
                    coord_trasl = candidate.coordinates - self.swarm.source_coordinates
                    if norm(coord_trasl) < self.swarm.spawn_radius:
                        count += 1
                print(f'{tc.green}Success{tc.end} at time {time_step*self.swarm.dt:.2f}, N. agents < Rb: {count}')
                break

            # # if all agents are out of the simulation box, stop
            # if not self.swarm.agents: 
            #     print(f'{tc.red}Fail{tc.end}: all agents are out of the box')
            #     break

            # PBC
            for agent in self.swarm.agents:
                if agent.coordinates[0] > self.swarm.length-1:
                    agent.coordinates[0] -= self.swarm.length
                if agent.coordinates[0] < 0:
                    agent.coordinates[0] += self.swarm.length
                if agent.coordinates[1] > self.swarm.height-1:
                    agent.coordinates[1] -= self.swarm.height
                if agent.coordinates[1] < 0:
                    agent.coordinates[1] += self.swarm.height

        return time_step*self.swarm.dt, count, success

class Swarm:
    def __init__(self, n_agents, spawn_center, spawn_radius, speed, 
            visual_radius, sensing_noise, wind_noise, trust, length, height,
            source_coordinates, reach_radius, dt):
        # parameters of the agents and initial spawn conditions
        self.n_agents = n_agents
        self.spawn_center = spawn_center
        self.spawn_radius = spawn_radius
        self.speed = speed
        self.visual_radius = visual_radius
        self.sensing_noise = sensing_noise
        self.wind_noise = wind_noise

        self.length = length
        self.height = height

        self.source_coordinates = source_coordinates
        self.reach_radius = reach_radius

        self.dt = dt

        # hack to avoid divisions by zero (could also be fixed by initialising private vel to random)
        if trust != 1.0: self.trust = trust
        else: self.trust = 0.9999999999

        self.traj = []

        # initialise empty list for the swarm of agents
        self.agents = []

        # extract uniformly random points within the initial spawn circle
        # https://stackoverflow.com/questions/5837572/generate-a-random-point-within-a-circle-uniformly
        for n_ag in range(self.n_agents):
            # spawn each agent randomly in the circle
            radius = self.spawn_radius*np.sqrt(rng.random())
            theta = rng.random()*2*np.pi
            rand_x = self.spawn_center[0]+radius*np.cos(theta)
            rand_y = self.spawn_center[1]+radius*np.sin(theta)

            new_agent = Agent(n_ag, [rand_x, rand_y], self.speed, 
                    self.visual_radius, self.trust, self.wind_noise, self.dt)
            self.agents.append(new_agent)

        # # initialise position of center of mass
        # self.center_of_mass = np.array([0.0, 0.0])
        # pos_x = [agent.coordinates[0] for agent in self.agents]
        # pos_y = [agent.coordinates[1] for agent in self.agents]
        # self.center_of_mass[0] = np.mean(pos_x)
        # self.center_of_mass[1] = np.mean(pos_y)

    def update(self, time_step):
        removed, success = False, False

        # self.traj.append(self.center_of_mass.copy())
        self.traj.append(self.agents[0].coordinates.copy())

        # print(f'--time {time}--')
        # print(f'v_priv = {self.agents[0].velocity_priv}')
        # print(f'v_pub = {self.agents[0].velocity_pub}')
        # print(f'v_comb = {self.agents[0].velocity_comb}')
        # print('----------')
        # print('')

        self.update_private_velocity(time_step)

        self.update_public_velocity()

        for agent in self.agents:
            # calculate velocity_comb (linear comb. of priv. and publ. cues)
            agent.velocity_comb = (1-agent.trust)*agent.velocity_priv + agent.trust*agent.velocity_pub

            # check if the odor source is within the reach radius of any of the agents
            if agent.coordinates[0] < self.source_coordinates[0] + self.reach_radius:
                coord_trasl = self.source_coordinates - agent.coordinates
                # if it is, the agent moves directly towards the source
                if norm(coord_trasl) < agent.visual_radius:
                    agent.velocity_comb = coord_trasl/norm(coord_trasl)
                    # check if the agent has reached the source
                    if norm(coord_trasl) <= agent.speed*agent.dt:
                        success = True

            # update agent's coordinates
            agent.coordinates += agent.speed*agent.dt*agent.velocity_comb/norm(agent.velocity_comb)

            # # if an agent is out of the simulation box, remove it
            # if (agent.coordinates[0] > self.length or agent.coordinates[0] < 0 or 
            #     agent.coordinates[1] > self.height or agent.coordinates[1] < 0):
            #     self.agents.remove(agent)
            #     removed = True

        # # update position of center of mass
        # pos_x = [agent.coordinates[0] for agent in self.agents]
        # pos_y = [agent.coordinates[1] for agent in self.agents]
        # self.center_of_mass[0] = np.mean(pos_x)
        # self.center_of_mass[1] = np.mean(pos_y)

        # return the removed and success flags
        return removed, success

    # update the agents perception of the mean velocity of neighborrs (i.e. public cues)
    def update_public_velocity(self):
        for agent in self.agents:
            # find neighbors (i.e. other agents within visual_radius) of the agent
            self.detect_neighbors(agent)
            # if there are neighbors:
            if agent.neighbors:
                # reset sum
                sum_vel = np.array([0, 0])
                for neighbor in agent.neighbors:
                    sum_vel = sum_vel + neighbor.velocity_comb
                # update public velocity
                agent.velocity_pub = agent.speed*sum_vel/norm(sum_vel)
            # otherwise, set public velocity to 0
            else:
                agent.velocity_pub = np.array([0, 0])

            # add noise to public velocity (random rotation)
            if self.sensing_noise != 0:
                random_angle = rng.uniform(-self.sensing_noise*3.141592653589793, self.sensing_noise*3.141592653589793)
                random_rot_matrix = [[np.cos(random_angle), -np.sin(random_angle)], [np.sin(random_angle), np.cos(random_angle)]]
                agent.velocity_pub = np.matmul(random_rot_matrix, agent.velocity_pub) 

    # determine private behavior of the agents
    def update_private_velocity(self, time_step):
        for agent in self.agents:
            # update private velocity according to the cast and surge program
            if agent.sniffed: agent.surge()
            else: agent.cast(time_step)

    # detect other agents within the visual_radius
    def detect_neighbors(self, agent):
        # reset neighbors list
        agent.neighbors = []
        for candidate in self.agents:
            coord_trasl = candidate.coordinates - agent.coordinates
            if (candidate != agent) and (norm(coord_trasl) < agent.visual_radius):
                agent.neighbors.append(candidate)

class Agent:
    def __init__(self,label, coordinates, speed, visual_radius, trust, wind_noise, dt):
        # parameters of the agent
        self.label = label
        self.coordinates = np.array(coordinates)
        self.speed = speed
        self.dt = dt
        self.visual_radius = visual_radius
        self.trust = trust

        # counters and flags for the surging phase
        self.t_prime: int = 0
        self.clock: int = 0
        self.flip_dir: bool = False

        # rotation matrices for 45deg and 90deg rotations
        self._rot_matrix_45 = [[-2**(-0.5), 2**(-0.5)], [2**(-0.5), 2**(-0.5)]]
        self._rot_matrix_neg45 = [[-2**(-0.5), 2**(-0.5)], [-2**(-0.5), -2**(-0.5)]]
        self._rot_matrix_90 = [[0, -1], [1, 0]]

        # these attributes are updated by the Swarm() class:
        # estimate of the local wind velocity 
        self.wind_estimate = np.array([1.0, 0.0])
        # list of other agents within the visual_radius
        self.neighbors = []
        # flag to determine if a particle was sniffed
        self.sniffed: bool = False
        # private and public velocity of the agent
        self.velocity_priv = np.array([0.0, 0.0])
        self.velocity_pub = np.array([0.0, 0.0])

        # linear combination of the two 
        random_angle = rng.uniform(-3.141592653589793/2, 3.141592653589793/2)
        random_rot_matrix = [[np.cos(random_angle), -np.sin(random_angle)], [np.sin(random_angle), np.cos(random_angle)]]
        self.velocity_comb = np.matmul(random_rot_matrix, np.array([-1.0, 0])) 

        # self.velocity_comb = np.array([0.0, 0.0]) 

        # instantaneous velocity
        self.inst_velocity = np.copy(self.velocity_comb)
        # noise on the estimate of the mean wind
        self.wind_noise = wind_noise
        self.mean_wind = [1.0,0.0]

        # calculate how many steps in une casting unit
        self.cast_steps = int(1/self.dt)

        self.move_diagonal: bool = True
        self.diagonal_clock: int = 1
        self.crosswind_clock: int = 1
        self.crosswind_multi: int = 1

    def extract_random_wind_estimate(self):
        # compute wind estimate as mean wind + noise
        self.wind_estimate[0] = self.mean_wind[0] + (2*rng.random()-1)*self.wind_noise
        self.wind_estimate[1] = self.mean_wind[1] + (2*rng.random()-1)*self.wind_noise
        # divide the wind estimate by its norm to obtain a unit vector
        self.wind_estimate = self.wind_estimate/norm(self.wind_estimate)

    # cast and surge behavior 
    # NB here and in cast() we only update the private velocity, we do NOT update the coordinates yet!
    def surge(self):
        if self.wind_noise != 0:
            self.extract_random_wind_estimate()

        # update value of private velocity to move upwind
        self.velocity_priv = -self.wind_estimate*self.speed

        # reset counters
        self.diagonal_clock = 0
        self.crosswind_clock = 0

    def cast(self, time_step):
        if self.wind_noise != 0:
            self.extract_random_wind_estimate()

        # move diagonally for casting_steps
        if self.move_diagonal:
            if self.flip_dir: direction_45 = np.matmul(self._rot_matrix_45, self.wind_estimate)
            else: direction_45 = np.matmul(self._rot_matrix_neg45, self.wind_estimate)
            # assign value to private velocity
            self.velocity_priv = direction_45*self.speed
            if self.diagonal_clock == self.cast_steps:
                # reset the clock for moving diagonally
                self.diagonal_clock = 0
                # set flag to move diagonally to False (now we want to go crosswind)
                self.move_diagonal = False
                # increase the multiplier for the crosswind movement
                self.crosswind_multi += 1
                # flip the direction for the next movement
                self.flip_dir = not self.flip_dir
            # increase counter for diagonal movement
            self.diagonal_clock += 1

        # move crosswind for crosswind_multi*casting_steps
        else:
            if self.flip_dir: direction_crosswind = np.matmul(self._rot_matrix_90, self.wind_estimate)
            else: direction_crosswind = -np.matmul(self._rot_matrix_90, self.wind_estimate)
            # assign value to private velocity
            self.velocity_priv = direction_crosswind*self.speed
            if self.crosswind_clock == self.crosswind_multi*self.cast_steps:
                # reset the clock for moving crosswind
                self.crosswind_clock = 0
                # set flag to move diagonally to False (now we want to go diagonal)
                self.move_diagonal = True
            # increase counter for crosswind movement
            self.crosswind_clock += 1

