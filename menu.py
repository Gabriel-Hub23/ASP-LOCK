import pygame

class Menu():
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h, = self.game.DISPLAY_W/2, self.game.DISPLAY_H/2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20) #rectangle because we're using the arrow key
        self.offset = 150 #so it's on the left of our text --change----------------------------------------------------------------------
    
    def draw_cursor(self):
        self.game.draw_text('*', 25, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0)) #align display with window
        pygame.display.update() #moves image onto the screen
        self.game.reset_keys()

class MainMenu(Menu): #inherited Menu class
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Start" #point cursor at start
        self.startx, self.starty = self.mid_w, self.mid_h-55 #move height a bit down in the screen
        self.optionsx, self.optionsy = self.mid_w, self.mid_h-5 #move height a bit down in the screen
        self.creditsx, self.creditsy = self.mid_w, self.mid_h+45 #move height a bit down in the screen
        self.cursor_rect.midtop = (self.startx-self.offset, self.starty+4) #starting position of our cursor
        self.background_image = pygame.image.load("locknchase\stuff/bg_game.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))
    
    def display_menu(self):
        self.run_display = True #to make sure lol
        while self.run_display:
            self.game.check_events() #sets all the flags for the logic of cursor movement
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.display.blit(self.background_image, (0, 0))
            self.game.draw_text("Start Game", 35, self.startx, self.starty)
            self.game.draw_text("Options", 35, self.optionsx, self.optionsy)
            self.game.draw_text("Credits", 35, self.creditsx, self.creditsy)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionsx-self.offset+45, self.optionsy+4)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx-self.offset+45, self.creditsy+4)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.startx-self.offset, self.starty+4)
                self.state = 'Start'
        elif self.game.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.creditsx-self.offset+45, self.creditsy+4)
                self.state = 'Credits'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx-self.offset, self.starty+4)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx-self.offset+45, self.optionsy+4)
                self.state = 'Options'
            
    def check_input(self):
        self.move_cursor() #check if user wanted to move the cursor
        if self.game.START_KEY:
            if self.state == 'Start':
                self.game.playing = True
            elif self.state == 'Options':
                self.game.curr_menu = self.game.options
            elif self.state == 'Credits':
                self.game.curr_menu = self.game.credits
            self.run_display = False #to make main menu stop displaying

class OptionsMenu(Menu): #inherited Menu class
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = 'Volume'
        self.volx, self.voly = self.mid_w, self.mid_h+20
        self.controlsx, self.controlsy = self.mid_w, self.mid_h+40
        self.cursor_rect.midtop = (self.volx+self.offset, self.voly)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text("Options", 20, self.game.DISPLAY_W/2, self.game.DISPLAY_H/2 - 30)
            self.game.draw_text("Volume", 15, self.volx, self.voly)
            self.game.draw_text("Controls", 15, self.controlsx, self.controlsy)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False #to change our menu at next iteration
        elif self.game.UP_KEY or self.game.DOWN_KEY:
            if self.state == 'Volume':
                self.state = 'Controls'
                self.cursor_rect.midtop = (self.controlsx+self.offset, self.controlsy)
            elif self.state == 'Controls':
                self.state = 'Volume'
                self.cursor_rect.midtop = (self.volx+self.offset, self.voly)
        elif self.game.START_KEY:
            pass #haven't made it yet (volume or control menu)

class CreditsMenu(Menu): #inherited Menu class
    def __init__(self, game):
        Menu.__init__(self, game)
        self.credits_image = pygame.image.load("locknchase\stuff\credits_game.png")
        self.credits_image = pygame.transform.scale(self.credits_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY or self.game.BACK_KEY: #way to send them back to the main menu
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.BLACK) #green is 203, 245, 203
            self.game.display.blit(self.credits_image, (0, 0))
            self.blit_screen() #sets all flags back to false and displays screen

