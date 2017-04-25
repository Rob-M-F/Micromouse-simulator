import numpy as np
import algorithms as alg
import turtle
from maze import Maze

class Robot(object):
    def __init__(self, maze_dim, algorithm="Dead_reckoning"):
        '''
        Initializes Robot objects.
        
        Args:
            maze: The maze object the robot will be exploring. this object provides maze dimensions and the window
            algorithm: Name of algorithm to use for maze exploration, if it is not in the internal algorithms list, it is assumed to be a 
                function name. Algorithms need to accept a robot object and output movement and rotation as integers. 
                Defaults to "Dead_reckoning"
        '''
        alg_choice = alg.Algorithms.get(algorithm)
        
        if alg_choice == None: 
            alg_choice = algorithm
            
        self.location = (0, 0)
        self.heading = 0
        
        self.maze_dim = maze_dim


    def next_move(self, sensors):
        '''
        Accept sensor data and return planned rotation and movement for the current timestep. Uses the algorithm defined for this robot to 
        determine planned steps.
        
        Args:
            sensors: list of 3 integers, representing the distance to the nearest wall to the left, front and right of the robot
            
        Returns:
            rotation: direction the robot should turn, in 90 degree increments, from -90 to +90. 'Reset' at the end of exploration phase.
            movement: number of cells the robot should move, after rotation, from 0 to 3 cells. 'Reset' at the end of exploration phase.
        '''
        walls = self.decode_sensors(sensors, self.heading) # Convert sensor data into cell representation
        rotation, movement = self.algorithm.next_move(walls, self.location, self.heading) # Request instructions from algorithm    
        self.heading = self.update_heading(rotation, heading=self.heading)
        self.location = self.update_location(self.location, self.heading)

        return rotation, movement
    
    
    def decode_sensors(self, sensors, heading):
        '''
        Map sensor data to directional information.
        
        Args:
            sensors: list of 3 integers representing left, straight and right sensor distance readings.
            
        Returns:
            walls: distance to sensed walls, in cells (-1 represents blind spot)
        '''
        
        walls = [-1, -1, -1, -1]
        left = heading - 1 # Find facing of left sensor
        for w in range(3):
            walls[(left + w) % 4] = sensors[w]
        return walls
    
    
    def update_heading(self, rotation, heading):
        '''
        Update robot's belief of it's current heading.
        
        Args:
            rotation: -1, 0 or 1, indicating direction to rotate, left, straight or right respectively
            heading: integer current heading 0 - 3 for North, East, South, West respectively
        
        Returns:
            heading: integer new heading 0 - 3 for North, East, South, West respectively
        '''
        if rotation % 90 != 0: # If rotation is not an even change in cardinal direction, get the proportional turn
            head_rotation = rotation / 90.
        else: # If rotation is an even change in cardinal direction, get the integer turn
            head_rotation = rotation // 90
        
        return ((heading + head_rotation + 4) % 4) # Add 4 then modulo 4 to prevent negative headings

      
def unit_tests():
    maze_dim = 12
    bot = Robot(12)
    assert bot.decode_sensors(0, [0,10,0]) == [10, 0, -1, 0]
    assert bot.decode_sensors(3, [0,10,0]) == [0, -1, 0, 10]
    
    assert bot.update_heading(0, 1) == 1
    assert bot.update_heading(90, 1) == 2
    assert bot.update_heading(-90, 1) == 3
    
    print "All tests passed."

if __name__ == '__main__':
    import sys
    unit_tests()
    testmaze = Maze( str(sys.argv[1]))
    bot = Robot(testmaze.get_dim())

                        