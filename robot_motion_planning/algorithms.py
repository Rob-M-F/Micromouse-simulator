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
    
    
    def __init__(self, maze_dim, goal):
        self.maze_dim = maze_dim
        self.goal = goal
        self.start = start
        self.exploring = True
        self.maze = self.blank_maze(maze_dim, map_layers=2, goal=self.goal)
        self.valid_walls = [1, 2, 4, 8]
        self.dead_ends = [7, 11, 13, 14]
        
        
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """   
        
        return 'Reset', 'Reset'

    
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
        
        if heading == 0: return (0, 1)
        if heading == 1: return (1, 0)
        if heading == 2: return (0, -1)
        if heading == 3: return (-1, 0)
    
    
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
    
    
    def get_name(self):
        return "Generic Algorithm"


# ********************************************************************************************************


class Wall_follower(Algorithm):
    """
    Follows the left wall unless there is a less frequently visited alternative.
    """

    def __init__(self, maze_dim, goal):
        self.maze_dim = maze_dim
        self.goal = goal
        self.maze = self.blank_maze(maze_dim, map_layers=2, goal=self.goal)
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

    def get_name(self):
        return "Wall Follower"

# ********************************************************************************************************


class Search_waterfall(Algorithm):
    def __init__(self, maze_dim, goal, start = (0, 0)):
        # Set state (Exploration / Speed)
        self.maze_dim = maze_dim
        self.goal = list(goal)
        self.start = list(start)
        self.exploring = True
        self.maze = self.blank_maze(maze_dim, map_layers=2, goal=self.goal)
        self.valid_walls = [1, 2, 4, 8] # Set maze wall values [North, East, South, West]
        self.plan_stack = list()
    
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """

        self.maze = self.update_maze(self.maze, walls, location)
        waterfall = self.waterfall_update(self.maze)
        

        if (location in self.goal): # If goal has been reached and back at start, end run.
            return 'Reset', 'Reset'

        return self.waterfall_choice(waterfall, heading, location)
    
    
    def decode_rotation(self, heading, rotation):
        if rotation == 0:
            return heading
        if rotation == 90:
            return (heading+1)%4
        if rotation == -90:
            return (heading+3)%4
    
    
    def waterfall_update(self, maze):
        """ Update the waterfall map to reflect new information. To return to start, recalcuate the map from start. """
        maze_size = maze.shape[0]
        center = maze_size // 2
        waterfall = np.zeros((maze_size, maze_size), dtype=np.uint8)
        stack = list(self.goal)
        for cell in stack:
            waterfall[cell[0], cell[1]] = 1
            
        while len(stack) > 0:
            loc = stack.pop(0)
            walls = self.decode_cell(maze[loc[0], loc[1], 0])
            for i in range(4):
                transform = self.decode_heading(i)
                x = loc[0] + transform[0]
                y = loc[1] + transform[1]
                if (max((x,y)) < maze_size) and (2**i not in walls):
                    if waterfall[x, y] == 0:
                        new_loc = (x, y)
                        stack.append(new_loc)
                        waterfall[x, y] = waterfall[loc[0], loc[1]] + 1
        return waterfall
            

    def waterfall_choice(self, waterfall, heading, location):
        """ Evaluate the current waterfall map and plan the next action """
        rotation = 0
        movement = 0
        x = location[0]
        y = location[1]
        h = heading
        for i in range(3):
            neighbors = self.waterfall_neighbors(waterfall, (x, y))
            rotate = -90
            move = 1
            if h in neighbors: rotation = 0
            elif (h+1)%4 in neighbors: rotate = 90
            elif (h+3)%4 in neighbors: rotate = -90
            else: move = 0
                
            if i == 0:
                rotation = rotate
                movement = move
            elif rotate == 0:
                movement += 1
            else:
                break
            if move == 0:
                break
            maze[x, y, 1] += 1
            h = self.decode_rotation(h, rotate)
            transform = self.decode_heading(h)
            x += transform[0]
            y += transform[1]
        return rotation, movement

    def waterfall_neighbors(self, waterfall, location):
        """ Examine the neighboring cells and return those which are equally good choices """
        maze_size = waterfall.shape[0]
        walls = self.decode_cell(self.maze[location[0], location[1], 0])
        neighbors = list()
        for i in range(4):
            transform = self.decode_heading(i)
            x = location[0] + transform[0]
            y = location[1] + transform[1]
            if (max((x, y)) < maze_size) and (2**i not in walls):
                neighbors.append(waterfall[x, y])
            else:
                neighbors.append(255)
        return [n for n, neighbor in enumerate(neighbors) if neighbor == min(neighbors)]
    
    
    def route_planner(self, waterfall):
        return self.plan_stack


    def get_name(self):
        return "Search Waterfall"

