#########################################
# File Name: game_v31.py
# Description: rocket simulator
# Author: Suyu Chen
# Date: 06/03/2020
#########################################
import pygame, time
from game_v31_classes import *

pygame.init()
pygame.mixer.init(22050, -16, 4, 1024)

width  = DEFAULT_RES[0]
height = DEFAULT_RES[1]
gameWindow = pygame.display.set_mode((width,height), pygame.RESIZABLE)

clock = pygame.time.Clock()
FPS = 60   

#---------------------------------------#
# Icon, Caption, Background and Fonts   #
#---------------------------------------#
pygame.display.set_icon(loadImg("icon.png"))
pygame.display.set_caption("Space Sim")

originalBg = loadImg("space.jpg", False)
bg = pygame.transform.scale(originalBg, (width, height))

largeFont = pygame.font.Font("fonts/font.ttf", 50)
medFont = pygame.font.Font("fonts/font.ttf", 35)
smallFont = pygame.font.Font("fonts/font.ttf", 25)
tinyFont = pygame.font.Font("fonts/font.ttf", 18)
titleFont = pygame.font.Font("fonts/titleFont.otf", 70)

#-----------------------------------#
# Rocket Data and Images            #
#-----------------------------------#
## rocket data format: [image, height (1 m = 2 px), mass, max thrust]
spaceShuttleData = [loadImg("spaceShuttle.png"), 112, 2030000, 34696128]
falcon9Data = [loadImg("falcon9.png"), 140, 541300, 5885000]
longMarch2FData = [loadImg("longMarch2F.png"), 124, 464000, 5920000]
soyuzData = [loadImg("soyuz.png"),91, 305000, 3357000]

rockets = [spaceShuttleData, falcon9Data, longMarch2FData, soyuzData]
chosenRocketData = None

#-----------------------------------#
# Sound and Music                   #
#-----------------------------------#
explosionVolume = 0.4
explosionSound = loadSound("explosion.wav", explosionVolume)
explosionChannel = pygame.mixer.Channel(1)

countdownVolume = 0.5
countdownSound = loadSound("countdown.wav", countdownVolume)
countdownChannel = pygame.mixer.Channel(2)

engineVolume = 0.15
engineSound = loadSound("engine.wav", engineVolume)
engineChannel = pygame.mixer.Channel(3)

rcsVolume = 0.1
rcsSound = loadSound("engine.wav", rcsVolume)
rcsChannel = pygame.mixer.Channel(4)

