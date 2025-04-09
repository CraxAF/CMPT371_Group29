# game.py
import pygame
from sprites import *
from config import *
import sys
import client


# Main game class that handles game state, drawing, and logic
class Game:
    def __init__(self):
        pygame.init()
        self.players = client.get_player_position()  # Maps player names to Player objects
        self.spawn_points = []  # Stores tilemap spawn point positions
        self.sprite_counter = 0  # Used to assign unique sprites
        self.screen = pygame.display.set_mode([win_width, win_height])  # Game window
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 32)

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
        sprite_idx = self.sprite_counter % 24  # Cycle through available sprites
        player = Player(self, x, y, sprite_idx)
        self.players[name] = player
        self.sprite_counter += 1

    # Sets up the level and sprite groups
    def new(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        #self.create_tilemap()  # Build the map
        client.main(player_name)
        self.playing = True

    # Handles game events (e.g., quitting)
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    # Updates all game objects
    def update(self):
        self.all_sprites.update()

    # Draws all game objects to the screen
    def draw(self):
        #self.screen.fill(black)
        #for sprite in self.all_sprites:
            #self.screen.blit(sprite.image, sprite.rect)
        #self.clock.tick(60)
        self.screen.fill(black)
        positions = client.get_player_position()
        for name, pos in positions.items():
            if name not in self.players:
                sprite_idx = 0
                self.players[name] = Player(self, pos["x"], pos["y"], sprite_idx)
            else:
                self.players[name].x = pos["x"]
                self.players[name].y = pos["y"]
                self.players[name].rect.topleft = (pos["x"], pos["y"])
            self.screen.blit(self.players[name].image, self.players[name].rect)

        objects = client.get_game_objects()
        for obj in objects.values():
            if obj["type"] == "door":
                self.screen.blit(self.door_img.image, (obj["x"], obj["y"]))
            elif obj["type"] == "pushable":
                self.screen.blit(self.key_img.image, (obj["x"], obj["y"]))
            elif obj["type"] == "wall":
                self.screen.blit(self.wall_img.image, (obj["x"], obj["y"]))

        pygame.display.update()

    # Creates game world from tile_map config
    def create_tilemap(self):
        for i, row in enumerate(tile_map):
            for j, tile in enumerate(row):
                if tile == "B":
                    Wall(self, j, i)
                elif tile == "D":
                    Door(self, j, i)
                elif tile == ".":
                    Floor(self, j, i)
                elif tile == "K":
                    Key(self, j, i)
                elif tile == "P":
                    Floor(self, j, i)
                    self.spawn_points.append((j, i))

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
g.new()

# Assign players to available spawn points
names = ["Alice", "Bob", player_name]
for i, name in enumerate(names):
    if i < len(g.spawn_points):
        x, y = g.spawn_points[i]
        g.add_player(name, x, y)

# Run the main loop
while g.running:
    g.main()

pygame.quit()
sys.exit()
