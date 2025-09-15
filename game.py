import pygame
from menu import *
import time
import random
import math
import heapq
import copy
import os
import time
from ASP.EMBASP.lnc_solver import SolverLNC
from ASP.EMBASP.predicates import *
from os_checker import os_checker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
program = os_checker();
DLV2_PATH = r"ASP/DLV/{}".format(program)
ENCODING_PATH = r"ASP/encoding/aiGabriel.asp"


class Game():
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = 1280, 720
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode(((self.DISPLAY_W, self.DISPLAY_H)))
        self.font_name = "stuff/NTBrickSans.ttf"
        self.screen_colour = (245, 221, 203)
        self.main_menu = MainMenu(self)
        self.rules = RulesMenu(self)
        self.credits = CreditsMenu(self)
        self.gameover_menu = GameOverMenu(self)
        self.gamewon_menu = GameWonMenu(self)
        self.curr_menu = self.main_menu
        
        self.clock = pygame.time.Clock()

        pygame.mixer.music.load("stuff/lock_n_chase_ost_stage1-1.mp3") #add mp3 file
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(loops=-1) #-1 means run indefinitely

        self.level_menu = LevelMenu(self)
        self.selected_level = 1 #default

    
    def game_loop(self):
        maze_game = MazeGame(self, level=self.selected_level)
        player_move_timer = 0
        silly_move_timer = 0
        player_delay = 5+0+1.5
        silly_delay = 5+5+1.5


        while self.playing:
            self.check_events()
            if self.BACK_KEY:
                self.playing = False
            if maze_game.lives <= 0:
                maze_game.gameover_sfx.play()
                self.playing = False
                self.curr_menu = self.gameover_menu
                break
            if maze_game.player_score == 1480:
                maze_game.gamewon_sfx.play()
                self.playing = False
                self.curr_menu = self.gamewon_menu
                break

            self.display.fill(self.screen_colour)

            maze_game.update_lock()
            maze_game.draw_maze()
            maze_game.draw_lock(self.display) 
            maze_game.draw_player()
            maze_game.draw_silly()

            if player_move_timer >= player_delay:
                maze_game.handle_input_player()
                player_move_timer = 0

            if silly_move_timer >= silly_delay:
                maze_game.move_silly_with_asp()
                silly_move_timer = 0 


            player_move_timer += 1
            silly_move_timer += 1
            maze_game.check_collisions()
            self.window.blit(self.display, (0, 0))
            pygame.display.update()
            self.clock.tick(30) #fps 
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
                if event.key == pygame.K_s: #S pressed
                    self.DOWN_KEY = True
                if event.key == pygame.K_w: #W pressed
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

        self.rows = len(self.maze)
        self.cols = len(self.maze[0]) if self.rows else 0
       # (x=colonna, y=riga) — coerente con l’ASP: up = (x, y-1)
        # Costruisci i muri con coordinate corrette (x=colonna, y=riga)
        self.walls = [(j, i) for i, row in enumerate(self.maze) for j, v in enumerate(row) if v == 1]

        self.ai = SolverLNC(DLV2_PATH, ENCODING_PATH, debug=False)


        # 2.2) Set rapido per controlli muro (una volta sola)
        # normalizziamo walls_set in formato (row, col) perché le posizioni (player_pos/silly_pos)
        # sono memorizzate come [row, col] nel resto del codice
        self.walls_set = set((int(y), int(x)) for (x, y) in self.walls)

        # 2.3) Dimensioni cella (se non le hai già)
        self.cell_w = getattr(self, "cell_w", 16)
        self.cell_h = getattr(self, "cell_h", 16)
                

        #self.asp.set_static(self.rows, self.cols, self.walls)
        self.tick = 0

        self.cell_size = 36

        self.lives = 3
        self.player_pos = [15, 1]
        self.player_old_pos = [15, 2]
        self.player_score = 0
        self.player_image = pygame.image.load("stuff/lupin_colour-Photoroom.png")
        self.player_image = pygame.transform.scale(self.player_image, (self.cell_size, self.cell_size))

        self.silly_pos = [1, 1]
        self.silly_image = pygame.image.load("stuff/silly_colour.png")
        self.silly_image = pygame.transform.scale(self.silly_image, (self.cell_size, self.cell_size))

        # posizione precedente del nemico (usata dall'ASP come prev(X,Y))
        self.prev_silly_pos = None

        self.coin_image = pygame.image.load("stuff/coin_colour.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (self.cell_size, self.cell_size))
        self.coin_sound = pygame.mixer.Sound("stuff/coin_sound_effect.mp3")
        self.coin_sound.set_volume(0.5)

        self.life_lost_sound = pygame.mixer.Sound("stuff/life_lost_sound.wav")
        self.life_lost_sound.set_volume(0.7)

        self.gamewon_sfx =  pygame.mixer.Sound("stuff/game_won_sfx.wav")
        self.life_lost_sound.set_volume(0.3)
        self.gameover_sfx = pygame.mixer.Sound("stuff/game_over_sfx.wav")
        self.life_lost_sound.set_volume(0.3)

        #dimensions and offsets of maze (will use these to place in centre)
        self.maze_width = len(self.maze[0]) * self.cell_size
        self.maze_height = len(self.maze) * self.cell_size
        self.x_offset = (self.game.DISPLAY_W - self.maze_width) // 2
        self.y_offset = (self.game.DISPLAY_H - self.maze_height) // 2

        #lvl 1:
        self.maze_image3_lvl1 = pygame.image.load("stuff/lv1_3lives.png")
        self.maze_image3_lvl1 = pygame.transform.scale(self.maze_image3_lvl1, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image2_lvl1 = pygame.image.load("stuff/lv1_2lives.png")
        self.maze_image2_lvl1 = pygame.transform.scale(self.maze_image2_lvl1, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image1_lvl1 = pygame.image.load("stuff/lv1_1lives.png")
        self.maze_image1_lvl1 = pygame.transform.scale(self.maze_image1_lvl1, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        #lvl 2:
        self.maze_image3_lvl2 = pygame.image.load("stuff/lv2_3lives.png")
        self.maze_image3_lvl2 = pygame.transform.scale(self.maze_image3_lvl2, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image2_lvl2 = pygame.image.load("stuff/lv2_2lives.png")
        self.maze_image2_lvl2 = pygame.transform.scale(self.maze_image2_lvl2, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image1_lvl2 = pygame.image.load("stuff/lv2_1lives.png")
        self.maze_image1_lvl2 = pygame.transform.scale(self.maze_image1_lvl2, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        #lvl 3:
        self.maze_image3_lvl3 = pygame.image.load("stuff/lv3_3lives.png")
        self.maze_image3_lvl3 = pygame.transform.scale(self.maze_image3_lvl3, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image2_lvl3 = pygame.image.load("stuff/lv3_2lives.png")
        self.maze_image2_lvl3 = pygame.transform.scale(self.maze_image2_lvl3, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        self.maze_image1_lvl3 = pygame.image.load("stuff/lv3_1lives.png")
        self.maze_image1_lvl3 = pygame.transform.scale(self.maze_image1_lvl3, (self.game.DISPLAY_W, self.game.DISPLAY_H))

        #lock things:
        self.lock_pos = None #to store lock's position
        self.lock_timer = 0 #will remain ON 5 seconds
        self.lock_image = pygame.image.load("stuff/lock.png")
        self.lock_image = pygame.transform.scale(self.lock_image, (self.cell_size, self.cell_size))

        # -------------- simulated annealing --------------
        self.temperature = 50.0 # now ive set it to a high value bcz i dont know how long the game is gonna keep runnning so i need a large value that would kind of sustain till end moves  
        self.cooling_factor = 0.99
        self.temperature_min = 0.01
        # ------------------- a* + csp --------------------
        self.path=[] #this is the shortest path silly would take to catch lupin 
        self.player_moved = False
        self.obstacle_changed = False
        # --------- minimax + alpha beta pruning ----------
        self.move_history = []
            
    def apply_ai_move(self, move):
        """Applica la mossa dell'AI (stringa o numero). Aggiorna posizione e sprite del nemico."""
        # accetta sia stringhe sia numeri (0..3)
        dir_map = {"0":"up","1":"right","2":"down","3":"left", 0:"up",1:"right",2:"down",3:"left"}
        move = dir_map.get(move, move)  # normalizza in 'up/down/left/right'

        # usa (row, col) — up = row-1, down = row+1, left = col-1, right = col+1
        delta = {"up":(-1,0), "down":(1,0), "left":(0,-1), "right":(0,1)}
        dr, dc = delta.get(move, (0,0))

        row, col = map(int, self.silly_pos)
        nrow, ncol = row + dr, col + dc

        # blocco su muro: non muovere ma stampa (debug chiaro)
        if (nrow, ncol) in self.walls_set:
            print(f"[AI] Move '{move}' bloccata da wall @ {(nrow,ncol)}. Pos attuale={self.silly_pos}")
            return

        # salva posizione precedente prima di aggiornare
        self.prev_silly_pos = self.silly_pos[:]

        # aggiorna posizione logica (manteniamo lista come il codice originale)
        self.silly_pos = [nrow, ncol]

        # aggiorna sprite/rect se esiste (usando offset e cell_size)
        if hasattr(self, "silly_rect"):
            self.silly_rect.topleft = (self.x_offset + ncol * self.cell_size, self.y_offset + nrow * self.cell_size)

        print(f"[AI] MOVE({move}) -> {self.silly_pos}")


    # dentro la classe MazeGame

    def update_lock(self):
        """Aggiorna il lucchetto: countdown e sblocco cella quando scade."""
        # se non c'è un lock attivo → niente da fare
        if self.lock_pos is None:
            return

        # scala il timer
        self.lock_timer -= 1
        if self.lock_timer <= 0:
            # disattiva il lock
            self.lock_pos = None
            self.lock_timer = 0

    def place_lock(self, grid_x, grid_y, duration_frames=150):
        """Attiva un lock su una cella di griglia (grid_x, grid_y) per 'duration_frames' frame."""
        # evita di mettere lock sui muri
        if (int(grid_x), int(grid_y)) in self.walls_set:
            return
        self.lock_pos = (int(grid_x), int(grid_y))
        self.lock_timer = int(duration_frames)

    def draw_lock(self, surface=None):
        """Disegna il lock (se attivo)."""
        if self.lock_pos is None:
            return
        if surface is None:
            surface = self.game.display  # o self.game.display/screen a seconda del tuo codice
        x, y = self.lock_pos
        surface.blit(self.lock_image, (self.x_offset + x * self.cell_size,
                                    self.y_offset + y * self.cell_size))


    def draw_maze(self):
        if self.level == 1:
            if self.lives == 3:
                self.game.display.blit(self.maze_image3_lvl1, (0, 0))
            elif self.lives == 2:
                self.game.display.blit(self.maze_image2_lvl1, (0, 0))
            elif self.lives == 1:
                self.game.display.blit(self.maze_image1_lvl1, (0, 0))
        elif self.level == 2:
            if self.lives == 3:
                self.game.display.blit(self.maze_image3_lvl2, (0, 0))
            elif self.lives == 2:
                self.game.display.blit(self.maze_image2_lvl2, (0, 0))
            elif self.lives == 1:
                self.game.display.blit(self.maze_image1_lvl2, (0, 0))
        elif self.level == 3:
            if self.lives == 3:
                self.game.display.blit(self.maze_image3_lvl3, (0, 0))
            elif self.lives == 2:
                self.game.display.blit(self.maze_image2_lvl3, (0, 0))
            elif self.lives == 1:
                self.game.display.blit(self.maze_image1_lvl3, (0, 0))

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

        self.game.draw_text(f'Score: {self.player_score}', size=24, x=1100, y=510)


    def move_silly_with_asp(self):
        # passa lo stato corrente all’AI
        self.ai.set_state(self_pos=self.silly_pos, player_pos=self.player_pos, walls=self.walls, prev_pos=self.prev_silly_pos, rows_cols=(self.rows, self.cols))
        # prepara il bundle e le opzioni
        self.ai.startAsp()
        # prendi la mossa (stringa 'up'.. o numero '0'..)
        move = self.ai.recallAsp()
        print(f"Mossa scelta: {move}")
        # applica davvero la mossa al nemico
        self.apply_ai_move(move)


        '''
        dyn = self._asp_dynamic_facts()
       
        sx, sy = self.silly_pos[0], self.silly_pos[1]
        px, py = self.player_pos[0], self.player_pos[1]
        locks = getattr(self, "lock_cells", []) or getattr(self, "current_locks", [])
        nxt = self.asp.decide_move((sx, sy), (px, py), locks)


        self.tick += 1
        if nxt is None:
            print("NO_MOVE_FROM_SOLVER")
            return False
        nx, ny = nxt
        print(f"MOVE({nx},{ny})")  # conferma che IDLV ha risposto
        self.last_silly_pos = self.silly_pos[:]   # salva per pos_silly_prev
        if not self.is_blocked((nx, ny)):
            self.silly_pos = [nx, ny]
            return True
        print("SOLVER_MOVE_BLOCKED")
        return False
        '''

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
        if self.lock_pos is None and self.player_old_pos != self.silly_pos:
            self.lock_pos = self.player_old_pos[:] #shallow copy of list, separate object in memory
            self.lock_timer = time.time() #start timer
            self.obstacle_changed=True
    
    def update_lock(self):
        if self.lock_pos and time.time() - self.lock_timer >= 5: #5 seconds passed
            self.lock_pos = None
            self.obstacle_changed=False

    def check_collisions(self):
        if self.player_pos == self.silly_pos:
            self.life_lost_sound.play()
            self.lives -= 1 #lives--
            #now reset positions:
            self.lock_pos=None
            self.player_pos = [15, 1]
            self.silly_pos = [1, 1]
            self.path=None

    def move_silly(self, row_offset, col_offset):
        new_x, new_y = self.silly_pos[0]+row_offset, self.silly_pos[1]+col_offset
        if self.maze[new_x][new_y] != 1 and [new_x, new_y] != self.lock_pos:
            self.silly_pos = [new_x, new_y]

    def move_player(self, row_offset, col_offset):
        new_x, new_y = self.player_pos[0] + row_offset, self.player_pos[1] + col_offset
        if self.maze[new_x][new_y] != 1 and [new_x, new_y] != self.lock_pos:
            self.player_old_pos = self.player_pos[:]
            self.player_pos = [new_x, new_y]
            self.player_target_pos = [new_x, new_y]
            self.player_moved=True
            if self.maze[new_x][new_y] == 2:
                self.player_score += 10
                self.maze[new_x][new_y] = 0
                self.coin_sound.play()

    # --------------------------------- simulated annealing ----------------------------------

    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_random_neighbor(self, current_pos):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        random.shuffle(directions) #generate koi bhi up down left right random movement for silly
        possible_positions = []
        for direction in directions:
            neighbor = [current_pos[0] + direction[0], current_pos[1] + direction[1]]
            if 0 <= neighbor[0] < len(self.maze) and 0 <= neighbor[1] < len(self.maze[0]):
                # here i added check k do not overlap silly position with player cz simmulated annealing do be OVERPERFORMING
                # the current pos is silly position 
                # self is lupin 
                if self.maze[neighbor[0]][neighbor[1]] != 1 and (self.lock_pos is None or not self.is_one_step_away((neighbor[0], neighbor[1]), self.lock_pos)):
                    # print(neighbor)
                    possible_positions.append(neighbor)
        return random.choice(possible_positions) if possible_positions else None

    def is_one_step_away(self, pos, lock_pos): #lock is one step away from playa
        if lock_pos is None:
            return False
        x_diff = abs(pos[0] - lock_pos[0])
        y_diff = abs(pos[1] - lock_pos[1])
    
        # One step away means either x_diff is 1 and y_diff is 0, or y_diff is 1 and x_diff is 0
        if (x_diff == 1 and y_diff == 0) or (y_diff == 1 and x_diff == 0):
            return True
        else:
            return False

    def handle_input_silly_level1_simulated_annealing(self):
        if self.temperature <= self.temperature_min:
            return  
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
        
    # -------------------------------------- A* + CSP ----------------------------------------

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
        if self.maze[x][y] == 1 :
            return True
            #print("walls or lock heyyyy")
        if self.lock_pos is not None and tuple(pos) == tuple(self.lock_pos):
            return True
        return False

    def reconstruct_path(self, came_from, start, goal):
        current = tuple(goal)
        path = []
        while current != tuple(start):
            if current in came_from:
                path.append(list(current))  #Convert tuple back to list for consistency in game
                current = came_from[current]
            else:
                #handle the case where the path is incomplete or the goal/start is blocked
                return []  #return an empty path
        path.reverse()
        return path

    def move_silly_locks(self, next_pos):
        if self.is_blocked(next_pos):
            return False
        else:
            self.silly_pos = list(next_pos)
            return True
    
    # ------------------- minimax + alpha beta pruning (depth limited) -----------------------

    def evaluate_position(self): #evaluation function , returns basically a score how good a move is 
        if self.player_pos == self.silly_pos: #a v v v large amazing value if it leads to catching lupin
            return float('inf') 
        else:#find manhattan distance bw lupin and silly
            distance_to_lupin = abs(self.silly_pos[0] - self.player_pos[0]) + abs(self.silly_pos[1] - self.player_pos[1])
            # we are also keeping track of coins collected aka the player score towards evaluation 
            #returning a negative value cz silly is minimizing the distance , and overall maximizing the evaluation score
            #jinta silly is close to lupin  utna better score 
            return -distance_to_lupin - (0.5 * self.player_score)
        
    def get_all_possible_moves(self):
        possible_moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        for direction in directions:
            new_pos = [self.silly_pos[0] + direction[0], self.silly_pos[1] + direction[1]] 
            #ake sure that when generating moves hum khyaal rakhen of walls and locks
            if 0 <= new_pos[0] < len(self.maze) and 0 <= new_pos[1] < len(self.maze[0]) and self.maze[new_pos[0]][new_pos[1]] != 1 and (self.lock_pos is None or tuple(new_pos) != tuple(self.lock_pos)):
                possible_moves.append(new_pos)
        return possible_moves 
    
    def minimax(self, depth, alpha, beta, is_maximizing):
        if depth == 0 or self.game_over():
            return self.evaluate_position()
        if is_maximizing:#AI tuern aka SILLY turn 
            max_eval = float('-inf')
            for move in self.get_all_possible_moves():
                # we cant simulate moves on roiginal game cz we have not yet decided best move yet
                #hence creating a clone of current game state , later well restore the game state too
                new_game = self.clone_state()
                new_game.silly_pos = move #simulate move on silly
                #create all counter moves of human is_maximizing=False
                eval = new_game.minimax(depth - 1, alpha, beta, False)
                #keep track of best move saath saaath , like update if a behter move found at ebery iteration
                max_eval = max(max_eval, eval)
                #alpha picks the larger value move everytime
                alpha = max(alpha, eval)
                if beta <= alpha: #pruning condition , iss sey neechey tree explore karney ki zarooorat hi nahi , cz jitna acha score aa chuka iss sey kam hi aaye ga , iss sey zyaada aa hi nahi sakta
                    break
            return max_eval
        else: #is_maximizing=False   ###its Human Player (lupin's) turn
            min_eval = float('inf')
            for move in self.get_all_possible_moves():
                new_game = self.clone_state()
                new_game.silly_pos = move
                #human k liye counter AI moves check and pick best move human could make (hehe then later on well counter this human move too in best move function)
                eval = new_game.minimax(depth - 1, alpha, beta, True) #True for AI move 
                min_eval = min(min_eval, eval)
                #beta always picks the lower value side
                beta = min(beta, eval)
                if alpha >= beta:
                    break
            return min_eval
   
    def best_move(self, depth, is_maximizing):
        alpha= float('-inf') #next alpha(max value) iss sey to kam hi ho ga
        beta= float('inf') #next beta (min vlaue) iss sey to zyaada hi ho gi 
        best_score = float('-inf') if is_maximizing else float('inf')
        best_move = None
        #aik dafa run is_maximizing code yahan bhi , this actually like initiates the gae tree ka root , yahan sey neechey game tree generate hota hey
        for move in self.get_all_possible_moves():
            cloned_game = self.clone_state()
            cloned_game.silly_pos = move
            score = cloned_game.minimax(depth - 1, alpha, beta, not is_maximizing)
            #agar this move is already in the move history 
            #penalize it by reducing its score -1 so that baar baar same move na li jaaye
            #this solves the oscillation problem  silly moving back and forth in maze cz of similar scores
            if move in self.move_history[-3:]:  #last 3 moves look at 
                score -= 1  

            if is_maximizing and score > best_score:
                #keeping yrack of and updating the best score and best move all same as we did in tic tac toe too
                best_score = score
                best_move = move
                alpha = max(alpha, best_score)
            elif not is_maximizing and score < best_score:
                best_score = score
                best_move = move
                beta = min(beta, best_score)
            if alpha >= beta:
                break

        self.move_history.append(best_move) #update the move_hisotry too na
        if len(self.move_history) > 10:  #pop form head if its getting larger than a certain mempory limit ie 10
            self.move_history.pop(0)
        return best_move, best_score
    
    def game_over(self):#winning/losing conditions
        return self.lives <= 0 or self.player_pos == self.silly_pos #or self.player_score>=1480
    
    def clone_state(self):
        #could not use deep copy function of copy library cz it was not copying surfaces and stuff of pygame library
        cloned_game = MazeGame(self.game, self.level)  
        #create copy for only those relevant attributes we could need
        cloned_game.maze = [row[:] for row in self.maze]  
        cloned_game.cell_size = self.cell_size

        cloned_game.lives = self.lives
        cloned_game.player_pos = self.player_pos[:]
        cloned_game.player_old_pos = self.player_old_pos[:]
        cloned_game.player_score = self.player_score

        cloned_game.silly_pos = self.silly_pos[:]
        
        cloned_game.lock_pos = None if self.lock_pos is None else self.lock_pos[:]
        cloned_game.lock_timer = self.lock_timer

        return cloned_game
    
# happy gaming! :D