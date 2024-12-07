# #GAME.PY CODE
# #we are using manhattan distance in our game cz its grid based navigation meaning u could move up down right left (no diagonal moves(straight line like euclidean distance) allowed) hence a manhattan distance heuristic used in levels

import pygame
from menu import *
import time
import random
import math
import heapq

class Game():
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = 1280, 720
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode(((self.DISPLAY_W, self.DISPLAY_H)))
        self.font_name = "C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\NTBrickSans.ttf"
        self.BLACK, self.WHITE = (245, 221, 203), (196, 125, 18)
        #blue: 197, 219, 237
        #black: 0, 0, 0 self.BLACK isn't black rn lol
        #white: 255, 255, 255 self.WHITE isn't white rn either
        self.main_menu = MainMenu(self)
        self.rules = RulesMenu(self)
        self.credits = CreditsMenu(self)
        self.curr_menu = self.main_menu
        #new:
        self.clock = pygame.time.Clock()

        pygame.mixer.music.load("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\lock_n_chase_ost_stage1-1.mp3") #add mp3 file
        pygame.mixer.music.set_volume(0) #make it less maybe
        #pygame.mixer.music.play()
        pygame.mixer.music.play(loops=-1)

        #new:
        self.level_menu = LevelMenu(self)
        self.selected_level = 1 #default
       #NNN
    def game_loop(self):
        maze_game = MazeGame(self, level=self.selected_level)
        move_delay_silly = 0
        while self.playing:
            self.check_events()
            if self.BACK_KEY: #player clicks to end
                self.playing = False
            if maze_game.lives <= 0: #player game over -> go back to main menu ------------------------------------game won/lost screen?
                self.playing = False
                self.curr_menu = self.main_menu
                break
            #put canvas on screen
            self.display.fill(self.BLACK) #reset screen by filling it black (flipbook vibes)
            maze_game.update_lock()
            maze_game.draw_maze()
            maze_game.draw_silly()
            maze_game.draw_player()
            maze_game.handle_input_player()
            #dynamicaaly move silly 
            if maze_game.level == 1:
                if move_delay_silly % 1 == 0:  # itni movs k baad do simmulated annealing thing
                #maze_game.handle_input_silly_level1_simulated_annealing()
                    maze_game.handle_input_silly_level1_simulated_annealing()
                    move_delay_silly = 0
                move_delay_silly += 1
                #NNNNN
          
            elif maze_game.level == 2:
                print("I am in level 2")
                # This will continuously check if the path needs to be recalculated due to movement or obstacles.
                if maze_game.player_moved or maze_game.obstacle_changed or not maze_game.path:
                    #print("printing old path"+str(maze_game.path))
                    #print("Recalculating route because of dynamic changes.")
                    maze_game.path=None
                    maze_game.path = maze_game.a_star_search(tuple(maze_game.silly_pos), tuple(maze_game.player_pos))
                    maze_game.player_moved = False
                    maze_game.obstacle_changed = False
                    #print("New recalculated path:", maze_game.path)

                # Processing the current path
                if maze_game.path:
                    next_pos = maze_game.path.pop(0)
                    print("Player position:", maze_game.player_pos)
                    print("Attempting to move Silly to:", next_pos)
                    # Attempt to move Silly to the next position in the path
                    if not maze_game.move_silly_locks(next_pos):
                        print("Movement blocked due to locks, need to recalculate path.")
                        # Recalculate from current position to player position immediately
                        print("printing old path"+str(maze_game.path))
                        maze_game.path=None
                        maze_game.path = maze_game.a_star_search(tuple(maze_game.silly_pos), tuple(maze_game.player_pos))
                        print("New path after blockage:", maze_game.path)
                        if maze_game.path:
                            next_pos = maze_game.path.pop(0)
                            maze_game.move_silly_locks(next_pos)
                


            maze_game.check_collisions() 
            #if level == 1, then handle_silly_input_level1
            print("i am out of level loop now")
            #maze_game.check_collisions()
            #self.draw_text('Thanks for Playing', 20, self.DISPLAY_W/2, self.DISPLAY_H/2) #center of circle
            self.window.blit(self.display, (0, 0)) #align display with window
            pygame.display.update() #moves image onto the screen
            #new:
            self.clock.tick(2.5) #speed
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
    def __init__(self, game, level):
        self.game = game
        self.level = level
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
        self.player_image = pygame.image.load("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\lupin_colour-Photoroom.png")
        self.player_image = pygame.transform.scale(self.player_image, (self.cell_size, self.cell_size))

        self.silly_pos = [1, 1]
        self.silly_image = pygame.image.load("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\silly_colour.png")
        self.silly_image = pygame.transform.scale(self.silly_image, (self.cell_size, self.cell_size))

        self.coin_image = pygame.image.load("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\coin_colour.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (self.cell_size, self.cell_size))
        self.coin_sound = pygame.mixer.Sound("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\coin_sound_effect.mp3")
        self.coin_sound.set_volume(0.5)

        self.life_lost_sound = pygame.mixer.Sound("C:\\Users\\HP\Downloads\\LockNChase-main\stuff\\life_lost_sound.wav")
        self.life_lost_sound.set_volume(0.7)

        #dimensions and offsets of maze (will use these to place in centre)
        self.maze_width = len(self.maze[0]) * self.cell_size
        self.maze_height = len(self.maze) * self.cell_size
        self.x_offset = (self.game.DISPLAY_W - self.maze_width) // 2
        self.y_offset = (self.game.DISPLAY_H - self.maze_height) // 2

        #lvl 1 ??
        self.maze_image3 = pygame.image.load("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\lv1_3lives.png")
        self.maze_image3 = pygame.transform.scale(self.maze_image3, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image2 = pygame.image.load("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\lv1_2lives.png")
        self.maze_image2 = pygame.transform.scale(self.maze_image2, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image1 = pygame.image.load("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\lv1_1lives.png")
        self.maze_image1 = pygame.transform.scale(self.maze_image1, (self.game.DISPLAY_W, self.game.DISPLAY_H))

        #lock
        self.lock_pos = None #to store lock's position
        self.lock_timer = 0 #will remain ON 5 seconds
        self.lock_image = pygame.image.load("C:\\Users\\HP\\Downloads\\LockNChase-main\stuff\\lock.png")
        self.lock_image = pygame.transform.scale(self.lock_image, (self.cell_size, self.cell_size))


        # -------------- simulated annealing --------------
        #NNNNN
        self.temperature = 50.0 # now ive set it to a high value bcz i dont know how long the game is gonna keep runnning so i need a large value that would kind of sustain till end moves  
        self.cooling_factor = 0.99
        self.temperature_min = 0.01
        # -------------------------------------------------

        #-------------a_star+csp----------------------------
        #NNNNN
        self.path=[] #this is the shortest path silly would take to catch lupin 
        self.player_moved = False
        self.obstacle_changed = False

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
                   
        if self.lock_pos: #if placed/is not None
            lock_x = self.lock_pos[1] * self.cell_size + self.x_offset
            lock_y = self.lock_pos[0] * self.cell_size + self.y_offset
            self.game.display.blit(self.lock_image, (lock_x, lock_y))

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
        
        if keys[pygame.K_q]: #q for lock pressed
            self.place_lock()

    def place_lock(self):
        #NNNN
        if self.lock_pos is None and self.player_old_pos != self.silly_pos:
            self.lock_pos = self.player_old_pos[:] #shallow copy of list, separate object in memory
            self.lock_timer = time.time() #start timer
            self.obstacle_changed=True
            print(f"lock placed at: {self.lock_pos}")
    
    def update_lock(self):
        #NNNNN
        if self.lock_pos and time.time() - self.lock_timer >=8 : #5 seconds passed nabs changes it to 15 seconds 
            self.lock_pos = None
            self.obstacle_changed=False
            print(f"lock removed from: {self.lock_pos}")

    def check_collisions(self):
        print("i am in check collision function")
        print("player pos "+str(self.player_pos))
        print("silly pos "+str(self.silly_pos))
        
        if self.player_pos == self.silly_pos:
            self.life_lost_sound.play()
            self.lives -= 1 #lives--
            print(f"collided with silly. lives left: {self.lives}")
            #now reset positions:
            self.player_pos = [15, 1]
            self.silly_pos = [1, 1]
            #NNN
            self.path=None
            # if self.lives == 0: #check if lives r 0
            #     print("game over")
            #     self.game.playing = False

    def move_player(self, row_offset, col_offset):
        new_x, new_y = self.player_pos[0]+row_offset, self.player_pos[1]+col_offset
        if self.maze[new_x][new_y] != 1 and [new_x, new_y] != self.lock_pos: #cant go on wall and lock areas
            self.player_old_pos = self.player_pos[:] #shallow copy of list, separate object in memory
            self.player_pos = [new_x, new_y]
            #NNNN
            self.player_moved=True
            if self.maze[new_x][new_y] == 2: #check for coin
                self.player_score += 10
                self.maze[new_x][new_y] = 0 #remove coin from board basically
                self.coin_sound.play()
                
                print(f'score: {self.player_score}')

    def move_silly(self, row_offset, col_offset):
        new_x, new_y = self.silly_pos[0]+row_offset, self.silly_pos[1]+col_offset
        if self.maze[new_x][new_y] != 1 and [new_x, new_y] != self.lock_pos:
            self.silly_pos = [new_x, new_y]
        
    #-------------------------------- simulated annealing --------------------------------
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    #NNNNN
    def get_random_neighbor(self, current_pos):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        random.shuffle(directions) #generate koi bhi up down left right random movement for silly
        possible_positions = []
        for direction in directions:
            neighbor = [current_pos[0] + direction[0], current_pos[1] + direction[1]]
            if 0 <= neighbor[0] < len(self.maze) and 0 <= neighbor[1] < len(self.maze[0]):
                 # here i added check k do not overlap silly position with player cz simmulated annealing do be OVERPERFORMING
                #if self.maze[neighbor[0]][neighbor[1]] != 1 and neighbor != self.player_pos:
                # #the current pos is silly position 
                # self is lupin 
                if self.maze[neighbor[0]][neighbor[1]] != 1 and (self.lock_pos is None or not self.is_one_step_away((neighbor[0], neighbor[1]), self.lock_pos)):
                   # print(neighbor)
                    possible_positions.append(neighbor)
        return random.choice(possible_positions) if possible_positions else None
#NNNNN
    def is_one_step_away(self, pos, lock_pos): #lock is one step away from playa
        if lock_pos is None:
            return False
        x_diff = abs(pos[0] - lock_pos[0])
        y_diff = abs(pos[1] - lock_pos[1])
        print("lock pos"+str(lock_pos))
        print("silly pos" +str(pos))
        
    # One step away means either x_diff is 1 and y_diff is 0, or y_diff is 1 and x_diff is 0
        if (x_diff == 1 and y_diff == 0) or (y_diff == 1 and x_diff == 0):
            print("lock one step away detected ")
            return True
        else:
            return False
#NNNNN
    def handle_input_silly_level1_simulated_annealing(self):
        if self.temperature <= self.temperature_min:
            return  
        print("self.temperature"+str(self.temperature))
        current_pos = self.silly_pos
        current_cost = self.calculate_distance(current_pos, self.player_pos)

        neighbor = self.get_random_neighbor(current_pos)
        if neighbor is None:
            return  

        neighbor_cost = self.calculate_distance(neighbor, self.player_pos)
        if neighbor_cost < current_cost:
            self.silly_pos = neighbor  
        else:
            change_in_energy = neighbor_cost - current_cost
            if math.exp(-change_in_energy / self.temperature) > random.random():
                self.silly_pos = neighbor  

        self.temperature *= self.cooling_factor  
        #NNNNN
    #------------------------Astar+CSP-----------------------------------------------------------

    def a_star_search(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next in self.get_neighbors(current):
                if self.is_blocked(next):
                    continue
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        return self.reconstruct_path(came_from, start, goal)

    def heuristic(self, a, b):
        (x1, y1), (x2, y2) = a, b
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, pos):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = pos[0] + dx, pos[1] + dy
            if 0 <= nx < len(self.maze) and 0 <= ny < len(self.maze[0]) and not self.is_blocked((nx, ny)):
                neighbors.append((nx, ny))
        return neighbors

    def is_blocked(self, pos):
        x, y = pos
        #if self.maze[x][y] == 1 or (self.lock_pos is not None and self.is_one_step_away(pos, self.lock_pos)):
        if self.maze[x][y] == 1 :
            return True
            #print("walls or lock heyyyy")
        #if self.maze[x][y] == 1 :
        if self.lock_pos is not None and tuple(pos) == tuple(self.lock_pos):
            return True
        return False

    # def reconstruct_path(self, came_from, start, goal):
    #     current = goal
    #     path = []
    #     while current != start:
    #         path.append(current)
    #         current = came_from[current]
    #     path.reverse() #cz bactracking hum ney goal sey sillly tak ki hey
    #     #we need path from silly to goal
    #     return path
    def reconstruct_path(self, came_from, start, goal):
        current = tuple(goal)
        path = []
        while current != tuple(start):
            if current in came_from:
                path.append(list(current))  # Convert tuple back to list for consistency in your game
                current = came_from[current]
            else:
                # Handle the case where the path is incomplete or the goal/start is blocked
                print(f"Path reconstruction failed: {current} not reachable from {start}")
                return []  # Return an empty path or handle as needed
        path.reverse()
        return path

    def move_silly_locks(self, next_pos):
        if self.is_blocked(next_pos):
            #print(f"Blocked: Cannot move to {next_pos}")
            return False
        #if self.is_one_step_away(next_pos,self.lock_pos):
            #print(f"Blocked die to lock placed : Cannot move to {next_pos}")
         #   return False
        else:
            self.silly_pos = list(next_pos)
            #print(f"Moving Silly to {self.silly_pos}")
            return True

