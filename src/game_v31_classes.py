#########################################
# File Name: game_v31_classes.py
# Description: Classes for rocket simulator
# Author: Suyu Chen
# Date: 06/03/2020
#########################################
import pygame
from random import randint
from math import sqrt, degrees, radians, sin, cos, atan2, pi

#-----------------------------#
# Constants                   #
#-----------------------------#
DEFAULT_RES = (800,600)

BLACK   = (  0,  0,  0)
WHITE   = (255,255,255)
GREY    = (143,143,143)
RED     = (255,  0,  0)
GREEN   = (  0,255,  0)
BLUE    = (  0,  0,255)
YELLOW  = (255,255,  0)
MAGENTA = (255,  0,255)
CYAN    = (  0,255,255)
LIGHT_GREY = (200,200,200)
DARK_BLUE =  (  9, 12,189)


G = 6.674e-11 # Gravitational constant

#-----------------------------#
# Functions                   #
#-----------------------------#

def loadImg(filename, alpha=True):
    if alpha:
        return pygame.image.load("images/" + filename).convert_alpha()
    else:
        return pygame.image.load("images/" + filename).convert()

def loadSound(filename, volume):
    sound = pygame.mixer.Sound("audio/" + filename)
    sound.set_volume(volume)
    return sound

def rotate(surface,angle):
    originalRect = surface.get_rect()
    rotatedSurface = pygame.transform.rotate(surface,angle)
    rotatedRect = originalRect.copy()
    rotatedRect.center = rotatedSurface.get_rect().center
    rotatedSurface = rotatedSurface.subsurface(rotatedRect).copy()
    return rotatedSurface

def getDistance(p1,p2):
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def getDistSquared(p1, p2):
    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

def scaleSurface(surf, surfSize, screenSize, defaultScrenRes):
    wScaleFactor = surfSize[0]/sqrt(defaultScrenRes[0]*defaultScrenRes[1])
    hScaleFactor = surfSize[1]/sqrt(defaultScrenRes[0]*defaultScrenRes[1])
    scaled = pygame.transform.scale(surf, (int(sqrt(screenSize[0]*screenSize[1])*wScaleFactor),
                                           int(sqrt(screenSize[0]*screenSize[1])*hScaleFactor)))
    return scaled

def scaleMaintainAspect(surf, newW=None, newH=None, returnNewSize=False):
    aspectRatio = surf.get_width()/surf.get_height()
    if newH == None:
        newH = int(newW/aspectRatio)
    elif newW == None:
        newW = int(newH*aspectRatio)
    newSurf = pygame.transform.scale(surf, (newW, newH))
    if returnNewSize:
        return (newSurf, newW, newH)
    else:
        return newSurf

def centerHorizontally(screenW, surfaceW):
    x = round((screenW - surfaceW)/2)
    return x

#-------------------------------#
# Classes                       #
#-------------------------------#

class ScalableSurf():
    def __init__(self, surf, center=(0,0)):
        self.surf = surf
        self.surfSize = self.surf.get_size()
        self.scaledSurf = self.surf
        self.scaledRect = self.scaledSurf.get_rect()
        self.scaledRect.center = center

    def scale(self, screenSize, defaultScreenSize):
        self.scaledSurf = scaleSurface(self.surf, self.surfSize, screenSize, defaultScreenSize)
        self.scaledRect = self.scaledSurf.get_rect()

    def resize(self, center, screenSize, defaultScreenSize):
        self.scale(screenSize, defaultScreenSize)
        self.scaledRect.center = center

    def resizeFromTopLeft(self, topLeft, screenSize, defaultScreenSize):
        self.scale(screenSize, defaultScreenSize)
        self.scaledRect.topleft = topLeft
        
    def draw(self, screen):
        screen.blit(self.scaledSurf, self.scaledRect.topleft)

class ScalableText(ScalableSurf):
    def __init__(self, text, font, clr, center=(0,0)):
        ScalableSurf.__init__(self, font.render(text, 1, clr), center)

