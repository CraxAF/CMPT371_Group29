# config.py

# Window dimensions (in pixels)
win_width = 800
win_height = 800

# Size of each tile in the grid (in pixels)
tile_size = 32

# Common colors used in the game (RGB format)
black = (0, 0, 0)
white = (255, 255, 255)

# Dimensions of each sprite in the sprite sheet (before scaling)
sprite_width = 32
sprite_height = 32

# Rendering layers (lower numbers get drawn first, higher numbers on top)
floor_layer = 1    # Base layer for floor tiles
item_layer = 2     # Layer for keys or other items
wall_layer = 3     # Layer for walls and doors
player_layer = 4   # Topmost layer for player sprites

# Map layout using a list of strings
# Each character represents a type of tile:
# 'B' = Wall, '.' = Floor, 'D' = Door, 'K' = Key, 'P' = Player spawn point
tile_map = [
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.............B.........B',
    'B.BBBBB.BBBBB.B.BBBBBBB.B',
    'B.B.....B...B.......B...B',
    'B.B.B.BBB.B.B.B.BBB.B.B.B',
    'B...B.....B.B.B.B...B.B.B',
    'BBBBB.BBBBB.B.B.B.BBB.B.B',
    'B.....B...B.B.B.B.......B',
    'B.BBBBB.B.B.B.B.BBBBBBB.B',
    'B.B.....B.B.B.B.......B.B',
    'B.B.BBBBB.B.B.B.BBBBB.B.B',
    'B.D.......B.B.B.......B.B',
    'B.BBBBBBBBB.B.BBBBBBBBB.B',
    'D......K.............. .B',
    'BBBBBB.BBBBB.BBBBBBBBBBBB',
    'B...........K...........B',
    'B.BBBBBBBBBB.BBBBBBBBB.BB',
    'B.B.................B..PB',
    'B.B.BBBBB.BBBDBBBBB.B.BBB',
    'B.B.....B.B.K...B.....B.B',
    'B.B.BBB.B.B.BBB.B.BBB.B.B',
    'B...B...B.B...B.B.B...B.B',
    'B.BBB.BBB.B.B.B.B.B.BBB.B',
    'B.P.P.....B.B.B.B.B.....B',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
]
