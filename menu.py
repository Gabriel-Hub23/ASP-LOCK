import pygame

class Menu():
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h, = self.game.DISPLAY_W/2, self.game.DISPLAY_H/2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20) #rectangle because we're using the arrow key
        self.offset = 150 #so it's on the left of our text
    
    def draw_cursor(self):
        self.game.draw_text('*', 25, self.cursor_rect.x+80, self.cursor_rect.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0)) #align display with window
        pygame.display.update() #moves image onto the screen
        self.game.reset_keys()

class MainMenu(Menu): #inherited Menu class
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Start" #point cursor at start
        self.startx, self.starty = self.mid_w, self.mid_h-55 #move height a bit down in the screen
        self.rulesx, self.rulesy = self.mid_w, self.mid_h-5 #move height a bit down in the screen
        self.creditsx, self.creditsy = self.mid_w, self.mid_h+45 #move height a bit down in the screen
        self.cursor_rect.midtop = (self.startx-self.offset, self.starty+4) #starting position of our cursor
        self.background_image = pygame.image.load("locknchase\\stuff\\bg_game.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))
    
    def display_menu(self):
        self.run_display = True #to make sure lol
        while self.run_display:
            self.game.check_events() #sets all the flags for the logic of cursor movement
            self.check_input()
            self.game.display.fill(self.game.screen_colour)
            self.game.display.blit(self.background_image, (0, 0))
            self.game.draw_text("Play", 35, self.startx, self.starty)
            self.game.draw_text("Rules", 35, self.rulesx, self.rulesy)
            self.game.draw_text("Credits", 35, self.creditsx, self.creditsy)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.rulesx-self.offset-13.5, self.rulesy+4)
                self.state = 'Rules'
            elif self.state == 'Rules':
                self.cursor_rect.midtop = (self.creditsx-self.offset-35.5, self.creditsy+4)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.startx-self.offset, self.starty+4)
                self.state = 'Start'
        elif self.game.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.creditsx-self.offset-35.5, self.creditsy+4)
                self.state = 'Credits'
            elif self.state == 'Rules':
                self.cursor_rect.midtop = (self.startx-self.offset, self.starty+4)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.rulesx-self.offset-13.5, self.rulesy+4)
                self.state = 'Rules'
            
    def check_input(self):
        self.move_cursor() #check if user wanted to move the cursor
        if self.game.START_KEY:
            if self.state == 'Start':
                #self.game.playing = True
                self.game.curr_menu = self.game.level_menu
            elif self.state == 'Rules':
                self.game.curr_menu = self.game.rules
            elif self.state == 'Credits':
                self.game.curr_menu = self.game.credits
            self.run_display = False #to make main menu stop displaying

class RulesMenu(Menu): #inherited Menu class
    def __init__(self, game):
        Menu.__init__(self, game)
        self.rules_image = pygame.image.load("locknchase\\stuff\\rules.png")
        self.rules_image = pygame.transform.scale(self.rules_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.screen_colour)
            self.game.display.blit(self.rules_image, (0, 0))
            self.blit_screen() #sets all flags back to false and displays screen

class CreditsMenu(Menu): #inherited Menu class
    def __init__(self, game):
        Menu.__init__(self, game)
        self.credits_image = pygame.image.load("locknchase\\stuff\\credits_game.png")
        self.credits_image = pygame.transform.scale(self.credits_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY or self.game.BACK_KEY: #way to send them back to the main menu
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.screen_colour)
            self.game.display.blit(self.credits_image, (0, 0))
            self.blit_screen() #sets all flags back to false and displays screen

class LevelMenu(Menu): #inherited Menu class
    def __init__(self, game):
        super().__init__(game) #same as Menu.__init__(self, game), but better actually
        self.state = "Level 1"
        self.level1x, self.level1y = self.mid_w, self.mid_h - 30
        self.level2x, self.level2y = self.mid_w, self.mid_h + 10
        self.level3x, self.level3y = self.mid_w, self.mid_h + 50
        self.cursor_rect.midtop = (self.level1x - self.offset, self.level1y + 4)
        self.selectlvl_image = pygame.image.load("locknchase\\stuff\\select_level.png")
        self.selectlvl_image = pygame.transform.scale(self.selectlvl_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.screen_colour)
            self.game.display.blit(self.selectlvl_image, (0, 0))
            #self.game.draw_text("Select Level", 35, self.mid_w, self.mid_h - 100)
            self.game.draw_text("Level 1", 30, self.level1x, self.level1y)
            self.game.draw_text("Level 2", 30, self.level2x, self.level2y)
            self.game.draw_text("Level 3", 30, self.level3x, self.level3y)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == "Level 1":
                self.state = "Level 2"
                self.cursor_rect.midtop = (self.level2x - self.offset, self.level2y + 4)
            elif self.state == "Level 2":
                self.state = "Level 3"
                self.cursor_rect.midtop = (self.level3x - self.offset, self.level3y + 4)
            elif self.state == "Level 3":
                self.state = "Level 1"
                self.cursor_rect.midtop = (self.level1x - self.offset, self.level1y + 4)
        elif self.game.UP_KEY:
            if self.state == "Level 1":
                self.state = "Level 3"
                self.cursor_rect.midtop = (self.level3x - self.offset, self.level3y + 4)
            elif self.state == "Level 2":
                self.state = "Level 1"
                self.cursor_rect.midtop = (self.level1x - self.offset, self.level1y + 4)
            elif self.state == "Level 3":
                self.state = "Level 2"
                self.cursor_rect.midtop = (self.level2x - self.offset, self.level2y + 4)
        
    def check_input(self):
        self.move_cursor()
        if self.game.BACK_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False
        elif self.game.START_KEY:
            if self.state == "Level 1":
                self.game.playing = True
            elif self.state == "Level 2":
                self.game.playing = True
                self.game.selected_level = 2
            elif self.state == "Level 3":
                self.game.playing = True
                self.game.selected_level = 3
            self.run_display = False

class GameOverMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.gameover_image = pygame.image.load("locknchase\\stuff\\game_over.png")
        self.gameover_image = pygame.transform.scale(self.gameover_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.screen_colour)
            self.game.display.blit(self.gameover_image, (0, 0))
            self.blit_screen() #sets all flags back to false and displays screen

class GameWonMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.gamewon_image = pygame.image.load("locknchase\\stuff\\game_won.png")
        self.gamewon_image = pygame.transform.scale(self.gamewon_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.screen_colour)
            self.game.display.blit(self.gamewon_image, (0, 0))
            self.blit_screen() #sets all flags back to false and displays screen