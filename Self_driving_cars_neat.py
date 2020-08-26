import os
from math import sin, radians, degrees, copysign
import math
import time
import pygame
from pygame.math import Vector2
import neat
import numpy as np
pygame.init()

SC_Height = 648
SC_Width = 1152


Generation_counter = -1




class car:

    def __init__(self,x,y,angle,identity,length =4, maxx_acc = 5, Max_steer = 3):#max accelartion if 5 meters per second per second.
        self.id = str(identity)
        self.position = Vector2(x,y)
        self.velocity = Vector2(0.0,0.0)
        self.angle = angle ## angle das car
        self.img = pygame.image.load('car_3232.png')
        self.chas_length = length ## length of chasses in meters
        self.max_acceleration = maxx_acc   #Maximum value of acceleration, in meters per second squared
        self.max_steering = Max_steer
        self.acceleration = 0.0
        self.steering = 0.0
        self.max_velocity = 30
        self.brake_deceleration = 5
        self.free_deceleration = 3
        self.length = length
        self.checkpoint = 0
        self.checkpoint_duration = 0
        self.fitness = 0
        self.previous = 0 # Determines previous position (dt-1)
        self.alive = True
        self.mask = None # Mask around car for collision detection with background
        self.mask_center = None
        self.traces = {'left':[],'right':[],'middle':[]} # The vision traces
        self.traces_length = {'left': [], 'right': [], 'middle': []}
        self.outline = None
        self.scrap_potential = 0

    def draw(self,displaying):
        rotated_image = pygame.transform.rotate(self.img, (360-self.angle))
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.position[1], self.position[0])).center)  ## make it rotate at the center not at point 0,0
        #win.blit(rotated_image, new_rect.topleft)
        displaying.blit(rotated_image,new_rect.topleft)

    # Update current checkpoint objective if previous checkbpoint has been passed
    def checkpoint_check(self,checkpoints):
        if checkpoints[self.checkpoint][1] == 'horz':
            if checkpoints[self.checkpoint][2] == 'left':
                if self.position[0] > checkpoints[self.checkpoint][0]:
                    self.checkpoint = 0
                    increase = 0
                    self.checkpoint_duration = 0
                else:
                     increase =  self.position[0] - self.previous[0]
                     self.checkpoint_duration += 1
                     if increase > 0:
                         self.fitness += increase
            if checkpoints[self.checkpoint][2] == 'right':
                if self.position[0] < checkpoints[self.checkpoint][0]:
                    self.checkpoint += 1
                    increase = 0
                    self.checkpoint_duration = 0
                else:
                     increase = self.previous[0] - self.position[0]
                     self.checkpoint_duration += 1
                     if increase > 0:
                         self.fitness += increase
        if checkpoints[self.checkpoint][1] == 'vert':
            if checkpoints[self.checkpoint][2] == 'upper':
                if self.position[1] < checkpoints[self.checkpoint][0]:
                    self.checkpoint += 1
                    increase = 0
                    self.checkpoint_duration = 0
                else:
                     increase =  self.previous[1] - self.position[1]
                     self.checkpoint_duration += 1
                     if increase > 0:
                         self.fitness += increase
            if checkpoints[self.checkpoint][2] == 'lower':
                if self.position[1] > checkpoints[self.checkpoint][0]:
                    self.checkpoint += 1
                    increase = 0
                    self.checkpoint_duration = 0
                else:
                     increase =  self.position[1] - self.previous[1]
                     #print(increase)
                     self.checkpoint_duration += 1
                     if increase > 0:
                         self.fitness += increase
        if abs(self.position[0] - self.previous[0]) < 2 and abs(self.position[1] - self.previous[1]) < 2:
            self.scrap_potential += 1
            if self.scrap_potential == 20:
                self.alive = False
                self.fitness -= 50
        else:
            self.scrap_potential = 0

        if self.checkpoint_duration > 400:
            self.alive = False
            self.fitness -= 100000


        self.previous = list(self.position).copy()

    #Update position based on speed and direction.

    def update(self, dt):

        self.velocity += (self.acceleration * dt, 0) ## for linear movement. we will take a displacment pointand increase it times the accelaration
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))
        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0


        self.angle += degrees(angular_velocity) * dt
        if self.angle < 0:
            self.angle = 359.9999
        elif self.angle > 360:
            self.angle = 0

        self.position += self.velocity.rotate(-self.angle) * dt

    def set_mask(self):

        self.mask = pygame.mask.from_surface(self.img)
        self.mask_center = list(self.mask.centroid())
        self.mask_center[0] += self.position[0]
        self.mask_center[1] += self.position[1]
        self.outline = self.mask.outline()

    def set_traces(self):
        for ton in range(0, 400, 20):
            center = [0, 0]
            trace = center.copy()
            trace[0] -= 16 + ton
            self.traces['middle'].append(trace)

            trace_left = center.copy()
            trace_left[0] -= 16 + ton
            self.traces['left'].append(trace_left)

            trace_right = center.copy()
            trace_right[0] -= 16 + ton
            self.traces['right'].append(trace_right)



    #Updates the positions of the 3 vision traces

    def update_trace(self,borders,dt,display):
        l = r = m = True
        for i in range(0, len(self.traces['middle'])):

            if l:
                left = self.traces['left'][i] + self.mask_center
                left_twist = rotate_vector((self.mask_center[0], self.mask_center[1]), left,
                                           radians(self.angle) - radians(125), dt)
                pygame.draw.circle(display, (0, 200, 0), left_twist, 1)
                if left_twist[0] < SC_Width and left_twist[1] < SC_Height and left_twist[0] > 0 and left_twist[1] > 0:
                    if borders.get_at(left_twist) == 1:
                        l = False
                        self.traces_length['left'] = i
                else:
                    l = False
                    self.traces_length['left'] = i
            if r:
                right = self.traces['right'][i] + self.mask_center
                right_twist = rotate_vector((self.mask_center[0], self.mask_center[1]), right,
                                            radians(self.angle) - radians(65), dt)
                pygame.draw.circle(display, (0, 200, 0), right_twist, 1)
                if right_twist[0] < SC_Width and right_twist[1] < SC_Height and right_twist[0] > 0 and right_twist[
                    1] > 0:
                    if borders.get_at(right_twist) == 1:
                        r = False
                        self.traces_length['right'] = i
                else:
                    r = False
                    self.traces_length['right'] = i

            if m:
                middle = self.traces['middle'][i] + self.mask_center
                middle_twist = rotate_vector((self.mask_center[0], self.mask_center[1]), middle,
                                             radians(self.angle) - radians(90), dt)
                pygame.draw.circle(display, (0, 200, 0), middle_twist, 1)

                if borders.get_at(middle_twist) == 1:
                    m = False
                    self.traces_length['middle'] = i

        #In case a trace does not overlap with background boundaries

        if l == True:
            self.traces_length['left'] = len(self.traces['middle'])

        if r == True:
            self.traces_length['right'] = len(self.traces['middle'])

        if m == True:
            self.traces_length['middle'] = len(self.traces['middle'])


    # If the mask of the car collides with the background boundary it will be removed from the current generation and
    # the current fitness value is saved

    def colision(self, mask, dt,display,starting_point):

        message = False
        self.mask_center += self.velocity.rotate(-self.angle) * dt
        new_grens = []



        for j in self.outline:
            vectored = Vector2(j[0], j[1])
            vectored += self.velocity.rotate(-self.angle) * dt

            new_grens.append(vectored)



        for point in new_grens:
            xeta = point[0] + starting_point[0]
            yeta = point[1] + starting_point[1]
            posit = rotate_vector(self.mask_center, (xeta, yeta), radians(self.angle), dt)
            #pygame.draw.circle(display, (0, 0, 255), (posit[0], posit[1]), 1)


            if mask.get_at(posit) == 1:
                message = True
                #print('hold up')

        if message:
            self.alive = False
            self.fitness -= 50
        self.outline = new_grens

        #for ui in self.outline:
         #   pygame.draw.circle(display, (0, 0, 255), (ui[0], ui[1]), 1)

        return(not self.alive)



