#!/usr/bin/python
from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE

print "2 running"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


if rank == 1:
    import controller0 
    #import td_pong_play_vs as controller0
    controller0.run()
if rank == 2:
    #import controller0 as controller1 
    import td_pong_play_vs as controller1
    controller1.run()

if rank == 0:
    import Queue
    import threading
    import time
    from pong import pong_vs as pong
    import numpy
    import sys

    world_dim = {'y':4, 'x': 4}
    global state
    state = [{'y': 0, 'x':0}, {'y': 0, 'x':0}]

    class PongGame(threading.Thread):
        state_lock = None
        state_queue = None
        action_lock0 = None
        action_queue0 = None
        action_lock1 = None
        action_queue1 = None
        
        def __init__(self, action_lock0, action_queue0, action_lock1, action_queue1, state_lock, state_queue ):
        	self.action_lock0 = action_lock0
        	self.action_queue0 = action_queue0
        	self.action_lock1 = action_lock1
        	self.action_queue1 = action_queue1
        	self.state_lock = state_lock
        	self.state_queue = state_queue
        
        	threading.Thread.__init__(self)
        
        def run(self):
        	pong.main(self.action_lock0, self.action_queue0, self.action_lock1, self.action_queue1, self.state_lock, self.state_queue)

    class StateCommunicator(threading.Thread):
        mpi_dest = None

        def __init__(self, mpi_dest):
            self.mpi_dest = mpi_dest
            
            threading.Thread.__init__(self)

        def run(self):
            global state
            old_state = state[self.mpi_dest-1]
            print "state commander running"
            while True:
                if not old_state['x'] == state[self.mpi_dest-1]['x'] or not old_state['y'] == state[self.mpi_dest-1]['y']:
                    comm.ssend(state[self.mpi_dest-1], dest = self.mpi_dest)
                    old_state = state[self.mpi_dest-1]
                    time.sleep(0.01)

    class ActionCommunicator(threading.Thread):
        mpi_source = None
        action_queue = None
        action_lock = None

        def __init__(self, mpi_source, action_queue, action_lock):
            self.mpi_source = mpi_source
            self.action_queue = action_queue
            self.action_lock = action_lock
            threading.Thread.__init__(self)

        def run(self):
            print "action commander running"
            while True:
                action = comm.recv(source = self.mpi_source)
                if not self.action_queue.empty():
                	self.action_lock.acquire()
                	self.action_queue.get()
                	self.action_lock.release()
                
                if self.action_queue.empty():
                	self.action_lock.acquire()
                	self.action_queue.put(action)
                	self.action_lock.release()
                time.sleep(0.01)

    
    action_queue0 = Queue.Queue(1)
    action_lock0 = threading.Lock()
    action_queue1 = Queue.Queue(1)
    action_lock1 = threading.Lock()
    
    state_queue = Queue.Queue(3 * 1024)
    state_lock = threading.Lock()
    
    pong_thread = PongGame(  action_lock0, action_queue0, action_lock1, action_queue1, state_lock, state_queue )
    pong_thread.start()
    
    print "Pong started"

    controller0_action_comm = ActionCommunicator(1, action_queue0, action_lock0)
    controller0_action_comm.start()

    controller1_action_comm = ActionCommunicator(2, action_queue1, action_lock1)
    controller1_action_comm.start()


    controller0_state_comm = StateCommunicator(1)
    controller0_state_comm.start()

    controller1_state_comm = StateCommunicator(2)
    controller1_state_comm.start()

    # poll state from pong
    while True:
        pass
        if not state_queue.empty():
            state_lock.acquire()
            ball_y = min(world_dim['y']-1, int(state_queue.get()/(480 / world_dim['y'])))
            paddle0 = min(world_dim['x']-1, int(state_queue.get()/(480 / world_dim['x'])))
            paddle1 = min(world_dim['x']-1, int(state_queue.get()/(480 / world_dim['x'])))
            state_lock.release()
            state = [{'y': ball_y, 'x': paddle0}, {'y': ball_y, 'x': paddle1}]
            time.sleep(0.01)
        



