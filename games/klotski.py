from collections import namedtuple

from games import Game
from settings import *
import globals

import pygame

from utils import get_font

pygame.font.init()

TILE_SIZE = 100
main_font = pygame.font.Font(None, 50)
FONT_HEIGHT = main_font.get_height()
MARGIN = int(TILE_SIZE * 0.1)

# Window sizes
WIDTH, HEIGHT = 4 * TILE_SIZE + 2 * MARGIN, 5 * TILE_SIZE + 2 * MARGIN + 4 * FONT_HEIGHT

# Board positions
BOARD_OFFSETS = (SCREEN_WIDTH / 2) - 2 * TILE_SIZE, (SCREEN_HEIGHT / 2) - 2.5 * TILE_SIZE
BOARD_SIZE = 4 * TILE_SIZE, 5 * TILE_SIZE

# Score card positions
SCORE_OFFSETS = 0, HEIGHT - 2 * FONT_HEIGHT
SCORE_SIZE = WIDTH, 2 * FONT_HEIGHT

# Title positions
TITLE_OFFSETS = BOARD_OFFSETS[0], BOARD_OFFSETS[1] - FONT_HEIGHT
TITLE_SIZE = WIDTH, 2 * FONT_HEIGHT

def darken_color(color, factor):
    return tuple(int(c * factor) for c in color)

Position = namedtuple('Position', ['x', 'y'])

def draw_piece(surf, color, left, top, width, height, size):
    padding_factor = 0.025
    shadow_factor = 0.085
    margin_factor = 0.05

    base_color = color
    margin_color = darken_color(color, 0.8)
    bottom_color = darken_color(color, 0.4)

    # Applying padding
    padding = int(size * padding_factor)
    left, top = left + padding, top + padding
    width, height = width - 2 * padding, height - 2 * padding
    size = size - 2 * padding

    # Applying shadow effect
    shadow = int(size * shadow_factor)
    top_rect = (left, top, width - shadow, height - shadow)
    bottom_rect = (left + shadow, top + shadow, width - shadow, height - shadow)

    pygame.draw.rect(surf, bottom_color, bottom_rect)
    pygame.draw.rect(surf, base_color, top_rect)

    # Draw margins
    pygame.draw.rect(surf, margin_color, top_rect, int(size * margin_factor))

def is_neighbour(_pos1: Position, _pos2: Position):
    # Manhattan distance is 1 then neighbour
    return abs(_pos1.x - _pos2.x) + abs(_pos1.y - _pos2.y) == 1


class Piece:
    COLOR = (193, 154, 107)
    WIDTH = 0
    HEIGHT = 0

    def __init__(self, x, y):
        self.position = Position(x, y)

    @property
    def positions(self):
        # returns the positions the piece occupies
        raise NotImplemented

    def update_position(self, position):
        # Could be used later for tracking ??
        self.position = position

    def possible_moves(self, empty_positions):
        # returns all positions the piece can move to.
        # empty_positions - set of empty positions
        # NOTE: USED BY SOLVER
        raise NotImplemented

    def possible_moves_ui(self, empty_positions):
        # same as above, however takes UI into consideration
        # return value is a tuple (ignore second value, as it is specific for UI)
        #  - first element is the list of all positions the piece can move
        #  - second element is a list corresponding to click positions
        #     which should result in new positions specified in the first element
        raise NotImplemented

    def draw(self, surf, size):
        draw_piece(surf, self.COLOR, self.position.x * size, self.position.y * size, self.WIDTH * size,
                   self.HEIGHT * size, size)


class Piece1x1(Piece):
    WIDTH = 1
    HEIGHT = 1

    @property
    def positions(self):
        yield self.position

    def possible_moves_ui(self, empty_positions):
        if is_neighbour(*empty_positions):
            # if empty positions are neighbouring each other and piece is neighbouring one of these positions
            # the piece can go to any of the empty positions
            if any(is_neighbour(self.position, empty_position) for empty_position in empty_positions):
                return list(empty_positions), [{empty_position} for empty_position in empty_positions]

        new_positions = []
        click_positions = []
        for empty_position in empty_positions:
            # if empty position is a neighbour of piece,
            # then it's possible position to move to
            if is_neighbour(self.position, empty_position):
                new_positions.append(empty_position)
                click_positions.append({empty_position})

        # positions where the UI is clicked is the same as new resultant positions
        return new_positions, click_positions

    def possible_moves(self, empty_positions):
        if is_neighbour(*empty_positions):
            # if piece neighbours an empty position and empty positions themselves neighbour each other,
            # piece can move to any of the positions
            if any(is_neighbour(self.position, empty_position) for empty_position in empty_positions):
                return list(empty_positions)
            return []

        # if empty position is a neighbour, piece can move there.
        return [empty_position for empty_position in empty_positions if is_neighbour(self.position, empty_position)]


