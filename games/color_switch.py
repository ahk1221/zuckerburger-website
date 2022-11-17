import datetime
import pickle
import pygame, pygame.gfxdraw, math, random
from games import Game
from settings import *
import sys

from utils import get_font
import globals

WINNING_SCORE = 10

PURPLE = (140, 19, 251)
RED = (255, 0, 128)
TEAL = (53, 226, 242)
YELLOW = (246, 223, 14)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

obstacles = list()
stars = list()
colorswitches = list()
MENU, GAMEPLAY, PAUSE, GAMEOVER, WON = range(5)
gamestate = MENU
score = 0
highscore = 0

GRAVITY = 850

pygame.font.init()
font = pygame.font.SysFont('arial', 24)
menu_font = pygame.font.SysFont('arial', 60)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

cam = Camera()

class Obstacle:
    def __init__(self, surface, x=250, y=150, rad=220, angle = 0, vel = 150):
        self.x = x
        self.y = y
        self.rad = rad
        self.angle = angle
        self.surface = surface
        self.vel = vel
        self.thickness = 25

    def update(self, dt):
        x, y = (self.x-float(self.rad/2)-cam.x, self.y-float(self.rad/2)-cam.y)
        if(y >= SCREEN_HEIGHT):
            obstacles.remove(self)
            print("obstacle was removed")
            return
        self.angle+=self.vel * dt
        if(self.angle > 360):
            self.angle-=360
        elif(self.angle <= 0):
            self.angle+=360


    def draw(self):
        #pygame.gfxdraw.arc(self.surface, self.x, self.y, 100, 0, 180, (255,255,255))
        x, y = (self.x-float(self.rad/2)-cam.x, self.y-float(self.rad/2)-cam.y)
        x, y = int(x), int(y)
        thick = self.thickness
        pygame.draw.arc(self.surface, PURPLE , (x, y, self.rad, self.rad), math.radians(0+self.angle) ,math.radians(90+self.angle), thick)
        pygame.draw.arc(self.surface, PURPLE , (x, y+1, self.rad, self.rad), math.radians(0+self.angle) ,math.radians(90+self.angle), thick)
        pygame.draw.arc(self.surface, YELLOW , (x, y, self.rad, self.rad), math.radians(90+self.angle) , math.radians(180+self.angle), thick)
        pygame.draw.arc(self.surface, YELLOW , (x, y+1, self.rad, self.rad), math.radians(90+self.angle) ,math.radians(180+self.angle), thick)
        pygame.draw.arc(self.surface, TEAL , (x, y, self.rad, self.rad), math.radians(180+self.angle) ,math.radians(270+self.angle), thick)
        pygame.draw.arc(self.surface, TEAL , (x, y+1, self.rad, self.rad), math.radians(180+self.angle) ,math.radians(270+self.angle), thick)
        pygame.draw.arc(self.surface, RED , (x, y, self.rad, self.rad), math.radians(270+self.angle) ,math.radians(360+self.angle), thick)
        pygame.draw.arc(self.surface, RED , (x, y+1, self.rad, self.rad), math.radians(270+self.angle) ,math.radians(360+self.angle), thick)

        #pygame.gfxdraw.aacircle(self.surface, int(self.x), int(self.y), int(self.rad/2), (20,20,20))
        pygame.gfxdraw.aacircle(self.surface, int(self.x-cam.x), int(self.y-cam.y), int(self.rad/2)+1, (20,20,20))
        pygame.gfxdraw.aacircle(self.surface, int(self.x-cam.x), int(self.y-cam.y), int(self.rad/2), (20,20,20))
        pygame.gfxdraw.aacircle(self.surface, int(self.x-cam.x), int(self.y-cam.y), int(self.rad/2)-thick-1, (20,20,20))
        pygame.gfxdraw.aacircle(self.surface, int(self.x-cam.x), int(self.y-cam.y), int(self.rad/2)-thick, (20,20,20))


