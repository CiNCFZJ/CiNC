import Queue
import threading
import time
from pong import pong_continious as pong
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
state = { 'diff':0, 'xPlank': 240, 'xBall': 240 }
old_state = state.copy()
last_outcomes = [0]

def get_num_possible_actions():
	return num_possible_moves


def moveLeft():
    return -30

def moveLeftLong():
    return -50

def stay():
    return 0

def moveRight():
    return 30

def moveRightLong():
    return 50

actionsAvailable = [moveLeft, stay, moveRight]
	
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
    	ball = state_queue.get()
        paddle = state_queue.get()
    
    	state = {'xBall': ball, 'xPlank': paddle, 'diff': 0.0}
        state['diff'] = state['xBall'] - state['xPlank']
    
    state_lock.release()
    
    
    return [state, outcome, False]

def init_new_trial():
	global num_reward, num_punishment, state
	return [state, 0, False]

def getState():
	global state
	state_lock.acquire()
	if not state_queue.empty():
		ball = state_queue.get()
		paddle = state_queue.get()

		state = {'xBall': ball, 'xPlank': paddle, 'diff': 0.0}
        state['diff'] = state['xBall'] - state['xPlank']

	state_lock.release()

	return state

