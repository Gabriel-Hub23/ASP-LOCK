import pygame
from menu import *

class Game():
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = 1280, 720#960, 700#960, 540#480, 270
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode(((self.DISPLAY_W, self.DISPLAY_H)))
        #self.font_name = pygame.font.get_default_font()
        #self.font_name = "D:\VSCode Setup\Projects VSCode\8bit_wonder\8-BIT WONDER.TTF"
        #self.font_name = "D:\VSCode Setup\Projects VSCode\lock_n_chase/font\Money3D-mLA0a.ttf"
        #self.font_name = "D:\VSCode Setup\Projects VSCode/bad-guy-black-font\BadGuyBlack-Pv4g.ttf"
        self.font_name = "locknchase\stuff/NTBrickSans.ttf"
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

        pygame.mixer.music.load("locknchase\stuff\lock_n_chase_ost_stage1-1.mp3") #add mp3 file
        pygame.mixer.music.set_volume(0.2)
        #pygame.mixer.music.play()
        pygame.mixer.music.play(loops=-1)

       
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
            maze_game.draw_silly()
            maze_game.draw_player()
            maze_game.handle_input_player()
            #self.draw_text('Thanks for Playing', 20, self.DISPLAY_W/2, self.DISPLAY_H/2) #center of circle
            self.window.blit(self.display, (0, 0)) #align display with window
            pygame.display.update() #moves image onto the screen
            #new:
            self.clock.tick(7) #speed
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
        text_surface = font.render(text, True, (0, 0, 0)) #True is for anti-aliasing. using black for text
        text_rect = text_surface.get_rect() #rectangle that will hold the text
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

class MazeGame:
    def __init__(self, game):
        self.game = game
        self.maze = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 1, 2, 1],
            [1, 2, 2, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1],
            [1, 2, 1, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1],
            [1, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 1],
            [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 1, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        #new:
        #self.clock = pygame.time.Clock()
        self.cell_size = 31

        self.player_pos = [1, 1]
        self.player_score = 0
        self.player_image = pygame.image.load("locknchase\stuff\lupin_colour-Photoroom.png")
        self.player_image = pygame.transform.scale(self.player_image, (self.cell_size, self.cell_size))

        self.silly_pos = [1, 2]
        self.silly_image = pygame.image.load("locknchase\stuff\silly_colour.png")
        self.silly_image = pygame.transform.scale(self.silly_image, (self.cell_size, self.cell_size))

        self.coin_image = pygame.image.load("locknchase\stuff\coin_colour.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (self.cell_size, self.cell_size))
        self.coin_sound = pygame.mixer.Sound("locknchase\stuff\coin_sound_effect.mp3")
        self.coin_sound.set_volume(0.5)

        #dimensions and offsets of maze (will use these to place in centre)
        self.maze_width = len(self.maze[0]) * self.cell_size
        self.maze_height = len(self.maze) * self.cell_size
        self.x_offset = (self.game.DISPLAY_W - self.maze_width) // 2
        self.y_offset = (self.game.DISPLAY_H - self.maze_height) // 2

        self.maze_image = pygame.image.load("locknchase\stuff\maze_qm.png")
        self.maze_image = pygame.transform.scale(self.maze_image, (self.game.DISPLAY_W, self.game.DISPLAY_H))



    # def draw_maze(self):
    #     for row_index, row in enumerate(self.maze):
    #         for col_index, cell in enumerate(row):
    #             x = col_index * self.cell_size + self.x_offset
    #             y = row_index * self.cell_size + self.y_offset
    #             if cell == 1:
    #                 pygame.draw.rect(self.game.display, (99, 168, 89), (x, y, self.cell_size, self.cell_size))
    #                 pygame.draw.rect(self.game.display, (34, 128, 20), (x, y, self.cell_size, self.cell_size), width=1)
    #                 offset = self.cell_size // 4 #to draw X in the rectangles which r actually squares lol
    #                 pygame.draw.line(self.game.display, (79, 130, 72), (x + offset, y + offset), (x + self.cell_size - offset, y + self.cell_size - offset), 2)
    #                 pygame.draw.line(self.game.display, (79, 130, 72), (x + self.cell_size - offset, y + offset), (x + offset, y + self.cell_size - offset), 2)
    #             elif cell == 0:
    #                 colour = (245, 221, 203)
    #                 pygame.draw.rect(self.game.display, colour, (x, y, self.cell_size, self.cell_size))
    #             elif cell == 2: #coin
    #                 self.game.display.blit(self.coin_image, (x, y))        
    #                 print(f'cell printed at: {row_index}{col_index}')           
    #     self.game.draw_text(f'Score: {self.player_score}', size=24, x=200, y=600)

    def draw_maze(self):
        # Draw the maze walls using the background image
        #self.game.display.blit(self.maze_image, (self.x_offset, self.y_offset))
        self.game.display.blit(self.maze_image, (0, 0))
        # Overlay coins and other game elements
        for row_index, row in enumerate(self.maze):
            for col_index, cell in enumerate(row):
                x = col_index * self.cell_size + self.x_offset
                y = row_index * self.cell_size + self.y_offset

                if cell == 2:  # Coin
                    self.game.display.blit(self.coin_image, (x, y))
                    print(f'Coin placed at: {row_index}, {col_index}')

        # Display the score (adjust the position as needed)
        self.game.draw_text(f'Score: {self.player_score}', size=24, x=200, y=600)


    def draw_player(self):
        x, y = self.player_pos[1]*self.cell_size + self.x_offset, self.player_pos[0]*self.cell_size + self.y_offset
        #pygame.draw.rect(self.game.display, (0, 255, 0), (x, y, self.cell_size, self.cell_size))
        self.game.display.blit(self.player_image, (x, y))
        print('player printed')

    def draw_silly(self):
        x, y = self.silly_pos[1] * self.cell_size + self.x_offset, self.silly_pos[0] * self.cell_size + self.y_offset
        self.game.display.blit(self.silly_image, (x, y))
        print('silly printed')

    def handle_input_player(self):
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
        elif self.maze[new_x][new_y] == 2:
            self.player_pos = [new_x, new_y]
            self.player_score += 10
            self.maze[new_x][new_y] = 0
            self.coin_sound.play()
            print(f'score: {self.player_score}')

    def move_silly(self, row_offset, col_offset):
        new_x, new_y = self.silly_pos[0]+row_offset, self.silly_pos[1]+col_offset
        if self.maze[new_x][new_y] == 0:
            self.silly_pos = [new_x, new_y]
        elif self.maze[new_x][new_y] == 2:
            self.silly_pos = [new_x, new_y]

        # elif == players coords, then player's lives-- same but opposite condition will also be applied to the player

        pass
    
    def game_loop(self):
        while self.game.playing:
            self.game.check_events()
            self.handle_input_player()
            self.game.display.fill((0, 0, 0)) #cls
            self.draw_maze()
            self.draw_player()
            self.draw_silly()
            pygame.display.update()
            #self.clock.tick(6) #control frame rate
            self.game.reset_keys()
