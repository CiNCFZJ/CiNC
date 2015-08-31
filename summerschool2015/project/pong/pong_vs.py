#!/usr/bin/env python3

# Pong
# Written in 2013 by Julian Marchant <onpon4@riseup.net>
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any
# warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

import sge
import Queue
import threading
import numpy.random as random

STATE_DIMENSIONS = 4

PADDLE_SPEED = 8
COMPUTER_PADDLE_SPEED = 480 / STATE_DIMENSIONS 
PADDLE_VERTICAL_FORCE = 1 / 12
BALL_START_SPEED = 4 
BALL_ACCELERATION = 0.2
BALL_MAX_SPEED = 15

paddle_size = COMPUTER_PADDLE_SPEED 

class glob:

    # This class is for global variables.  While not necessary, using a
    # container class like this is less potentially confusing than using
    # actual global variables.

    player1 = None
    computer_player = None
    computer_player2 = None
    ball = None
    hud_sprite = None
    bounce_sound = None
    bounce_wall_sound = None
    score_sound = None
    game_in_progress = True


class Game(sge.Game):

    def event_key_press(self, key, char):
        if key == 'f8':
            sge.Sprite.from_screenshot().save('screenshot.jpg')
        elif key == 'escape':
            self.event_close()
        elif key in ('p', 'enter'):
            self.pause()

    def event_close(self):
        m = "Are you sure you want to quit?"
        if sge.show_message(m, ("No", "Yes")):
            self.end()

    def event_paused_key_press(self, key, char):
        if key == 'escape':
            # This allows the player to still exit while the game is
            # paused, rather than having to unpause first.
            self.event_close()
        else:
            self.unpause()

    def event_paused_close(self):
        # This allows the player to still exit while the game is paused,
        # rather than having to unpause first.
        self.event_close()

class ComputerPlayer(sge.StellarClass):
    action_lock = None
    action_queue = None
    state_lock = None
    state_queue = None
    
    def __init__(self, action_lock, action_queue, state_lock, state_queue):
        x = sge.game.width - 32
        y = 0# sge.game.height / 2
        self.hit_direction = -1
        glob.computer_player = self
        self.action_lock = action_lock
        self.action_queue = action_queue
        self.state_lock = state_lock 
        self.state_queue = state_queue
        super(ComputerPlayer, self).__init__(x,y, sprite="paddle")
    
    def event_step(self, time_passed, delta_mult):
        self.state_lock.acquire()
        while not self.state_queue.empty():
             # clear queue first
             self.state_queue.get()
             
        # put new state
        self.state_queue.put(glob.ball.y)
        self.state_queue.put(glob.computer_player.y)
        self.state_queue.put(glob.computer_player2.y)
        self.state_lock.release()

        if not self.action_queue.empty():
            self.action_lock.acquire()
            move_direction = self.action_queue.get()
            self.action_lock.release()
            self.yvelocity = move_direction * COMPUTER_PADDLE_SPEED
        else:
            self.yvelocity = 0
        
        # Keep the paddle inside the window
        if self.bbox_top < 0:
            self.bbox_top = 0
        elif self.bbox_bottom > sge.game.height:
        	self.bbox_bottom = sge.game.height


class ComputerPlayer2(sge.StellarClass):
    action_lock = None
    action_queue = None
    
    def __init__(self, action_lock, action_queue):
        x = 32
        y = 0# sge.game.height / 2
        self.hit_direction = 1
        glob.computer_player2 = self
        self.action_lock = action_lock
        self.action_queue = action_queue
        super(ComputerPlayer2, self).__init__(x,y, sprite="paddle")
    
    def event_step(self, time_passed, delta_mult):
            
        if not self.action_queue.empty():
            self.action_lock.acquire()
            move_direction = self.action_queue.get()
            self.action_lock.release()
            self.yvelocity = move_direction * COMPUTER_PADDLE_SPEED
        else:
        	self.yvelocity = 0
        
        # Keep the paddle inside the window
        if self.bbox_top < 0:
            self.bbox_top = 0
        elif self.bbox_bottom > sge.game.height:
        	self.bbox_bottom = sge.game.height



