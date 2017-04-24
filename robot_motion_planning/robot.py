import numpy as np
import turtle
from maze import Maze

class Robot(object):
    def __init__(self, maze_dim, algorithm="waterfall"):
        '''
        Initializes Robot objects.
        
        Args:
            maze: The maze object the robot will be exploring. this object provides maze dimensions and the window
            algorithm: Name of algorithm to use for maze exploration, if it is not in the internal algorithms list, it is assumed to be a 
                function name. Algorithms need to accept a robot object and output movement and rotation as integers. 
                Defaults to "wall_follower"
        '''
        # Set chosen algorithm, if it is not on the algorithms list below, assume the passed value is a function name
        algorithms = {"wall_follower":self.wall_follower, "dead_recon":self.dead_reckoning, "waterfall":self.waterfall}

        if algorithm in algorithms.keys(): 
            self.algorithm = algorithms[algorithm]
        else: 
            self.algorithm = algorithm

        # Set state (Exploration / Speed)
        self.exploring = True
        
        # Set maze wall values [North, East, South, West]
        self.walls = [1, 2, 4, 8]

        # Set initial location and define heading
        self.location = (0, 0)
        self.heading = 0
        
        # Create internal map of the maze
        self.maze_dim = maze_dim
        self.maze = self.blank_map(self.maze_dim)
    
    
    def blank_map(self, maze_dim):
        '''
        Generate internal representation of maze environment.
        
        Args:
            maze_dim: Integer length of one side of the square maze, in cells.
        
        Returns:
            maze: Unsigned integer numpy array of shape (maze_dim, maze_dim, 3).
                Layers of the array represent 0: Discovered cell configurations
                                              1: Algorithm's score for the cell
                                              2: Number of times cell was visited
        '''
        maze = np.zeros((maze_dim,maze_dim,3), dtype=np.uint8)
        center = maze_dim // 2

        # Prepare wall layer
        maze[:, -1, 0] += 1 # North
        maze[:, 0, 0] += 4 # South
        maze[-1, :, 0] += 2 # East
        maze[0, :, 0] += 8  # West

        # Prepare distance to goal layer
        maze[:,:,1] = 250 # Assume all spaces are 250 from goal until otherwise defined
        maze[0,0,1] = 255 # Mark starting square as worst possible location
        maze[center, center, 1] = 0 # Mark center cell with distance = 0
        if maze_dim % 2 == 0: # If maze has even dimensions, set all 4 center cells with distance = 0
            maze[center-1, center-1, 1] = 0
            maze[center, center-1, 1] = 0
            maze[center-1, center, 1] = 0
        
        # Prepare visit count layer
        maze[:,:,2] = 0 # Mark all cells as having received 0 visits
        maze[0,0,2] = 1 # Mark started cell as having been visited

        return maze
    
        
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
        if (self.maze[self.location[0], self.location[1], 1] == 0):
            self.exporing = False
            self.location = (0,0)
            self.heading = 0
            return 'Reset', 'Reset'

        if self.exploring:
            walls = self.decode_sensors(self.heading, sensors) # Update maze representation to match new sensor data.
            self.maze[:,:,0] = self.update_maze(self.maze[:,:,0], self.heading, self.location, sensors)

        rotation, movement = self.algorithm(self.maze, self.location, self.heading) # Request instructions from algorithm    
        self.heading = self.update_heading(rotation, heading=self.heading)
        
        for i in range(movement):
            if self.check_movement(self.heading, self.maze[self.location[0], self.location[1], 0]):
                if movement < 0:
                    self.location = self.decode_heading((self.heading+2)%4, self.location)
                else:
                    self.location = self.decode_heading(self.heading, self.location)
                self.maze[self.location[0], self.location[1], 2] += 1
