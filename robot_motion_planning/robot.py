import numpy as np

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''

        self.location = [0, 0]
        self.heading = 'up'
        self.maze_dim = maze_dim
        self.blank_map(self.maze_dim) #Create internal map of the maze
    
    def blank_map(self, maze_dim):
        maze = np.zeros((maze_dim,maze_dim,2), dtype=np.uint8)
        maze[0, :, 0] += 1
        maze[-1, :, 0] += 2
        maze[:, 0, 0] += 4
        maze[:, -1, 0] += 8

        maze[:,:,1] = 255
        
        center = maze_dim // 2
        maze[center, center, 1] = 0
        if maze_dim % 2 == 0:
            maze[center-1, center-1, 1] = 0
            maze[center, center-1, 1] = 0
            maze[center-1, center, 1] = 0

        self.maze = maze

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

        print self.maze[:,:,0]
        print self.maze[:,:,1]
        
        if sensors[1] == 0:
            if sensors[0] > 0:
                rotation = -90
                if sensors[0] > 2:
                    movement = 3
                else:
                    movement = sensors[0]

            else:
                rotation = 90
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

        
        
        return rotation, movement