class Star:
    def __init__(self, surface, x, y):
        self.x = x
        self.y = y
        self.w = 10
        self.h = 10
        self.surface = surface
        self.color = WHITE
        self.dead = False
        self.dead_counter = 0

    def update(self, dt):
        if(self.dead and self.dead_counter < 40):
            self.dead_counter+=50 * dt
        elif(self.dead):
            stars.remove(self)

    def draw(self):
        x,y = self.x-cam.x,self.y-cam.y
        if(not self.dead):
            points = ((x,y-16),(x-7,y-5), (x-20,y-3), (x-11,y+8), (x-13, y+21), (x, y+16), (x+13, y+21), (x+11, y+8), (x+20, y-3), (x+7,y-5))
            pygame.gfxdraw.aapolygon(self.surface, points, self.color)
            pygame.gfxdraw.filled_polygon(self.surface, points, self.color)
        else:
            self.surface.blit(font.render("+1", True, (255-self.dead_counter*5, 255-self.dead_counter*5, 255-self.dead_counter*5)), (x-10,y-self.dead_counter))

def draw_pie(x, y, rad, s_angle, e_angle, color, screen):
    points = [(x,y)]
    for n in range(s_angle, e_angle+1):
        tx = x + int(rad*math.cos(math.radians(n)))
        ty = y + int(rad*math.sin(math.radians(n)))
        points.append((tx, ty))
    points.append((x,y))
    if(len(points)>2):
        pygame.gfxdraw.aapolygon(screen, points, color)
        pygame.gfxdraw.filled_polygon(screen, points, color)
        # pygame.draw.polygon(screen, RED, points)

def random_color():
    rand = random.randint(0,3)
    if(rand == 0):
        return PURPLE
    elif(rand == 1):
        return RED
    elif(rand == 2):
        return TEAL
    elif(rand == 3):
        return YELLOW

class ColorSwitch:
    def __init__(self, surface, x, y, color = random_color()):
        self.x = x
        self.y = y
        self.surface = surface
        self.rad = 22
        self.color = color

    def draw(self, screen):
        x, y = int(self.x-cam.x), int(self.y-cam.y)
        draw_pie(x, y, self.rad, 0, 90, RED, screen)
        draw_pie(x, y, self.rad, 90, 180, TEAL, screen)
        draw_pie(x, y, self.rad, 180, 270, YELLOW, screen)
        draw_pie(x, y, self.rad, 270, 360, PURPLE, screen)
        pygame.gfxdraw.aacircle(self.surface, x, y,self.rad-1, (20,20,20))
        pygame.gfxdraw.aacircle(self.surface, x, y,self.rad, (20,20,20))



class ExplosionBall:
    def __init__(self, surface, x=250, y=400):
        self.x = x
        self.y = y
        #self.rad = 3
        self.rad = random.randint(2,5)
        self.surface = surface
        self.vel = [random.uniform(-1000,1000),random.uniform(-1000,1000)]
        self.color = random_color()

    def draw(self):
        x, y = int(self.x-cam.x), int(self.y-cam.y)
        pygame.gfxdraw.aacircle(self.surface, x, y, self.rad, self.color)
        pygame.gfxdraw.filled_circle(self.surface, x, y, self.rad, self.color)

    def update(self, dt):
        X,Y = 0,1
        self.vel[Y] += GRAVITY * dt
        self.x += self.vel[X] * dt
        if(self.x >= SCREEN_WIDTH or self.x <= 0):
            self.vel[X] = -self.vel[X]
        self.y += self.vel[Y] * dt


