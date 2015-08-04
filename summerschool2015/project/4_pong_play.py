import nest
import nest.raster_plot as rplt
import numpy as np
import matplotlib.pyplot as plt
import pong_environment_play as env
from mpl_toolkits.mplot3d import Axes3D
import os
import json
import time

def SaveNetworkToFile(filename, source, target):
	if os.path.exists(filename):
		os.remove(filename)
	status = nest.GetStatus(nest.GetConnections(source, target))
	status = [{'source': i['source'], 'target': i['target'], 'weight': i['weight'], 'delay': i['delay'], 'synapse_model': "static_synapse"} for i in status] 
	f = open(filename, 'w+')
	f.write(json.dumps(status))
	f.close()

def RestoreNetworkFromFile(filename):
	if os.path.exists(filename):
		f = open(filename, 'r+')
		status = json.loads(f.read())
		f.close()
		nest.DataConnect(status)

#env.set_environment(9)

NUM_ITERATIONS = 5000
LEARNING_RATE = 0.5
NUM_STATE_NEURONS = 20
NUM_WTA_NEURONS = 50
WEIGHT_SCALING = 100 / NUM_STATE_NEURONS

nest.ResetKernel()
nest.set_verbosity("M_FATAL")

rank = nest.Rank()
size = nest.NumProcesses() 
seed = np.random.randint(0, 1000000)
num_threads = 4
nest.SetKernelStatus({"local_num_threads": num_threads})
nest.SetKernelStatus({"rng_seeds": range(seed+num_threads * size + 1, seed + 2 * (num_threads * size) + 1),
        		      "grng_seed": seed+size+num_threads,
                      "resolution": 0.1})

# Create states
world_dim = env.get_world_dimensions()
states = []
for i in range(world_dim['x']):
    states.append([])
    for j in range(world_dim['y']):
        states[i].append(nest.Create('iaf_psc_alpha', NUM_STATE_NEURONS))
all_states = np.ravel(states).tolist()

# Create actions
num_actions = env.get_num_possible_actions()[0][1]
actions = []
for i in range(num_actions):
    actions.append(nest.Create('iaf_psc_alpha', NUM_WTA_NEURONS))
all_actions = np.ravel(actions).tolist()

# Create WTA circuit
wta_ex_weights = 10.5
wta_inh_weights = -2.6
wta_ex_inh_weights = 2.8
wta_noise_weights = 2.1

wta_inh_neurons = nest.Create('iaf_psc_alpha', NUM_WTA_NEURONS)

for i in range(len(actions)):
    nest.Connect(actions[i], actions[i], 'all_to_all', {'weight': wta_ex_weights})
    nest.Connect(actions[i], wta_inh_neurons, 'all_to_all', {'weight': wta_ex_inh_weights}) 

nest.Connect(wta_inh_neurons, all_actions, 'all_to_all', {'weight': wta_inh_weights})

wta_noise = nest.Create('poisson_generator', 10, {'rate': 3000.})
nest.Connect(wta_noise, all_actions, 'all_to_all', {'weight': wta_noise_weights})
nest.Connect(wta_noise, wta_inh_neurons, 'all_to_all', {'weight': wta_noise_weights * 0.9})

# Create noise
noise = nest.Create('poisson_generator', 1, {'rate': 65000.})
nest.Connect(noise, all_states, 'all_to_all', {'weight': 1.})

# Create stimulus
stimulus = nest.Create('poisson_generator', 1, {'rate': 5000.})
nest.Connect(stimulus, all_states, 'all_to_all', {'weight': 0.})

# Create spike detector
sd_wta = nest.Create('spike_detector')
nest.Connect(all_actions, sd_wta)
nest.Connect(wta_inh_neurons, sd_wta)
sd_actions = nest.Create('spike_detector', num_actions)
for i in range(len(actions)):
    nest.Connect(actions[i], [sd_actions[i]])
sd_states = nest.Create('spike_detector')
nest.Connect(all_states, sd_states)



values = []
# Value expectations for Q(s,a)
for i in range(world_dim['x']):
    values.append([])
    for j in range(world_dim['y']):
        values[i].append(np.zeros(num_actions))
        
# Connect states to actions with initial weight 0.0
RestoreNetworkFromFile("connections.dat")


gamma = 0.8

def update_values(position, chosen_action, new_position, outcome):
    # prediction error
    best_new_action = values[new_position['x']][new_position['y']].argmax()
    prediction_error = outcome + gamma * values[new_position['x']][new_position['y']][best_new_action] - values[position['x']][position['y']][chosen_action]
    
    # update values
    values[position['x']][position['y']][chosen_action] += prediction_error * LEARNING_RATE 

    return prediction_error



# Main loop
#values_hist = [np.ravel(values.copy())]
actions_executed = 0
last_action_time = 0
position = env.getState().copy()
in_end_position = False

while actions_executed < NUM_ITERATIONS:
    if not in_end_position:
        # stimulate new state
        nest.SetStatus(nest.GetConnections(stimulus, states[position['x']][position['y']]), {'weight': 0.})
        position = env.getState().copy()
        nest.SetStatus(nest.GetConnections(stimulus, states[position['x']][position['y']]), {'weight': 1.})
        
        nest.SetStatus(wta_noise, {'rate': 3000.})
        for t in range(8):
            nest.Simulate(5)
            time.sleep(0.01)

        max_rate = -1
        chosen_action = -1
        for i in range(len(sd_actions)):
            rate = len([e for e in nest.GetStatus([sd_actions[i]], keys='events')[0]['times'] if e > last_action_time]) # calc the "firerate" of each actor population
            if rate > max_rate:
                max_rate = rate # the population with the hightes rate wins
                chosen_action = i

        nest.SetStatus(stimulus, {'rate': 5000.})

        possible_actions = env.get_possible_actions() 

        new_position, outcome, in_end_position = env.move(possible_actions[chosen_action])

        nest.SetStatus(wta_noise, {'rate': 0.})
        for t in range(4):
            nest.Simulate(5)
            time.sleep(0.01)
        
              
        last_action_time += 60
        actions_executed += 1
    else:
        position = env.get_agent_pos().copy()        
        _, in_end_position = env.init_new_trial()
        nest.SetStatus(nest.GetConnections(stimulus, states[position['x']][position['y']]), {'weight': 0.})

rplt.from_device(sd_wta, title="WTA circuit")
rplt.from_device(sd_states, title="states")
rplt.show()
       
#fig = plt.figure()

#plt.xlabel("# action")
#plt.ylabel("valence")
#plt.title("valence of each action")
#ax = fig.add_subplot(111, projection='3d')

#x, y = np.meshgrid(range(world_dim['x'] * num_actions), range(NUM_ITERATIONS))
#x = x.flatten()
#y = y.flatten()

#ax.bar3d(x, y, np.zeros(len(x)), np.ones(len(x)) * 0.5, np.ones(len(x)) * 0.5, np.ravel(values_hist))

#plt.show()



