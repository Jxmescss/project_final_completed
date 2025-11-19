import pygame
import os

# ---------- General Config ----------
GRID_ROWS, GRID_COLS = 8, 8
TILE_SIZE, PADDING = 64, 16
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 800
FPS = 60
MATCH_MIN = 3

# Game Rules
MOVES_LIMIT = 20 
STAR_SCORES = [1000, 2000, 3000]
SPECIAL_SPAWN_RATE = 10000 # 10 seconds

# Shop Config
ITEM_MOVE_PRICE = 15
ITEM_MOVE_BONUS = 5
ITEM_MUSIC_PRICE = 30

# UI Config
STONE_SIZE = 60
BOARD_WIDTH = GRID_COLS * TILE_SIZE
BOARD_HEIGHT = GRID_ROWS * TILE_SIZE
OFFSET_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
OFFSET_Y = SCREEN_HEIGHT - BOARD_HEIGHT - 30

# Colors
WHITE = (255, 255, 255)
DARK_GRAY = (45, 45, 45)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GRAY_LOCK = (100, 100, 100)
SPECIAL_COLOR = (255, 255, 255)
BG_COLOR = (30, 30, 30)
GREEN_BUY = (50, 200, 50)
RED_NO_MONEY = (200, 50, 50)

TILE_COLORS = [
    (239, 83, 80), (129, 199, 132), (100, 181, 246),
    (255, 241, 118), (171, 71, 188), (255, 167, 38)
]

# ---------- File Paths (Fixed Logic) ----------
# หาตำแหน่งปัจจุบันของไฟล์ settings.py เพื่อใช้อ้างอิงตำแหน่งโฟลเดอร์ assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_FOLDER = os.path.join(BASE_DIR, 'assets')
SAVE_FILE_PATH = os.path.join(BASE_DIR, 'save_data.json')

def get_path(filename):
    return os.path.join(ASSET_FOLDER, filename)

SPLASH_BG_PATH = get_path('dwasdaw.png')
MENU_BG_PATH = get_path('aaaaaa.png')
LEVEL_SELECT_BG_PATH = get_path('level.png')
GAME_BG_PATH = get_path('bbb2.png')
STONE_BTN_PATH = get_path('stone.png')
SETTINGS_BG_PATH = get_path('PAUSE2.png')
SHOP_BG_PATH = get_path('SHOP.png') # ตรวจสอบว่าไฟล์ชื่อ SHOP.png หรือ sss.png กันแน่
GAME_OVER_BG_PATH = get_path('gameover.png') # <<< ต้องมีไฟล์ชื่อนี้ใน assets
BG_MUSIC_PATH = get_path('bgmusic.mp3')