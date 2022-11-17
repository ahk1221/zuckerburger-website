import random
import pygame

from settings import *
from games import Game

"""
10 x 20 grid
play_height = 2 * play_width

tetriminos:
    0 - S - green
    1 - Z - red
    2 - I - cyan
    3 - O - yellow
    4 - J - blue
    5 - L - orange
    6 - T - purple
"""

pygame.font.init()

WINNING_SCORE = 50

# global variables

col = 10  # 10 columns
row = 20  # 20 rows

play_width = 300  # play window width; 300/10 = 30 width per block
play_height = 600  # play window height; 600/20 = 20 height per block
block_size = 30  # size of block

top_left_x = (SCREEN_WIDTH - play_width) // 2
top_left_y = (SCREEN_HEIGHT - play_height) // 2

filepath = 'assets/high_scores.ttf'
fontpath = 'assets/fonts/ARCADE_N.TTF'
fontpath_mario = 'assets/fonts/SuperMario.ttf'

# shapes formats

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['.....',
      '..0..',
      '..0..',
      '..0..',
      '..0..'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# index represents the shape
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# class to represent each of the pieces


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]  # choose color from the shape_color list
        self.rotation = 0  # chooses the rotation according to index


# initialise the grid
def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]  # grid represented rgb tuples

    # locked_positions dictionary
    # (x,y):(r,g,b)
    for y in range(row):
        for x in range(col):
            if (x, y) in locked_pos:
                color = locked_pos[
                    (x, y)]  # get the value color (r,g,b) from the locked_positions dictionary using key (x,y)
                grid[y][x] = color  # set grid position to color

    return grid


def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]  # get the desired rotated shape from piece

    '''
    e.g.
       ['.....',
        '.....',
        '..00.',
        '.00..',
        '.....']
    '''
    for i, line in enumerate(shape_format):  # i gives index; line gives string
        row = list(line)  # makes a list of char from string
        for j, column in enumerate(row):  # j gives index of char; column gives char
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)  # offset according to the input given with dot and zero

    return positions


# checks if current position of piece in grid is valid
def valid_space(piece, grid):
    # makes a 2D list of all the possible (x,y)
    accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
    # removes sub lists and puts (x,y) in one list; easier to search
    accepted_pos = [x for item in accepted_pos for x in item]

    formatted_shape = convert_shape_format(piece)

    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1] >= 0:
                return False
    return True


# check if piece is out of board
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


# chooses a shape randomly from shapes list
def get_shape():
    return Piece(5, 0, random.choice(shapes))


# draws text in the middle
def draw_text_middle(text, size, color, surface, offset=(0,0)):
    font = pygame.font.Font(fontpath, size, bold=False, italic=True)
    label = font.render(text, 1, color)

    surface.blit(label, label.get_rect(center=((SCREEN_WIDTH/2) + offset[0], (SCREEN_HEIGHT/2) + offset[1])))


# draws the lines of the grid for the game
def draw_grid(surface):
    r = g = b = 0
    grid_color = (r, g, b)

    for i in range(row):
        # draw grey horizontal lines
        pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                         (top_left_x + play_width, top_left_y + i * block_size))
        for j in range(col):
            # draw grey vertical lines
            pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                             (top_left_x + j * block_size, top_left_y + play_height))


# clear a row when it is filled
def clear_rows(grid, locked):
    # need to check if row is clear then shift every other row above down one
    increment = 0
    for i in range(len(grid) - 1, -1, -1):      # start checking the grid backwards
        grid_row = grid[i]                      # get the last row
        if (0, 0, 0) not in grid_row:           # if there are no empty spaces (i.e. black blocks)
            increment += 1
            # add positions to remove from locked
            index = i                           # row index will be constant
            for j in range(len(grid_row)):
                try:
                    del locked[(j, i)]          # delete every locked element in the bottom row
                except ValueError:
                    continue

    # shift every row one step down
    # delete filled bottom row
    # add another empty row on the top
    # move down one step
    if increment > 0:
        # sort the locked list according to y value in (x,y) and then reverse
        # reversed because otherwise the ones on the top will overwrite the lower ones
        for key in sorted(list(locked), key=lambda a: a[1])[::-1]:
            x, y = key
            if y < index:                       # if the y value is above the removed index
                new_key = (x, y + increment)    # shift position to down
                locked[new_key] = locked.pop(key)

    return increment


# draws the upcoming piece
def draw_next_shape(piece, surface):
    font = pygame.font.Font(fontpath, 30)
    label = font.render('Next shape', 1, (255, 255, 255))

    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)

    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + i*block_size, block_size, block_size), 0)

    surface.blit(label, (start_x, start_y - 30))

    # pygame.display.update()


