import numpy as np
from collections import deque

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
    
    
    def __init__(self, maze_dim, goal, start=(0,0)):
        self.name = "Wall Follower"
        self.maze_dim = maze_dim
        self.goal = goal
        self.start = start
        self.exploring = True
        self.maze = self.blank_maze(maze_dim, map_layers=2, goal=self.goal)
        self.valid_walls = [1, 2, 4, 8]
        self.dead_ends = [7, 11, 13, 14]
        
        
    def algorithm_choice(self, walls = list(), heading=0, location =(0, 0)):
        """ Determine the next action to take in searching for the goal. """

        if location in self.goal:
            return 'Reset', 'Reset'

        self.maze = self.update_maze(self.maze, walls, location)
        self.maze[location[0], location[1], 1] += 1 # Update visits to the current cell
        
        visits = self.get_visits(self.maze, location)
        if visits[(heading + 3) % 4] == min(visits): # If turning left is an option, and best or tied for best, turn left.
            return -90, 1
        elif visits[heading] == min(visits): # If turning left isn't an option, check straight for the same qualities.
            return 0, 1
        elif visits[(heading + 1) % 4] == min(visits): # If turning straight also isn't an option, check right.
            return 90, 1
       
        return 90, 0 # If all else fails, turn right but don't move.

    
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
            if wall == 0: # If this cell has a wall in the given direction.
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

        
    def heading_to_rotation(self, heading, new_heading):
        """ Determine implied rotation between two headings. """
        if heading == new_heading:
            rotate = 0
        elif (heading+1)%4 == new_heading:
            rotate = 90
        elif (heading+3)%4 == new_heading:
            rotate = -90
        else:
            rotate = "None"
        return rotate
    
    
    def decode_rotation(self, heading, rotation):
        """ Change provided heading according to provided rotation. """
        assert rotation in [-90, 0, 90]
        if rotation == 0:
            return heading
        if rotation == 90:
            return (heading+1)%4
        if rotation == -90:
            return (heading+3)%4
    
    
    def get_name(self):
        return self.name


# ********************************************************************************************************


