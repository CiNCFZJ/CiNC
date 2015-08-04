import random
import environment_parameter as params
#import tools
#import static_parameter as sparams
import numpy
import json
import sys


def check_valid_pos(agent_pos, outcomes):
    if agent_pos['x'] > len(outcomes[0]) - 1 or agent_pos['x'] < 0:
        return False
    if agent_pos['y'] > len(outcomes) - 1 or agent_pos['y'] < 0:
        return False
    return True


def move_north():
    agent_pos['y'] -= 1


def move_east():
    agent_pos['x'] += 1


def move_south():
    agent_pos['y'] += 1


def move_west():
    agent_pos['x'] -= 1

# python switch case to move in a direction defined in the "directions" list
actions = {0: move_north,
           1: move_east,
           2: move_south,
           3: move_west}

def set_environment(env):
    global agent_pos, outcomes, reward_collected, punishment_collected, is_end_pos, num_actions, num_possible_moves, possible_moves, states_visited, end_pos, start_pos
    params.set_environment(env)

    outcomes = params.outcomes
    start_pos = params.start_pos
    end_pos = params.end_pos
    agent_pos = start_pos.copy()
    
    states_visited = numpy.zeros(len(params.outcomes) * len(params.outcomes[0]))
    states_visited = numpy.reshape(states_visited, [len(params.outcomes), len(params.outcomes[0])])
    
    states_visited[agent_pos['y']][agent_pos['x']] += 1
    
    num_possible_moves = numpy.zeros(len(params.outcomes) * len(params.outcomes[0]), int)
    num_possible_moves = numpy.reshape(num_possible_moves, [len(params.outcomes), len(params.outcomes[0])])
    
    possible_moves = []
    if len(outcomes) == 1:
        num_possible_moves += 2
        possible_moves.append(actions[3])
        possible_moves.append(actions[1])
    else:
        num_possible_moves += 4
        possible_moves.append(actions[0])
        possible_moves.append(actions[1])
        possible_moves.append(actions[2])
        possible_moves.append(actions[3])
    
    
    is_end_pos = False
    reward_collected = 0
    punishment_collected = 0
    num_actions = 0

def agent_is_in_end_pos(agent_pos):
    for i in range(len(end_pos)):
        if agent_pos == end_pos[i]:
            return True
    return False

def move(action):
    global agent_pos, outcomes, reward_collected, punishment_collected, is_end_pos, num_actions
    agent_last_pos = agent_pos.copy()
    num_actions += 1
#    if num_actions > 20:
#        print outcomes
#        for i in range(len(outcomes)):
#            for j in range(len(outcomes[i])):
#                outcomes[i][j] *= -1
#        print outcomes
#        num_actions = -10000
    

    action()
    
    if not check_valid_pos(agent_pos, outcomes):
       	agent_pos = agent_last_pos
        return ([agent_pos, -1, is_end_pos])
    
    
    outcome = outcomes[agent_pos['y']][agent_pos['x']]
    states_visited[agent_pos['y']][agent_pos['x']] += 1
    
    if outcome > 0:
        reward_collected = reward_collected + outcome
    elif outcome < 0:
        punishment_collected = punishment_collected - outcome
    
    if agent_is_in_end_pos(agent_pos):
    	is_end_pos = True

    return ([agent_pos, outcome, is_end_pos])

def init_new_trial():
	global is_end_pos, agent_pos, outcomes, reward_collected, punishment_collected
	is_end_pos = False
	agent_pos = start_pos.copy()

	return ([agent_pos, is_end_pos])

def get_world_dimensions():
    global outcomes
    dimensions = {'x': len(outcomes[0]), 'y': len(outcomes)}
    return dimensions


def get_agent_pos():
    global agent_pos
    return (agent_pos)


def get_num_possible_actions():
	return num_possible_moves[0][1]

def print_world():
    print "\nWORLD\n"
    for i in range(len(outcomes)):
        o = ""
        for j in range(len(outcomes[0])):
            o = o + " " + str(int(outcomes[i][j]))
        print o


def print_states_visited():
    print "\nSTATES VISITED\n"
    for i in range(len(states_visited)):
        o = ""
        for j in range(len(states_visited[0])):
            o = o + " " + str(int(states_visited[i][j]))
        print o

#def save_states_visited():
#    tools.log(json.dumps(states_visited.tolist()), sparams.states_visited_filename)

def print_result():
    print "\nREWARD COLLECTED\n" + str(reward_collected)
    print "\nPUNISHMENT COLLECTED\n" + str(punishment_collected)


#def print_result_to_log():
#    tools.log("\nREWARD COLLECTED\n" + str(reward_collected), sparams.log_filename)
#    tools.log("\nPUNISHMENT COLLECTED\n" + str(punishment_collected), sparams.log_filename)
#
#
#def print_world_file():
#    # print world to file
#    tools.reset_log(sparams.world_filename)
#    tools.log(json.dumps(outcomes), sparams.world_filename)

def get_possible_actions():
    return possible_moves


