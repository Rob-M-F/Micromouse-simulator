import numpy as np

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''

        self.exploring = 1
        self.location = [0, -1]
        self.directions = ['North', 'East', 'South', 'West']
        self.heading = 0
        self.maze_dim = maze_dim
        self.maze = self.blank_map(self.maze_dim) #Create internal map of the maze
    
    def blank_map(self, maze_dim):
        
        # Define map dimensions: maze wall layer = 0, waterfall calculation layer = 1
        maze = np.zeros((maze_dim,maze_dim,2), dtype=np.uint8)

        # Define exterior walls on map
        maze[0, :, 0] += 1  # North
        maze[:, -1, 0] += 8 # East
        maze[-1, :, 0] += 2 # South
        maze[:, 0, 0] += 4 # West

        maze[:,:,1] = 200 # Assume all spaces are 200 from goal until otherwise defined
        maze[-1,0,0] = 14 # Mark standard starting walls for standard starting cell
        maze[0,0,1] = 255 # Mark starting square as worst possible location
        
        center = maze_dim // 2
        
        
        maze[center, center, 1] = 0 # Mark center cell with distance = 0
        if maze_dim % 2 == 0: # If maze has even dimensions, set all 4 center cells with distance = 0
            maze[center-1, center-1, 1] = 0
            maze[center, center-1, 1] = 0
            maze[center-1, center, 1] = 0

        return maze
    
    def update_maze(self, sensors):
        pass
    
    def update_heading(self, rotation):
        if rotation < 0:
            self.heading = (self.heading - 1) % 4
        elif rotation > 0:
            self.heading = (self.heading + 1) % 4
        if self.heading < 0:
            self.heading += 4
    
    def update_location(self, movement):
        if self.heading == 0:
            self.location = (self.location[0], self.location[1]+movement)
        if self.heading == 1:
            self.location = (self.location[0]+movement, self.location[1])
        if self.heading == 2:
            self.location = (self.location[0], self.location[1]-movement)
        if self.heading == 3:
            self.location = (self.location[0]-movement, self.location[1])
        
        
    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''
        if self.maze[self.location[0], self.location[1], 1] == 0:
            return 'Reset', 'Reset'
        
        print self.maze[:,:,0]
#        print self.maze[:,:,1]
        
        this_maze = self.maze[:,:,0]
        this_maze[self.location[0], self.location[1]] = 100
        print this_maze
        
        if sensors[1] == 0:
            if sensors[0] > 0:
                rotation = -90
                if sensors[0] > 2:
                    movement = 3
                else:
                    movement = sensors[0]
            else:
                rotation = 90
                self.heading = (self.heading + 1) % 4
                if sensors[2] > 2:
                    movement = 3
                else:
                    movement = sensors[2]
        else:
            rotation = 0
            if sensors[1] > 2:
                movement = 3
            else:
                movement = sensors[1]

        self.update_heading(rotation)
        self.update_location(movement)
        
        print self.location, self.directions[self.heading], movement
        
        return rotation, movement