#        _ = raw_input(self.maze[:,:,0])
        return rotation * 90, movement
    
    
    def decode_sensors(self, heading, sensors):
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

    
    def decode_cell(self, cell):
        '''
        Decode cell wall value and add flag value if not already present.
        Args:
            cell: integer from 0 to 15 inclusive.
            
        Returns:
            walls: list of integers representing walls, [1 (North, 2(East), 4(South), 8(West)]
        '''
        wall_values = list(self.walls)
        wall_values.reverse()
        
        walls = []
        for heading in wall_values:
            if cell >= heading:
                cell -= heading
                walls.append(heading)
        walls.reverse()
        return walls
    
    
    def decode_heading(self, heading, location):
        '''
        
        '''
        if heading == 0:
            return location[0], location[1]+1
        if heading == 1:
            return location[0]+1, location[1]
        if heading == 2:
            return location[0], location[1]-1
        if heading == 3:
            return location[0]-1, location[1]
    
    
    def update_heading(self, rotation, heading):
        '''
        Update robot's belief of it's current heading.
        
        Args:
            rotation: -1, 0 or 1, indicating direction to rotate, left, straight or right respectively
            heading: integer current heading 0 - 3 for North, East, South, West respectively
        
        Returns:
            heading: integer new heading 0 - 3 for North, East, South, West respectively
        '''
        return ((heading + rotation + 4) % 4)

    
    def update_maze(self, maze, heading, location, sensors):
        '''
        Update maze representation to reflect current sensor data.
        
        Args:
            maze: uint8 representation of the wall layout of the maze
            walls: list of 4 integers indicating the distance to the nearest visible wall, -1 represents a blind spot
            location: tuple of integers indication current position in the maze
        
        Returns:
            maze: uint8 representation of the wall layout of the maze, updated to reflect new data
        '''
        dead_ends = [7, 11, 13, 14]
        max_dim = maze.shape[0] - 1
        walls = self.decode_sensors(heading, sensors)
        
        for w, wall in enumerate(walls):
            if wall != -1: # If this heading is not a blind spot
                loc = location
                for i in range(wall):
                    loc = self.decode_heading(w, loc) # Step through the maze to the cell with visible wall
                maze[loc[0], loc[1]] = self.mark_wall(maze[loc[0], loc[1]], self.walls[w]) # Mark visible wall
                try:
                    loc1 = self.decode_heading(w, loc)
                    maze[loc1[0], loc1[1]] = self.mark_wall(maze[loc1[0], loc1[1]], self.walls[(w+2)%4]) # Mark other side of visible wall
                except IndexError:
                    pass
        try:
            loc = self.decode_heading((heading+2)%4, location)
            if (sum(self.decode_cell(maze[loc[0], loc[1]])) in dead_ends) and loc != (0,0):
                maze[loc[0], loc[1]] = 15
                maze[location[0], location[1]] = self.mark_wall(maze[location[0], location[1]], self.walls[(heading+2)%4])
        except IndexError:
            pass
        return maze

    
    def mark_wall(self, cell, flag):
        '''
        Decode cell wall value and add flag value if not already present.
        Args:
            cell: list of integers representing walls [1, 2, 4, 8]
            flag: integer in [1, 2, 4, 8] representing which wall to add.
            
        Returns:
            cell: integer from 0 to 15 inclusive representing walls present
                    1: North, 2: East, 4: South, 8: West
        '''
        assert flag in self.walls # Throw error on invalid flag values
        walls = self.decode_cell(cell)
        
        if flag not in walls:
            walls.append(flag)
        return sum(walls)
    
    
    def check_movement(self, heading, cell):
        '''
        Check if a given movement is valid.
        Args:
            heading: current heading 0 - 3 for North, East, South, West respectively
            walls: list of integers representing wall presence, [1, 2, 4, 8]
            
        Returns:
            checked: bool indicating whether the proposed movement is valid
        '''
        if 2**heading in self.decode_cell(cell):
            return False
        else:
            return True
        
        
    def get_visits(self, maze, location):
        '''
        '''
        cell_walls = self.decode_cell(maze[location[0], location[1], 0])
        visits = [255,255,255,255]
        for w, wall in enumerate(self.walls):
            if wall not in cell_walls:
                loc = self.decode_heading(w, location)
                visits[w] = maze[loc[0], loc[1], 2]
        return visits
    
    
    def wall_follower(self, maze, location, heading, exploring=True):
        '''
        Follow left hand wall when possible.
        '''
        if exploring:
            visits = self.get_visits(maze, location)
            if visits[(heading + 3) % 4] == min(visits): # If turning left is an option, and best or tied for best, turn left.
                rotation = -1
            elif visits[heading] == min(visits): # If turning left isn't an option, check straight for the same qualities.
                rotation = 0
            else: # If straight also isn't an option, turn right.
                rotation = 1

            walls = self.decode_cell(maze[location[0], location[1], 0])
            new_heading = self.update_heading(rotation, heading)
            
            if self.walls[new_heading] in walls:
                movement = 0
            else:
                movement = 1
        return rotation, movement


    def dead_reckoning(self, maze, location, heading):
        return 0, 0

    def waterfall_update(self, maze):
        maze_size = maze.shape[0]
        center = maze_size // 2
        new_maze = np.zeros((maze_size, maze_size), dtype=np.uint8)
        stack = list()
        if (maze_size % 2) == 0:
            stack.extend([(center, center), (center-1, center), (center, center-1), (center-1, center-1)])
            new_maze[center-1:center+1, center-1:center+1] = 1
        else:
            stack.append((center, center))
            new_maze[center, center] = 1
        while len(stack) > 0:
            loc = stack.pop(0)
            walls = self.decode_cell(maze[loc[0], loc[1], 0])
            for i in range(4):
                check_loc = self.decode_heading(i, loc)
                if (max(check_loc) < maze_size) and (2**i not in walls):
                    if new_maze[check_loc[0], check_loc[1]] == 0:
                        stack.append(check_loc)
                        new_maze[check_loc[0], check_loc[1]] = new_maze[loc[0], loc[1]] + 1
        print new_maze
        maze[:,:,1] = new_maze - 1
        return maze
    
    
    def waterfall_choice(self, maze, location, heading):
        neighbors = self.waterfall_neighbors(maze, location)
        min_value = min(neighbors)
        if neighbors[heading] == min_value:
            return heading
        else:
            return neighbors.index(min_value)

        
    def waterfall_neighbors(self, maze, location):
        maze_size = maze.shape[0]
        walls = self.decode_cell(maze[location[0], location[1], 0])
        neighbors = list()
        for i in range(4):
            check_loc = self.decode_heading(i, location)
            if (max(check_loc) < maze_size) and (2**i not in walls):
                dist = maze[check_loc[0], check_loc[1], 1]
                if self.exploring:
                    visits = maze[check_loc[0], check_loc[1], 2]
                else:
                    visits = 0
                neighbors.append(dist + visits)
            else:
                neighbors.append(255)
        return neighbors
        
    def waterfall(self, maze, location, heading):
        self.maze = self.waterfall_update(maze)
        new_head = self.waterfall_choice(maze, location, heading)
        head_turn_left = {0:3, 1:0, 2:1, 3:2}
        if new_head == heading:
            rotation = 0
        elif new_head == head_turn_left[heading]:
            rotation = -1
        elif heading == head_turn_left[new_head]:
            rotation = 1
        else:
            return 1, 0
        
        movement = 1
        new_loc = location
        while self.exploring:
            new_loc = self.decode_heading(new_head, new_loc)
            new_heading = self.waterfall_choice(maze, new_loc, new_head)
            if (new_heading != new_head) or movement > 2:
                return rotation, movement
            else:
                movement += 1
        return rotation, movement
            
      
def unit_tests():
    maze_dim = 12
    bot = Robot(12)
    assert bot.decode_sensors(0, [0,10,0]) == [10, 0, -1, 0]
    assert bot.decode_sensors(3, [0,10,0]) == [0, -1, 0, 10]

    assert bot.decode_cell(6) == [2, 4]
    assert bot.decode_cell(11) == [1, 2, 8]
    assert bot.decode_cell(15) == [1, 2, 4, 8]
    
    maze = bot.waterfall_update(bot.maze)
    
    print "All tests passed."

if __name__ == '__main__':
    import sys
    unit_tests()
    testmaze = Maze( str(sys.argv[1]))
    bot = Robot(testmaze.get_dim())

                        