class Button():
    def __init__(self, surf, selectedSurf, center=(0,0)):
        self.surf = ScalableSurf(surf, center)
        self.selectedSurf = ScalableSurf(selectedSurf, center)
        self.selected = False

    def resize(self, center, screenSize, defaultScreenSize):
        self.surf.resize(center, screenSize, defaultScreenSize)
        self.selectedSurf.resize(center, screenSize, defaultScreenSize)

    def draw(self, screen):
        if self.selected:
            self.selectedSurf.draw(screen)
        if not self.selected:
            self.surf.draw(screen)

    def detectMouseHover(self, mousePos):
        if self.surf.scaledRect.collidepoint(mousePos):
            self.selected = True
        else:
            self.selected = False

class ImgButton(Button):
    def __init__(self, img,  center=(0,0)):
        Button.__init__(self, img, pygame.transform.scale(img, (round(img.get_width()*1.2), round(img.get_height()*1.1))), center)

##class TextButton(Button):
##    def __init__(self, text, font, clr, center=(0,0)):
##        Button.__init__(self, font.render(text, 1, clr), font.render("> " + text + " <", 1, clr), center)

class TextButton(ImgButton):
    def __init__(self, text, font, clr, center=(0,0)):
        ImgButton.__init__(self, font.render(text, 1, clr), center)

class AnimatedSprite():
    def __init__(self, spritesheetImg, cols, rows):
        self.sheet = loadImg(spritesheetImg)
        self.cols = cols
        self.rows = rows
        self.colW = self.sheet.get_width()/cols
        self.rowH = self.sheet.get_height()/rows
        self.currentCol = 0
        self.currentRow = 0
        self.currentSprite = self.sheet.subsurface((0, 0, self.colW, self.rowH))
        self.transformedCurrentSprite = self.currentSprite
        self.angle = 0
        self.finished = False

    def transform(self, camera):
        self.transformedCurrentSprite = rotate(pygame.transform.scale(self.currentSprite,
                                        (int((self.colW - 1)/camera.zoom), int((self.rowH - 1)/camera.zoom))), self.angle)
    
    def loadNextImg(self):
        self.currentCol += 1
        if self.currentCol == self.cols:
            self.currentCol = 0
            self.currentRow += 1
            if self.currentRow == self.rows:
                self.finished = True
        if not self.finished:
            self.currentSprite = self.sheet.subsurface((self.currentCol*self.colW, self.currentRow*self.rowH,
                                                        int(self.colW - 1), int(self.rowH - 1))) # -1 to account for rounding error
            
    def draw(self, surf, center, camera):
        topLeft = int(center[0] - self.colW/2), int(center[1] - self.rowH/2)
        surf.blit(self.transformedCurrentSprite, camera.worldToScreen(topLeft))       

class ExplosionSprite(AnimatedSprite):
    def __init__(self, spritesheetImg, cols, rows):
        AnimatedSprite.__init__(self, spritesheetImg, cols, rows)
        self.angle = randint(0,360)

