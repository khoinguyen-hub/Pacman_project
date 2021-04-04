from pygame import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import *
from fruit import Fruit
from pauser import Pauser
from text import TextGroup
from sprites import Spritesheet
from maze import Maze
from portal import *
from levels import *
from button import *

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_flash = None
        self.setBackground()
        self.clock = pygame.time.Clock()
        self.pelletsEaten = 0
        self.fruit = None
        self.pause = Pauser(True)
        self.text = TextGroup()
        self.score = 0
        self.gameover = False
        self.sheet = Spritesheet()
        self.maze = Maze(self.sheet)
        self.flashBackground = False
        self.portal = None
        self.portal2 = None
        self.portal3 = None
        self.portal4 = None
        self.level = LevelController()
        self.mainScreen = True
        self.gameScreen = False
        self.hsScreen = False
        self.eat_sound = pygame.mixer.Sound("pacman_chomp.wav")
        self.main_menu_sound = pygame.mixer.Sound("pacman_intermission.wav")
        self.beginning_sound = pygame.mixer.Sound("pacman_beginning.wav")
        self.eat_fruit = pygame.mixer.Sound("pacman_eatfruit.wav")
        self.eat_ghost = pygame.mixer.Sound("pacman_eatghost.wav")
        self.death_sound = pygame.mixer.Sound("pacman_death.wav")
        
    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):
        print("Start game")
        self.level.reset()
        self.maze.getMaze("maze")
        self.maze.constructMaze(self.background, self.background_flash, 0)
        self.nodes = NodeGroup("maze.txt")
        self.pellets = PelletGroup("maze.txt")
        self.pacman = Pacman(self.nodes, self.sheet)
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.pelletsEaten = 0
        self.fruit = None
        self.pause.force(True)
        self.text.showReady()
        self.gameover = False
        self.maze.reset()
        self.flashBackground = False
        self.text.updateLevel(self.level.level + 1)
        self.portal = None
        self.portal2 = None
        self.portal3 = None
        self.portal4 = None

    def startLevel(self):
        print("Start game")
        self.setBackground()
        self.maze.getMaze("maze")
        self.maze.constructMaze(self.background, self.background_flash, 0)
        self.nodes = NodeGroup("maze.txt")
        self.pellets = PelletGroup("maze.txt")
        self.pacman.nodes = self.nodes
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.pelletsEaten = 0
        self.text.updateLevel(self.level.level+1)
        self.fruit = None
        self.pause.force(True)
        self.flashBackground = False
        self.maze.reset()
        self.portal = None
        self.portal2 = None
        self.portal3 = None
        self.portal4 = None

    def resolveLevelClear(self):
        self.level.nextLevel()
        self.startLevel()
        self.pause.pauseType = None

    def restartLevel(self):
        print("Restart game")
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.pause.force(True)
        self.fruit = None
        self.flashBackground = False
        self.maze.reset()
        # self.portal = None  # commented so portals dont disappear on reset/death
        # self.portal2 = None
        # self.portal3 = None
        # self.portal4 = None
        
    def update(self):
        if not self.gameover:
            dt = self.clock.tick(30) / 1000.0
            if not self.pause.paused:
                self.pacman.update(dt)
                self.ghosts.update(dt, self.pacman)
                if self.fruit is not None:
                    self.fruit.update(dt)

                if self.portal is not None:
                    self.portal.update(dt)
                    self.portal2.update(dt)
                if self.portal3 is not None:
                    self.portal3.update(dt)
                    self.portal4.update(dt)

                if self.pause.pauseType != None:
                    self.pause.settlePause(self)
            
                self.checkPelletEvents()
                self.checkGhostEvents()
                self.checkFruitEvents()
                self.checkPortalEvents()

            else:
                if self.flashBackground:
                    self.maze.flash(dt)
                    
                if self.pacman.animateDeath:
                    self.pacman.updateDeath(dt)

            self.pause.update(dt)
            self.pellets.update(dt)
            self.text.update(dt)
        self.checkEvents()
        self.text.updateScore(self.score)
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                if self.score > 0:
                    with open("high_scores.txt", 'a') as f:
                        f.write(f'Highscore was {game.score}\n')
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.gameover:
                        self.startGame()
                    else:
                        self.pause.player()
                        if self.pause.paused:
                            self.text.showPause()
                        else:
                            self.text.hideMessages()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.play_button.rect.collidepoint(mouse_x, mouse_y):
                    self.mainScreen = False
                    self.gameScreen = True
                elif self.score_button.rect.collidepoint(mouse_x, mouse_y):
                    self.mainScreen = False
                    self.hsScreen = True
                elif self.back_button.rect.collidepoint(mouse_x, mouse_y):
                    self.mainScreen = True
                    self.hsScreen = False

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.eat_sound.set_volume(0.2)
            self.eat_sound.play()
            self.pelletsEaten += 1
            self.score += pellet.points
            if self.pelletsEaten == 25 or self.pelletsEaten == 150:
                if self.fruit is None:
                    self.fruit = Fruit(self.nodes, self.sheet, "cherry")
            if self.pelletsEaten == 75:
                if self.portal is None:
                    self.portal = Portal(self.nodes, self.sheet)
                if self.portal2 is None:
                    self.portal2 = Portal(self.nodes, self.sheet)
            if self.pelletsEaten == 125:
                if self.portal3 is None:
                    self.portal3 = Portal2(self.nodes, self.sheet)
                if self.portal4 is None:
                    self.portal4 = Portal2(self.nodes, self.sheet)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == "powerpellet":
                self.ghosts.resetPoints()
                self.ghosts.freightMode()
            if self.pellets.isEmpty():
                self.pacman.visible = False
                self.ghosts.hide()
                self.pause.startTimer(3, "clear")
                self.flashBackground = True
                

    def checkGhostEvents(self):
        self.ghosts.release(self.pelletsEaten)
        ghost = self.pacman.eatGhost(self.ghosts)
        if ghost is not None:
            if ghost.mode.name == "FREIGHT":
                self.eat_ghost.set_volume(0.2)
                self.eat_ghost.play()
                self.score += ghost.points
                self.text.createTemp(ghost.points, ghost.position)
                self.ghosts.updatePoints()
                ghost.spawnMode(speed=2)
                self.pause.startTimer(1)
                self.pacman.visible = False
                ghost.visible = False

            elif ghost.mode.name != "SPAWN":
                self.death_sound.set_volume(0.2)
                self.death_sound.play()
                self.pacman.loseLife()
                self.ghosts.hide()
                self.pause.startTimer(3, "die")

    def checkFruitEvents(self):
        if self.fruit is not None:
            if self.pacman.eatFruit(self.fruit):
                self.eat_fruit.set_volume(0.2)
                self.eat_fruit.play()
                self.score += self.fruit.points 
                self.text.createTemp(self.fruit.points, self.fruit.position)
                self.fruit = None
                
            elif self.fruit.destroy:
                self.fruit = None

    def checkPortalEvents(self):
        if self.portal is not None:
            if self.pacman.enterPortal(self.portal):
                b = self.nodes.getNode(19*TILEWIDTH, 4*TILEHEIGHT, self.nodes.nodeList)
                self.pacman.node = b
                self.pacman.setPosition()
                self.pacman.direction = STOP
            elif self.portal.destroy:
                self.portal = None

        if self.portal2 is not None:
            if self.pacman.enterPortal(self.portal2):
                b = self.nodes.getNode(3*TILEWIDTH, 32*TILEHEIGHT, self.nodes.nodeList)
                self.pacman.node = b
                self.pacman.setPosition()
                self.pacman.direction = STOP
            elif self.portal2.destroy:
                self.portal2 = None

        if self.portal3 is not None:
            if self.pacman.enterPortal(self.portal3):
                b = self.nodes.getNode(21*TILEWIDTH, 32*TILEHEIGHT, self.nodes.nodeList)
                self.pacman.node = b
                self.pacman.setPosition()
                self.pacman.direction = STOP
            elif self.portal3.destroy:
                self.portal3 = None

        if self.portal4 is not None:
            if self.pacman.enterPortal(self.portal4):
                b = self.nodes.getNode(5*TILEWIDTH, 4*TILEHEIGHT, self.nodes.nodeList)
                self.pacman.node = b
                self.pacman.setPosition()
                self.pacman.direction = STOP
            elif self.portal4.destroy:
                self.portal4 = None

    def resolveDeath(self):
        if self.pacman.lives == 0:
            self.gameover = True
            self.pacman.visible = False
            self.text.showGameOver()
        else:
            self.restartLevel()
        self.pause.pauseType = None
    
    def render(self):
        self.screen.blit(self.maze.background, (0,0))
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        if self.portal is not None:
            self.portal.render(self.screen)
        if self.portal2 is not None:
            self.portal2.render(self.screen)
        if self.portal3 is not None:
            self.portal3.render(self.screen)
        if self.portal4 is not None:
            self.portal4.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.pacman.renderLives(self.screen)
        self.text.render(self.screen)
        pygame.display.update()

    def main_screen_ani(self, current_time):
        if current_time <= 0.5:
            self.screen.blit(self.sheet.getImage(4, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
            pygame.draw.circle(self.screen, WHITE, (25 * TILEWIDTH, 19.2 * TILEHEIGHT), 8)
        elif 0.5 < current_time <= 1:
            self.screen.blit(self.sheet.getImage(1, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (3*TILEWIDTH, 18 * TILEHEIGHT))
            pygame.draw.circle(self.screen, WHITE, (25 * TILEWIDTH, 19.2 * TILEHEIGHT), 8)
        elif 1 < current_time <= 1.5:
            self.screen.blit(self.sheet.getImage(1, 1, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
            pygame.draw.circle(self.screen, WHITE, (25 * TILEWIDTH, 19.2 * TILEHEIGHT), 8)
        elif 1.5 < current_time <= 2:
            self.screen.blit(self.sheet.getImage(1, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (9 * TILEWIDTH, 18 * TILEHEIGHT))
            pygame.draw.circle(self.screen, WHITE, (25 * TILEWIDTH, 19.2 * TILEHEIGHT), 8)
            self.screen.blit(self.sheet.getImage(6, 2, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
        elif 2 < current_time <= 2.5:
            self.screen.blit(self.sheet.getImage(4, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (12 * TILEWIDTH, 18 * TILEHEIGHT))
            pygame.draw.circle(self.screen, WHITE, (25 * TILEWIDTH, 19.2 * TILEHEIGHT), 8)
            self.screen.blit(self.sheet.getImage(6, 2, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 3, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
        elif 2.5 < current_time <= 3:
            self.screen.blit(self.sheet.getImage(1, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (15 * TILEWIDTH, 18 * TILEHEIGHT))
            pygame.draw.circle(self.screen, WHITE, (25 * TILEWIDTH, 19.2 * TILEHEIGHT), 8)
            self.screen.blit(self.sheet.getImage(6, 2, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 3, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 4, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
        elif 3 < current_time <= 3.5:
            self.screen.blit(self.sheet.getImage(1, 1, TILEWIDTH * 2, TILEHEIGHT * 2), (18 * TILEWIDTH, 18 * TILEHEIGHT))
            pygame.draw.circle(self.screen, WHITE, (25 * TILEWIDTH, 19.2 * TILEHEIGHT), 8)
            self.screen.blit(self.sheet.getImage(6, 2, TILEWIDTH * 2, TILEHEIGHT * 2), (9 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 3, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 4, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 5, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
        elif 3.5 < current_time <= 4:
            self.screen.blit(self.sheet.getImage(1, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (21 * TILEWIDTH, 18 * TILEHEIGHT))
            pygame.draw.circle(self.screen, WHITE, (25 * TILEWIDTH, 19.2 * TILEHEIGHT), 8)
            self.screen.blit(self.sheet.getImage(6, 2, TILEWIDTH * 2, TILEHEIGHT * 2), (12 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 3, TILEWIDTH * 2, TILEHEIGHT * 2), (9 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 4, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 5, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
        elif 4 < current_time <= 4.5:
            self.screen.blit(self.sheet.getImage(4, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (23 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 2, TILEWIDTH * 2, TILEHEIGHT * 2), (15 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 3, TILEWIDTH * 2, TILEHEIGHT * 2), (12 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 4, TILEWIDTH * 2, TILEHEIGHT * 2), (9 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(6, 5, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
        elif 4.5 < current_time <= 5:
            self.screen.blit(self.sheet.getImage(0, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (23 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (15 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (12 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (9 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
        elif 5 < current_time <= 5.5:
            self.screen.blit(self.sheet.getImage(0, 1, TILEWIDTH * 2, TILEHEIGHT * 2), (21 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (12 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (9 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
        elif 5.5 < current_time <= 6:
            self.screen.blit(self.sheet.getImage(0, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (18 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (9 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
        elif 6 < current_time <= 6.5:
            self.screen.blit(self.sheet.getImage(4, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (15 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
        elif 6.5 < current_time <= 7:
            self.screen.blit(self.sheet.getImage(0, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (12 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
        elif 7 < current_time <= 7.5:
            self.screen.blit(self.sheet.getImage(0, 1, TILEWIDTH * 2, TILEHEIGHT * 2), (9 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(self.sheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2), (TILEWIDTH, 18 * TILEHEIGHT))
        elif 7.5 < current_time <= 8:
            self.screen.blit(self.sheet.getImage(0, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (6 * TILEWIDTH, 18 * TILEHEIGHT))
        elif 8 < current_time <= 8.5:
            self.screen.blit(self.sheet.getImage(4, 0, TILEWIDTH * 2, TILEHEIGHT * 2), (3 * TILEWIDTH, 18 * TILEHEIGHT))
        elif 9 < current_time <= 11:
            self.screen.blit(self.sheet.getImage(6, 2, TILEWIDTH * 2, TILEHEIGHT * 2), (21 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(pygame.image.load('blinky_text.png'), (10 * TILEWIDTH, 15 * TILEHEIGHT))
        elif 11 < current_time <= 13:
            self.screen.blit(self.sheet.getImage(6, 3, TILEWIDTH * 2, TILEHEIGHT * 2), (21 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(pygame.image.load('pinky_text.png'), (10 * TILEWIDTH, 15 * TILEHEIGHT))
        elif 13 < current_time <= 15:
            self.screen.blit(self.sheet.getImage(6, 4, TILEWIDTH * 2, TILEHEIGHT * 2), (21 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(pygame.image.load('inkey_text.png'), (10 * TILEWIDTH, 15 * TILEHEIGHT))
        elif 15 < current_time <= 17:
            self.screen.blit(self.sheet.getImage(6, 5, TILEWIDTH * 2, TILEHEIGHT * 2), (21 * TILEWIDTH, 18 * TILEHEIGHT))
            self.screen.blit(pygame.image.load('clyde_text.png'), (10 * TILEWIDTH, 15 * TILEHEIGHT))

    def main(self):
        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.play_button = Button(self.screen, 'Play Game', 10 * TILEWIDTH, 29 * TILEHEIGHT, TILEHEIGHT, 9)
                self.score_button = Button(self.screen, 'High Score', 9.5 * TILEWIDTH, 32 * TILEHEIGHT, TILEHEIGHT, 10)
                self.image = pygame.image.load('pacman_title.png')
                self.screen.blit(self.image, (3 * TILEWIDTH, TILEHEIGHT))
                self.timer = pygame.time.get_ticks() / 1000
                self.main_screen_ani(self.timer)
                self.main_menu_sound.set_volume(0.2)
                self.main_menu_sound.play()
                self.play_button.draw()
                self.score_button.draw()
                self.checkEvents()
            elif self.gameScreen:
                game.startGame()
                self.main_menu_sound.stop()
                self.beginning_sound.set_volume(0.2)
                self.beginning_sound.play()
                while True:
                    game.update()
            elif self.hsScreen:
                self.screen.blit(self.background, (0, 0))
                self.row = 0
                self.font = pygame.font.Font("PressStart2P-vaV7.ttf", TILEHEIGHT)
                with open('high_scores.txt') as f:
                    for line in f:
                        temp_string = self.font.render(line, True, WHITE)
                        self.screen.blit(temp_string, (TILEWIDTH, self.row * TILEHEIGHT))
                self.back_button = Button(self.screen, 'Go back', 20 * TILEWIDTH, 29 * TILEHEIGHT, TILEHEIGHT, 7)
                self.back_button.draw()
                self.checkEvents()

            pygame.display.update()
            self.clock.tick(30)

if __name__ == "__main__":
    game = GameController()
    game.main()
