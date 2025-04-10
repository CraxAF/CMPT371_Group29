import pygame
from config import tile_size

def handle_tile_movement(player, keys):
    if player.moving:
        #print("[DEBUG] Player is already moving, skipping input.")
        return

    dx, dy = 0, 0
#wasd free movement
    if keys[pygame.K_a]:
        dx = -1
        #print("[DEBUG] A pressed - move left")
    elif keys[pygame.K_d]:
        dx = 1
        #print("[DEBUG] D pressed - move right")
    elif keys[pygame.K_w]:
        dy = -1
        #print("[DEBUG] W pressed - move up")
    elif keys[pygame.K_s]:
        dy = 1
        #print("[DEBUG] S pressed - move down")
#acceleration to determine collision
    if dx != 0 or dy != 0:
        for sprite in player.game.blocks:
            if hasattr(sprite, "try_unlock"):
                sprite.try_unlock(player, dx * tile_size, dy * tile_size)

        target_x = player.rect.x + dx * tile_size
        target_y = player.rect.y + dy * tile_size
        #print(f"[DEBUG] Target position: ({target_x}, {target_y})")

        future_rect = player.rect.copy()
        future_rect.x = target_x
        future_rect.y = target_y

        #print(f"[DEBUG] Current tile: ({player.rect.x // tile_size}, {player.rect.y // tile_size})")
        

        #for wall in player.game.blocks:
            #if future_rect.colliderect(wall.rect):
                #print("[DEBUG] Movement blocked by wall.")
                #return


        #print("[DEBUG] Movement allowed. Starting move.")
        player.target_pos = (target_x, target_y)
        player.moving = True
