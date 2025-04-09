# mechanics.py

import pygame
from config import win_height

def handle_player_movement(player, keys):
    speed = 4
    dx = 0
    dy = 0


    if keys[pygame.K_a]:
        dx -= speed
    if keys[pygame.K_d]:
        dx += speed

    # Jumping
    if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and player.on_ground:
        player.vel_y = player.jump_strength
        player.is_jumping = True
        player.on_ground = False

    # Apply gravity
    player.vel_y += player.gravity
    dy += player.vel_y

    # Horizontal collision
    player.rect.x += dx
    for wall in player.game.blocks:
        if player.rect.colliderect(wall.rect):
            if dx > 0:  # Moving right
                player.rect.right = wall.rect.left
            if dx < 0:  # Moving left
                player.rect.left = wall.rect.right

    # Vertical collision
    player.rect.y += dy
    player.on_ground = False  # Assume midair unless proven on wall
    for wall in player.game.blocks:
        if player.rect.colliderect(wall.rect):
            if dy > 0:  # Falling down
                player.rect.bottom = wall.rect.top
                player.vel_y = 0
                player.on_ground = True
                player.is_jumping = False
            elif dy < 0:  # Jumping up
                player.rect.top = wall.rect.bottom
                player.vel_y = 0