class Piece1x2(Piece):
    WIDTH = 1
    HEIGHT = 2

    @property
    def positions(self):
        yield self.position
        yield Position(self.position.x, self.position.y + 1)

    def possible_moves_ui(self, empty_positions):
        new_positions = []
        click_positions = []
        x, y = self.position
        if Position(x, y - 1) in empty_positions:
            # if movement possible towards top
            new_positions.append(Position(x, y - 1))
            click_positions.append({Position(x, y - 1)})

            if Position(x, y - 2) in empty_positions:
                new_positions.append(Position(x, y - 2))
                click_positions.append({Position(x, y - 2)})

        if Position(x, y + 2) in empty_positions:
            # if movement possible towards bottom
            new_positions.append(Position(x, y + 1))
            click_positions.append({Position(x, y + 2)})

            if Position(x, y + 3) in empty_positions:
                new_positions.append(Position(x, y + 2))
                click_positions.append({Position(x, y + 3)})

        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_positions:
            # if movement possible towards left
            new_positions.append(Position(x - 1, y))
            click_positions.append(empty_positions)

        if {Position(x + 1, y), Position(x + 1, y + 1)} == empty_positions:
            # if movement possible towards right
            new_positions.append(Position(x + 1, y))
            click_positions.append(empty_positions)

        return new_positions, click_positions

    def possible_moves(self, empty_positions):
        new_positions = []
        x, y = self.position
        if Position(x, y - 1) in empty_positions:
            new_positions.append(Position(x, y - 1))
            if Position(x, y - 2) in empty_positions:
                new_positions.append(Position(x, y - 2))
        if Position(x, y + 2) in empty_positions:
            new_positions.append(Position(x, y + 1))
            if Position(x, y + 3) in empty_positions:
                new_positions.append(Position(x, y + 2))

        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_positions:
            new_positions.append(Position(x - 1, y))
        if {Position(x + 1, y), Position(x + 1, y + 1)} == empty_positions:
            new_positions.append(Position(x + 1, y))

        return new_positions


class Piece2x1(Piece):
    WIDTH = 2
    HEIGHT = 1

    @property
    def positions(self):
        yield self.position
        yield Position(self.position.x + 1, self.position.y)

    def possible_moves_ui(self, empty_positions):
        new_positions = []
        click_positions = []
        x, y = self.position
        if Position(x - 1, y) in empty_positions:
            # if movement possible towards left
            new_positions.append(Position(x - 1, y))
            click_positions.append({Position(x - 1, y)})

            if Position(x - 2, y) in empty_positions:
                new_positions.append(Position(x - 2, y))
                click_positions.append({Position(x - 2, y)})

        if Position(x + 2, y) in empty_positions:
            # if movement possible towards right
            new_positions.append(Position(x + 1, y))
            click_positions.append({Position(x + 2, y)})

            if Position(x + 3, y) in empty_positions:
                new_positions.append(Position(x + 2, y))
                click_positions.append({Position(x + 3, y)})

        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_positions:
            # if movement possible towards top
            new_positions.append(Position(x, y - 1))
            click_positions.append(empty_positions)

        if {Position(x, y + 1), Position(x + 1, y + 1)} == empty_positions:
            # if movement possible towards bottom
            new_positions.append(Position(x, y + 1))
            click_positions.append(empty_positions)

        return new_positions, click_positions

    def possible_moves(self, empty_positions):
        new_positions = []
        x, y = self.position
        if Position(x - 1, y) in empty_positions:
            new_positions.append(Position(x - 1, y))
            if Position(x - 2, y) in empty_positions:
                new_positions.append(Position(x - 2, y))
        if Position(x + 2, y) in empty_positions:
            new_positions.append(Position(x + 1, y))
            if Position(x + 3, y) in empty_positions:
                new_positions.append(Position(x + 2, y))

        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_positions:
            new_positions.append(Position(x, y - 1))
        if {Position(x, y + 1), Position(x + 1, y + 1)} == empty_positions:
            new_positions.append(Position(x, y + 1))

        return new_positions


