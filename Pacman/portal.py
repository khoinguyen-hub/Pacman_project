import pygame as pg
from entity import MazeRunner
from constants import *

class Portal(MazeRunner):
    def __init__(self, nodes, spritesheet, ftype="portal"):
        MazeRunner.__init__(self, nodes, spritesheet)
        self.name = "portal"
        self.color = (255, 140, 0)
        self.setStartPosition()
        self.lifespan = 10
        self.timer = 0
        self.destroy = False
        self.image = pg.image.load("pac_portal1.png")

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True

    def setStartPosition(self):
        self.node = self.findStartNode()
        self.target = self.node.neighbors[LEFT]
        self.setPosition()
        self.position.x -= (self.node.position.x - self.target.position.x) / 2

    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.portalStart:
                node.portalStart = False
                return node
            elif node.portal2Start:
                node.portal2Start = False
                return node
        return None


class Portal2(Portal):
    def __init__(self, nodes, spritesheet, ftype="portal"):
        MazeRunner.__init__(self, nodes, spritesheet)
        self.name = "portal"
        self.color = (255, 140, 0)
        self.setStartPosition()
        self.lifespan = 10
        self.timer = 0
        self.destroy = False
        self.image = pg.image.load("pac_portal2.png")

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True

    def setStartPosition(self):
        self.node = self.findStartNode()
        self.target = self.node.neighbors[LEFT]
        self.setPosition()
        self.position.x -= (self.node.position.x - self.target.position.x) / 2

    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.portal3Start:
                node.portal3Start = False
                return node
            elif node.portal4Start:
                node.portal4Start = False
                return node
        return None
