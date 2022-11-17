import pygame
import pickle
import requests

import globals

from globals import *
from utils import *
from settings import *

class StartMenu():
    def __init__(self, main_screen: pygame.Surface, timer: pygame.time.Clock) -> None:
        self.main_screen = main_screen
        self.greeting_font = get_font(100)
        self.greeting_text = self.greeting_font.render("Zuckerberg's IDE", True, (255, 255, 255))
        self.greeting_text_rect = self.greeting_text.get_rect(center=(self.main_screen.get_width() / 2, self.main_screen.get_height() * 0.15))

        self.prompt_text_font = get_font(30)
        self.prompt_text = self.prompt_text_font.render("Enter your HC ID and password and click START!", True, (255, 255, 255))
        self.prompt_text_rect = self.prompt_text.get_rect(center=(self.main_screen.get_width() / 2, (self.main_screen.get_height() / 2) - 100))

        self.hc_input_box = InputBox((self.main_screen.get_width() / 2, self.main_screen.get_height() / 2), 50)
        self.password_input_box = InputBox((self.main_screen.get_width() / 2, (self.main_screen.get_height() / 2) + 80), 50, isPassword=True)

        self.start_button = Button(None, (self.main_screen.get_width() / 2, (self.main_screen.get_height() / 2) + 200), "START", get_font(50), (255, 255, 255), (192, 34, 200))

    def OnEvent(self, event: pygame.event.Event):
        self.hc_input_box.OnEvent(event)
        self.password_input_box.OnEvent(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.checkForInput(pygame.mouse.get_pos()):
                dictToSend = {"hcid": str(self.hc_input_box.text), "password": str(self.password_input_box.text) }
                res = requests.post(f'{BASE_URL}/login', json=dictToSend, timeout=5)
                if res.status_code == 401:
                    # Unauthorized
                    pass
                else:
                    with open('currentUser', 'wb') as f:
                        pickle.dump(str(self.hc_input_box.text), f)
                    globals.StartChallenge()
                    print('Started!')

    def Update(self, dt):
        self.hc_input_box.Update(dt)
        self.password_input_box.Update(dt)
        return None

    def Render(self):
        self.main_screen.fill((0, 0, 0))

        self.main_screen.blit(self.greeting_text, self.greeting_text_rect)
        self.main_screen.blit(self.prompt_text, self.prompt_text_rect)
        self.hc_input_box.Render(self.main_screen)
        self.password_input_box.Render(self.main_screen)

        self.start_button.update(self.main_screen)