class Waterfall(Algorithm): # Basic waterfall
    def __init__(self, maze_dim, goal, start = (0, 0)):
        super(Waterfall, self).__init__(maze_dim, goal, start)
        # Set state (Exploration / Speed)
        self.name = "Basic Waterfall"
        self.maze = self.blank_maze(maze_dim, map_layers=1, goal=goal)
        self.plan = deque()
        self.laps = maze_dim - 9
        self.current_lap = self.laps
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """
        self.maze = self.update_maze(self.maze, walls, location)
        if ((self.laps - self.current_lap)%2 == 0) or not self.exploring:
            target = list(self.goal)
        else:
            target = [self.start]
        waterfall = self.waterfall_update(self.maze, target)
        if self.exploring:
            if (location in target): # If goal has been reached and back at start, end run.
                self.laps -= 1
            if self.laps == 0:
                self.exploring = False
                return 'Reset', 'Reset'
            return self.waterfall_choice(waterfall, heading, location)
        else:
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


    def waterfall_neighbors(self, waterfall, location, all=False):
        """ Examine the neighboring cells and return those which are equally good choices """
        maze_size = waterfall.shape[0]
        current = waterfall[location[0], location[1]]
        walls = self.decode_cell(self.maze[location[0], location[1], 0])
        neighbors = list()
        no_pass = 255
        for i in range(4):
            transform = self.decode_heading(i)
            x = location[0] + transform[0]
            y = location[1] + transform[1]
            if (max((x, y)) < maze_size) and (2**i not in walls):
                neighbors.append(waterfall[x, y])
            else:
                neighbors.append(no_pass)
        if all:
            return [n for n, neighbor in enumerate(neighbors) if neighbor <= current]
        else:
            return [n for n, neighbor in enumerate(neighbors) if neighbor == min(neighbors)]
    
    
    def waterfall_update(self, maze, goal=None):
        """ Update the waterfall map to reflect new information. To return to start, recalcuate the map from start. """
        maze_size = maze.shape[0]
        center = maze_size // 2
        waterfall = np.zeros((maze_size, maze_size), dtype=np.uint8)
        if goal == None:
            goal = self.goal
        stack = list(goal)
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
    

# ********************************************************************************************************


class Search_waterfall(Waterfall):
    def __init__(self, maze_dim, goal, start = (0, 0)):
        super(Search_waterfall, self).__init__(maze_dim, goal, start)
        # Set state (Exploration / Speed)
        self.name = "Search_waterfall"
        self.maze = self.blank_maze(maze_dim, map_layers=2, goal=goal)
        self.target = list(goal)
        
    
    def algorithm_choice(self, walls = list(), heading=0, location = (0, 0)):
        """ Determine the next action to take in searching for the goal. """
        if location in self.target:
            self.target.remove(location)
        if (not self.target) and (location not in self.goal):
            self.target = list(self.goal)
        if (not self.target) and (location != self.start):
            self.target = [self.start]
        if self.plan:
            return self.plan.popleft()
        self.maze = self.update_maze(self.maze, walls, location)
        self.maze[location[0], location[1],1] += 1
        waterfall = self.waterfall_update(self.maze, self.target)
        routes = self.route_planner(waterfall)            
        if routes: 
            potential_plan = min(routes, key=len)
            empty_cells = self.verify_plan(potential_plan)
            if empty_cells:
                self.target = deque(empty_cells)
            elif (len(potential_plan) > 1):
                self.plan = potential_plan
                self.target = self.goal
                return 'Reset', 'Reset'
        return self.waterfall_choice(waterfall, heading, location)

                      
    def verify_plan(self, plan):
        """ Check the plan. Return list of spaces in plan that have not been explored """
        current = deque(plan)
        location = self.start
        heading = 0
        empty_cells = list()
        while current:
            step = current.popleft()
            heading = self.decode_rotation(heading, step[0])
            transform = self.decode_heading(heading)
            for cell in range(step[1]):
                location = location[0]+transform[0], location[1]+transform[1]
                if (max(location) < self.maze.shape[0]) and (min(location) >= 0):
                    if self.maze[location[0], location[1], 1] == 0:
                        empty_cells.append(location)
        return empty_cells
    
    
    def route_planner(self, waterfall):
        """ Convert mapped routes into movement optimized routes. """
        process_stack = self.route_mapper(waterfall, (0,0), 0)
        plan_stack = deque()
        while process_stack:
            plan = process_stack.popleft()
            rotate = 0
            move = 0
            new_plan = deque()
            while plan:
                step = plan.popleft()
                next_step = (rotate, move)
                if (step[0] == 0) and move < 3:
                    move += 1
                else:
                    new_plan.append(next_step)
                    rotate = step[0]
                    move = step[1]
            if len(new_plan) > 1:
                new_plan.append(next_step)
            plan_stack.append(new_plan)       
        return plan_stack
    
    
    def route_mapper(self, waterfall, location, heading):
        """ Recursively generate all descending routes from start to goal. """
        neighbors = self.waterfall_neighbors(waterfall, location, True)
        plan_stack = deque()
        if waterfall[location[0], location[1]] == 1:
            base = deque([(0,0)])
            plan_stack.append(base)
        else:
            for n in neighbors:
                rotate = self.heading_to_rotation(heading, n)
                step = (rotate, 1)
                if rotate != "None":
                    transform = self.decode_heading(n)
                    x = location[0] + transform[0]
                    y = location[1] + transform[1]
                    plan = self.route_mapper(waterfall, (x, y), n)
                    while plan:
                        route = plan.pop()
                        route.appendleft(step)
                        plan_stack.append(route)
        return plan_stack
    

# ********************************************************************************************************


class Oracle_waterfall(Search_waterfall): # Perfect score by knowing the maze
    def __init__(self, maze_dim, goal, start = (0, 0)):
        super(Oracle_waterfall, self).__init__(maze_dim, goal, start)
        self.name = "Oracle Waterfall"

        
    def maze_oracle(self, maze):
        """ Accept maze object and fill in the internal maze to match. """
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
        if not self.plan:
            waterfall = self.waterfall_update(self.maze)
            self.plan = min(self.route_planner(waterfall), key=len)
        if (location in self.goal): # If goal has been reached and back at start, end run.
            return 'Reset', 'Reset'

        return self.plan.popleft()
    

# ********************************************************************************************************


if __name__ == '__main__':
    assert bot.decode_cell(6) == [2, 4]
    assert bot.decode_cell(11) == [1, 2, 8]
    assert bot.decode_cell(15) == [1, 2, 4, 8]
    
    maze = bot.waterfall_update(bot.maze)
