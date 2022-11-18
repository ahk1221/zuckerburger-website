import datetime
import random
import sys
import pygame
from games import Game
from settings import BLACK, FPS
from utils import get_font
import globals



AMOUNT_OF_OBJ = 10
HOVER_OBJ_COLOR = (190, 120, 255)
OBJ_COLOR = (190, 120, 0)
bg = pygame.transform.scale(pygame.image.load("assets/images/bg.png"), (1280, 720))

class Object(pygame.sprite.Sprite):
    def __init__(self, groups: list[pygame.sprite.Group], pos: tuple[int, int], scale: tuple[int, int], image_path: str):
        """
        `__init__` is a function that takes in a list of groups, a tuple of position, a tuple of scale,
        and a string of image path, and then it calls the `__init__` function of the parent class, which
        is `pygame.sprite.Sprite`, and then it sets the image to the image at the image path, scaled to
        the scale, and then it sets the rect to the rect of the image, with the top left corner at the
        position
        :param groups: list[pygame.sprite.Group]
        :type groups: list[pygame.sprite.Group]
        :param pos: The position of the sprite
        :type pos: tuple[int, int]
        :param scale: The size of the image
        :type scale: tuple[int, int]
        :param image_path: The path to the image you want to use
        :type image_path: str
        """
        super().__init__(groups)
        self.image = pygame.transform.scale(
            pygame.image.load(image_path).convert_alpha(),
            scale
        )

        self.rect = self.image.get_rect(topleft=pos)

    def isMouseHovering(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hovering = True
        else:
            self.hovering = False

    def Update(self):
        """
        If the mouse is hovering over the button, then change the balls color to a lighter shade of
        blue
        TODO change the balls color to a lighter shade
        """
        self.isMouseHovering()



class FindTheHiddenObj(Game):
    def __init__(self, main_screen: pygame.Surface, timer: pygame.time.Clock) -> None:
        """
        This function initializes the game state, and sets up the game
        :param main_screen: pygame.Surface = The screen that the game is being played on
        :type main_screen: pygame.Surface
        :param timer: pygame.time.Clock = The timer that is used to keep track of the time
        :type timer: pygame.time.Clock
        """
        super().__init__(main_screen, timer)

        self.width: int = main_screen.get_width()
        self.height: int = main_screen.get_height()

        self.totalTimeRemaining = datetime.timedelta(seconds=5)
        self.timerText: pygame.Surface = get_font(100).render("30:00", True, (255, 255, 255))
        self.timerTextRect: pygame.Rect = self.timerText.get_rect(center=(100, 50))
        self.started: bool = False

        self.gameOver: bool = False
        self.won: bool = False
        self.numOfMovesTaken: int = 0

        self.hovering: bool = False

        self.object_group = pygame.sprite.Group()
        for _ in range(AMOUNT_OF_OBJ):
            Object([self.object_group], (random.randint(100, 1180), random.randint(100, 620)), (6, 6), "assets/images/ball.png")

        self.timer_string = None
        self.counting_time = None

    def OnEvent(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONUP:
            for object in self.object_group:
                position = pygame.mouse.get_pos()
                if position[0] in range(object.rect.left, object.rect.right) and position[1] in range(object.rect.top, object.rect.bottom):
                    object.kill()

    def Update(self, dt):
        """
        It loops through all the objects in the object group and calls the Update function for each
        object
        """
        for object in self.object_group:
            object.Update()

        if len(self.object_group) == 0:
            return True
        else:
            return None



    def Render(self):
        """
        It takes the image of each object in the object group and blits it to the main screen
        """

        self.main_screen.blit(bg, (0,0))
        for object in self.object_group:
            self.main_screen.blit(object.image, object.rect)