class Ball:
    def __init__(self, surface, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2):
        self.x = x
        self.y = y
        self.rad = 10
        self.surface = surface
        self.vel = 0
        self.color = random_color()
        self.dead = False
        self.dead_counter = 0.0
        self.explosion_balls = []

    def collision_detection(self):
        global score
        x, y = self.x-cam.x, self.y-cam.y
        for star in stars:
            if(star.y+16 >= self.y):
                star.color = BLACK
                if(not star.dead):
                    score+=1
                    self.color = random_color()
                star.dead = True

        for obstacle in obstacles:
            if(obstacle.y+int(obstacle.rad/2) >= self.y and obstacle.y+int(obstacle.rad/2)-25 <= self.y):
                if(self.color != YELLOW and obstacle.angle > 90 and obstacle.angle <= 180):
                    self.die()
                elif(self.color != PURPLE and obstacle.angle > 180 and obstacle.angle <= 270):
                    self.die()
                elif(self.color != RED and obstacle.angle > 270 and obstacle.angle <= 360):
                    self.die()
                elif(self.color != TEAL and obstacle.angle <= 90):
                    self.die()
                #elif(self.surface==screen):
                    #self.die()

            elif(obstacle.y-(obstacle.rad/2)+25 >= self.y-self.rad and obstacle.y-(obstacle.rad/2) <= self.y):
                if(self.color != RED and obstacle.angle > 90 and obstacle.angle <= 180):
                    self.die()
                elif(self.color != TEAL and obstacle.angle > 180 and obstacle.angle <= 270):
                    self.die()
                elif(self.color != YELLOW and obstacle.angle > 270 and obstacle.angle <= 360):
                    self.die()
                elif(self.color != PURPLE and obstacle.angle <= 90):
                    self.die()

            elif(self.y>=SCREEN_HEIGHT):
                self.die()

                #elif(self.surface==screen):
                    #self.die()
            '''elif(self.color ==RED or self.color ==TEAL or self.color==YELLOW or self.color==PURPLE):
                if(self.surface==screen and gamestate ==GAMEPLAY):
                    self.die();'''


        for cs in colorswitches:
            if(cs.y >= self.y-self.rad*2):
                self.color = random_color()
                colorswitches.remove(cs)

    def die(self):
        self.dead = True
        for i in range(50):
            temp = ExplosionBall(self.surface, self.x, self.y)
            self.explosion_balls.append(temp)

    def update(self, dt):
        if(not self.dead):
            self.vel -= GRAVITY * dt
            self.y -= self.vel * dt
            if(cam.y >= self.y-SCREEN_HEIGHT/2):
                cam.y = self.y-SCREEN_HEIGHT/2
            self.collision_detection()
        elif(self.dead and self.dead_counter <= 1):
            self.dead_counter+=dt
            for xball in self.explosion_balls:
                xball.update(dt)

        else:
            global score, highscore, gamestate
            gamestate = GAMEOVER
            if(score > highscore):
                highscore = score

    def draw(self):
        x = int(self.x-cam.x)
        y = int(self.y-cam.y)
        if(self.y > 10000):
            self.y = 9000
        if(not self.dead):
            pygame.gfxdraw.aacircle(self.surface, x, y, self.rad, self.color)
            pygame.gfxdraw.filled_circle(self.surface, x, y, self.rad, self.color)
        elif(self.dead_counter <= 1):
            dc = self.dead_counter
            #pygame.gfxdraw.aacircle(self.surface, x, y, self.rad-dc, self.color)
            #pygame.gfxdraw.filled_circle(self.surface, x, y, self.rad-dc, self.color)
            for ball in self.explosion_balls:
                ball.draw()

# ball = Ball(screen)


def restart(screen):
    global cam, ball, obstacles, score, stars
    cam = Camera()
    ball = Ball(screen)
    del stars[:]
    del obstacles[:]
    del colorswitches[:]
    for i in range(WINNING_SCORE):
        o_type = 0
        if(o_type == 0):
            temp = Obstacle(screen, SCREEN_WIDTH/2, -600*i)
            obstacles.append(temp)
            temp_colorswitch = ColorSwitch(screen, SCREEN_WIDTH/2, -600*i+300)
        elif(o_type == 1):
            temp = Obstacle(screen, SCREEN_WIDTH/2, -600*i, 300,45,1)
            temp2 = Obstacle(screen, SCREEN_WIDTH/2, -600*i, temp.rad-temp.thickness*2-5, 180+45, -1)
            obstacles.append(temp)
            obstacles.append(temp2)
            t = random.randint(0,1)
            if(t == 0):
                col = RED
            else:
                col = YELLOW
            temp_colorswitch = ColorSwitch(screen, SCREEN_WIDTH/2, -600*i+300, col)
        elif(o_type == 2):
            temp = Obstacle(screen, SCREEN_WIDTH/2-100, -600*i, 200, 45, 1)
            temp2 = Obstacle(screen, SCREEN_WIDTH/2+100, -600*i, 200, 45, -1)
            obstacles.append(temp)
            obstacles.append(temp2)
            temp_colorswitch = ColorSwitch(screen, SCREEN_WIDTH/2, -600*i+300, random_color())

        temp_star = Star(screen, SCREEN_WIDTH/2, -600*i)
        stars.append(temp_star)
        colorswitches.append(temp_colorswitch)

    score = 0