class Player(sge.StellarClass):

    def __init__(self, player=1):
        self.up_key = "up"
        self.down_key = "down"
        x = 32
        glob.player1 = self
        self.hit_direction = 1
        y = sge.game.height / 2
        super(Player, self).__init__(x, y, 0, sprite="paddle")

    def event_step(self, time_passed, delta_mult):
		# Movement
		key_motion = (sge.get_key_pressed(self.down_key) -
		              sge.get_key_pressed(self.up_key))
		
		self.yvelocity = key_motion * PADDLE_SPEED
		
		# Keep the paddle inside the window
		if self.bbox_top < 0:
		    self.bbox_top = 0
		elif self.bbox_bottom > sge.game.height:
		    self.bbox_bottom = sge.game.height

		


class Ball(sge.StellarClass):
       
    
    def __init__(self):
    	x = sge.game.width / 2
    	y = sge.game.height / 2
    	super(Ball, self).__init__(x, y, 1, sprite="ball")
    
    def event_create(self):
        self.serve()
    
    def event_step(self, time_passed, delta_mult):
        # Scoring
        if self.bbox_right < 0:
            self.serve(1)
        elif self.bbox_left > sge.game.width:
            self.serve(1)
        
        # Bouncing off of the edges
        if self.bbox_bottom > sge.game.height:
        	self.bbox_bottom = sge.game.height
        	self.yvelocity = -abs(self.yvelocity)
        elif self.bbox_top < 0:
        	self.bbox_top = 0
        	self.yvelocity = abs(self.yvelocity)
        
            
    
    def event_collision(self, other):
    	if isinstance(other, ComputerPlayer2) or isinstance(other, ComputerPlayer):
    	    if other.hit_direction == 1:
    	    	self.bbox_left = other.bbox_right + 1
    	    	self.xvelocity = min(abs(self.xvelocity) + BALL_ACCELERATION, BALL_MAX_SPEED)
    	    else:
    	    	self.bbox_right = other.bbox_left - 1
    	    	self.xvelocity = max(-abs(self.xvelocity) - BALL_ACCELERATION, -BALL_MAX_SPEED)
    
    	    self.yvelocity += (self.y - other.y) * (PADDLE_VERTICAL_FORCE + 0.01)
       
    
    
    def serve(self, direction=1):
    	self.x = 50 
    	self.y = random.randint(40, 440)
    	
        # Next round
    	#self.xvelocity = BALL_START_SPEED * direction + (random.rand()-0.3) * (8.0 * random.rand())
    	#self.yvelocity = random.rand() * 2 - 1 
    	self.xvelocity = BALL_START_SPEED
    	self.yvelocity = 0



def main(  action_lock0, action_queue0, action_lock1, action_queue1, state_lock, state_queue): 
	# Create Game object
	Game(640, 480, fps=120)
	
	# Load sprites
    	paddle_sprite = sge.Sprite(ID="paddle", width=8, height=120, origin_x=4,
	                           origin_y=60)
	paddle_sprite.draw_rectangle(0, 0, paddle_sprite.width,
	                             paddle_sprite.height, fill="white")

	paddle_sprite_pc = sge.Sprite(ID="paddle_pc", width=8, height=paddle_size, origin_x=4,
								origin_y=paddle_size/2.0)
	paddle_sprite_pc.draw_rectangle(0, 0, paddle_sprite.width,
	                             paddle_sprite.height, fill="white")


	ball_sprite = sge.Sprite(ID="ball", width=24, height=24, origin_x=12,
	                         origin_y=12)
	ball_sprite.draw_rectangle(0, 0, ball_sprite.width, ball_sprite.height,
	                           fill="white")
	
	# Load backgrounds
	layers = (sge.BackgroundLayer("ball", sge.game.width / 2, 0, -10000, xrepeat=False),)
	background = sge.Background (layers, "black")
	
	# Create objects
	ComputerPlayer(action_lock0, action_queue0, state_lock, state_queue)
	ComputerPlayer2(action_lock1, action_queue1)
	glob.ball = Ball()
	
	objects = (glob.computer_player2, glob.computer_player, glob.ball)
	
	# Create rooms
	room1 = sge.Room(objects, background=background)
	
        sge.game.start()
	

if __name__ == '__main__':
    main()
