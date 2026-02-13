"""Shared constants for the Feral Gods GUI."""

# Window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
DARK_GREY = (64, 64, 64)
LIGHT_GREY = (192, 192, 192)

RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (240, 220, 60)
ORANGE = (240, 160, 40)
CYAN = (50, 200, 220)
PURPLE = (160, 60, 220)
BROWN = (140, 100, 50)

# UI colours
HP_GREEN = (40, 180, 40)
HP_RED = (200, 40, 40)
ENERGY_BLUE = (40, 120, 220)
XP_YELLOW = (220, 200, 40)
BAR_BG = (40, 40, 40)
PANEL_BG = (20, 20, 35)
PANEL_BORDER = (80, 80, 120)
MENU_HIGHLIGHT = (60, 60, 100)
MENU_BG = (30, 30, 50)
TEXT_COLOR = (230, 230, 230)
TEXT_DIM = (160, 160, 180)
GOLD = (255, 215, 0)
SHADOW = (10, 10, 20)

# God-specific colour palettes
GOD_COLORS = {
    "Ophidia": (200, 60, 30),     # fire/red-orange
    "Galanth": (100, 180, 240),   # sky blue
    "Pelagon": (30, 80, 180),     # deep blue
    "Myriad": (180, 160, 40),     # yellow-green
    "Karn": (180, 100, 40),       # brown-orange
    "Pachymos": (140, 140, 140),  # stone grey
    "Skulk": (80, 40, 120),       # dark purple
    "Sagax": (180, 60, 200),      # bright purple
}

# Map tile types
TILE_GRASS = 0
TILE_PATH = 1
TILE_WATER = 2
TILE_TREE = 3
TILE_STONE = 4
TILE_SHRINE = 5
TILE_WALL = 6
TILE_DOOR = 7
TILE_SAND = 8

# Tile passability
PASSABLE_TILES = {TILE_GRASS, TILE_PATH, TILE_SAND, TILE_DOOR}

# Movement
MOVE_SPEED = 4  # pixels per frame

# Combat
COMBAT_TRANSITION_TIME = 500  # ms
ATTACK_ANIM_TIME = 300  # ms
DAMAGE_FLASH_TIME = 200  # ms
MESSAGE_DISPLAY_TIME = 1500  # ms
MESSAGE_HISTORY_LIMIT = 50

# Random encounter rate (chance per step)
ENCOUNTER_RATE = 0.06
