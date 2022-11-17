import pickle
from games.tetris import Tetris
import globals
import pygame
import requests

from utils import *
from settings import *
from globals import *
from debug import *

from games.tower_of_hanoi import *
from games.find_the_hidden_object import *
from games.klotski import *
import games.color_switch
from start_menu import StartMenu

from datetime import datetime

pygame.init()
main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zuckerburger")

clock = pygame.time.Clock()

startMenuScreen = StartMenu(main_screen, clock)
screens = [startMenuScreen, FindTheHiddenObj(main_screen, clock), TowerOfHanoi(main_screen, clock), Tetris(main_screen, clock), Klotski(main_screen, clock), games.color_switch.MainGame(main_screen, clock)]

defaultFont = get_font(50)

def send_data(time, puzzle_level):
    user = None
    with open('currentUser', 'rb') as f:
        user = pickle.load(f)

    dictToSend = {"hcid": str(user), 'time': str(time), 'puzzle_level': str(puzzle_level)}
    res = requests.post(f'{BASE_URL}/add-shit', json=dictToSend, timeout=5)
    if res.status_code == 401:
        # Unauthorized
        pass

def main():
    won = False
    completed = False
    time_completed = datetime(1, 1, 1)

    while True:
        dt = clock.tick(FPS) / 1000  # Amount of seconds between each loop.

        startMenuScreen.start_button.changeColor(pygame.mouse.get_pos())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if globals.active_game_index < len(screens) and screens[globals.active_game_index] != None:
                screens[globals.active_game_index].OnEvent(event)

                # active_game_index += 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    globals.active_game_index += 1
                    globals.start_time = datetime.now()
                    print(globals.start_time)
                if event.key == pygame.K_o:
                    globals.active_game_index += 1

                    if globals.active_game_index >= len(screens):
                        # Completed all the games
                        won = True
                        completed = True

                    print(globals.start_time)
                #pass


        main_screen.fill(BLACK)

        if not completed and globals.active_game_index < len(screens) and screens[globals.active_game_index] != None:
            output = screens[globals.active_game_index].Update(dt)
            screens[globals.active_game_index].Render()

            if output != None and output is True:
                if globals.active_game_index >= len(screens) - 1:
                    # Completed all the games
                    time_completed = datetime.now()
                    time_taken = time_completed - globals.start_time

                    send_data(time_taken.total_seconds(), globals.active_game_index)
                    won = True
                    completed = True
                else:
                    globals.active_game_index += 1

            if globals.active_game_index != 0:
                time_completed = datetime.now()
                time_taken = time_completed - globals.start_time

                text = get_font(50).render(str(time_taken)[2:7], 1, (255,255,255))
                level_text = get_font(50).render('Level ' + str(globals.active_game_index), 1, (255,255,255))
                main_screen.blit(text, (10, 10))
                main_screen.blit(level_text, (10, text.get_height() + 5))

                if int(time_taken.total_seconds()) >= 60 * 60:
                    completed = True
                    send_data(time_taken.total_seconds(), globals.active_game_index)

        if won:
            main_screen.fill((0,0,0))
            gameWonText = get_font(50).render("You Won", True, (255, 255, 255))
            main_screen.blit(gameWonText, gameWonText.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))

        elif completed:
            main_screen.fill((0,0,0))
            gameOverText = get_font(50).render("Game over, get lost", 1, (255, 255, 255))
            main_screen.blit(gameOverText, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        pygame.display.update()


if __name__ == "__main__":
    main()
