# config.py

# Window dimensions (in pixels)
win_width = 800
win_height = 800

# Size of each tile in the grid (in pixels)
tile_size = 32

#Colors used in the game (RGB format)
black = (0, 0, 0)
white = (255, 255, 255)

colors = {
    "black": (0, 0, 0),
    "orange": (255, 140, 0),
    "maroon": (128, 0, 0),
    "blue": (0, 0, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
}


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
    'B.B.B.BBB.B.B.BEBBB.B.B.B',
    'B...B.....B.B.B.B...B.B.B',
    'BBBBB.BBBBB.B.B.B.BBB.B.B',
    'B.....B..XB.B.B.B.......B',
    'B.BBBBB...B.B.B.BBBBBBB.B',
    'B.B.....B.B.B.B.....K.B.B', 
    'B.B.BBBBB.B.B.B.BBBBB.B.B',
    'B.D.......B.B.B.......B.B',  
    'B.BBBBBBBBB.B.BBBBBBBBB.B',
    'Z.......................B',
    'BBBBBB.BBBBB.BBBBBBBBBBBB',
    'B...........Y...........B',  
    'B.BBBBBBBBBB.BBBBBBBBB.BB',
    'B.B.................B..PB',
    'B.B.BBBBB.BBBFBBBBB.B.BBB',  
    'B.B.....B.B.....B.....B.B',
    'B.B.BBB.B.B.BBB.B.BBB.B.B',
    'B...B...B.B..GB.B.B...B.B',  
    'B.BBB.BBB.B.B.B.B.B.BBB.B',
    'B.P..P....B.B.B.B.B..P..B',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
]