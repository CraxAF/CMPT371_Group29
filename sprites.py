# sprites.py
import pygame
import random
from config import *
import math 
from mechanics import handle_tile_movement
import traceback
import client

def tint_image(image, tint_color):
    """Tints a surface by blending it with a given RGB color."""
    tinted_image = image.copy()
    tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint.fill(tint_color)  # This is already an RGB tuple
    tinted_image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image


# Handles character sprite sheet and allows extracting individual sprites
class CharSprite:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert_alpha()  # Load sprite sheet
        self.sheet = pygame.transform.scale(self.sheet, (tile_size * 6, tile_size * 4))  # Resize sheet for easier slicing
        
    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height], pygame.SRCALPHA)  # Create transparent surface
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))  # Extract sprite from sheet
        return sprite


# Handles single-tile sprites (walls, doors, keys, etc.)
class Sprite:
    def __init__(self, file):
        original = pygame.image.load(file).convert_alpha()  # Load image
        self.image = pygame.transform.scale(original, (tile_size, tile_size))  # Resize to tile size
        
    def get_sprite(self, *_):  # Crop parameters are ignored for single-tile sprites
        return self.image


# Represents a player character in the game
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, player_name, main, sprite_idx=0):
        self.player_name = player_name
        self.main = main
        self.game = game
        self._layer = player_layer
        self.groups = self.game.all_sprites 
        pygame.sprite.Sprite.__init__(self, self.groups)
        


        self.x = x * tile_size
        self.y = y * tile_size

        self.width = tile_size
        self.height = tile_size

        # Determine sprite sheet coordinates based on index
        sprites_per_row = 6
        sx = (sprite_idx % sprites_per_row) * tile_size
        sy = (sprite_idx // sprites_per_row) * tile_size

        # Load and extract sprite from sheet
        self.spritesheet = CharSprite("img/character_sprites.png")
        raw_sprite = self.spritesheet.get_sprite(sx, sy, 32, 32)  # Original sprite size

        self.image = pygame.transform.scale(raw_sprite, (self.width, self.height))  # Scale to tile size

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Also reset target position
        self.target_pos = (self.rect.x, self.rect.y)

        self.moving = False
        self.move_speed = 4  # Pixels per frame (smooth stepping)


    def update(self):
        if(self.main):
            keys = pygame.key.get_pressed()

            # Handle movement intent
            handle_tile_movement(self, keys)

            # Move toward target
            if self.moving:
                tx, ty = self.target_pos
                dx = tx - self.rect.x
                dy = ty - self.rect.y

                if dx != 0:
                    self.rect.x += self.move_speed if dx > 0 else -self.move_speed
                if dy != 0:
                    self.rect.y += self.move_speed if dy > 0 else -self.move_speed

                # Snap if close enough
                if abs(dx) <= self.move_speed and abs(dy) <= self.move_speed:
                    self.rect.x = tx
                    self.rect.y = ty
                    self.moving = False
                client.send_action("move", self.player_name, None, None, position=(self.rect.x/tile_size, self.rect.y/tile_size))


# Represents a wall tile
class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y, objectid):
        self.objectid = objectid
        self.game = game
        self._layer = wall_layer
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * tile_size
        self.y = y * tile_size
        self.width = tile_size
        self.height = tile_size

        self.image = self.game.wall_img.get_sprite(0, 0, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


# Represents a door tile

class Door(pygame.sprite.Sprite):
    def __init__(self, game, x, y, objectid, color="red"):
        self.color = color
        self.objectid = objectid
        self.game = game
        self._layer = wall_layer
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * tile_size
        self.y = y * tile_size
        self.width = tile_size
        self.height = tile_size

        base_image = self.game.door_img.get_sprite(0, 0, self.width, self.height)
        self.image = tint_image(base_image, colors.get(color, (255,0,0)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.locked = True

    def try_unlock(self, player, dx, dy):
        if not self.locked:
            return

        # Predict player's next tile
        next_x = player.rect.x + dx
        next_y = player.rect.y + dy

        next_rect = player.rect.copy()
        next_rect.x = next_x
        next_rect.y = next_y

        #print(f"[DEBUG] {player.player_name} at {player.rect.topleft} trying to move to {next_rect.topleft} (checking door at {self.rect.topleft})")

        if self.rect.colliderect(next_rect):
            # Does the player have a key?
            for sprite in self.game.all_sprites:
                if isinstance(sprite, Key) and sprite.carried_by == player:
                    if sprite.color == self.color:
                        # print(f"[DEBUG] Door unlocked via try_unlock with matching key: {sprite.color}")
                        self.unlock()
                        client.send_action("unlock", player.player_name, player.player_name, self.objectid, position=(self.rect.x, self.rect.y))
                        return

    def unlock(self):
        if not self.locked:
            return

        #print("[DEBUG] Door unlocking — replacing with floor and removing key.")
        self.locked = False
        

        # Remove the key being carried by the player who unlocked the door
        for sprite in list(self.game.all_sprites):
            if isinstance(sprite, Key) and sprite.carried_by:
                player = sprite.carried_by
                #print(f"[DEBUG] Key used by {player} — removing key.")
                sprite.carried_by = None
                sprite.used = True  # optional
                sprite.kill()
                client.send_action("delete_key", player.player_name, player.player_name, sprite.objectid, position=(sprite.rect.x, sprite.rect.y))
                break

        #print(f"[DEBUG] Keys in game: {[k for k in self.game.all_sprites if isinstance(k, Key)]}")
        
        # Replace door with a floor tile
        Floor(self.game, self.rect.x // tile_size, self.rect.y // tile_size, "floorx")
        self.kill()

        self.game.check_win_condition()
        #print("[DEBUG] Player added. Call stack:")
        #traceback.print_stack()


# Represents a walkable floor tile
class Floor(pygame.sprite.Sprite):
    def __init__(self, game, x, y, objectid):
        self.objectid = objectid
        self.game = game
        self._layer = floor_layer
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * tile_size
        self.y = y * tile_size
        self.width = tile_size
        self.height = tile_size

        self.image = self.game.floor_img.get_sprite(0, 0, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


# Represents a collectible key item
class Key(pygame.sprite.Sprite):
    def __init__(self, game, x, y, objectid, color="yellow"):
        self.color = color
        self.objectid = objectid
        self.game = game
        self._layer = item_layer
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * tile_size
        self.y = y * tile_size
        self.width = tile_size
        self.height = tile_size

        base_image = game.key_img.get_sprite(32, 0, 32, 32)  # example key sprite
        self.image = tint_image(base_image, colors.get(color, (255, 0, 0))) 
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.carried_by = None  # Player carrying the key
        self.used = False

    def update(self):
        if not self.alive():  # Skip update if killed
            return

        if self.carried_by:
            # Follow the player
            px, py = self.carried_by.rect.center
            kx, ky = self.rect.center
            self.rect.centerx += (px - kx) * 0.1
            self.rect.centery += (py - ky) * 0.1
        else:
            # Idle behavior or pickup logic
            for player in self.game.players.values():
                if self.rect.colliderect(player.rect):
                    self.carried_by = player
                    client.send_action("pickup", player.player_name, player.player_name, self.objectid, position=(self.rect.x, self.rect.y))
                    break

            #Only place a floor tile once, and only if not already used

#Tutorial mesage logic handler
class TutorialMessage(pygame.sprite.Sprite):
    def __init__(self, game, text, duration=3000):  # duration in ms
        self.game = game
        self._layer = 999  # Always on top
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.font = pygame.font.SysFont("verdana", 24)
        self.text = text
        self.image = self.font.render(self.text, True, (255, 255, 255))
        self.image.set_alpha(255)
        

        self.rect = self.image.get_rect(center=(800 // 2, 40))
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 255

    def update(self):
        # How long has it been visible
        elapsed = pygame.time.get_ticks() - self.start_time

        if elapsed > self.duration:
            self.kill()  # Remove from game
        else:
            # Fade out over time
            fade_speed = 255 / (self.duration / 100)  # adjust for smooth fade
            self.alpha = max(0, 255 - int(elapsed * fade_speed / 10))
            self.image.set_alpha(self.alpha)
