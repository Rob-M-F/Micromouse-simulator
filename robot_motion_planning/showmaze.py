from maze import Maze
import turtle
import sys

class display_maze(object):
    def __init__(self, testmaze, cell_size = 20):
        self.maze = testmaze
        self.window = turtle.Screen()
        self.wally = turtle.Turtle()
        self.wally.speed(0)
        self.wally.hideturtle()
        self.wally.penup()
        self.sq_size = cell_size
        self.origin = self.maze.dim * self.sq_size / -2
        self.draw_maze()

    def get_window(self):
        return self.window

    def draw_maze(self):
        '''
        This function uses Python's turtle library to draw a picture of the maze
        given as an argument when running the script.
        '''
        # iterate through squares one by one to decide where to draw walls
        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                if not self.maze.is_permissible([x,y], 'up'):
                    self.wally.goto(self.origin + self.sq_size * x, self.origin + self.sq_size * (y+1))
                    self.wally.setheading(0)
                    self.wally.pendown()
                    self.wally.forward(self.sq_size)
                    self.wally.penup()

                if not self.maze.is_permissible([x,y], 'right'):
                    self.wally.goto(self.origin + self.sq_size * (x+1), self.origin + self.sq_size * y)
                    self.wally.setheading(90)
                    self.wally.pendown()
                    self.wally.forward(self.sq_size)
                    self.wally.penup()

                # only check bottom wall if on lowest row
                if y == 0 and not self.maze.is_permissible([x,y], 'down'):
                    self.wally.goto(self.origin + self.sq_size * x, self.origin)
                    self.wally.setheading(0)
                    self.wally.pendown()
                    self.wally.forward(self.sq_size)
                    self.wally.penup()

                # only check left wall if on leftmost column
                if x == 0 and not self.maze.is_permissible([x,y], 'left'):
                    self.wally.goto(self.origin, self.origin + self.sq_size * y)
                    self.wally.setheading(90)
                    self.wally.pendown()
                    self.wally.forward(self.sq_size)
                    self.wally.penup()

if __name__ == '__main__':
    testmaze = Maze( str(sys.argv[1]) )
    maze_window = display_maze(testmaze).get_window().exitonclick() # Draw maze then exit on click