# ********************************************************************************************************


class Double_waterfall(Algorithm):
    def __init__(self, maze_dim, goal, start = (0, 0)):
        # Set state (Exploration / Speed)
        self.exploring = True
        self.outbound = True
        self.maze_dim = maze_dim
        self.goal = goal
        self.start = [start]
        self.maze = self.blank_maze(maze_dim, map_layers=3, goal=self.goal)
        self.valid_walls = [1, 2, 4, 8] # Set maze wall values [North, East, South, West]
        self.dead_ends = [7, 11, 13, 14]
        self.location = start
        
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """

        self.maze = self.update_maze(self.maze, walls, location)
        self.maze[location[0], location[1], 1] += 1 # Update visits to the current cell
        self.maze = self.waterfall_update(self.maze)
        visits = self.get_visits(self.maze, location)

        if (location in self.start) and not self.outbound: # If goal has been reached and back at start, end run.
            self.outbound = True
            self.exploring = False
            return 'Reset', 'Reset'

        if (location in self.goal) and self.outbound: # If goal is reached, return to start
            self.outbound = False

        return self.waterfall_choice(self.maze, heading, location)
        
    
    def waterfall_update(self, maze):
        maze_size = maze.shape[0]
        center = maze_size // 2
        new_maze = np.zeros((maze_size, maze_size), dtype=np.uint8)
        if self.outbound:
            stack = list(self.goal)
        else:
            stack = list(self.start)
            
        for cell in stack:
            new_maze[cell[0], cell[1]] = 1
            
        while len(stack) > 0:
            loc = stack.pop(0)
            walls = self.decode_cell(maze[loc[0], loc[1], 0])
            for i in range(4):
                transform = self.decode_heading(i)
                x = loc[0] + transform[0]
                y = loc[1] + transform[1]
                if (max((x,y)) < maze_size) and (2**i not in walls):
                    if new_maze[x, y] == 0:
                        new_loc = (x, y)
                        stack.append(new_loc)
                        new_maze[x, y] = new_maze[loc[0], loc[1]] + 1
        maze[:,:,2] = new_maze
        return maze


    def waterfall_choice(self, maze, heading, location):
        neighbors = self.waterfall_neighbors(maze, location)
        if heading in neighbors:
            new_heading = heading
            rotation = 0
            movement = 1
        elif (heading+1)%4 in neighbors:
            new_heading = (heading+1)%4
            rotation = 90
            movement = 1
        elif (heading+3)%4 in neighbors:
            new_heading = (heading+3)%4
            rotation = -90
            movement = 1
        else:
            new_heading = (heading+3)%4
            rotation = -90
            movement = 0
        return rotation, movement


    def waterfall_neighbors(self, maze, location):
        maze_size = maze.shape[0]
        walls = self.decode_cell(maze[location[0], location[1], 0])
        neighbors = list()
        for i in range(4):
            transform = self.decode_heading(i)
            x = location[0] + transform[0]
            y = location[1] + transform[1]
            if (max((x, y)) < maze_size) and (2**i not in walls):
                neighbors.append(maze[x, y, 2])
            else:
                neighbors.append(255)
        value = min(neighbors)
        valued_neighbors = list()
        for n, neighbor in enumerate(neighbors):
            if neighbor == value:
                valued_neighbors.append(n)
        return valued_neighbors

            
    def get_name(self):
        return "Double Waterfall"
    
            
# ********************************************************************************************************

class Basic_waterfall(Algorithm):
    def __init__(self, maze_dim, goal, start = (0, 0)):
        # Set state (Exploration / Speed)
        self.exploring = True
        self.outbound = True
        self.maze_dim = maze_dim
        self.goal = goal
        self.start = [start]
        self.maze = self.blank_maze(maze_dim, map_layers=3, goal=self.goal)
        self.valid_walls = [1, 2, 4, 8] # Set maze wall values [North, East, South, West]
        self.dead_ends = [7, 11, 13, 14]
        
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """

        self.maze = self.update_maze(self.maze, walls, location)
        self.maze[location[0], location[1], 1] += 1 # Update visits to the current cell
        self.maze = self.waterfall_update(self.maze)
        visits = self.get_visits(self.maze, location)