# Helper function for orienting car based on steering input

def rotate_vector(origin, point, angle,dt):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    angle += radians(90)
    oy, ox = origin

    py, px = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return (int(round(qx,0)), int(round(qy,0)))










# The running program starts here

def main(genomes,config):
    nets = []  ## nets for each car
    ge = []
    cars = []

    windo = pygame.display.set_mode((SC_Width, SC_Height))


    windo.fill((0, 0, 0))

    start_x = 530
    start_y = 200

    collection = {}
    nr_of_cars = 49

    background = pygame.image.load('New_background.png')
    borderings = pygame.image.load('New_background_transparent_set.png')
    masks = pygame.mask.from_surface(borderings)
    checkpoints = [[300, 'vert', 'lower'], [700, 'vert', 'lower'], [400, 'horz', 'right'], [700, 'vert', 'upper'],
                   [300, 'vert', 'upper'], [250, 'horz', 'left']]



    name_car = 0

    # genome is a tupple with first and index which is not needed so create bin _
    for _, g in genomes:  # For each car set up a nn and a genome
        name_car += 1
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        mercedes = car(start_x,start_y,90, name_car)
        mercedes.previous = [start_x-1,start_y]
        mercedes.draw(windo)
        mercedes.set_mask()
        mercedes.set_traces()
        cars.append(mercedes)
        g.fitness = 0  # This will give a fitness value after we update it and will be returned to the neat program
        ge.append(g)
    pygame.display.update()


    run = True
    clock = pygame.time.Clock()

    removed = []
    removed_nets = []

    global Generation_counter
    Generation_counter += 1

    while run:


        if len(cars)==0:
            run = False
            print(removed[-1].fitness)
            print(removed[-1].scrap_potential)
            time.sleep(1)
            break

        dt = clock.get_time()/100

        windo.blit(background, [0, 0])
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                run = False

        #Cars which collided with the backgound or were to slow the previous cycle are removed here
        # Otherwise, the car movement is updataed

        to_remove = []
        for x, carr in enumerate(cars):

            #output is a list
            carr.update(dt)
            if carr.colision(masks,dt,windo,(start_x,start_y)):
                to_remove.append(x)

            carr.checkpoint_check(checkpoints)
            carr.update_trace(masks, dt, windo)


            ge[x].fitness = carr.fitness / 1000  # fitness for staying alive
            output = nets[x].activate((carr.traces_length['left'], carr.traces_length['right'],
                                       carr.traces_length['middle'], carr.velocity[0], carr.velocity[1], carr.steering))

            #print(output)


            # going forward
            if carr.velocity.x > 0:
                carr.acceleration = -carr.brake_deceleration
            else:
                carr.acceleration -= 10 * dt

            # Use ouput NN created by neat to determine steering input

            if output[0] > 5:
                #right
                carr.steering -= 1* dt

            if output[1] > 5:
                #left
                carr.steering += 1* dt

            if output[2] > 1:
                #break
                if carr.velocity.x != 0:
                    carr.acceleration = copysign(carr.max_acceleration, -carr.velocity.x)

            if not output[0] > 0.5 or not output[1] > 0.5:
                carr.steering = 0
                carr.steering = max(-carr.max_steering,
                                                min(carr.steering, carr.max_steering))

            carr.draw(windo)

        # Remove colided cars

        if len(to_remove) > 0:

            dup_list = []
            dup_nets = []
            ge_dup = []
            for crashed in range(0,len(cars)):
                if crashed not in to_remove:
                    dup_list.append(cars[crashed])
                    dup_nets.append(nets[crashed])
                    ge_dup.append(ge[crashed])
                else:
                    #print('removed' + str(crashed))
                    removed.append(cars[crashed])
                    removed_nets.append(nets[crashed])
                    #print(crashed)

            cars = dup_list
            nets = dup_nets
            ge = ge_dup

            trace_middle = 0
            trace_left = 0
            trace_right = 0

        # distance_left = carr.traces_length['left']
        # distance_middle = carr.traces_length['middle']
        # distance_right = carr.traces_length['right']

        # render the distances on screen (only useful when generation size = 1)
        font = pygame.font.SysFont("arial", 30)
        #text = font.render("coordinates (" + str(distance_left) + ', ' + str(distance_middle) + ', ' + str(distance_right)+')', True, (0, 128, 0))

        #Generation counter
        text = font.render("Generation nr: " + str(Generation_counter), True, (255, 255, 255))
        windo.blit(text,(round(SC_Width//5*3+15,0),40))
        ##text2 = font.render(str(mercedes.checkpoint), True,(0, 128, 0))
        ##windo.blit(text2, (20 // 2, 50 // 2))
        ##text3 = font.render(str(mercedes.fitness), True, (0, 128, 0))
        ##windo.blit(text3, (20 // 2, 95 // 2))



        ## Draw the check points


        for checky in checkpoints:
            if checky[1] == 'vert':
                if checky[2] == 'lower':
                    pygame.draw.line(windo,(0,0,0),(checky[0],500),(checky[0],SC_Height))
                elif checky[2] == 'upper':
                    pygame.draw.line(windo, (0, 0, 0), (checky[0],0), (checky[0],500))
                else:
                    time.sleep(40)
                    print('fu')
            elif checky[1] == 'horz':
                if checky[2] == 'left':
                    pygame.draw.line(windo, (0, 0, 0), (0,checky[0]), (300,checky[0]))
                elif checky[2] == 'right':
                    pygame.draw.line(windo, (0, 0, 0), (600,checky[0]), (SC_Width,checky[0]))
                else:
                    time.sleep(40)
                    print('fu')

        #print(carr.traces_length)

        pygame.display.update()
        clock.tick()
        pressed=pygame.key.get_pressed()

        if pressed[pygame.K_SPACE]:
            position=pygame.mouse.get_pos()
            print(position)




#Neat setup

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    p = neat.Population(config)  ## Get from the configruation file

    # p.add_reporter(neat.StdOutReporter(True))
    # stats = neat.StatisticsReporter()
    # p.add_reporter(stats)
    # Add statistics on populations

    # to determine the fitness of the algorthim is the distance of the cars in a game so we pass it the game with
    # the current genome of the game

    winner = p.run(main, 500)  # Determine fitness of each genome




if __name__=='__main__':
    local_dir = os.path.dirname(__file__) ## gives local directory
    config_path = os.path.join(local_dir,'neat_conf.txt')
    run(config_path)