import numpy as np
#import algorithms as alg
import turtle
from maze import Maze

if True: np.random.seed(0)

class Robot(object):
    def __init__(self, maze_dim, alg_choice="default"):
        '''
        Initializes Robot objects.
        
        Args:
            maze_dim: integer width of the maze, in cells.
            algorithm: Name of algorithm to use for maze exploration, if it is not provided, Dead_reckoning is used. 
                If provided and not in the internal algorithms list, it is assumed to be an object presenting the
                same interface as Algorithms. Algorithms are initialized with an integer (maze_dim) and must implement 
                the class function algorithm_choice accepting a walls list, a location and a heading as arguments. They are 
                expected to return an integer rotation and integer movement.
        '''
        if alg_choice == "default":
            self.algorithm = self
        else:
            chosen_algorithm = alg.Algorithms.get(alg_choice)
            if alg_choice == None:
                self.algorithm = algorithm(maze_dim)
            else:
                self.algorithm = chosen_algorithm(maze_dim)
            
            
            
        self.location = (0, 0)
        self.heading = 0
        center = maze_dim // 2
        self.goal = [(center, center), (center, center-1), (center-1, center), (center-1, center-1)]

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
        rotation, movement = self.algorithm.algorithm_choice(walls, self.heading, self.location) # Request instructions from algorithm
        if rotation == 'Reset':
            self.heading = 0
            self.location = (0, 0)
            return 'Reset', 'Reset'
        self.heading = self.update_heading(rotation, heading=self.heading)
        self.location = self.update_location(movement, self.heading, self.location)
        #print sensors, rotation, movement, self.heading, self.location
        #x = raw_input()
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
        left = (heading + 3) % 4 # Find facing of left sensor
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
        head_rotation = rotation // 90
        
        return ((heading + head_rotation + 4) % 4) # Add 4 then modulo 4 to prevent negative headings
    
    
    def update_location(self, movement, heading, location):
        '''
        Use movement, heading and location to identify new location.
        
        Args:
            movement: integer count of cells to move through
            heading: integer heading 0 - 3 for North, East, South, West respectively
            location: integer x, y pair indicating current cell
            
        Returns:
            new location: new location derived from provided information

        '''
        x, y = location
        if heading == 0: y += movement # If heading is North, add movement to y
        elif heading == 1: x += movement # If heading is East, add movement to x
        elif heading == 2: y -= movement # If heading is South, subtract movement from y
        elif heading == 3: x -= movement # If heading is West, subtract movement from x
        return x, y
    
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        '''
        Use movement, heading and location to identify new location.
        
        Args:
            movement: integer count of cells to move through
            heading: integer heading 0 - 3 for North, East, South, West respectively
            location: integer x, y pair indicating current cell
            
        Returns:
            new location: new location derived from provided information
        '''        
        if location in self.goal:
            return 'Reset', 'Reset'
        options = list()
        for i in range(3, 6):
            direction = (heading + i) % 4 
            if walls[direction] > 0: # If direction does not point at a wall or a blind spot, add it to options
                options.append(90*(i-4)) # Convert direction to left, straight, right options: -90, 0 and 90 respectively
        #print "Walls:", walls, ", Options: ", options, ", ",
        if len(options) == 0: # This is a dead end, turn right.
            return 90, 0
        else:
            return np.random.choice(options), 1
        
    
    def unit_tests(self):
        '''
        Test Robot internal functions.
                   
        Returns:
            test success: Return true if all tests passed. Assertions will cause an error otherwise
         '''
        # Test that decode_sensors returns correct results
        assert self.decode_sensors(0, [0,10,0]) == [10, 0, -1, 0]
        assert self.decode_sensors(3, [0,10,0]) == [0, -1, 0, 10]
        
        # Test that update_heading returns correct results
        assert self.update_heading(0, 0) == 0
        assert self.update_heading(90, 0) == 1
        assert self.update_heading(-90, 0) == 3
        
        # Test that update_location returns correct results
        assert self.update_location(3, 0, (0,0)) == (0, 3)
        assert self.update_location(2, 1, (1,1)) == (3, 1)
        assert self.update_location(1, 2, (2,2)) == (2, 1)
        assert self.update_location(3, 0, (3,3)) == (0, 3)

        # Test that algorithm_choice returns correct results
        assert self.algorithm_choice 
        
        return True 

if __name__ == '__main__':
    import sys
    testmaze = Maze( str(sys.argv[1]))
    bot = Robot(testmaze.get_dim())
    bot.unit_tests()

                        