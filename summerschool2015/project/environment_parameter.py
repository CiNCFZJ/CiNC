"""
In this file, several Grid Worlds are pre-defined. To choose one of them, just change the "env" variable to the number of the environment you want.

An environment consists of states in form of a two-dimensional array called 'outcomes', a start position (start_pos) and end positions (end_pos). 

The numbers in the 'outcomes' array represent the reward/punishment the agent obtains in this state.
start_pos is an dictionary with the x and y coordinate of the position where the agent starts.
end_pos is an list of dictionaries of x and y positions where the agent is re-set to the start position.

"""


global outcomes, start_pos, end_pos
 
def set_environment(env = 0):
    global outcomes, start_pos, end_pos
    if env == 0:
        outcomes = [[1.0, 0, -1.0]]
        start_pos = {'x':1, 'y':0}
        end_pos = [{'x':0, 'y':0}, {'x':2, 'y':0}]
    
    elif env == 1: 
        outcomes = [[ 1., 0, 0, 0, -1. ]]
        start_pos = {'x':2, 'y':0}
        end_pos = [{'x':0, 'y':0}, {'x':4, 'y':0}]
    
    elif env == 2: 
        outcomes = [[ 1, 0, 0, 0, 0, 0, -1 ]]
        start_pos = {'x':3, 'y':0}
        end_pos = [{'x':0, 'y':0}, {'x':6, 'y':0}]
    
    elif env == 3:
        outcomes = [[0., 0., 0.]]
        start_pos = {'x':1, 'y':0}
        end_pos = [{'x':0, 'y':0}, {'x':2, 'y':0}]
    
    elif env == 4:
        outcomes = [[.5, 0., 0., .0, 1.]]
        start_pos = {'x':2, 'y':0}
        end_pos = [{'x':0, 'y':0}, {'x':4, 'y':0}]
    
    elif env == 5: 
        outcomes = [[ -1., 0, 0, 0, -1. ]]
        start_pos = {'x':2, 'y':0}
        end_pos = [{'x':0, 'y':0}, {'x':4, 'y':0}]
    
    elif env == 6: 
        outcomes = [[  0,    0 ],
                    [  0,    1.]]
        start_pos = {'x':0, 'y':0}
        end_pos = [{'x':1, 'y':1}]
    
    elif env == 7: 
        outcomes = [[  0,  0,  0 ],
                    [  0,  0,  0 ],
                    [  0,  0,  1.]]
        start_pos = {'x':0, 'y':0}
        end_pos = [{'x':2, 'y':2}]
    
    elif env == 8: 
        outcomes = [[  0, -1,  1.],
                    [  0,  0,  0 ],
                    [  0,  0,  0 ]]
        start_pos = {'x':0, 'y':0}
        end_pos = [{'x':1, 'y':0}, {'x':2, 'y':0}]

    elif env == 9: 
        outcomes = [[  0, -1, -1,  1.],
                    [  0,  0,  0,  0 ],
                    [  0,  0,  0,  0 ],
                    [  0,  0,  0,  0 ]]
        start_pos = {'x':0, 'y':0}
        end_pos = [{'x':1, 'y':0}, {'x':2, 'y':0}, {'x':3, 'y':0}]

    elif env == 10: 
        outcomes = [[  0, -1, -1, -1,  1.],
                    [  0,  0,  0,  0,  0 ],
                    [  0,  0,  0,  0,  0 ],
                    [  0,  0,  0,  0,  0 ],
                    [  0,  0,  0,  0,  0 ]]
        start_pos = {'x':0, 'y':0}
        end_pos = [{'x':1, 'y':0}, {'x':2, 'y':0}, {'x':3, 'y':0}, {'x':4, 'y':0}]