#        if (location in self.start) and not self.outbound: # If goal has been reached and back at start, end run.
        if (location in self.goal): # If goal has been reached and back at start, end run.
#            self.outbound = True
            self.exploring = False
            return 'Reset', 'Reset'

#        if (location in self.goal) and self.outbound: # If goal is reached, return to start
#            self.outbound = False
    
        return self.waterfall_choice(self.maze, heading, location)
    
    
    def waterfall_update(self, maze):
        """ Update the waterfall map to reflect new information. To return to start, recalcuate the map from start. """
        maze_size = maze.shape[0]
        center = maze_size // 2
        new_maze = np.zeros((maze_size, maze_size), dtype=np.uint8)
        if self.outbound:
            stack = list(self.goal)
        else:
            stack = list(self.start)
            
        for cell in stack:
            new_maze[cell[0], cell[1]] = 1
            
        while len(stack) > 0:
            loc = stack.pop(0)
            walls = self.decode_cell(maze[loc[0], loc[1], 0])
            for i in range(4):
                transform = self.decode_heading(i)
                x = loc[0] + transform[0]
                y = loc[1] + transform[1]
                if (max((x,y)) < maze_size) and (2**i not in walls):
                    if new_maze[x, y] == 0:
                        new_loc = (x, y)
                        stack.append(new_loc)
                        new_maze[x, y] = new_maze[loc[0], loc[1]] + 1
        maze[:,:,2] = new_maze
        return maze
            

    def waterfall_choice(self, maze, heading, location):
        """ Evaluate the current waterfall map and plan the next action """
        neighbors = self.waterfall_neighbors(maze, location)
        if heading in neighbors:
            new_heading = heading
            rotation = 0
            movement = 1
        elif (heading+1)%4 in neighbors:
            new_heading = (heading+1)%4
            rotation = 90
            movement = 1
        elif (heading+3)%4 in neighbors:
            new_heading = (heading+3)%4
            rotation = -90
            movement = 1
        else:
            new_heading = (heading+3)%4
            rotation = -90
            movement = 0
        return rotation, movement


    def waterfall_neighbors(self, maze, location):
        """ Examine the neighboring cells and return those which are equally good choices """
        maze_size = maze.shape[0]
        walls = self.decode_cell(maze[location[0], location[1], 0])
        neighbors = list()
        for i in range(4):
            transform = self.decode_heading(i)
            x = location[0] + transform[0]
            y = location[1] + transform[1]
            if (max((x, y)) < maze_size) and (2**i not in walls):
                neighbors.append(maze[x, y, 2])
            else:
                neighbors.append(255)
        value = min(neighbors)
        valued_neighbors = list()
        for n, neighbor in enumerate(neighbors):
            if neighbor == value:
                valued_neighbors.append(n)
        return valued_neighbors

            
    def get_name(self):
        return "Basic Waterfall"
            

# ********************************************************************************************************


