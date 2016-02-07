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


class Hexagon:

    radius = 50
    offset=100

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

<<<<<<< HEAD
    def __init__(self, col, row):
        self.x = row
        self.y = col

=======
>>>>>>> 0d3bac41a1fab61e98e5e2e23fba1c7030f8dfd5

    def vertices(self):

        for ind in range(6):
            angle_deg = 60 * ind
<<<<<<< HEAD
            angle_rad = math.pi / 180 * angle_deg
            self.point_x = self.x_pixel + self.radius * math.cos(angle_rad)
            self.point_y = self.y_pixel + self.radius * math.sin(angle_rad)
=======
            angle_rad e= math.pi / 180 * angle_deg
            point_x = self.x_pixel + self.radius * math.cos(angle_rad)
            point_y = self.y_pixel + self.radius * math.sin(angle_rad)
>>>>>>> 0d3bac41a1fab61e98e5e2e23fba1c7030f8dfd5
            self.vertex

    def hex_2_pix(self):
        self.y_pixel = self.offset + 3/2*self.radius*self.x
        self.x_pixel = self.offset + math.sqrt(3)*self.radius*self.x

# Set the height and width of the screen
scr_height = 1000
scr_width = 1000
size = [scr_width, scr_height]
screen = pygame.display.set_mode(size)

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()

while not done:

    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

    # All drawing code happens after the for loop and but
    # inside the main while done==False loop.

    # Clear the screen and set the screen background
    screen.fill(WHITE)
    grid_size = 15
    grid_height = 10
    d = 30  # Hexagon's size
    shift = 100
    start = d + shift
    hex_h = d * 2  # Hexagon's height
    hex_w = hex_h * math.sqrt(3) * 0.5  # Hexagon's width
    for col in range(0, grid_size):
        if col < grid_size * 0.5:
            pygame.draw.aalines(screen, BLACK, True,
                                hex_point([start + hex_h * col * 1.5, start + grid_height * hex_w], d), True)
        for row in range(0, grid_height):
            if col % 2 == 1:
                pygame.draw.aalines(screen, BLACK, True,
                                    hex_point([start + col * hex_h * 0.75, start + (row + 0.5) * hex_w], d), True)
            else:
                pygame.draw.aalines(screen, BLACK, True,
                                    hex_point([start + col * hex_h * 0.75, start + row * hex_w], d), True)
            cubcoord = cart2cube(col, row)

    # This MUST happen after all the other drawing commands.
    pygame.display.flip()

    # Be IDLE friendly

    # x_mouse,y_mouse=pygame.mouse.get_pos()
