import os
from math import sin, radians, degrees, copysign
import math
import time
import pygame
from pygame.math import Vector2

pygame.init()

SC_Height = 648
SC_Width = 1152






class car:

    def __init__(self,x,y,angle,identity,length =4, maxx_acc = 5, Max_steer = 3):#max accelartion if 5 meters per second per second.
        self.id = str(identity)
        self.position = Vector2(x,y)
        self.velocity = Vector2(0.0,0.0)
        self.angle = angle ## angle das car
        self.img = pygame.image.load('car_3232.png')
        self.chas_length = length ## length fo cahsses in meters
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
        self.previous = 0
        self.alive = True
        self.mask = None
        self.mask_center = None
        self.traces = {'left':[],'right':[],'middle':[]}
        self.traces_length = {'left': [], 'right': [], 'middle': []}
        self.outline = None

    def draw(self):
        rotated_image = pygame.transform.rotate(self.img, (360-self.angle))
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.position[1], self.position[0])).center)  ## make it rotate at the center not at point 0,0
        #win.blit(rotated_image, new_rect.topleft)
        windo.blit(rotated_image,new_rect.topleft)

    ## start defining here for checkpoinsts
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
                     self.checkpoint_duration += 1
                     #print(increase)
                     if increase > 0:
                         self.fitness += increase
        if increase > 0:
            self.previous = list(self.position).copy()


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

            center = [0,0]
            trace = center.copy()
            trace[0] -= 16 + ton
            self.traces['middle'].append(trace)



            trace_left = center.copy()
            trace_left[0] -= 16 + ton
            self.traces['left'].append(trace_left)


            trace_right = center.copy()
            trace_right[0] -= 16 + ton
            self.traces['right'].append(trace_right)




    def update_trace(self,borders,dt):
        l = r = m = True
        for i in range(0, len(self.traces['middle'])):

            if l:
                left = self.traces['left'][i] + self.mask_center
                left_twist = rotate_vector((self.mask_center[0], self.mask_center[1]), left,
                                           radians(self.angle) - radians(125), dt)
                pygame.draw.circle(windo, (0, 200, 0), left_twist, 1)
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
                pygame.draw.circle(windo, (0, 200, 0), right_twist, 1)
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
                pygame.draw.circle(windo, (0, 200, 0), middle_twist, 1)

                if borders.get_at(middle_twist) == 1:
                    m = False
                    self.traces_length['middle'] = i

        if l == True:
            self.traces_length['left'] = len(self.traces['middle'])

        if r == True:
            self.traces_length['right'] = len(self.traces['middle'])

        if m == True:
            self.traces_length['middle'] = len(self.traces['middle'])



    def colision(self, mask, dt):
        run = True
        message = False
        self.mask_center += self.velocity.rotate(-self.angle) * dt
        new_grens = []

        for j in self.outline:
            vectored = Vector2(j[0], j[1])
            vectored += self.velocity.rotate(-self.angle) * dt

            new_grens.append(vectored)
        for point in new_grens:
            xeta = point[0] + start_x
            yeta = point[1] + start_y
            posit = rotate_vector(self.mask_center, (xeta, yeta), radians(self.angle), dt)
            pygame.draw.circle(windo, (0, 0, 255), (posit[0], posit[1]), 1)

        pygame.draw.circle(windo, (0, 0, 255), (posit[0], posit[1]), 1)
        print('############################')
        print(self.id)
        print('the position')
        print(self.angle)
        print(self.mask_center)
        print((xeta, yeta))
        print(self.position)
        print(posit)
        print(self.outline[1])
        print(vectored)
        if mask.get_at(posit) == 1:
            message = True
        if message:
            self.alive = False
            self.fitness -= 50
            print('booooo')
        self.outline = new_grens

        return (run)




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




windo = pygame.display.set_mode((SC_Width,SC_Height))

windo.fill((0,0,0))


start_x = 500
start_y = 200

collection = {}
nr_of_cars = 0


background = pygame.image.load('background 2.png')
borderings = pygame.image.load('background 3.png')
masks = pygame.mask.from_surface(borderings)
checkpoints = [[300,'vert','lower'],[700,'vert','lower'],[400,'horz','right'],[700,'vert','upper'],[300,'vert','upper'],[250,'horz','left']]

for carrs in range(0,(nr_of_cars + 1)):

    collection[str(carrs)] = car(start_x,start_y,90, carrs)
    collection[str(carrs)].previous = [start_x-1,start_y]
    collection[str(carrs)].draw()
    collection[str(carrs)].set_mask()
    collection[str(carrs)].set_traces()


pygame.display.update()



def run(config):


    run = True
    clock = pygame.time.Clock()


    while run:
        dt = clock.get_time()/100

        windo.blit(background, [0, 0])
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                run = False

        pressed = pygame.key.get_pressed()

        for turn in collection:


            collection[turn].update(dt)
            run = collection[turn].colision(masks,dt)

            collection[turn].checkpoint_check(checkpoints)
            collection[turn].update_trace(masks,dt)

            if pressed[pygame.K_DOWN]:

                if collection[turn].velocity.x < 0:
                    collection[turn].acceleration = collection[turn].brake_deceleration
                else:
                    collection[turn].acceleration += 10* dt
            elif pressed[pygame.K_UP]:

                if collection[turn].velocity.x > 0:
                    collection[turn].acceleration = -collection[turn].brake_deceleration
                else:
                    collection[turn].acceleration -= 10 * dt
            elif pressed[pygame.K_SPACE]:
                if collection[turn].velocity.x != 0:
                    collection[turn].acceleration = copysign(collection[turn].max_acceleration, -collection[turn].velocity.x)
            else:
                if collection[turn].velocity.x != 0:
                    collection[turn].acceleration = -copysign(collection[turn].free_deceleration, collection[turn].velocity.x)
                else:
                    collection[turn].acceleration = 0

                    collection[turn].acceleration = max(-collection[turn].max_acceleration, min(collection[turn].acceleration, collection[turn].max_acceleration))

            if pressed[pygame.K_RIGHT]:
                collection[turn].steering -= 1 * dt
            elif pressed[pygame.K_LEFT]:
                collection[turn].steering += 1 * dt
            else:
                collection[turn].steering = 0
                collection[turn].steering = max(-collection[turn].max_steering, min(collection[turn].steering, collection[turn].max_steering))

            collection[turn].draw()


            trace_middle = 0
            trace_left = 0
            trace_right = 0

            distance_left = round(collection[turn].traces_length['left'],0)
            distance_middle = round(collection[turn].traces_length['middle'],0)
            distance_right = round(collection[turn].traces_length['right'],0)


        ## render the distances on screen
        font = pygame.font.SysFont("arial", 16)
        text = font.render("coordinates (" + str(distance_left) + ', ' + str(distance_middle) + ', ' + str(distance_right)+')', True, (255, 255, 255))
        windo.blit(text,(5// 2, 5// 2))
        text2 = font.render(str(collection[turn].checkpoint_duration), True,(255, 255, 255))
        windo.blit(text2, (20 // 2, 50 // 2))
        ##text3 = font.render(str(mercedes.fitness), True, (0, 128, 0))
        ##windo.blit(text3, (20 // 2, 95 // 2))


        #### render the check points

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


        pygame.display.update()
        clock.tick()

        if pressed[pygame.K_SPACE]:
            position=pygame.mouse.get_pos()
            print(position)

    time.sleep(4)
    windo.fill((0,0,0))
    time.sleep(5)




if __name__=='__main__':
    local_dir = os.path.dirname(__file__) ## gives local directory
    config_path = os.path.join(local_dir,'neat_conf.txt')
    run(config_path)