class Oracle_waterfall(Algorithm): # Perfect score benchmark
    def __init__(self, maze_dim, goal, start = (0, 0)):
        # Set state (Exploration / Speed)
        self.maze_dim = maze_dim
        self.goal = goal
        self.start = [start]
        self.maze = self.blank_maze(maze_dim, map_layers=1, goal=self.goal)
        self.valid_walls = [1, 2, 4, 8] # Set maze wall values [North, East, South, West]

        
    def maze_oracle(self, maze):
        d = ['u', 'r', 'd', 'l']
        maze_dim = maze.get_dim()
        maze_walls = np.zeros((maze_dim, maze_dim, 1), dtype=np.uint8)
        for x in range(maze_dim):
            for y in range(maze_dim):
                for w in range(4):
                    if not maze.is_permissible([x, y], d[w]):
                        maze_walls[x, y] += 2**w
        self.maze[:,:,:] = maze_walls[:,:,:]
        return True
        
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """

        self.maze = self.update_maze(self.maze, walls, location)
        waterfall = self.waterfall_update(self.maze)

        if (location in self.goal): # If goal has been reached and back at start, end run.
            return 'Reset', 'Reset'
        rotation = 0
        movement = 0
        x = location[0]
        y = location[1]
        h = heading
        for i in range(3):
            rotate, move = self.waterfall_choice(waterfall, h, (x, y))
            h = self.decode_rotation(h, rotate)
            transform = self.decode_heading(h)
            x += transform[0]
            y += transform[1]
            if i == 0:
                rotation = rotate
                movement = move
            elif rotate == 0:
                movement += 1
            else:
                break
            if move == 0:
                break
        return rotation, movement
    
    
    def decode_rotation(self, heading, rotation):
        if rotation == 0:
            return heading
        if rotation == 90:
            return (heading+1)%4
        if rotation == -90:
            return (heading+3)%4
    
    def waterfall_update(self, maze):
        """ Update the waterfall map to reflect new information. To return to start, recalcuate the map from start. """
        maze_size = maze.shape[0]
        center = maze_size // 2
        waterfall = np.zeros((maze_size, maze_size), dtype=np.uint8)
        stack = list(self.goal)
        for cell in stack:
            waterfall[cell[0], cell[1]] = 1
            
        while len(stack) > 0:
            loc = stack.pop(0)
            walls = self.decode_cell(maze[loc[0], loc[1], 0])
            for i in range(4):
                transform = self.decode_heading(i)
                x = loc[0] + transform[0]
                y = loc[1] + transform[1]
                if (max((x,y)) < maze_size) and (2**i not in walls):
                    if waterfall[x, y] == 0:
                        new_loc = (x, y)
                        stack.append(new_loc)
                        waterfall[x, y] = waterfall[loc[0], loc[1]] + 1
        return waterfall
            

    def waterfall_choice(self, waterfall, heading, location):
        """ Evaluate the current waterfall map and plan the next action """
        neighbors = self.waterfall_neighbors(waterfall, location)
        rotation = -90
        movement = 1
        if heading in neighbors: rotation = 0
        elif (heading+1)%4 in neighbors: rotation = 90
        elif (heading+3)%4 in neighbors: rotation = -90
        else: movement = 0
        return rotation, movement


    def waterfall_neighbors(self, waterfall, location):
        """ Examine the neighboring cells and return those which are equally good choices """
        maze_size = waterfall.shape[0]
        walls = self.decode_cell(self.maze[location[0], location[1], 0])
        neighbors = list()
        for i in range(4):
            transform = self.decode_heading(i)
            x = location[0] + transform[0]
            y = location[1] + transform[1]
            if (max((x, y)) < maze_size) and (2**i not in walls):
                neighbors.append(waterfall[x, y])
            else:
                neighbors.append(255)
        return [n for n, neighbor in enumerate(neighbors) if neighbor == min(neighbors)]

            
    def get_name(self):
        return "Oracle Waterfall"
            

# ********************************************************************************************************


if __name__ == '__main__':
    assert bot.decode_cell(6) == [2, 4]
    assert bot.decode_cell(11) == [1, 2, 8]
    assert bot.decode_cell(15) == [1, 2, 4, 8]
    
    maze = bot.waterfall_update(bot.maze)
