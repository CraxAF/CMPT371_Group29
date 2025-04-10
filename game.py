# game.py
import time
import pygame
from sprites import *
from config import *
import sys
import client
# Main game class that handles game state, drawing, and logic
class Game:
    def __init__(self):
        pygame.init()
        self.players = {}  # Maps player names to Player objects
        self.doors = {}
        self.keys = {}
        self.spawn_points = []  # Stores tilemap spawn point positions
        self.sprite_counter = 0  # Used to assign unique sprites
        self.screen = pygame.display.set_mode([win_width, win_height])  # Game window
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 32)
        self.waiting_for_restart = False
        self.key_number = 0
        self.door_number = 0

        # Load all sprite resources
        self.spritesheet = CharSprite("img/character_sprites.png")
        self.wall_img = Sprite("img/wall.png")
        self.door_img = Sprite("img/door.png")
        self.floor_img = CharSprite("img/floor.png")
        self.key_img = Sprite("img/key.png")

    # Intro screen that asks the player for their name
    def intro_screen(self):
        font = pygame.font.Font(None, 36)
        input_box = pygame.Rect(300, 350, 200, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        player_name = ""
        intro = True

        while intro:
            self.screen.fill(black)
            text_surface = font.render("Enter your name:", True, white)
            self.screen.blit(text_surface, (300, 300))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
                    return None  # Quit early if window is closed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Toggle input box focus
                    active = input_box.collidepoint(event.pos)
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            intro = False
                        elif event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        else:
                            player_name += event.unicode

            # Draw input box and name text
            txt_surface = font.render(player_name, True, white)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.screen, color, input_box, 2)

            pygame.display.flip()
            self.clock.tick(30)

        return player_name

    # Adds a new player sprite to the game
    def add_player(self, name, x, y):
        #print(f"[DEBUG] Adding player {name} at ({x}, {y})")
        sprite_idx = self.sprite_counter % 24  # Cycle through available sprites
        main = (name == player_name)  # Check if this is the main player
        player = Player(self, x, y, name, main, sprite_idx)
        self.players[name] = player
        self.sprite_counter += 1        
        
    # Sets up the level and sprite groups
    def new(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.players = {}  # Clear existing players
        self.spawn_points = []  # Reset spawn points
        start = time.time()
        while not client.get_game_objects() and time.time() - start < 5:
            pygame.time.wait(100)
        self.create_tilemap()
        self.playing = True
        TutorialMessage(self, "Press WASD to move – Press R to restart", duration=60000)
        while not client.get_player_position() and time.time() - start < 5:
            pygame.time.wait(100)
        #print(f"[DEBUG] Player positions: {client.get_player_position()}")
        g = self  # alias for brevity
        positions = client.get_player_position()  # Fetch player positions from the server
        for name, pos in positions.items():
            x,y = pos["x"],pos["y"]
            self.add_player(name, x, y)
        #for i, name in enumerate([player_name]):
        #    if i < len(g.spawn_points):
        #        x, y = g.spawn_points[i]
        #        g.add_player(name, x, y)

        #print("[DEBUG] Wall tile positions:")
        #for wall in self.blocks:
            #print(f"  - ({wall.rect.x}, {wall.rect.y})  tile=({wall.rect.x // tile_size}, {wall.rect.y // tile_size})")

    # Handles game events (e.g., quitting)
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.playing = False
                #restart key
                elif event.key == pygame.K_r:
                    #print("[DEBUG] R key pressed – restarting game.")
                    self.restart()

    # Updates all game objects
    def update(self):
        self.all_sprites.update()
        positions = client.get_player_position()
        for name, pos in positions.items():
            #print(f"[DEBUG] Updating position for {name}: {pos}")
            if name not in self.players:
                self.add_player(name, pos["x"], pos["y"])
            elif name in self.players and name != player_name:
                player = self.players[name]
                player.x = pos["x"] * tile_size
                player.y = pos["y"] * tile_size
                player.rect.topleft = (player.x , player.y)
        for player in self.players:
            if player not in positions:
                self.players[player].kill()
                del self.players[player]
                break
        objects = client.get_game_objects()
        for object in objects.values():
            for door in self.doors:
                if self.doors[door].objectid == object["id"]:
                    self.doors[door].locked = object["locked"] 
                    if not object["locked"]:
                        self.doors[door].locked = True
                        #print(f"[DEBUG] Door {door} unlocked!")
                        self.doors[door].unlock()
                        del self.doors[door]
                        break
            if object["type"] == "pushable":
                if(object["id"] not in self.keys):
                    del self.keys[object["id"]]
                    break
        for key in self.keys:
            if(self.keys[key].objectid not in objects):
                del self.keys[key]
                break

                    


    # Draws all game objects to the screen
    def draw(self):
        self.screen.fill(black)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect)
        
        self.clock.tick(60)
        #WALL COLLISION [DEBUG]
        #for wall in self.blocks:
        #    pygame.draw.rect(self.screen, (255, 0, 0), wall.rect, 2)
        pygame.display.update()

    # Creates game world from tile_map config

    def create_tilemap(self):
        objects = client.get_game_objects()
        for object in objects.values():
            if object["type"] == "wall":
                Wall(self, object["x"], object["y"], object["id"])
            elif object["type"] == "door":
                door = Door(self, object["x"], object["y"], object["id"])
                self.doors[object["id"]] = door
            elif object["type"] == "pushable":
                key = Key(self, object["x"], object["y"], object["id"])
                self.keys[object["id"]] = key
            elif object["type"] == "floor":
                Floor(self, object["x"], object["y"], object["id"])
        #for i, row in enumerate(tile_map):
        #    for j, tile in enumerate(row):
        #        if tile == "B":
        #            Wall(self, j, i)
        #        elif tile == "D":
        #            Door(self, j, i, f"door{self.door_number}")
        #            self.door_number += 1
        #        elif tile == ".":
        #            Floor(self, j, i)
        #        elif tile == "K":
        #            Key(self, j, i, f"key{self.key_number}")
        #            self.key_number += 1
        #        elif tile == "P":
        #            Floor(self, j, i)
        #            self.spawn_points.append((j, i))
        

    #Create new instance of game
    def restart(self):
        self.new()   # Reset game objects, map, etc.

    #check win con
    def check_win_condition(self):
        # If there are no locked doors left, trigger win
        for sprite in self.all_sprites:
            if hasattr(sprite, "locked") and sprite.locked:
                return  # Still at least one locked door

        # If we get here, all doors are unlocked!
        #print("[DEBUG] All doors are unlocked! YOU WIN!")
        self.win()
    
    def win(self):
        # Freeze the game or show a message
        
        self.waiting_for_restart = True

        # Show a fading message (optional)
        from sprites import TutorialMessage  # or ui.py if you moved it
        TutorialMessage(self, "YOU ESCAPED! press R to restart", duration=999999)

        

    # Main game loop
    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False  # Exit when game ends


# Instantiate and run the game
g = Game()
player_name = g.intro_screen()  # Get player name
client.main(player_name)  # Start the main game loop
g.new()

# Assign players to available spawn points
#names = [player_name]
#for i, name in enumerate(names):
    #if i < len(g.spawn_points):
        #x, y = g.spawn_points[i]


# Run the main loop
while g.running:
    g.main()

pygame.quit()
sys.exit()
