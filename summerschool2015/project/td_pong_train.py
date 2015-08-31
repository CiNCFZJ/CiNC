import random
import numpy
import sys
import time
import os
import json
import pong_environment_training as env

policy_filename = "pong_policy.dat"
values_filename = "pong_values.dat"

if os.path.exists(values_filename):
    os.remove(values_filename)

if os.path.exists(policy_filename):
    os.remove(policy_filename)

alpha = 0.05 # values / critic learning parameter
beta = 0.01  # actor learning parameter
gamma = 0.5  # error signal: future states parameter

world_dim = env.getWorldDim()
num_possible_moves = env.getActionDim()

state = env.getState()

iterations = int(sys.argv[1])

pol_file = None
val_file = None

if os.path.exists(policy_filename):
	pol_file = open(policy_filename, 'r+')
	policy = numpy.array(json.loads(pol_file.read()))
	pol_file.close()
else:
	#create random policy
	policy = numpy.random.rand(world_dim[1], world_dim[0], num_possible_moves)

pol_file = open(policy_filename, 'w+')

if os.path.exists(values_filename):
	val_file = open(values_filename, 'r+')
	values = numpy.array(json.loads(val_file.read()))
	val_file.close()
else:
	#create empty value funcion
	values = numpy.zeros([world_dim[1], world_dim[0]])



val_file = open(values_filename, 'w+')

def cum_softmax_direction_prop(state):
	# calculates the cumulated softmax propability for every possible action
	current_policy = policy[state['y'], state['x'], :]  # prop in this agent_pos
	#print current_policy
	softmax_prop = numpy.exp(current_policy)
	#print numpy.sum(softmax_prop)
	softmax_prop = softmax_prop / numpy.sum(softmax_prop)  # softmax: (e^prop) / (sum(e^prop))
	cum_softmax_prop = numpy.cumsum(softmax_prop)  # cumulating
	return (cum_softmax_prop)


def pick_action(state):
    cum_softmax_prop = cum_softmax_direction_prop(state)
    r = numpy.random.rand()
    for i in range(len(cum_softmax_prop)):
        if cum_softmax_prop[i] > r:
            return i


def critic(state, last_state, reward):
    error = reward - values[last_state['y'], last_state['x']] + gamma * values[state['y'], state['x']]
    return (error)


i = 0
in_end_pos = False
while i < iterations:
    state = env.getState().copy()
    if not in_end_pos:
        possible_actions = env.get_possible_actions()
        #time.sleep(0.9)
        i += 1
        sys.stdout.write(str(float(i)/iterations) + "\r")
        direction = pick_action(state)
        	
        last_state = state.copy() 
        
        outcome = 0	
        state, outcome, in_end_pos = env.move(possible_actions[direction])
        	
        error = critic(state, last_state, outcome * 100)
        
        
        if outcome != 0 or state != last_state:
        #	print "error ", error
        	values[last_state['y'], last_state['x']] += alpha * error
        
        	policy[last_state['y'], last_state['x'], direction] += beta * error
        
   #     if outcome != 0:
   #     	for row in values:
   #     		print numpy.array(row, dtype=int) 
        
        
        
        pol_file.seek(0)
        val_file.seek(0)
        pol_file.write(json.dumps(policy.tolist()))
        val_file.write(json.dumps(values.tolist()))
        pol_file.truncate()
        val_file.truncate()
    else:
        _, in_end_pos = env.init_new_trial()



print values
pol_file.close()
val_file.close()
