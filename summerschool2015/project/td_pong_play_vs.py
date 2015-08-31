import random
import numpy
import sys
import time
import os
import json
import mpi_environment as env 

policy_filename = "pong_policy.dat"
values_filename = "pong_values.dat"

alpha = 0.1 # values / critic learning parameter
beta = 0.1  # actor learning parameter
gamma = 0.9  # error signal: future states parameter

world_dim = env.getWorldDim()
world_dim = {'y': world_dim[0], 'x': world_dim[1]}
num_possible_moves = env.getActionDim()
state = env.getState()

pol_file = None
val_file = None

if os.path.exists(policy_filename):
	pol_file = open(policy_filename, 'r+')
	policy = numpy.array(json.loads(pol_file.read()))
	pol_file.close()
else:
	#create random policy
	print num_possible_moves 
	policy = numpy.random.rand(world_dim['y'], world_dim['x'],  num_possible_moves)

#pol_file = open(policy_filename, 'w+')

if os.path.exists(values_filename):
	val_file = open(values_filename, 'r+')
	values = numpy.array(json.loads(val_file.read()))
	val_file.close()
else:
	#create empty value funcion
	values = numpy.zeros([world_dim['y'], world_dim['x']])



#val_file = open(values_filename, 'w+')

def cum_softmax_direction_prop(state):
    # calculates the cumulated softmax propability for every possible action
    current_policy = policy[state['y'], state['x'], :]  # prop in this agent_pos
    softmax_prop = numpy.exp(current_policy)
    softmax_prop = softmax_prop / numpy.sum(softmax_prop)  # softmax: (e^prop) / (sum(e^prop))
    cum_softmax_prop = numpy.cumsum(softmax_prop)  # cumulating
    return (cum_softmax_prop)


def pick_action(state):
    cum_softmax_prop = cum_softmax_direction_prop(state)
    r = numpy.random.rand()
    for i in range(len(cum_softmax_prop)):
        if cum_softmax_prop[i] > r:
            return i


while True:
    possible_actions = env.get_possible_actions()
    state = env.getState().copy()
    
    direction = pick_action(state)
    	
    last_state = state.copy()
    
    	
    outcome = 0	
    state, outcome, in_end_pos = env.move(possible_actions[direction])
    	
    time.sleep(0.1)



