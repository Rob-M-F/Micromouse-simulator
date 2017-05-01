from maze import Maze
import turtle
import sys

class display_maze(object):
    def __init__(self, testmaze, cell_size = 20):
        self.maze = testmaze
        self.window = turtle.Screen()
        self.sq_size = cell_size
        self.origin = self.maze.dim * self.sq_size / -2
        self.draw_maze()

    def get_window(self):
        return self.window
    
    def get_origin(self):
        return self.origin
    
    def get_cell_size(self):
        return self.sq_size
    
    def close_display(self):
        self.window.bye()
    
    def draw_maze(self):
        '''
        This function uses Python's turtle library to draw a picture of the maze
        given as an argument when running the script.
        '''
        # configure turtle for maze drawing
        wally = turtle.RawPen(self.window)
        wally.speed(0)
        wally.hideturtle()
        wally.penup()
        
        # iterate through squares one by one to decide where to draw walls
        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                if not self.maze.is_permissible([x,y], 'up'):
                    wally.goto(self.origin + self.sq_size * x, self.origin + self.sq_size * (y+1))
                    wally.setheading(0)
                    wally.pendown()
                    wally.forward(self.sq_size)
                    wally.penup()

                if not self.maze.is_permissible([x,y], 'right'):
                    wally.goto(self.origin + self.sq_size * (x+1), self.origin + self.sq_size * y)
                    wally.setheading(90)
                    wally.pendown()
                    wally.forward(self.sq_size)
                    wally.penup()

                # only check bottom wall if on lowest row
                if y == 0 and not self.maze.is_permissible([x,y], 'down'):
                    wally.goto(self.origin + self.sq_size * x, self.origin)
                    wally.setheading(0)
                    wally.pendown()
                    wally.forward(self.sq_size)
                    wally.penup()

                # only check left wall if on leftmost column
                if x == 0 and not self.maze.is_permissible([x,y], 'left'):
                    wally.goto(self.origin, self.origin + self.sq_size * y)
                    wally.setheading(90)
                    wally.pendown()
                    wally.forward(self.sq_size)
                    wally.penup()

class display_robot(object):
    def __init__(self, display_maze, shape="turtle", color="black", fill="green"):
        # Capture information from display_maze function needed to position robot
        self.window = display_maze
        self.cell_size = self.window.get_cell_size()
        self.origin = self.window.get_origin() + (self.cell_size // 2)
        
        # Configure pen
        self.pen = turtle.RawPen(self.window.get_window())
        self.pen.hideturtle()
        self.pen.penup()
        self.pen.setheading(90)
        self.pen.goto(self.origin, self.origin)
        self.pen.shape(shape)
        self.pen.color(color)
        self.pen.fillcolor(fill)
        self.pen.showturtle()
        self.stamp = self.pen.stamp()

    def move_bot(self, location, heading=0):
        # Find the start and end positions and orientations for the stamp
        x_start = self.pen.pos()[0]
        y_start = self.pen.pos()[1]
        h_start = int(self.pen.heading())
        
        x_range = ((location[0] * self.cell_size) + self.origin) - x_start
        y_range = ((location[1] * self.cell_size) + self.origin) - y_start

        if heading >= 0: mod = 1
        else: mod = -1

        # Rotate the stamp 10 degrees at a time
        if heading != 0:
            for i in range(0, 91, 30):
                self.pen.setheading(h_start - mod*i)
    #            self.pen.goto(x_start, y_start)
                self.pen.clearstamp(self.stamp)
                self.stamp = self.pen.stamp()
        
        # Move the stamp one pixel at a time
        if (x_range + y_range) >= 0: mod = 1
        else: mod = -1
        
        for i in range(0, abs(x_range + y_range + mod), 10):
            if abs(x_range) > abs(y_range):
                self.pen.goto(x_start + mod*i, y_start)
            else:
                self.pen.goto(x_start, y_start + mod*i)
            self.pen.clearstamp(self.stamp)                
            self.stamp = self.pen.stamp()
        
    def track_bot(self, location, heading=0):
        current_stamp = self.stamp
        self.stamp = self.pen.stamp()
        self.move_bot(location, heading)

        
if __name__ == '__main__':
    testmaze = Maze( str(sys.argv[1]) )
    maze_window = display_maze(testmaze, cell_size = 40)
    bot = display_robot(maze_window)
    import time
    for i in range(5):
        time.sleep(0.3)
        bot.move_bot((0, i+1))
    maze_window.get_window().exitonclick() # Draw maze then exit on click