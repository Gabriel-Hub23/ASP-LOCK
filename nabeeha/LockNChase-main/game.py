#GAME.PY CODE
import pygame
from menu import *
#for simmulated annealing
import math
import random

class Game():
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = 1280, 720
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode(((self.DISPLAY_W, self.DISPLAY_H)))
        self.font_name = "C:\\Users\\HP/Downloads\\LockNChase-main/stuff\\NTBrickSans.ttf"
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

        pygame.mixer.music.load("C:\\Users\\HP\\Downloads\\LockNChase-main/stuff\\lock_n_chase_ost_stage1-1.mp3") #add mp3 file
        pygame.mixer.music.set_volume(0) #make it less maybe
        #pygame.mixer.music.play()
        pygame.mixer.music.play(loops=-1)
        
    
    def game_loop(self):
        maze_game = MazeGame(self)
        move_delay_silly = 0
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
            #dynamicaaly move silly 
            if move_delay_silly % 10 == 0:  # itni movs k baad do simmulated annealing thing
            #maze_game.handle_input_silly_level1_simulated_annealing()
                maze_game.step_simulated_annealing()
                move_delay_silly = 0
            move_delay_silly += 1
            maze_game.check_collisions()
            #self.draw_text('Thanks for Playing', 20, self.DISPLAY_W/2, self.DISPLAY_H/2) #center of circle
            self.window.blit(self.display, (0, 0)) #align display with window
            pygame.display.update() #moves image onto the screen
            #new:
            self.clock.tick(5) #speed
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
        #the 1s mean walls
        #the 2s mean coins
        #later the 0s will mean emmpty space . no wall , no coin
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
        self.cell_size = 36

        self.lives = 3
        self.player_pos = [15, 1]
        self.player_old_pos = [15, 2]
        self.player_score = 0
        self.player_image = pygame.image.load("C:\\Users\\HP/Downloads\\LockNChase-main/stuff\\lupin_colour-Photoroom.png")
        self.player_image = pygame.transform.scale(self.player_image, (self.cell_size, self.cell_size))

        self.silly_pos = [1, 1]
        self.silly_image = pygame.image.load("C:\\Users\\HP/Downloads\\LockNChase-main/stuff\silly_colour.png")
        self.silly_image = pygame.transform.scale(self.silly_image, (self.cell_size, self.cell_size))

        self.coin_image = pygame.image.load("C:\\Users\\HP/Downloads\\LockNChase-main/stuff\coin_colour.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (self.cell_size, self.cell_size))
        self.coin_sound = pygame.mixer.Sound("C:\\Users\\HP/Downloads\\LockNChase-main/stuff\coin_sound_effect.mp3")
        self.coin_sound.set_volume(0.5)

        self.life_lost_sound = pygame.mixer.Sound("C:\\Users\\HP/Downloads\\LockNChase-main/stuff\\life_lost_sound.wav")
        self.life_lost_sound.set_volume(0)

        #dimensions and offsets of maze (will use these to place in centre)
        self.maze_width = len(self.maze[0]) * self.cell_size
        self.maze_height = len(self.maze) * self.cell_size
        self.x_offset = (self.game.DISPLAY_W - self.maze_width) // 2
        self.y_offset = (self.game.DISPLAY_H - self.maze_height) // 2

        #lvl 1 ??
        self.maze_image3 = pygame.image.load("C:\\Users\\HP/Downloads\\LockNChase-main\stuff\\lv1_3lives.png")
        self.maze_image3 = pygame.transform.scale(self.maze_image3, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image2 = pygame.image.load("C:\\Users\\HP/Downloads\\LockNChase-main\stuff\\lv1_2lives.png")
        self.maze_image2 = pygame.transform.scale(self.maze_image2, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image1 = pygame.image.load("C:\\Users\\HP/Downloads\\LockNChase-main\stuff\\lv1_1lives.png")
        self.maze_image1 = pygame.transform.scale(self.maze_image1, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.temperature = 1.0  
        self.cooling_factor = 0.99
        self.temperature_min = 0.01


    def draw_maze(self):
        if self.lives == 3:
            self.game.display.blit(self.maze_image3, (0, 0))
        elif self.lives == 2:
            self.game.display.blit(self.maze_image2, (0, 0))
        elif self.lives == 1:
            self.game.display.blit(self.maze_image1, (0, 0))

        for row_index, row in enumerate(self.maze):
            for col_index, cell in enumerate(row):
                x = col_index * self.cell_size + self.x_offset
                y = row_index * self.cell_size + self.y_offset
                if cell == 2: #coin
                    self.game.display.blit(self.coin_image, (x, y))        
                    #print(f'cell printed at: {row_index}{col_index}')           
        self.game.draw_text(f'Score: {self.player_score}', size=24, x=1100, y=75)


    def draw_player(self):
        x, y = self.player_pos[1] * self.cell_size + self.x_offset, self.player_pos[0] * self.cell_size + self.y_offset
        self.game.display.blit(self.player_image, (x, y))
        #print('player printed')

    def draw_silly(self):
        x, y = self.silly_pos[1] * self.cell_size + self.x_offset, self.silly_pos[0] * self.cell_size + self.y_offset
        self.game.display.blit(self.silly_image, (x, y))
        #print('silly printed')

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

            #i need to make like a handle_inpt_silly
            #move silly


    def check_collisions(self):
        if self.player_pos == self.silly_pos:
            self.life_lost_sound.play()
            self.lives -= 1 #lives--
            print(f"collided with silly. lives left: {self.lives}")
            #now reset positions:
            self.player_pos = [15, 1]
            self.silly_pos = [1, 1]
            if self.lives == 0: #check if lives r 0
                print("game over")
                self.game.playing = False

    def move_player(self, row_offset, col_offset):
        new_x, new_y = self.player_pos[0]+row_offset, self.player_pos[1]+col_offset
        if self.maze[new_x][new_y] == 0:
            self.player_old_pos = self.player_pos[:] #shallow copy of list, separate object in memory
            self.player_pos = [new_x, new_y]
        elif self.maze[new_x][new_y] == 2:
            self.player_old_pos = self.player_pos[:] #shallow copy of list, separate object in memory
            self.player_pos = [new_x, new_y]
            self.player_score += 10
            self.maze[new_x][new_y] = 0
            self.coin_sound.play()
            print(f'score: {self.player_score}')
        

    def move_silly(self, row_offset, col_offset):
        new_x, new_y = self.silly_pos[0]+row_offset, self.silly_pos[1]+col_offset
        if self.maze[new_x][new_y] == 0: #0 means an available space no coin nothing
            self.silly_pos = [new_x, new_y]
        elif self.maze[new_x][new_y] == 2: #coin hey 
            self.silly_pos = [new_x, new_y]

        

        pass
    
    # def game_loop(self):
    #     while self.game.playing:
    #         self.game.check_events()
    #         self.handle_input_player()
    #         self.game.display.fill((0, 0, 0)) #cls
    #         self.draw_maze()
    #         self.draw_player()
    #         self.draw_silly()
    #         pygame.display.update()
    #         #self.clock.tick(6) #control frame rate
    #         self.game.reset_keys()

#handle_input_silly_level1()
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    
    def get_random_neighbor(self, current_pos):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        random.shuffle(directions) #generate koi bhi up down left right random movement for silly
        possible_positions = []
        for direction in directions:
            neighbor = [current_pos[0] + direction[0], current_pos[1] + direction[1]]
            if 0 <= neighbor[0] < len(self.maze) and 0 <= neighbor[1] < len(self.maze[0]):
                 # here i added check k do not overlap silly position with player cz simmulated annealing do be OVERPERFRMING
                #if self.maze[neighbor[0]][neighbor[1]] != 1 and neighbor != self.player_pos: 
                if self.maze[neighbor[0]][neighbor[1]] != 1 :
                   # print(neighbor)
                    possible_positions.append(neighbor)
        return random.choice(possible_positions) if possible_positions else None


    def step_simulated_annealing(self):
        if self.temperature <= self.temperature_min:
            return  # Exit if the temperature has cooled down enough

        current_pos = self.silly_pos
        current_cost = self.calculate_distance(current_pos, self.player_pos)

        neighbor = self.get_random_neighbor(current_pos)
        if neighbor is None:
            return  # Skip if no valid moves

        neighbor_cost = self.calculate_distance(neighbor, self.player_pos)
        if neighbor_cost < current_cost:
            self.silly_pos = neighbor  # Move to better position
        else:
            change_in_energy = neighbor_cost - current_cost
            if math.exp(-change_in_energy / self.temperature) > random.random():
                self.silly_pos = neighbor  # Move to worse position probabilistically

        self.temperature *= self.cooling_factor  # Cool down


    def handle_input_silly_level1_simulated_annealing(self):
        
        current_pos = self.silly_pos
        print("current silly pos "+str(current_pos))
        current_cost = self.calculate_distance(current_pos, self.player_pos)
        print("current silly pos "+str(current_cost))
        temperature = 1.0
        temperature_min = 0.01
        cooling_factor = 0.99

        while temperature > temperature_min:
            neighbor = self.get_random_neighbor(current_pos)
            if neighbor is None:
                continue
            neighbor_cost = self.calculate_distance(neighbor, self.player_pos)

            if neighbor_cost < current_cost:
                current_pos = neighbor
                current_cost = neighbor_cost
            else:
                change_in_energy = neighbor_cost - current_cost
                if math.exp(-change_in_energy / temperature) > random.random():
                    current_pos = neighbor
                    current_cost = neighbor_cost

            temperature *= cooling_factor
        
        self.silly_pos = current_pos
