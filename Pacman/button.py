import pygame
from vector import Vector2
from constants import *

class Button:
    def __init__(self, screen, msg, pos_x, pos_y, size, tile):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.position = Vector2(pos_x, pos_y)
        self.size = size
        self.text_color = WHITE
        self.font = pygame.font.Font("PressStart2P-vaV7.ttf", self.size)

        self.prep_msg(msg)
        self.rect = pygame.Rect(pos_x, pos_y, tile*TILEWIDTH, TILEHEIGHT)


    def prep_msg(self, msg):
        self.msg_image = self.font.render(msg, True, self.text_color)

    def draw(self):
        x, y = self.position.asTuple()
        self.screen.blit(self.msg_image, (x, y))