class Piece2x2(Piece):
    COLOR = (119, 17, 0)
    WIDTH = 2
    HEIGHT = 2

    @property
    def positions(self):
        yield self.position
        yield Position(self.position.x + 1, self.position.y)
        yield Position(self.position.x, self.position.y + 1)
        yield Position(self.position.x + 1, self.position.y + 1)

    def possible_moves_ui(self, empty_positions):
        new_positions = []
        click_positions = []
        x, y = self.position
        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_positions:
            # if movement possible towards top
            new_positions.append(Position(x, y - 1))
            click_positions.append(empty_positions)

        if {Position(x, y + 2), Position(x + 1, y + 2)} == empty_positions:
            # if movement possible towards bottom
            new_positions.append(Position(x, y + 1))
            click_positions.append(empty_positions)

        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_positions:
            # if movement possible towards left
            new_positions.append(Position(x - 1, y))
            click_positions.append(empty_positions)

        if {Position(x + 2, y), Position(x + 2, y + 1)} == empty_positions:
            # if movement possible towards right
            new_positions.append(Position(x + 1, y))
            click_positions.append(empty_positions)

        return new_positions, click_positions

    def possible_moves(self, empty_positions):
        new_positions = []
        x, y = self.position
        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_positions:
            new_positions.append(Position(x, y - 1))
        if {Position(x, y + 2), Position(x + 1, y + 2)} == empty_positions:
            new_positions.append(Position(x, y + 1))
        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_positions:
            new_positions.append(Position(x - 1, y))
        if {Position(x + 2, y), Position(x + 2, y + 1)} == empty_positions:
            new_positions.append(Position(x + 1, y))

        return new_positions


class Board:
    def __init__(self, pieces):
        # pieces is the list of pieces on the board,
        # with last piece being the main piece (expectation)
        assert isinstance(pieces[-1], Piece2x2)
        self.pieces = pieces
        self.main_piece = pieces[-1]
        self.history = []
        self.history_insert = 0

    @property
    def number_of_steps(self):
        return self.history_insert

    @classmethod
    def from_start_position(cls):
        return cls([Piece1x1(0, 4), Piece1x1(1, 3), Piece1x1(2, 3), Piece1x1(3, 4),
                    Piece1x1(0, 0), Piece1x1(0, 1), Piece1x2(0, 2), Piece1x1(3, 0), Piece1x1(3, 1), Piece1x2(3, 2),
                    Piece1x1(1, 2), Piece1x1(2, 2), Piece2x2(1, 0)])

    def empty_positions(self):
        # positions: initial store all positions on the board
        positions = {Position(x, y) for x in range(4) for y in range(5)}
        for piece in self.pieces:
            for occupied_position in piece.positions:
                # remove positions occupied by each of the pieces
                positions.remove(occupied_position)
        assert len(positions) == 2
        # positions with no piece are empty
        return positions

    @property
    def is_solved(self):
        # check if main piece is in the expected finish position
        return self.main_piece.position == Position(1, 3)

    def get_piece(self, position):
        # Gets the piece in the specified position
        for piece in self.pieces:
            if position in piece.positions:
                return piece
        return None

    def draw(self, surf, size):
        for piece in self.pieces:
            piece.draw(surf, size)

    def can_move(self, piece, click_position):
        # click position is on of the empty positions,
        # to which user drags a piece.
        # NOTE: if the piece can move, returns
        # the new start position of the piece.
        empty_positions = self.empty_positions()
        possible_positions, click_positions = piece.possible_moves_ui(empty_positions)
        for possible_pos, click_pos in zip(possible_positions, click_positions):
            if click_position in click_pos:
                return possible_pos
        return None

    def _can_move(self, piece, position):
        # position is the new start position of the piece
        # Note: piece is denoted by the start position.
        empty_positions = self.empty_positions()
        possible_positions = piece.possible_moves(empty_positions)
        if position in possible_positions:
            return True

    def move(self, piece, position):
        # position is the new start position of the piece
        assert self._can_move(piece, position)
        # insert into history the previous position
        self.history = self.history[:self.history_insert]
        self.history.append((piece, piece.position))
        self.history_insert += 1
        piece.update_position(position)

    # The history functions manipulate the history stack to
    # support undo and redo of steps.
    def history_back(self):
        if self.history[:self.history_insert]:
            self.history_insert -= 1
            piece, position = self.history[self.history_insert]
            self.history[self.history_insert] = (piece, piece.position)
            piece.update_position(position)

    def history_forward(self):
        if self.history_insert < len(self.history):
            piece, position = self.history[self.history_insert]
            self.history[self.history_insert] = (piece, piece.position)
            self.history_insert += 1
            piece.update_position(position)

