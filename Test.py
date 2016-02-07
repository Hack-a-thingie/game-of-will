import math
import pygame

# Initializes the pygame library

# Color definition
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Hexagon(object):
    radius = 50
    offset = 100

    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.x_pixel=self.offset+3/2*self.radius*self.col
        self.y_pixel=self.offset+math.sqrt(3)/2*self.radius*self.row

    def axial(self):
        self.hex_z=self.row-((self.col-self.col%2))/2
        self.hex_x=self.col

    def cube(self):
        self.cube_z=self.row-((self.col-self.col%2))/2
        self.cube_x=self.col
        self.cube_y=-self.cube_x-self.cube_z

class hexgrid(object):

    def __init__(self):
        self.hexlistname= ["hex"+ str(x) + '_' + str(y) for x in range(15) for y in range(10)]
        self.hexdict={}
        for k in self.hexlistname:
            self.ksplit=k.split("hex")[1]
            self.col=self.ksplit.split('_')[0]
            self.row=self.ksplit.split('_')[1]
            self.hexdict[k]=Hexagon(int(self.col),int(self.row))

    def draw_hexgrid(self):
        for a in hexgrid1.hexdict:


