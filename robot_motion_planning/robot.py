import numpy as np
import turtle
from maze import Maze

if True: np.random.seed(0)

class Robot(object):
    """
    Simulated micro mouse robot, provides interface between simulated environment and algorithms.
    
    Attributes:
        maze_dim:   known number of cells in width in the maze.
        alg_choice: algorithm to use for maze exploration. If "default" built-in random choice algorithm is used.
        goal:       array of locations considered to be success conditions. 'None' defaults to center cell(s)
        sensors:    list of 3 integers, representing the distance to the nearest wall to the left, front and right of the robot
        heading:    direction of current facing of micro mouse. 0 - 3 inclusive. 2**heading = bit value of wall at that heading.
        location:   integer x, y pair indicating the current cell location of the micro mouse
        rotation:   one of [-90, 0, 90] indicating turn or straight.
        movement:   integer from 0 - 3 inclusive, indicating the number of cells to move in the new direction.
        walls: distance to sensed walls, in cells (-1 represents blind spot)
    """
    def __init__(self, maze_dim, alg_choice="default", goal=None):
        if goal == None:
            center = maze_dim // 2
            self.goal = [(center, center), (center, center-1), (center-1, center), (center-1, center-1)]
        else:
            self.goal = [goal]

        if alg_choice == "default":
            self.algorithm = self
        else:
            self.algorithm = alg_choice
            
        self.location = (0, 0)
        self.heading = 0
        

    def next_move(self, sensors):
        """ Accept sensor data and return planned rotation and movement for the current timestep. 
            Uses the algorithm defined for this robot to determine planned steps. """
        
        walls = self.decode_sensors(sensors, self.heading) # Convert sensor data into cell representation
        rotation, movement = self.algorithm.algorithm_choice(walls, self.heading, self.location) # Request instructions from algorithm
        if rotation == 'Reset':
            self.heading = 0
            self.location = (0, 0)
            return 'Reset', 'Reset'
        self.heading = self.update_heading(rotation, heading=self.heading)
        self.location = self.update_location(movement, self.heading, self.location)
        return rotation, movement
    
    
    def decode_sensors(self, sensors, heading):
        """ Map sensor data to directional information. """
        
        walls = [-1, -1, -1, -1]
        left = (heading + 3) % 4 # Find facing of left sensor
        for w in range(3):
            walls[(left + w) % 4] = sensors[w]
        return walls
    
    
    def update_heading(self, rotation, heading):
        """ Update robot's belief of it's current heading. """

        return ((heading + (rotation // 90) + 4) % 4) # Add 4 then modulo 4 to prevent negative headings
    
    
    def update_location(self, movement, heading, location):
        """ Use movement, heading and location to identify new location. """
        
        x, y = location
        if heading == 0: y += movement # If heading is North, add movement to y
        elif heading == 1: x += movement # If heading is East, add movement to x
        elif heading == 2: y -= movement # If heading is South, subtract movement from y
        elif heading == 3: x -= movement # If heading is West, subtract movement from x
        return x, y
    
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Use movement, heading and location to identify new location. """        
        if location in self.goal:
            return 'Reset', 'Reset'
        options = list()
        for i in range(3, 6):
            direction = (heading + i) % 4 
            if walls[direction] > 0: # If direction does not point at a wall or a blind spot, add it to options
                options.append(90*(i-4)) # Convert direction to left, straight, right options: -90, 0 and 90 respectively
        if len(options) == 0: # This is a dead end, turn right.
            return 90, 0
        else:
            return np.random.choice(options), 1

    
    def unit_tests(self):
        """ Test Robot internal functions. """
                   
        # Test that decode_sensors returns correct results
        assert self.decode_sensors([0,10,0], 0) == [10, 0, -1, 0]
        assert self.decode_sensors([0,10,0], 3) == [0, -1, 0, 10]
        
        # Test that update_heading returns correct results
        assert self.update_heading(0, 0) == 0
        assert self.update_heading(90, 0) == 1
        assert self.update_heading(-90, 0) == 3
        
        # Test that update_location returns correct results
        assert self.update_location(3, 0, (0,0)) == (0, 3)
        assert self.update_location(2, 1, (1,1)) == (3, 1)
        assert self.update_location(1, 2, (2,2)) == (2, 1)
        assert self.update_location(3, 3, (3,3)) == (0, 3)

        # Test that algorithm_choice returns correct results
        assert self.algorithm_choice([0, 0, -1, 0], 0, (0,0)) == (90, 0)
        assert self.algorithm_choice([-1, 0, 1, 0], 2, (0,0)) == (0, 1)
        assert self.algorithm_choice([1, 0, 1, -1], 1, (0,0)) in [(90, 1),  (-90, 1)]
        
        return True 

if __name__ == '__main__':
    import sys
    testmaze = Maze( str(sys.argv[1]))
    bot = Robot(testmaze.get_dim())
    bot.unit_tests()

                        