class Klotski(Game):
    def __init__(self, main_screen: pygame.Surface, timer: pygame.time.Clock):
        super().__init__(main_screen, timer)
        self.time_taken = timer.get_time()
        self.board = Board.from_start_position()
        self.selected_piece = None

        # A surface to draw the board onto..
        self.board_surf = pygame.Surface(BOARD_SIZE)
        self.timer_string = None

    def Draw(self):

        board_color = (205, 127, 50)
        text_background = (0, 100, 255)
        text_color = (255, 255, 255)
        # Fill the window and the board
        self.main_screen.fill(darken_color(board_color, 0.5))
        self.board_surf.fill(board_color)

        # Draw the board and copy it onto the window
        self.board.draw(self.board_surf, TILE_SIZE)
        self.main_screen.blit(self.board_surf, BOARD_OFFSETS)

        font = pygame.font.Font('assets/fonts/ARCADE_N.TTF', 35, bold=True)
        label = font.render('KLOTSKI', 1, (255, 255, 255))  # initialise 'Tetris' text with white

        self.main_screen.blit(label, label.get_rect(center=(SCREEN_WIDTH / 2, 45)))  # put surface on the center of the window


    def handle_select(self, pos):
        # Handles mouse button down event.
        # Sets the selected_piece if a piece is selected
        self.selected_piece = None
        pos = pos[0] - BOARD_OFFSETS[0], pos[1] - BOARD_OFFSETS[1]
        if 0 <= pos[0] < BOARD_SIZE[0] and 0 <= pos[1] < BOARD_SIZE[1]:
            position = Position(pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)
            self.selected_piece = self.board.get_piece(position)

    def handle_drop(self, pos):
        # Handles mouse button up event.
        # Moves the selected_piece if to specified position if allowed.
        # Specified position must be an empty position!
        pos = pos[0] - BOARD_OFFSETS[0], pos[1] - BOARD_OFFSETS[1]
        if 0 <= pos[0] < BOARD_SIZE[0] and 0 <= pos[1] < BOARD_SIZE[1]:
            click_position = Position(pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)
            if self.selected_piece:
                possible_pos = self.board.can_move(self.selected_piece, click_position)
                if possible_pos:
                    self.board.move(self.selected_piece, possible_pos)

    def reset(self):
        # creates a new board to reset it
        self.board = Board.from_start_position()
        self.selected_piece = None
        # Reset the solver as well

    def handle_user_event(self, _event):

        if _event.type == pygame.KEYDOWN:
            # Board reset
            if _event.key == pygame.K_r:
                self.reset()

            # History events
            if _event.key == pygame.K_LEFT:
                self.board.history_back()
            if _event.key == pygame.K_RIGHT:
                self.board.history_forward()

        if _event.type == pygame.MOUSEBUTTONDOWN and _event.button == 1:  # left click
            self.handle_select(_event.pos)

        if _event.type == pygame.MOUSEBUTTONUP and _event.button == 1:  # left click
            self.handle_drop(_event.pos)


    def OnEvent(self, event: pygame.event.Event):
        super().OnEvent(event)
        self.handle_user_event(event)

    def Update(self, dt):
        return self.board.is_solved

    def Render(self):
        super().Render()
        self.Draw()

        # Power keys while navigating history
        # Allows continuous press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            self.board.history_back()
        elif keys[pygame.K_UP]:
            self.board.history_forward()



