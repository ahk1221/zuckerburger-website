import pygame
import datetime

from utils import get_font
from games import Game

from settings import *
import sys
import globals


TOWER_HEIGHT = 400
TOWER_WIDTH = 30

TILE_HEIGHT = 30
TILE_WIDTH = 70

NUM_TILES = 3

TILE_COLOR = (190, 120, 0)
HOVER_TILE_COLOR = (190, 120, 255)

TOWER_COLOR = (255, 255, 255)
HOVER_TOWER_COLOR = (123, 230, 98)

class Tower:
    def __init__(self, main_screen: pygame.Surface, x_position, y_position):
        self.main_screen = main_screen
        self.tiles = []
        self.x_position = x_position
        self.y_position = y_position
        self.color = TOWER_COLOR

        self.rect = pygame.Rect(self.x_position, self.y_position, TOWER_WIDTH, TOWER_HEIGHT)
        self.rect.center = (self.x_position, self.y_position)

        self.image = pygame.image.load("assets/images/Bar.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TOWER_WIDTH, TOWER_HEIGHT))

    def AddTile(self, tile, insertAtStart=False):
        if insertAtStart and len(self.tiles) != 0:
            self.tiles.insert(0, tile)
        else:
            self.tiles.append(tile)

    def RemoveTile(self, tile):
        self.tiles.remove(tile)

    def OnEvent(self, event):
        for tile in self.tiles:
            tile.OnEvent(event)

    def Update(self, game):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and game.currentlyDraggingTile != None and game.CanMoveTileToTower(game.currentlyDraggingTile, self):
            self.color = HOVER_TOWER_COLOR
        else:
            self.color = TOWER_COLOR

        for tile in self.tiles:
            tile.Update()

        i = len(self.tiles) - 1

        for tile in self.tiles:
            if not tile.isBeingDragged:
                tile.UpdatePosition((self.x_position, self.rect.bottom -(i * (TILE_HEIGHT + 10)) ))

            tile.Update()
            i -= 1

    def Render(self):
        pygame.draw.rect(self.main_screen, self.color, self.rect)

        #self.main_screen.blit(self.image, self.rect)

        for tile in self.tiles:
            if not tile.isBeingDragged:
                tile.Render()


class Tile:

    def __init__(self, main_screen: pygame.Surface, width) -> None:
        self.main_screen = main_screen
        self.width = width
        self.color = TILE_COLOR

        self.image = pygame.image.load("assets/images/Bar2.png")
        self.image = pygame.transform.scale(self.image, (width, TILE_HEIGHT))
        self.image.fill(TILE_COLOR, special_flags=pygame.BLEND_ADD)

        self.rect = None

        self.isBeingDragged = False

    def UpdatePosition(self, centerPos):
        if self.rect is None:
            self.rect = pygame.rect.Rect(centerPos, (self.width, TILE_HEIGHT))

        self.rect.center = centerPos

    def OnEvent(self, event):
        pass

    def Update(self):
        if self.rect is None:
            return

        # Check if mouse is over rect
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.color = HOVER_TILE_COLOR
        else:
            self.color = TILE_COLOR

    def Render(self):
        if self.rect is not None:
            pygame.draw.rect(self.main_screen, self.color, self.rect)
        #self.main_screen.blit(self.image, self.rect)


class TowerOfHanoi(Game):

    def __init__(self, main_screen: pygame.Surface, timer: pygame.time.Clock):
        super().__init__(main_screen, timer)

        self.width = main_screen.get_width()
        self.height = main_screen.get_height()
        self.towers = []
        self.tiles = []
        self.currentlyDraggingTile = None
        self.score = 10
        self.started = False

        self.gameOver = False
        self.won = False
        self.numOfMovesTaken = 0

        self.timer_string = None

        # Some calculations for where to position the 3 towers
        difference = (self.width - 100) / 3
        for i in range(3):
            xPos = (self.width / 2) + ((i - 1) * difference)

            tower = Tower(self.main_screen, xPos, self.height - (TOWER_HEIGHT / 2) - 100)
            self.towers.append(tower)

        # Add all tiles dynamically to the first tower
        for i in range(NUM_TILES):
            tile = Tile(self.main_screen, TILE_WIDTH + (i * TILE_WIDTH))
            self.tiles.append(tile)
            self.towers[0].AddTile(tile)

    def GetTowerForTile(self, tile):
        for tower in self.towers:
            for towerTile in tower.tiles:
                if towerTile == tile:
                    return tower

    def MoveTileToTower(self, tile, tower):
        currentTower = self.GetTowerForTile(tile)

        if currentTower == None:
            return

        currentTower.RemoveTile(tile)
        tower.AddTile(tile, True)

        if not self.started:
            self.started = True

        self.numOfMovesTaken += 1

    def CanMoveTileToTower(self, tile, tower):
        # If there are no tiles on the tower, means can move to that tower
        if len(tower.tiles) == 0:
            return True

        # Get the topmost tile of the tower
        topmostTile = tower.tiles[0]

        if topmostTile == None:
            return True

        # If the tile being moved is smaller than the topmost tile on the tower being moved to
        # then the move is valid
        if tile.width < topmostTile.width:
            return True

        return False

    def OnEvent(self, event: pygame.event.Event):
        if self.gameOver:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and self.currentlyDraggingTile == None:
            # Find the tile clicked on
            for tile in self.tiles:
                if tile.rect is not None:
                    if tile.rect.collidepoint(pygame.mouse.get_pos()) and self.GetTowerForTile(tile).tiles[0] == tile:
                        self.currentlyDraggingTile = tile
                        self.currentlyDraggingTile.isBeingDragged = True
                        break

        elif event.type == pygame.MOUSEBUTTONUP and self.currentlyDraggingTile != None:
            # Find the tower the mouse is on
            for tower in self.towers:
                if tower.rect.collidepoint(pygame.mouse.get_pos()) and self.CanMoveTileToTower(self.currentlyDraggingTile, tower):
                    self.MoveTileToTower(self.currentlyDraggingTile, tower)
                    break

            self.currentlyDraggingTile.isBeingDragged = False
            self.currentlyDraggingTile = None

        for tower in self.towers:
            tower.OnEvent(event)

    def GetCurrentGameState(self):
        # Check in the second and third tower
        # if either of them have all the tiles on them
        # If they do, game won
        for i in range(1, 3):
            tower = self.towers[i]
            if len(tower.tiles) == NUM_TILES:
                return True, True

        return False, False

    def Update(self, dt):

        # Update all 3 towers and each of its childs
        for tower in self.towers:
            tower.Update(self)

        # GetCurrentGameState returns a tuple
        # with 2 bools, game over and game won
        (gameOver, gameWon) = self.GetCurrentGameState()
        #print(gameOver, gameWon)

        if self.numOfMovesTaken > 7:
            self.score -= 1

        # If game is over, return out of the functions
        if gameOver:
            self.gameOver = True
            self.won = gameWon

            if self.currentlyDraggingTile != None:
                self.currentlyDraggingTile.isBeingDragged = False
                self.currentlyDraggingTile = None

            return True

        if self.currentlyDraggingTile != None:
            self.currentlyDraggingTile.UpdatePosition(pygame.mouse.get_pos())


        return None

    def Render(self):

        # Renders all 3 towers and each of its tiles
        for tower in self.towers:
            tower.Render()

        # Separate rendering for tile being dragged
        if self.currentlyDraggingTile != None:
            self.currentlyDraggingTile.Render()