pygame.mixer.music.load("audio/music.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(loops = -1)

#-----------------------------------#
# Main Program                      #
#-----------------------------------#
gameMode = "menuLoad"

# dev stuff
drawDev = False
printDev = False
showFps = True

inPlay = True
while inPlay:  
    pygame.display.update()
    mousePos = pygame.mouse.get_pos()
    gameWindow.blit(bg, (0,0))
    clock.tick(FPS)

    mouseClick = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            inPlay = False
        if event.type == pygame.VIDEORESIZE:
            width, height = event.w, event.h
            gameWindow = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            bg = pygame.transform.scale(originalBg, (width, height))
            if gameMode in ["menu", "controls", "rockets", "crashed"]:
                gameMode += "Resize"
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseClick = True
    
    if gameMode == "menuLoad":
        menuTitle1 = ScalableText("ROCKET", titleFont, WHITE)
        menuTitle2 = ScalableText("SIMULATOR", titleFont, WHITE)
        playButton = TextButton("Play", largeFont, WHITE)
        controlsButton = TextButton("Controls", largeFont, WHITE)
        quitButton = TextButton("Quit", largeFont, WHITE)
        gameMode = "menuResize"

    if gameMode == "menuResize":
        menuTitle1.resize((width//2, height*3//12), (width, height), DEFAULT_RES)
        menuTitle2.resize((width//2, height*9//24), (width, height), DEFAULT_RES)
        playButton.resize((width//2, height*13//24), (width, height), DEFAULT_RES)
        controlsButton.resize((width//2, height*8//12), (width, height), DEFAULT_RES)
        quitButton.resize((width//2, height*19//24), (width, height), DEFAULT_RES)
        gameMode = "menu"
        
    if gameMode == "menu":
        menuTitle1.draw(gameWindow)
        menuTitle2.draw(gameWindow)   
        playButton.draw(gameWindow)
        controlsButton.draw(gameWindow)
        quitButton.draw(gameWindow)

        playButton.detectMouseHover(mousePos)
        quitButton.detectMouseHover(mousePos)
        controlsButton.detectMouseHover(mousePos)

        if mouseClick:
            if playButton.selected:
                gameMode = "rocketsLoad"
            if controlsButton.selected:
                gameMode = "controlsLoad"
            if quitButton.selected:
                inPlay = False

    if gameMode == "controlsLoad":
        controlsTitle = ScalableText("CONTROLS", titleFont, WHITE)
        controlsText = ["SPACE - Launch or Throttle to Max",
                        "X - Engines Off",
                        "W - Throttle Up",
                        "S - Throttle Down",
                        "A - Rotate Counterclockwise",
                        "D - Rotate Clockwise",
                        "M - Slow Rotation",
                        "1 - Slow Down Simulation",
                        "2 - Normal Speed Simulation",
                        "3 - Speed Up Simulation",
                        "ESC - Exit Game, Return to Menu"]
        controlLines = []
        for controlText in controlsText:
            controlLines.append(ScalableText(controlText, smallFont, WHITE))
        backButton = TextButton("Back to Menu", medFont, WHITE)
        gameMode = "controlsResize"

    if gameMode == "controlsResize":
        controlsTitle.resize((width//2, height*2//12), (width, height), DEFAULT_RES)
        controlLinesPositions = [(width//2, height*11//40)]
        for i in range(len(controlLines) - 1):
            controlLinesPositions.append((width//2, controlLinesPositions[0][1] + height//20*(i+1)))
        for i in range(len(controlLines)):
            controlLines[i].resize(controlLinesPositions[i], (width, height), DEFAULT_RES)
        backButton.resize((width//2, height*14//16), (width, height), DEFAULT_RES)
        gameMode = "controls"

    if gameMode == "controls":
        controlsTitle.draw(gameWindow)
        for controlLine in controlLines:
            controlLine.draw(gameWindow)
        backButton.draw(gameWindow)

        backButton.detectMouseHover(mousePos)
        if mouseClick and backButton.selected:
            gameMode = "menuLoad"

    if gameMode == "rocketsLoad":
        chosenRocketData = None
        rocketsTitle = ScalableText("SELECT ROCKET", titleFont, WHITE)
        rocketButtons = []
        for rocket in rockets:
            img = scaleMaintainAspect(rocket[0], newH=round(rocket[1]*1.5))
            rocketButtons.append(ImgButton(img))
        backButton = TextButton("Back to Menu", largeFont, WHITE)
        gameMode = "rocketsResize"

    if gameMode == "rocketsResize":
        rocketsTitle.resize((width//2, height//6), (width, height), DEFAULT_RES)
        for i in range(len(rockets)):
            rocketButtons[i].resize((width//(len(rockets)+1)*(i+1), height//2), (width, height), DEFAULT_RES)
        backButton.resize((width//2, height*5//6), (width, height), DEFAULT_RES)
        gameMode = "rockets"

    if gameMode == "rockets":
        rocketsTitle.draw(gameWindow)
        backButton.draw(gameWindow)
        backButton.detectMouseHover(mousePos)
        if mouseClick and backButton.selected:
            gameMode = "menuLoad"

        for i in range(len(rocketButtons)):
            rocketButtons[i].draw(gameWindow)
            rocketButtons[i].detectMouseHover(mousePos)
            if mouseClick and rocketButtons[i].selected:
                chosenRocketData = rockets[i]
                gameMode = "gameLoad"

    if gameMode == "gameLoad":
        mouseHeld = False
        timeWarp = 1
        rcs = False
        explosionPlayed = False

        # resetting sound volumes
        rcsSound.set_volume(rcsVolume)
        engineSound.set_volume(engineVolume)
        countdownSound.set_volume(countdownVolume)
        explosionSound.set_volume(explosionVolume)

        # countdown
        countdownStart = None
        countdownLength = countdownSound.get_length()

        # delay after rocket explosion
        crashedTime = None
        crashedDelay = 4
        # planets
        earth = Planet("earth", 0, 0, 10000, 1.46838e19, DARK_BLUE) 
        moon = Planet("moon", 0, -100000, 3000, 2.1846e17, GREY)
        planets = [earth, moon]

        # sprites
        explosionSprite = ExplosionSprite("explosion.png", 8, 8)
        rocket = Rocket(200, chosenRocketData, earth, planets)

        # camera
        camera = Camera(round(rocket.center.x - width/2),
                        round(rocket.center.y - height/2),
                        width, height, 1)

        infoText = []

        gameMode = "game"
    
    while gameMode == "game":       # game uses nested loop since game has different event loop, calculates dt, etc.
        pygame.display.update()
        mousePos = pygame.mouse.get_pos()
        gameWindow.blit(bg, (0,0))

        dt = clock.get_time()/1000  # time since last tick in seconds
        clock.tick(FPS)
            
        # Drawing objects on screen
        rocket.path.draw(gameWindow, camera)
        earth.draw(gameWindow, camera)
        moon.draw(gameWindow, camera)
        rocket.draw(gameWindow, camera)       

        # displaying numbers
        infoText = ["Altitude: " + str(round(rocket.altitude)) + " m",
                    "Nearest Planet: " + str(rocket.nearestPlanet.name),
                    "Throttle: " + str(round(rocket.throttle*100)) + " %",
                    "Velocity: " + str(round(rocket.v.length())) + " m/s",
                    "Velocity Towards Planet: " + str(round(rocket.vToPlanet)) + " m/s",
                    "Velocity Tangent Planet: " + str(round(rocket.vTanPlanet)) + " m/s",
                    "Angular Velocity: " + str(round(rocket.angV)) + " degrees/s",
                    "Fuel and Oxidizer: " + str(round(rocket.fuelPercent)) + " %",
                    "Time Warp: " + str(round(timeWarp, 1)) + "X"]
        for i in range(len(infoText)):
            textLineSurf = ScalableText(infoText[i], tinyFont, WHITE)
            textLineSurf.resizeFromTopLeft((width//20, height*(i+1)//30), (width, height), DEFAULT_RES)
            textLineSurf.draw(gameWindow)

        # Showing dev stuff
        if drawDev and not rocket.crashed:
            rocket.drawDevInfo(gameWindow, camera)
        if printDev:
            print("\nROCKET\n̅̅̅̅̅̅̅̅\n" + str(rocket))
            print("\nCAMERA\n̅̅̅̅̅̅̅̅\n" + str(camera))
            for planet in planets:
                print("\nPLANET\n̅̅̅̅̅̅̅̅\n" + str(planet))
            print("Timewarp: " + str(timeWarp) + "\n")
        if showFps:
            pygame.display.set_caption(str(clock.get_fps()))

        # updating rocket variables
        if not rocket.crashed and rocket.launched:
            rocket.update(planets, dt, timeWarp)
            
        # dealing with rocket crashing        
        if rocket.crashed:
            rocket.freeze()
            rcs = False
            if not explosionPlayed:
                pygame.mixer.stop()
                explosionSound.set_volume((1/sqrt(camera.zoom))*explosionVolume)  # sets volume based on zoom level
                explosionChannel.play(explosionSound, loops = -1)
                explosionPlayed = True
            if crashedTime == None:
                crashedTime = time.time()
            if not explosionSprite.finished:
                explosionSprite.loadNextImg()
                explosionSprite.transform(camera)
                explosionSprite.draw(gameWindow, rocket.center, camera)
            if time.time() - crashedTime > crashedDelay:
                pygame.mixer.stop()
                gameMode = "crashedLoad"
            
        # rocket launching
        if countdownStart != None:
            if time.time() - countdownStart > countdownLength:
                rocket.throttleMax()
                rocket.launched = True
                countdownStart = None

        # rocket engine sounds
        if rocket.throttle > 0:
            engineSound.set_volume((1/sqrt(camera.zoom))*engineVolume*rocket.throttle)
            if not engineChannel.get_busy():
                engineChannel.play(engineSound, loops = -1)
        if rocket.throttle <= 0:
            engineChannel.stop()
        if rcs:
            rcsSound.set_volume((1/sqrt(camera.zoom))*rcsVolume)
            if rcsSound.get_num_channels() == 0:
                rcsChannel.play(rcsSound, loops = -1)
        if not rcs:
            rcsChannel.stop()

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameMode = None
                inPlay = False

            # window resizing
            if event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                gameWindow = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                bg = pygame.transform.scale(originalBg, (width, height))
                camera.resize(width, height)

            # rocket controls (engines disabled when time sped up)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and timeWarp <= 1:
                    if not rocket.launched:
                        countdownSound.play() # does not immediately launch rocket, waits until countdown is over
                        countdownStart = time.time()
                    else:
                        rocket.throttleMax()                    
                elif event.key == pygame.K_x:
                    rocket.throttleZero()

            # Camera controls
                if event.key == pygame.K_t:
                    camera.tether = not camera.tether
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseHeld = True
                    camera.tether = False
                if event.button == 4:
                    camera.changeZoom("in", mousePos)
                if event.button == 5:
                    camera.changeZoom("out", mousePos)
            if event.type == pygame.MOUSEBUTTONUP and not camera.tether:
                if event.button == 1:
                    mouseHeld = False
            if event.type == pygame.MOUSEMOTION:
                mouseMovedX, mouseMovedY = pygame.mouse.get_rel()
                if mouseHeld:
                    camera.move(-mouseMovedX, -mouseMovedY)

        # pressed keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.mixer.stop()
            gameMode = "menuLoad"
            
        # rocket controls (engines disabled when time sped up)
        rcs = False
        if timeWarp <= 1 and rocket.launched and not rocket.crashed:   
            if keys[pygame.K_w]:
                rocket.throttleUp()
            elif keys[pygame.K_s]:
                rocket.throttleDown()
            if keys[pygame.K_a]:
                rocket.rotCCW()
                rcs = True
            elif keys[pygame.K_d]:
                rocket.rotCW()
                rcs = True
            elif keys[pygame.K_m]:
                rocket.stabilize()
                rcs = True

        # time warping (engines must be off to speed up time, but not to slow down time)
        if rocket.launched and not rocket.crashed:
            if keys[pygame.K_2]:
                timeWarp = 1
            elif keys[pygame.K_1] and timeWarp > 0.5:    
                timeWarp -= 0.2
            elif keys[pygame.K_3] and timeWarp < 50:
                if timeWarp < 1 or (not rcs and rocket.throttle == 0):
                    timeWarp += 0.2

        # updating camera position if it is tethered 
        if camera.tether:
            camera.followRocket(rocket)

    if gameMode == "crashedLoad":
        crashedTitle = ScalableText("YOU CRASHED", titleFont, WHITE)
        backButton = TextButton("Back to Menu", largeFont, WHITE)
        quitButton = TextButton("Quit", largeFont, WHITE)
        gameMode = "crashedResize"

    if gameMode == "crashedResize":
        crashedTitle.resize((width//2, height//3), (width, height), DEFAULT_RES)
        backButton.resize((width//2, height*8/15), (width, height), DEFAULT_RES)
        quitButton.resize((width//2, height*2//3), (width, height), DEFAULT_RES)
        gameMode = "crashed"

    if gameMode == "crashed":
        crashedTitle.draw(gameWindow)
        backButton.draw(gameWindow)
        quitButton.draw(gameWindow)

        backButton.detectMouseHover(mousePos)
        quitButton.detectMouseHover(mousePos)

        if mouseClick:
            if backButton.selected:
                gameMode = "menuLoad"
            if quitButton.selected:
                inPlay = False        
    
pygame.quit()
        
        