class Camera():
    def __init__(self, x, y, w, h, zoom=1):
        self.x = x                          # x and y positions on world space
        self.y = y
        self.screenSize = (w,h)             # screen resolution
        self.worldSize = (w*zoom, h*zoom)   # size of camera on world space
        self.zoom = zoom
        self.radius = sqrt(self.worldSize[0]**2 + self.worldSize[1]**2)   # radius of circumscribed circle in world space
        self.rect = pygame.Rect((x,y), self.worldSize)    # rect on world space
        self.tether = True

    def __str__(self):
        return "x: " + str(self.x) + "\n" + \
               "y: " + str(self.y) + "\n" + \
               "screen size: " + str(self.screenSize) + "\n" + \
               "world size: " + str(self.worldSize) + "\n" + \
               "zoom: " + str(self.zoom) + "\n" + \
               "radius: " + str(self.radius) + "\n" + \
               "center: " + str(self.rect.center) + "\n" + \
               "tether: " + str(self.tether) + "\n"

    def changeZoom(self, inOrOut, mousePos):
        if not self.tether:
            oldMousePos = self.screenToWorld(mousePos)
        if inOrOut == "in" and self.zoom > 1:
            self.zoom *= 0.9
        elif inOrOut == "out" and self.zoom < 500:
            self.zoom *= 1.1
        if not self.tether:
            newMousePos = self.screenToWorld(mousePos)
            self.x += oldMousePos[0] - newMousePos[0]
            self.y += oldMousePos[1] - newMousePos[1]
        self.updateAll()
    
    def move(self, x, y):
        self.x += x*self.zoom
        self.y += y*self.zoom
        self.updateRectPos()

    def followRocket(self, rocket):
        self.x = rocket.center.x - self.worldSize[0]/2
        self.y = rocket.center.y - self.worldSize[1]/2
        self.updateRectPos()

    def resize(self, newW, newH):
        if not self.tether:
            dw, dh = newW - self.screenSize[0], newH - self.screenSize[1]
        self.screenSize = (newW, newH)
        if not self.tether:
            self.move(-dw/2,-dh/2)
        self.updateAll()
        
    def updateRectPos(self):
        self.rect.topleft = (self.x, self.y)

    def updateAll(self):
        self.worldSize = (self.screenSize[0]*self.zoom, self.screenSize[1]*self.zoom)
        self.radius = sqrt(self.worldSize[0]**2 + self.worldSize[1]**2)
        self.rect = pygame.Rect((self.x, self.y), self.worldSize)

    def worldToScreen(self,pos):
        """ Translate world space coordinates to screen space coordinates. """
        return [int((pos[0] - self.x)/self.zoom),
                int((pos[1] - self.y)/self.zoom)]

    def screenToWorld(self,pos):
        """ Translate screen space coordinates to world space coordinates. """
        return [pos[0]*self.zoom + self.x, pos[1]*self.zoom + self.y]

    def circleInFrame(self, pos, r):
        """ Check if a circle is visible in the frame """
        if getDistance(pos, self.rect.center) <= self.radius + r:
            return True
        else:
            return False

    def rectInFrame(self,center,size):
        topLeft = (center[0] - size[0]/2, center[1] - size[1]/2)
        if self.rect.colliderect(pygame.Rect(topLeft,size)):
            return True
        else:
            return False

class Planet():
    def __init__(self, name, x, y, r, mass, clr):
        self.name = name
        self.pos = (x,y)
        self.r = r
        self.mass = mass
        self.clr = clr

    def __str__(self):
        return self.name + "\n" + \
               "position: " + str(self.pos) + "\n" + \
               "radius: " + str(self.r) + "\n" + \
               "mass: " + str(self.mass) + "\n"

    def draw(self, surface, camera):
        if camera.circleInFrame(self.pos, self.r):
            pygame.draw.circle(surface, self.clr, camera.worldToScreen(self.pos),
                               int(self.r/camera.zoom))

    def getGravityVec(self, rocket):
        if self == rocket.nearestPlanet and rocket.altitude <= 0:
            return pygame.Vector2(0,0)
        else:
            dSquared = getDistSquared(rocket.center,self.pos)
            g = G*self.mass/dSquared
            vec = pygame.Vector2(self.pos - rocket.center)
            vec.scale_to_length(g)
            return vec

class Path():
    def __init__(self, clr):
        self.clr = clr
        self.points = []
        
    def extend(self, point):
        self.points.append(point)
        
    def draw(self, surface, camera):
        if len(self.points) > 1:
            destPoints = []
            for point in self.points:
                destPoints.append(camera.worldToScreen(point))
            pygame.draw.lines(surface, self.clr, False, destPoints)

class Rocket():
    def __init__(self, surfSide, rocketData, startPlanet, planets):   # rocketData format: [image, height, mass, max thrust]      
        self.surfSide = surfSide        # width/height of rocket surface 
        self.surf = pygame.Surface((surfSide,surfSide), pygame.SRCALPHA)    # original rocket surface

        try:
            scaledImg, self.w, self.h = scaleMaintainAspect(rocketData[0], newH=rocketData[1], returnNewSize=True)
            self.surf.blit(scaledImg, (int((self.surfSide - self.w)/2), int((self.surfSide - self.h)/2)))
            self.surf = rotate(self.surf, -90)
        except:
            self.w = 20
            self.h = 150
            pygame.draw.rect(self.surf, RED, (int((self.surfSide - self.h)/2),
                                              int((self.surfSide - self.w)/2), self.h, self.w))  # rocket is drawn sideways, rotated in place after

        self.transformedSurf = self.surf
       
        self.center = pygame.Vector2(int(startPlanet.pos[0]),   # center in world space
                                     int(startPlanet.pos[1] - startPlanet.r - self.h/2)) 

        self.corners = []
        self.angle = 90     # in degrees from positive x axis
        
        self.mass = rocketData[2]         # all masses in kg
        self.fuelPercent = 100
        self.maxThrust = rocketData[3]      # in N
        self.throttle = 0           
        self.thrust = self.throttle*self.maxThrust  
        self.thrustA = pygame.Vector2() # instantaneous acceleration due to thrust in m/s^2

        self.v = pygame.Vector2()       # instantaneous velocity in m/s
        self.angV = 0           

        self.gravityVectors = []
        for planet in planets:
            self.gravityVectors.append(pygame.Vector2())

        self.nearestPlanet = startPlanet
        self.altitude = 0
        self.angFromPlanet = 90     # relate to nearest planet
        self.vToPlanet = 0
        self.vTanPlanet = 0

        self.path = Path(LIGHT_GREY)     

        self.crashed = False
        self.launched = False

    def __str__(self):
        rocketStr = "center (x,y): " + str(self.center) + "\n" + \
                    "altitude: " + str(self.altitude) + "\n" + \
                    "crashed: " + str(self.crashed) + "\n" + \
                    "nearest planet: " + str(self.nearestPlanet.name) + "\n" + \
                    "angle from nearest planet (deg): " + str(self.angFromPlanet) + "\n" + \
                    "angle (deg): " + str(self.angle) + "\n" + \
                    "mass (kg): " + str(self.mass) + "\n" + \
                    "fuel % left: " + str(self.fuelPercent) + "\n" + \
                    "throttle (0 to 1):" + str(self.throttle) + "\n" + \
                    "thrust (int): " + str(self.thrust) + "\n" + \
                    "thrust acceleration (polar): " + str(self.thrustA.as_polar()) + "\n" + \
                    "velocity (polar): " + str(self.v.as_polar()) + "\n" + \
                    "velocity towards nearest planet: " + str(self.vToPlanet) + "\n" + \
                    "velocity tangent to nearest planet: " + str(self.vTanPlanet) + "\n" + \
                    "angular velocity (int): " + str(self.angV) + "\n" + \
                    "fuel %: " + str(self.fuelPercent) + "\n"

                
        for vec in self.gravityVectors:
            rocketStr += "gravity acceleration: " + str(vec.as_polar()) + "\n"
        return rocketStr

    def draw(self, surface, camera):
        if camera.rectInFrame(self.center, (self.surfSide, self.surfSide)) and not self.crashed:
            scaledSide = int(self.surfSide/camera.zoom)
            if scaledSide < 30:
                scaledSide = 30
                destCenter = camera.worldToScreen(self.center)
                destPos = destCenter[0] - 15, destCenter[1] - 15
            else:
                destPos = camera.worldToScreen((self.center.x - self.surfSide/2,
                                            self.center.y - self.surfSide/2))
            scaled = pygame.transform.scale(self.surf, (scaledSide, scaledSide))
            self.transformedSurf = rotate(scaled, self.angle)
            surface.blit(self.transformedSurf, destPos)

    def drawDevInfo(self, surface, camera):
        pygame.draw.line(surface, GREEN, camera.worldToScreen(self.center),
                         camera.worldToScreen(self.center + self.v*2), 1) # velocity vector
        pygame.draw.line(surface, CYAN, camera.worldToScreen(self.center),
                         camera.worldToScreen(self.center + self.thrustA*2), 1) # thrust vector
        for vec in self.gravityVectors:
            pygame.draw.line(surface, YELLOW, camera.worldToScreen(self.center),
                             camera.worldToScreen(self.center + vec*2), 1) # all gravity vectors           
        for corner in self.corners:
            pygame.draw.circle(surface, CYAN, camera.worldToScreen(corner), 3)
        pygame.draw.circle(self.surf, GREEN, (int(self.surfSide/2 + self.h/2),
                                              int(self.surfSide/2)), 5)   # top of rocket
        pygame.draw.circle(surface, WHITE, camera.worldToScreen(self.center), 3)  # center of rocket
        pygame.draw.rect(self.surf, GREEN, self.surf.get_rect(), 2)     # border of rocket surface
    
    def detectCrash(self):
        if self.altitude <= 0:
            self.v.update(0,0)
            self.angV *= 0.3
            if abs(self.angle - self.angFromPlanet) > 5 and self.vToPlanet < 7 and self.vTanPlanet < 5:
                self.crashed = True
    
    def update(self, planets, dt, timeWarp):
        self.detectCrash()            

        if self.fuelPercent > 0:
            self.fuelPercent -= (self.throttle*dt*timeWarp*0.2)
        
        self.angle += (self.angV*dt*timeWarp)%360

        if self.fuelPercent > 0:
            self.thrust = self.throttle*self.maxThrust
            self.thrustA.from_polar((self.thrust/self.mass, -self.angle))
        else:
            self.throttle = 0
            self.thrust = 0
            self.thrustA.update(0,0)

        for i in range(len(planets)):
            self.gravityVectors[i].update(planets[i].getGravityVec(self))

        self.v += self.thrustA*dt*timeWarp
        for vec in self.gravityVectors:
            self.v += vec*dt*timeWarp
            
        self.center += self.v*dt*timeWarp
        
        self.corners = [[self.center.x + (self.h/2)*cos(radians(self.angle)) + (self.w/2)*cos(radians(self.angle + 90)),    
                         self.center.y - (self.h/2)*sin(radians(self.angle)) - (self.w/2)*sin(radians(self.angle + 90))],   
                        [self.center.x + (self.h/2)*cos(radians(self.angle)) + (self.w/2)*cos(radians(self.angle - 90)),    
                         self.center.y - (self.h/2)*sin(radians(self.angle)) - (self.w/2)*sin(radians(self.angle - 90))],   
                        [self.center.x + (self.h/2)*cos(radians(self.angle + 180)) + (self.w/2)*cos(radians(self.angle + 90)),
                         self.center.y - (self.h/2)*sin(radians(self.angle + 180)) - (self.w/2)*sin(radians(self.angle + 90))],
                        [self.center.x + (self.h/2)*cos(radians(self.angle + 180)) + (self.w/2)*cos(radians(self.angle - 90)),
                         self.center.y - (self.h/2)*sin(radians(self.angle + 180)) - (self.w/2)*sin(radians(self.angle - 90))]]

        for planet in planets:
            if getDistSquared(planet.pos, self.center) < getDistSquared(self.nearestPlanet.pos, self.center):
                self.nearestPlanet = planet

        altitudesOfCorners = []
        for corner in self.corners:
            altitudesOfCorners.append(getDistance(corner, self.nearestPlanet.pos) - self.nearestPlanet.r)
        self.altitude = min(altitudesOfCorners)
        
        self.angFromPlanet = (degrees(atan2(self.nearestPlanet.pos[1] - self.center.y,
                                            self.center.x - self.nearestPlanet.pos[0])))%360

        self.vToPlanet = cos(self.v.as_polar()[1] - self.angFromPlanet + 180)*self.v.length()
        self.vTanPlanet = abs(sin(self.v.as_polar()[1] - self.angFromPlanet + 180)*self.v.length())

        self.path.extend([self.center.x + (self.h/2)*cos(radians(self.angle + 180)),
                          self.center.y - (self.h/2)*sin(radians(self.angle + 180))])

    def freeze(self):
        self.v.update(0,0)
        self.angV = 0
        self.throttle = 0
        self.altitude = 0
                                                
    def throttleMax(self):
        self.throttle = 1

    def throttleZero(self):
        self.throttle = 0
    
    def throttleUp(self):
        if self.throttle < 1:
            self.throttle += 0.05

    def throttleDown(self):
        if self.throttle > 0:
            self.throttle -= 0.05

    def rotCCW(self):
        self.angV += 0.5

    def rotCW(self):
        self.angV -= 0.5

    def stabilize(self):
        if self.angV > 0.5:
            self.angV -= 0.5
        elif self.angV < -0.5:
            self.angV += 0.5
        else:
            self.angV = 0




















        
