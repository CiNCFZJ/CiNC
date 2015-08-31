from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE
import Queue
import threading
import numpy
import time

global state
state = {'y': 1, 'x':0}
world_dim = {'y':4, 'x': 4}

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

class StateCommunicator(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global state
        print "state commander running"
        while True:
            state = comm.recv()
            time.sleep(0.1)

state_comm = StateCommunicator()
state_comm.start()



num_possible_moves = numpy.zeros(world_dim['y'] * world_dim['x'], int)
num_possible_moves = numpy.reshape(num_possible_moves, [world_dim['y'], world_dim['x']])

num_possible_moves += 3

def getState():
    return state

def move(direction):
    outcome = 0
    comm.isend(direction())
    return [state, outcome, False]

def get_world_dimensions():
	return world_dim 

def getWorldDim():
	return [world_dim['y'], world_dim['x']] 

def getActionDim():
	return 3 

def get_num_possible_actions():
	return num_possible_moves

def move_up():
	return 1

def move_down():
	return -1

def stay():
	return 0

def get_possible_actions():
	return [move_up, stay, move_down]
