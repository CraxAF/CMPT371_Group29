# sprites.py
import pygame
import random
from config import *
import math 

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
    def __init__(self, game, x, y, sprite_idx=0):
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

    def update(self):
        pass  # Update method placeholder (for future movement, animation, etc.)


# Represents a wall tile
class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
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
    def __init__(self, game, x, y):
        self.game = game
        self._layer = wall_layer
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * tile_size
        self.y = y * tile_size
        self.width = tile_size
        self.height = tile_size

        self.image = self.game.door_img.get_sprite(0, 0, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


# Represents a walkable floor tile
class Floor(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = floor_layer
        self.groups = self.game.all_sprites, self.game.blocks
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
    def __init__(self, game, x, y):
        self.game = game
        self._layer = item_layer  # Item layer must be defined in config.py
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * tile_size
        self.y = y * tile_size
        self.width = tile_size
        self.height = tile_size

        self.image = self.game.key_img.get_sprite(0, 0, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
