import nest
import nest.raster_plot as rplt
import numpy as np
import matplotlib.pyplot as plt
import pong_environment_play_continious as env
from mpl_toolkits.mplot3d import Axes3D
import os
import json
import time
import math

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

# Create left right sensors
diff_K = 100. # specify K between diff and generator rate
diff_K2 = 10000.
sensors = {'left':nest.Create('poisson_generator')[0], 'right':nest.Create('poisson_generator')[0], 'middle':nest.Create('poisson_generator')[0] }

# Create diff neurons
density = 0.3 # neurons for one pixel
diffNeuronsPositions = []
diffNeurons = []
for i in range(env.params['screenSize']):
    if(np.random.rand() < density):
        neuron = nest.Create('iaf_psc_alpha')[0]
        diffNeurons.append(neuron)
        diffNeuronsPositions.append({'position':i, 'neuron':neuron})

# connect left-right 
m = 20.
length = env.params['screenSize']
p1 = length / 2
k1 = m/p1
s = 500
for i in range(len(diffNeuronsPositions)):
    neuronPosition = diffNeuronsPositions[i]
    x = neuronPosition['position']
    #connect neuron to the difference sensor depends on it position
    if(x >= 0 and x <= p1):
        nest.Connect(sensors['left'], neuronPosition['neuron'], {"weight":x*k1})
    if(x >= p1 and x <= length):
        nest.Connect(sensors['right'], neuronPosition['neuron'], {"weight":-(x * k1) + m*2})
    nest.Connect(sensors['middle'], neuronPosition['neuron'], {"weight":4000*m*(1/math.sqrt(2*math.pi*s))*math.exp(-(x-p1)**2/(2*s))})

#create actions
wta_ex_weights = 10.5
wta_inh_weights = -2.6
wta_ex_inh_weights = 2.8
noise_weights = 2.1
numActions = len(env.actionsAvailable)
actions = []
for i in range(numActions):
    actions.append(nest.Create('iaf_psc_alpha', 20))
    nest.Connect(actions[i], actions[i], 'all_to_all', {'weight': wta_ex_weights})
    nest.Connect(diffNeurons, actions[i], 'all_to_all', {'weight': 0.1})
all_actions = np.ravel(actions).tolist()

# create inhibitory pool
wta_inh_neurons = nest.Create('iaf_psc_alpha', 60)
nest.Connect(all_actions, wta_inh_neurons, 'all_to_all', {'weight': wta_ex_inh_weights})
nest.Connect(wta_inh_neurons, all_actions, 'all_to_all', {'weight': wta_inh_weights})
 
# create noise
noise = nest.Create('poisson_generator', 10, {'rate': 3000.})
nest.Connect(noise, all_actions, 'all_to_all', {'weight': noise_weights})
#nest.Connect(noise, diffNeurons, 'all_to_all', {'weight': noise_weights* 0.2})
nest.Connect(noise, wta_inh_neurons, 'all_to_all', {'weight': noise_weights * 0.9})

sd_actions = nest.Create('spike_detector', numActions)
for i in range(numActions):
    nest.Connect(actions[i], [sd_actions[i]], 'all_to_all')
sd_all_actions = nest.Create('spike_detector')
nest.Connect(all_actions, sd_all_actions, 'all_to_all')
sd_all = nest.Create('spike_detector')
nest.Connect(diffNeurons, sd_all)
       
# Connect states to actions with initial weight 0.0
RestoreNetworkFromFile("connections.dat")

actions_executed = 0
last_action_time = 0
position = env.getState().copy()
in_end_position = False
NUM_ITERATIONS = 10000
while actions_executed < NUM_ITERATIONS:
    if not in_end_position:
        state = env.getState().copy()
        state['diff'] = -state['diff']
        print 'difference: ', state['diff']
        input
        if(state['diff'] >= 0):
            nest.SetStatus([sensors['right']], {'rate':diff_K*state['diff']})
        else:
            nest.SetStatus([sensors['left']], {'rate':-diff_K*state['diff']})
        nest.SetStatus([sensors['middle']], {'rate':abs(diff_K2*1/(0.01 + state['diff']))})
        
        for t in range(10):
            nest.Simulate(10)
            time.sleep(0.01)

        max_rate = -1
        chosen_action = -1
        for i in range(len(sd_actions)):
            rate = len([e for e in nest.GetStatus([sd_actions[i]], keys='events')[0]['times'] if e > last_action_time]) # calc the "firerate" of each actor population
            if rate > max_rate:
                max_rate = rate # the population with the hightes rate wins
                chosen_action = i
        possible_actions = env.actionsAvailable
        new_position, outcome, in_end_position = env.move(possible_actions[chosen_action])

        nest.SetStatus([sensors['right']], {'rate':0.})
        nest.SetStatus([sensors['left']], {'rate':0.})
        nest.SetStatus([sensors['middle']], {'rate':0.})

        for t in range(5):
            nest.Simulate(10)
            time.sleep(0.01)
        
        last_action_time += 150
        actions_executed += 1
    else:
        state = env.getState().copy()        
        _, in_end_position = env.init_new_trial()


rplt.from_device(sd_all_actions, title="Actions")
rplt.from_device(sd_all, title="Difference neurons")
rplt.show()

