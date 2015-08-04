import time
import numpy.random as rand
import sys
import numpy


from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

world_dim = {'y':4, 'x': 4}

num_possible_moves = numpy.zeros(world_dim['y'] * world_dim['x'], int)
num_possible_moves = numpy.reshape(num_possible_moves, [world_dim['y'], world_dim['x']])

in_end_pos = False

num_possible_moves += 3

def get_num_possible_actions():
	return num_possible_moves

def move_up():
	global state
	state['x'] += 1

def move_down():
	global state
	state['x'] -= 1

def stay():
	pass

global num_reward, num_punishment, state, old_state
num_reward = 1
num_punishment = 1

state = {'y': 1, 'x':0} #(1,0) 
old_state = state.copy()
last_outcomes = [0]

beam_next = False
beam_timer = 2

def getWorldDim():
	return [world_dim['y'], world_dim['x']] 

def get_world_dimensions():
	return world_dim 

def getActionDim():
	return 3

def get_agent_pos():
	global state
	return state

def get_possible_actions():
	return [move_up, stay, move_down]
	

def checkValid():
	global state
	if state['x'] < 0:
		state['x'] = 0
	if state['x'] > world_dim['x']-1:
		state['x'] = world_dim['x']-1 # -= 1

def randomBeam():
	global state
	#print "BEAM!!"

	r = rand.randint(0, world_dim['x'])
	state['y'] = r
#	state = comm.bcast(state, root=0)

global iteration
iteration = 0

def move(action):
    global num_reward, num_punishment, state, beam_next, beam_timer, iteration, old_state
    
    in_end_pos = False
    action()
    
    checkValid()	
    
    #outcome = (abs(state['y'] - old_state['x']) - abs(state['y'] - state['x'] ) - 1) * 0.5
    outcome = -.2
    
    if (state['x'] == state['y'] and old_state['x'] == state['y']):
        in_end_pos = True
    	outcome = 1
        iteration += 1

    old_state = state.copy()
    return [state, outcome, in_end_pos]


def getState():
	return state

def print_world():
	pass
def print_states_visited():
	pass
def save_states_visited():
	pass

def init_new_trial():

	randomBeam()
	outcome = 0
	in_end_pos = False
	if (state['x'] == state['y']):
		in_end_pos = True
	return [outcome, in_end_pos]

def print_world_file():
    pass
    



