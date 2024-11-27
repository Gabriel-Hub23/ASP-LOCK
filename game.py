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

    def game_loop(self):
        while self.playing:
            self.check_events()
            if self.START_KEY: #player clicks to end
                self.playing = False
            #put canvas on screen
            self.display.fill(self.BLACK) #reset screen by filling it black (flipbook vibes)
            self.draw_text('Thanks for Playing', 20, self.DISPLAY_W/2, self.DISPLAY_H/2) #center of circle
            self.window.blit(self.display, (0, 0)) #align display with window
            pygame.display.update() #moves image onto the screen
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
