import pygame
from menu import *

class Game():
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = 960, 700#960, 540#480, 270
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode(((self.DISPLAY_W, self.DISPLAY_H)))
        #self.font_name = pygame.font.get_default_font()
        #self.font_name = "D:\VSCode Setup\Projects VSCode\8bit_wonder\8-BIT WONDER.TTF"
        #self.font_name = "D:\VSCode Setup\Projects VSCode\lock_n_chase/font\Money3D-mLA0a.ttf"
        self.font_name = "D:\VSCode Setup\Projects VSCode/bad-guy-black-font\BadGuyBlack-Pv4g.ttf"
        self.BLACK, self.WHITE = (245, 221, 203), (196, 125, 18)
        #blue: 197, 219, 237
        #black: 0, 0, 0 self.BLACK isn't black rn lol
        #white: 255, 255, 255 self.WHITE isn't white rn either
        self.main_menu = MainMenu(self)
        self.options = OptionsMenu(self)
        self.credits = CreditsMenu(self)
        self.curr_menu = self.main_menu
        #new:
        self.clock = pygame.time.Clock()

    def game_loop(self):
            #new:
        maze_game = MazeGame(self)
            #
        while self.playing:
            self.check_events()
            if self.START_KEY: #player clicks to end
                self.playing = False
            #put canvas on screen
            self.display.fill(self.BLACK) #reset screen by filling it black (flipbook vibes)
            maze_game.draw_maze()
            maze_game.draw_player()
            maze_game.handle_input()
            #self.draw_text('Thanks for Playing', 20, self.DISPLAY_W/2, self.DISPLAY_H/2) #center of circle
            self.window.blit(self.display, (0, 0)) #align display with window
            pygame.display.update() #moves image onto the screen
            #new:
            self.clock.tick(6) #speed
            #
            self.reset_keys()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #cross clicked
                self.running, self.playing = False, False
                self.curr_menu.run_display = False #stops runnning whatever menu was being displayed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: #enter key clicked
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE: #backspace clicked
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN: #down arrow pressed
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP: #up arrow pressed
                    self.UP_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE) #True is for anti-aliasing
        text_rect = text_surface.get_rect() #rectangle that will hold the text
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

class MazeGame:
    def __init__(self, game):
        self.game = game
        self.maze = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.player_pos = [1, 1]
        #self.enemy_pos = [3, 3]
        self.cell_size = 30
        self.player_image = pygame.image.load("D:\VSCode Setup\Projects VSCode\lock_n_chase\player_images\start.png")
        self.player_image = pygame.transform.scale(self.player_image, (self.cell_size, self.cell_size))

    def draw_maze(self):
        for row_index, row in enumerate(self.maze):
            for col_index, cell in enumerate(row):
                x, y = col_index*self.cell_size, row_index*self.cell_size
                color = (0,0,0) if cell == 1 else (255,255,255)
                pygame.draw.rect(self.game.display, color, (x, y, self.cell_size, self.cell_size))

    def draw_player(self):
        x, y = self.player_pos[1]*self.cell_size, self.player_pos[0]*self.cell_size
        #pygame.draw.rect(self.game.display, (0, 255, 0), (x, y, self.cell_size, self.cell_size))
        self.game.display.blit(self.player_image, (x, y))

    def handle_input(self):
        keys = pygame.key.get_pressed() #this function actually returns a series of boolean values xD
        if keys[pygame.K_w]: #up
            self.move_player(-1, 0)
        if keys[pygame.K_s]: #down
            self.move_player(1, 0)
        if keys[pygame.K_a]: #left
            self.move_player(0, -1)
        if keys[pygame.K_d]: #right
            self.move_player(0, 1)

    def move_player(self, row_offset, col_offset):
        new_x, new_y = self.player_pos[0]+row_offset, self.player_pos[1]+col_offset
        if self.maze[new_x][new_y] == 0:
            self.player_pos = [new_x, new_y]

    def game_loop(self):
        while self.game.playing:
            self.game.check_events()
            self.handle_input()
            self.game.display.fill((0,0,0)) #cls
            self.draw_maze()
            self.draw_player()
            pygame.display.update()
            self.game.reset_keys()