# draws the content of the window
def draw_window(surface: pygame.Surface, grid, score=0):
    surface.fill((0, 0, 0))  # fill the surface with black

    pygame.font.init()  # initialise font
    font = pygame.font.Font(fontpath, 35, bold=True)
    label = font.render('TETRIS', 1, (255, 255, 255))  # initialise 'Tetris' text with white

    surface.blit(label, label.get_rect(center=(SCREEN_WIDTH / 2, top_left_y - 25)))  # put surface on the center of the window

    # winning score
    font = pygame.font.Font(fontpath, 17, bold=True)
    winning_score_text = font.render('Get to ' + str(WINNING_SCORE) + ' score to win!', 1, (255, 255, 255))
    surface.blit(winning_score_text, winning_score_text.get_rect(center=(SCREEN_WIDTH * 0.2, SCREEN_HEIGHT / 2)))  # put surface on the center of the window

    # controls
    font = pygame.font.Font(fontpath, 12, bold=True)
    controls_text = font.render('Use arrow keys to control the piece!', 1, (255, 255, 255))
    surface.blit(controls_text, controls_text.get_rect(center=(SCREEN_WIDTH * 0.2, SCREEN_HEIGHT / 2 + winning_score_text.get_height() + 20)))  # put surface on the center of the window

    # current score
    font = pygame.font.Font(fontpath, 30)
    label = font.render('SCORE   ' + str(score) , 1, (255, 255, 255))

    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)

    surface.blit(label, (start_x, start_y + 200))

    # draw content of the grid
    for i in range(row):
        for j in range(col):
            # pygame.draw.rect()
            # draw a rectangle shape
            # rect(Surface, color, Rect, width=0) -> Rect
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # draw vertical and horizontal grid lines
    draw_grid(surface)

    # draw rectangular border around play area
    border_color = (255, 255, 255)
    pygame.draw.rect(surface, border_color, (top_left_x, top_left_y, play_width, play_height), 4)

    # pygame.display.update()

class Tetris(Game):
    def __init__(self, main_screen: pygame.Surface, timer: pygame.time.Clock):
        super().__init__(main_screen, timer)
        self.Restart()

    def Restart(self):
        self.run = False
        self.lost = False
        self.locked_positions = {}
        create_grid(self.locked_positions)

        self.change_piece = False
        self.current_piece = get_shape()
        self.next_piece = get_shape()
        self.fall_time = 0
        self.fall_speed = 0.35
        self.level_time = 0
        self.score = 0
        self.last_score = 0

    def OnEvent(self, event: pygame.event.Event):
        super().OnEvent(event)

        if event.type == pygame.KEYDOWN:
            self.grid = create_grid(self.locked_positions)

            if event.key == pygame.K_SPACE:
                self.grid = create_grid(self.locked_positions)
                self.run = True

            if event.key == pygame.K_LEFT:
                self.current_piece.x -= 1  # move x position left
                if not valid_space(self.current_piece, self.grid):
                    self.current_piece.x += 1

            elif event.key == pygame.K_RIGHT:
                self.current_piece.x += 1  # move x position right
                if not valid_space(self.current_piece, self.grid):
                    self.current_piece.x -= 1

            elif event.key == pygame.K_DOWN:
                # move shape down
                self.current_piece.y += 1
                if not valid_space(self.current_piece, self.grid):
                    self.current_piece.y -= 1

            elif event.key == pygame.K_UP:
                # rotate shape
                self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
                if not valid_space(self.current_piece, self.grid):
                    self.current_piece.rotation = self.current_piece.rotation - 1 % len(self.current_piece.shape)

    def Render(self):
        super().Render()

        if not self.run:

            if self.lost:
                draw_text_middle('You Lost', 50, (255, 255, 255), self.main_screen, (0, -100))
                draw_text_middle('Press SPACE to try again', 30, (255, 255, 255), self.main_screen)
            else:
                draw_text_middle('TETRIS', 50, (255, 255, 255), self.main_screen, (0, -100))
                draw_text_middle('Press SPACE to begin', 30, (255, 255, 255), self.main_screen)

            return

        draw_window(self.main_screen, self.grid, self.score)
        draw_next_shape(self.next_piece, self.main_screen)

    def Update(self, dt):
        super().Update(dt)

        # need to constantly make new grid as locked positions always change
        self.grid = create_grid(self.locked_positions)

        # helps run the same on every computer
        # add time since last tick() to fall_time
        self.fall_time += self.timer.get_rawtime()  # returns in milliseconds
        self.level_time += self.timer.get_rawtime()

        if self.level_time/1000 > 5:    # make the difficulty harder every 10 seconds
            self.level_time = 0
            if self.fall_speed > 0.15:   # until fall speed is 0.15
                self.fall_speed -= 0.005

        if self.fall_time / 1000 > self.fall_speed:
            self.fall_time = 0
            self.current_piece.y += 1
            if not valid_space(self.current_piece, self.grid) and self.current_piece.y > 0:
                self.current_piece.y -= 1
                # since only checking for down - either reached bottom or hit another piece
                # need to lock the piece position
                # need to generate new piece
                self.change_piece = True

        piece_pos = convert_shape_format(self.current_piece)

        # draw the piece on the grid by giving color in the piece locations
        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                self.grid[y][x] = self.current_piece.color

        if self.change_piece:  # if the piece is locked
            for pos in piece_pos:
                p = (pos[0], pos[1])
                self.locked_positions[p] = self.current_piece.color       # add the key and value in the dictionary
            self.current_piece = self.next_piece
            self.next_piece = get_shape()
            self.change_piece = False
            self.score += clear_rows(self.grid, self.locked_positions) * 10    # increment score by 10 for every row cleared

            if self.last_score < self.score:
                self.last_score = self.score

        if check_lost(self.locked_positions):
            if self.score >= WINNING_SCORE:
                # Won
                return True

            # Lost, restart the game
            self.Restart()
            self.lost = True

