import numpy as np

class Algorithm(object):
    """
    Behavior model for simulated micro mouse.
    
    Attributes:
        maze_dim:    known number of cells in width in the maze.
        goal:        array of locations considered to be success conditions
        start:       robot starting location, defaults to (0,0)
        exploring:   track current simulation phase: exploration / speed
        map_layers:  number of layers being used to track cell specific information
        maze:         uint8 numpy array representing all data known by the algorithm about the maze
        valid_walls: array listing bit values for walls, North, East, South, West respectively
        cell_walls:  array of values taken from valid_walls representing present walls 
        cell:        integer sum of cell_walls for a given cell in the map
        heading:     direction of current facing of micro mouse. 0 - 3 inclusive. 2**heading = bit value of wall at that heading.
        location:    integer x, y pair indicating the current cell location of the micro mouse
        rotation:    one of [-90, 0, 90] indicating turn or straight.
        movement:    integer from 0 - 3 inclusive, indicating the number of cells to move in the new direction.
        transform:   integer tuple that can be added to a location to move it one cell in the direction of heading
    
    """
    
    
    def __init__(self, maze_dim, goal, start=(0,0), map_layers=1):
        self.maze_dim = maze_dim
        self.goal = goal
        self.start = start
        self.exploring = True
        self.maze = self.blank_maze(maze_dim, map_layers, goal)
        self.valid_walls = [1, 2, 4, 8]
    
    def blank_maze(self, maze_dim, map_layers, goal):
        """ Create a blank map of the maze. Fill in outer walls. """
        maze = np.zeros((maze_dim, maze_dim, map_layers), dtype=np.uint8)

        # Fill in outer walls
        maze[:, -1, 0] += 1 # North
        maze[:, 0, 0] += 4 # South
        maze[-1, :, 0] += 2 # East
        maze[0, :, 0] += 8  # West
        
        return maze
    
    
    def update_maze(self, maze, walls, location):
        """ Update maze representation to reflect current sensor data. """
        for w, wall in enumerate(walls):
            if wall == 0: # If this heading is not a blind spot
                x = location[0]
                y = location[1]
                maze[x, y, 0] = self.mark_wall(maze[x, y, 0], w) # Mark visible wall

                transform = self.decode_heading(w)                
                x += transform[0]
                y += transform[1]
                if (x < maze.shape[0]) and (x >= 0) and (y < maze.shape[1]) and (y >= 0):
                    maze[x, y, 0] = self.mark_wall(maze[x, y, 0], (w+2)%4) # Mark other side of visible wall
        return maze

    
    def decode_cell(self, cell):
        """ Decode cell wall value and add flag value if not already present. """
        reversed_walls = list(self.valid_walls)
        reversed_walls.reverse()
        print reversed_walls
        cell_walls = list()
        for heading in reversed_walls:
            if cell >= heading:
                cell -= heading
                cell_walls.append(heading)
        cell_walls.reverse()
        return cell_walls

    
    def mark_wall(self, cell, heading):
        """ Determine if a wall is already mapped at a given heading, if not, add it. """

        assert 2**heading in self.valid_walls  # Throw error on invalid heading values
        cell_walls = self.decode_cell(cell)
        if 2**heading not in cell_walls:
            cell_walls.append(2**heading)
        return sum(cell_walls)

    
    def decode_heading(self, heading):
        """ Convert directional heading into coordinate transformation. Addition with a location 
            transforms that location by 1 cell in the direction of the given heading. """
        
        if heading == 0:
            return (0, 1)
        if heading == 1:
            return (1, 0)
        if heading == 2:
            return (0, -1)
        if heading == 3:
            return (-1, 0)
    

    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """        
        return 'Reset', 'Reset'


# ********************************************************************************************************


class Wall_follower(Algorithm):
    """
    Follows the left wall unless there is a less frequently visited alternative.
    """

    def __init__(self, maze_dim, goal, start=(0,0), map_layers=2):
        self.maze_dim = maze_dim
        self.goal = goal
        self.start = start
        self.exploring = True
        self.maze = self.blank_maze(maze_dim, map_layers, goal)
        self.valid_walls = [1, 2, 4, 8]
        self.dead_ends = [7, 11, 13, 14]
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """
        
        self.maze = self.update_maze(self.maze, walls, location)
        
        if location in self.goal:
            return 'Reset', 'Reset'
        
        self.maze[location[0], location[1], 1] += 1 # Update visits to the current cell
        
        
        visits = self.get_visits(self.maze, location)
        if visits[(heading + 3) % 4] == min(visits): # If turning left is an option, and best or tied for best, turn left.
            return -90, 1
        
        if visits[heading] == min(visits): # If turning left isn't an option, check straight for the same qualities.
            return 0, 1
        
        if visits[(heading + 1) % 4] == min(visits): # If turning straight also isn't an option, check right.
            return 90, 1
        
        return 90, 0 # If all else fails, turn right but don't move.

    
    def get_visits(self, maze, location):
        """ Return the number of visits to each adjoining cell, organized by heading. """
        cell_walls = self.decode_cell(maze[location[0], location[1], 0])
        visits = [255,255,255,255]
        for w, wall in enumerate(self.valid_walls):
            if wall not in cell_walls:
                transform = self.decode_heading(w)
                x = location[0] + transform[0]
                y = location[1] + transform[1]
                if maze[x,y,0] in self.dead_ends:
                    maze[x,y,1] = 250
                visits[w] = maze[x, y, 1]
        return visits


# ********************************************************************************************************


class Basic_waterfall(Algorithm):
    def __init__(self):
        # Set state (Exploration / Speed)
        self.exploring = True
        
        # Set maze wall values [North, East, South, West]
        self.walls = [1, 2, 4, 8]

        pass

    
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
                elif maze[check_loc[0], check_loc[1], 2] == 0:
                    visits = 100
                else: 
                    visits = maze[check_loc[0], check_loc[1], 2]
                neighbors.append(dist + visits)
            else:
                neighbors.append(255)
        return neighbors

    
    def waterfall(self, maze, location, heading):
        if (self.maze[self.location[0], self.location[1], 1] == 0):
            self.exporing = False
            self.location = (0,0)
            self.heading = 0
            return 'Reset', 'Reset'
        
        self.maze[:,:,0] = self.update_maze(self.maze[:,:,0], self.heading, self.location, sensors)
                
        for i in range(movement):
            if self.check_movement(self.heading, self.maze[self.location[0], self.location[1], 0]):
                if movement < 0:
                    self.location = self.decode_heading((self.heading+2)%4, self.location)
                else:
                    self.location = self.decode_heading(self.heading, self.location)
                self.maze[self.location[0], self.location[1], 2] += 1
#        _ = raw_input(self.maze[:,:,0])

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

    
# ********************************************************************************************************


    def placeholder(self):
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


# ********************************************************************************************************

if __name__ == '__main__':
    assert bot.decode_cell(6) == [2, 4]
    assert bot.decode_cell(11) == [1, 2, 8]
    assert bot.decode_cell(15) == [1, 2, 4, 8]
    
    maze = bot.waterfall_update(bot.maze)
