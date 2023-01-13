import matplotlib.pyplot as plt
import numpy as np

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

class Simulation:
    def __init__(self, length, time_steps, heigth, source, swarm):
        # dimensions of the simulation box
        self.length = length
        self.heigth = heigth

        # total time steps of the simulation
        self.time_steps = time_steps

        # source and swarm objects
        self.source = source
        self.swarm = swarm

    def run(self):
        for time in range(1, self.time_steps+1):
            plt.pause(0.1)

            for agent in self.swarm.agents:
                agent.cast()

            self.swarm.detect_neighbors()

            # # print neighbors info in terminal
            # print(f'\ntime = {time}')
            # for ag in range(self.swarm.n_agents):
            #     print(f'neighbors of agent {ag}:')
            #     for ne in self.swarm.neighbors[ag]:
            #         print(ne.label)

            plt.title(f'time = {time}')
            plt.draw()

class Swarm:
    def __init__(self, length, heigth, n_agents, spawn_center, spawn_radius, measure_time, decision_time, 
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

        # dimensions of the simulation box
        self.length = length
        self.heigth = heigth

    def spawn(self):
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

    def detect_neighbors(self):
        # initialize empty list for the neighbors count
        self.neighbors = []
        # count neighbors of each agent
        for agent in self.agents:
            neighbors_list = []
            for candidate in self.agents:
                if candidate != agent:
                    x_trasl = candidate.coordinates[0]-agent.coordinates[0]
                    y_trasl = candidate.coordinates[1]-agent.coordinates[1]
                    if x_trasl**2 + y_trasl**2 < agent.visual_radius**2:
                        neighbors_list.append(candidate)
            self.neighbors.append(neighbors_list)

class Moth:
    def __init__(self, label, coordinates, agent_speed, measure_time, olfactory_radius, visual_radius):
        self.label = label
        self.coordinates = coordinates
        self.agent_speed = agent_speed
        self.measure_time = measure_time
        self.olfactory_radius = olfactory_radius
        self.visual_radius = visual_radius

        # SURGE
        # 1. If the agent has detected at least one odor particle in the time interval Delta_t (measure time), it moves
        # upwind by v_0*Delta_t units, v_0 being the speed of the agent. This phase is called "surging".  The agent 
        # remains in the surging phase as long as it detects odor particles within every Delta_t time and after taking 
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
        # Steps 2-5 describe the "casting" phase, which is terminated as soon as the agent detects an odor particle. Then 
        # the agent sets t' = 0 and starts the surging phase (step 1) from the next decision time.

    def surge(self):
        pass

    def cast(self):
        self.coordinates[0] -= self.agent_speed*self.measure_time 
        self.coordinates[1] += 2*(np.random.rand()-0.5)

class Source:
    def __init__(self, coordinates):
        self.coordinates = coordinates

