import math
import pygame

# Initializes the pygame library
pygame.init()

# Color definition
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Hexagon(object):

    def __init__(self, col, row, radius, offset_x,offset_y):
        self.radius = radius
    	self.offsetx = offset_x
    	self.offsety = offset_y
        self.col = col
        self.row = row
        self.x_pixel=self.offsetx+1.5*self.radius*self.col
        if self.col%2==1:
            self.y_pixel=self.offsety+math.sqrt(3)*self.radius*self.row+math.sqrt(3)/2*self.radius
        else:
            self.y_pixel=self.offsety+math.sqrt(3)*self.radius*self.row

    def axial(self):
        self.hex_z=self.row-((self.col-self.col%2))/2
        self.hex_x=self.col

    def cube(self):
        self.cube_z=self.row-((self.col-self.col%2))/2
        self.cube_x=self.col
        self.cube_y=-self.cube_x-self.cube_z


    def vertices(self):
        self.vertices_points = []
        for ind in range(6):
            angle_deg = 60*ind
            angle_rad = math.pi/180*angle_deg
            self.vertex_x = self.x_pixel+self.radius*math.cos(angle_rad)
            self.vertex_y = self.y_pixel+self.radius*math.sin(angle_rad)
            self.vertices_points.append([self.vertex_x, self.vertex_y])

class Hexgrid(object):

    def __init__(self,size,offset_x,offset_y,screen):
        self.hexlistname= ["hex"+ str(x) + '_' + str(y) for x in range(15) for y in range(11)]
        self.hexdict={}
        self.size=size
    	self.offsetx=offset_x
    	self.offsety=offset_y
    	self.screen = screen
        for k in self.hexlistname:
            self.ksplit=k.split("hex")[1]
            self.col=self.ksplit.split('_')[0]
            self.row=self.ksplit.split('_')[1]
        
            
            if int(self.row) == 10 and int(self.col)%2==1:
                pass
            else:
                self.hexdict[k]=Hexagon(int(self.col),int(self.row),self.size,self.offsetx,self.offsety)

    def draw_hexgrid(self):
        for a in self.hexdict:
            self.hexdict[a].vertices()
            self.plist=self.hexdict[a].vertices_points
            pygame.draw.polygon(self.screen, GREEN, self.plist, 0)
            pygame.draw.aalines(self.screen, BLACK, True, self.plist, True)

    def cube2hex(self,cube_coord):
        self.hex_x=cube_coord[0]
        self.hex_z=cube_coord[2]
        return self.hex_x,self.hex_z

    def hex2cube(self,hex_x, hex_z):
        self.cube_x = hex_x
        self.cube_y = -hex_x -hex_z
        self.cube_z = hex_z
        self.cube_coords= [self.cube_x,self.cube_y,self.cube_z]
        return self.cube_coords

    def pixel_to_hex(self,x_pixel, y_pixel):
        self.x_pixel=x_pixel-self.offsetx
        self.y_pixel=y_pixel-self.offsety

        self.q = (self.x_pixel*2.0/3.0)/self.size
        self.r =( (-self.x_pixel/3.0)+(math.sqrt(3)/3.0)*self.y_pixel)/self.size
        self.hex_frac= [self.q,self.r]
        return self.hex_frac

    def hex_round(self,x,y):
        return self.cube2hex(self.cube_round(self.hex2cube(self.pixel_to_hex(x,y)[0],self.pixel_to_hex(x,y)[1])))


    def cube_round(self,frac_cube):
        self.h = frac_cube
        self.rx = round(self.h[0])
        self.ry = round(self.h[1])
        self.rz = round(self.h[2])

        self.x_diff = abs(self.rx - self.h[0])
        self.y_diff = abs(self.ry - self.h[1])
        self.z_diff = abs(self.rz - self.h[2])

        if self.x_diff > self.y_diff and self.x_diff > self.z_diff:
            self.rx = -self.ry-self.rz
        elif self.y_diff > self.z_diff:
            self.ry = -self.rx-self.rz
        else:
            self.rz = -self.rx-self.ry
        self.cubes=(self.rx, self.ry, self.rz)
        return self.cubes