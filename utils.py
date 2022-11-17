import pygame
import copy
import datetime

from pygame.math import Vector3

class InputBox():
	def __init__(self, pos, size, maxCharacters=10, bounding_color=(255,255,255), text_color=(255,255,255), isPassword=False) -> None:
		self.pos = pos
		self.size = size
		self.bounding_color = bounding_color
		self.text_color = text_color
		self.isPassword = isPassword
		self.font = get_font(size)
		self.maxCharacters = maxCharacters
		self.text = ""
		self.text_surface = self.font.render(''.join(["A" for i in range(maxCharacters)]), True, (255, 255, 255))
		self.text_rect = self.text_surface.get_rect(center=pos)
		self.text_surface = self.font.render('', True, (255, 255, 255))

		self.boundingRect = self.text_rect.copy()
		self.boundingRect.width += 20
		self.boundingRect.x -= 10

		self.nextBlink = datetime.datetime.now() + datetime.timedelta(milliseconds=500)
		self.currentBlinkStatus = False
		self.cursor = self.font.render('|', True, self.text_color)
		self.cursor_rect = self.text_rect.copy()
		self.cursor_rect.y -= 1
		self.cursor_rect.x -= 10

		self.mouse_hovering = False
		self.bg_alpha = 0.0
		self.bg_alpha_target = 0.0
		self.is_focused = False

	def OnEvent(self, event: pygame.event.Event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.boundingRect.collidepoint(pygame.mouse.get_pos()):
				self.is_focused = True
				self.bg_alpha_target = 10.0
			else:
				self.is_focused = False
				self.bg_alpha_target = 0.0
		
		elif event.type == pygame.MOUSEBUTTONUP:
			if self.boundingRect.collidepoint(pygame.mouse.get_pos()):
				self.bg_alpha_target = 55.0

		elif event.type == pygame.KEYDOWN and self.is_focused:

			if event.unicode.isprintable() and len(self.text) < self.maxCharacters:
				self.text += event.unicode
			elif event.key == pygame.K_BACKSPACE and len(self.text) > 0:
				self.text = self.text[:-1]

			if not self.isPassword:
				self.text_surface = self.font.render(self.text, True, self.text_color)
			else:
				self.text_surface = self.font.render(''.join(['*' for i in range(len(self.text))]), True, self.text_color)
				
			self.cursor_rect.x = self.text_surface.get_width() + self.pos[0] - (self.boundingRect.width / 2) + 3

	def SetMouseHover(self, hover):
		self.mouse_hovering = hover
		
		if self.is_focused:
			return

		if self.mouse_hovering:
			self.bg_alpha_target = 55.0
		else:
			self.bg_alpha_target = 0.0

	def Update(self, dt):
		self.SetMouseHover(self.boundingRect.collidepoint(pygame.mouse.get_pos()))

		self.bg_alpha = lerp(self.bg_alpha, self.bg_alpha_target, clamp(dt * 10, 0.0, 1.0))

	def Render(self, screen: pygame.Surface):
		if datetime.datetime.now() >= self.nextBlink:
			self.currentBlinkStatus = not self.currentBlinkStatus
			self.nextBlink = datetime.datetime.now() + datetime.timedelta(milliseconds=500)

		draw_rect_alpha(screen, (255, 255, 255, self.bg_alpha), self.boundingRect)
		pygame.draw.rect(screen, self.bounding_color, self.boundingRect, 2)

		screen.blit(self.text_surface, self.text_rect)

		if self.currentBlinkStatus and self.is_focused:
			screen.blit(self.cursor, self.cursor_rect)

class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)
        
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def lerp(a: float, b: float, f: float):
    return a * (1.0 - f) + (b * f)
	
def draw_rect_alpha(surface: pygame.Surface, color, rect: pygame.rect.Rect, width=0):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), width=width)
    surface.blit(shape_surf, rect)

def get_font(size):
    return pygame.font.SysFont("Courier New", size)
