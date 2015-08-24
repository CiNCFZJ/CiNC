import Queue
import threading
import time
from pong import pong
import numpy
import sys

#sys.path.append("/home/philipp/opt/mpi4py/lib/python/")
#sys.path.append("/users/weidel/opt/mpi4py/lib64/python/")

from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

class PongGame(threading.Thread):
	action_lock = None
	action_queue = None
	state_lock = None
	state_queue = None

	def __init__(self, action_lock, action_queue, state_lock, state_queue ):
		self.action_lock = action_lock
		self.action_queue = action_queue
		self.state_lock = state_lock
		self.state_queue = state_queue

		threading.Thread.__init__(self)


	def run(self):
		pong.main(self.action_lock, self.action_queue, self.state_lock, self.state_queue)

if rank == size-1:
	action_queue = Queue.Queue(1)
	action_lock = threading.Lock()
	
	state_queue = Queue.Queue(3 * 1024)
	state_lock = threading.Lock()
	
	
	pong_thread = PongGame( action_lock, action_queue, state_lock, state_queue )
	
	pong_thread.start()
	
	print "Pong started"

num_possible_moves = 5
in_end_pos = False
params = { 'screenSize':480, 'screenSizeY':640, 'plankSize':40, 'ballSize':10, 'timeStep':0.5 }
contraints = { 'xMin' : params['plankSize']/2, 'xMax' : params['screenSize'] - params['plankSize']/2, 
    'yMin' : params['ballSize']/2, 'yMax' : params['screenSize'] - params['ballSize']/2,
    'vMax' : 120, 'vMin': 80, 'angleMax': 0, 'angleMin': 0 }

state = { 'diff':0, 'xPlank': 240, 'xBall': 240, 'yBall': 0, 'v':0, 'angle':0 }
old_state = state.copy()
last_outcomes = [0]

def get_num_possible_actions():
	return num_possible_moves


def getState():
	global state
	return state

def move_up():
	return 

def move_down():
	return -1

def stay():
	return 0

def get_possible_actions():
	return [move_up, stay, move_down]
	
def move(action):
    global num_reward, num_punishment, state
    
    direction = action() 
    print state, direction
    	
    if not action_queue.empty():
    	action_lock.acquire()
    	action_queue.get()
    	action_lock.release()
    
    if action_queue.empty():
    	action_lock.acquire()
    	action_queue.put(direction)
    	action_lock.release()
    	
    outcome = 0
    state_lock.acquire()
    if not state_queue.empty():
    	ball_x = state_queue.get()
    	ball_y = min(world_dim['y']-1, int(state_queue.get()/(480 / world_dim['y'])))
    	paddle = min(world_dim['x']-1, int(state_queue.get()/(480 / world_dim['x'])))
    
    	state = {'y': ball_y, 'x': paddle}
    
    state_lock.release()
    
    
    return [state, outcome, False]

def init_new_trial():
	global num_reward, num_punishment, state
	return [state, 0, False]

def getState():
	global state
	state_lock.acquire()
	if not state_queue.empty():
		ball_x = state_queue.get()
		ball_y = min(world_dim['y']-1, int(state_queue.get()/(480 / world_dim['y'])))
		paddle = min(world_dim['x']-1, int(state_queue.get()/(480 / world_dim['x'])))

		state = {'y': ball_y, 'x': paddle}

	state_lock.release()

	return state


def print_world():
	pass
def print_states_visited():
	pass
def save_states_visited():
	pass

def print_world_file():
    pass

