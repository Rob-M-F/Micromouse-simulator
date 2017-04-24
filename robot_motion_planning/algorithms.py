import numpy as np

class Algorithm(object):
    def __init__(self):
        pass
    
    def blank_map(self):
        pass
    
    def update_map(self):
        pass
    
    def decide_move(self):
        pass

# ********************************************************************************************************
    
class Wall_follower(Algorithm):
    def __init__(self):
        pass
    
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

# ********************************************************************************************************    
    
class Dead_reckoning(Algorithm):
    def __init__(self):
        pass

# ********************************************************************************************************
    
class Basic_Waterfall(Algorithm):
    def __init__(self):
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