def draw_menu(screen):
    screen.blit(font.render("P R E S S  S P A C E B A R  T O  C O N T I N U E", True, WHITE), (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2))

def draw_game_over(screen):
    #screen.blit(font.render("GAME OVER", True, WHITE), (SCREEN_WIDTH/2-50, SCREEN_HEIGHT/2))
    screen.blit(font.render("S C O R E", True, WHITE), (SCREEN_WIDTH/2-50, 120))
    screen.blit(menu_font.render(str(score), True, WHITE), (SCREEN_WIDTH/2-10, 150))
    screen.blit(font.render("B E S T   S C O R E", True, WHITE), (SCREEN_WIDTH/2-100, 250))
    screen.blit(menu_font.render(str(highscore), True, WHITE), (SCREEN_WIDTH/2-10, 290))
    #screen.blit(retry, (int(SCREEN_WIDTH/2-retry.get_height()/2), int(SCREEN_HEIGHT*7/12)))


def draw_ui(screen):
    screen.blit(font.render(str(score), True, WHITE), (SCREEN_WIDTH - 20, 10))
    if(highscore >= 1):
        w = SCREEN_WIDTH/5
        for i in range(6):
            pygame.draw.line(screen, WHITE, (w*i-20-cam.x, -600*(highscore-1)-cam.y), (w*i+20-cam.x, -600*(highscore-1)-cam.y), 10)

class MainGame(Game):
    def __init__(self, main_screen: pygame.Surface, timer: pygame.time.Clock):
        super().__init__(main_screen, timer)
        self.timer_string = None

    def OnEvent(self, event):
        global gamestate

        if(event.type == pygame.QUIT):
            sys.exit(1)
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_ESCAPE):
                return False
            elif(event.key == pygame.K_SPACE):
                if(gamestate == GAMEPLAY):
                    ball.vel = 350
                #elif(gamestate==GAMEPLAY and )
                elif(gamestate == GAMEOVER):
                    restart(self.main_screen)
                    gamestate = GAMEPLAY
                elif(gamestate == MENU):
                    restart(self.main_screen)
                    gamestate = GAMEPLAY

    def Render(self) -> int:
        self.main_screen.fill((20,20,20))

        if(gamestate == MENU):
            draw_menu(self.main_screen)
        elif(gamestate == GAMEPLAY):

            for obstacle in obstacles:
                if(obstacle.y+obstacle.rad/2-cam.y >= 0 and obstacle.y-obstacle.rad/2-cam.y <= SCREEN_HEIGHT):
                    obstacle.draw()
            for star in stars:
                if(star.y+13-cam.y >= 0 and star.y-13-cam.y <= SCREEN_HEIGHT):
                    star.draw()
            for cs in colorswitches:
                if(cs.y+cs.rad-cam.y >= 0 and cs.y-cs.rad-cam.y <= SCREEN_HEIGHT):
                    cs.draw(self.main_screen)
            ball.draw()
            draw_ui(self.main_screen)

        elif(gamestate == GAMEOVER):
            draw_game_over(self.main_screen)


    def Update(self, dt):

        if (score == WINNING_SCORE):
            return True

        if gamestate == GAMEPLAY:
            for obstacle in obstacles:
                obstacle.update(dt)
            ball.update(dt)
            for star in stars:
                star.update(dt)




