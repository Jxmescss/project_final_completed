import pygame
import json
import os
from settings import *

# ---------- Global State (ตัวแปรที่ใช้ร่วมกันทั้งเกม) ----------
player_coins = 0
level_stars = { "level_1": 0, "level_2": 0, "level_3": 0 }
extra_moves_active = False
is_music_unlocked = False

# ---------- Assets Containers ----------
game_background_image = None
stone_button_image = None
settings_bg_image = None
shop_bg_image = None
game_over_bg_image = None
TILE_IMAGES = [] 
SPECIAL_TILE_IMAGE = None

# ---------- Fonts ----------
pygame.font.init()
font = pygame.font.SysFont("arial", 22)
large_font = pygame.font.SysFont("arial", 32, bold=True)
title_font = pygame.font.SysFont("arial", 56, bold=True)

# ---------- Save / Load System ----------
def save_data():
    data = {
        "coins": player_coins,
        "stars": level_stars,
        "extra_moves": extra_moves_active,
        "music_unlocked": is_music_unlocked
    }
    try:
        with open(SAVE_FILE_PATH, 'w') as f:
            json.dump(data, f)
        print("Game Saved!")
    except Exception as e:
        print(f"Save Error: {e}")

def load_data():
    global player_coins, level_stars, extra_moves_active, is_music_unlocked
    if not os.path.exists(SAVE_FILE_PATH): return
    try:
        with open(SAVE_FILE_PATH, 'r') as f:
            data = json.load(f)
            player_coins = data.get("coins", 0)
            extra_moves_active = data.get("extra_moves", False)
            is_music_unlocked = data.get("music_unlocked", False)
            loaded_stars = data.get("stars", {})
            for k, v in loaded_stars.items():
                if k in level_stars:
                    level_stars[k] = v
        print("Data Loaded!")
        if is_music_unlocked:
            play_music()
    except Exception as e:
        print(f"Load Error: {e}")

# ---------- Asset Loading ----------
def safe_load(path, size=None):
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size: img = pygame.transform.scale(img, size)
            return img
    except: pass
    return None

def load_all_images():
    global game_background_image, stone_button_image, settings_bg_image, shop_bg_image, game_over_bg_image, SPECIAL_TILE_IMAGE
    
    game_background_image = safe_load(GAME_BG_PATH, (SCREEN_WIDTH, SCREEN_HEIGHT))
    if game_background_image: game_background_image = game_background_image.convert()

    stone_button_image = safe_load(STONE_BTN_PATH, (STONE_SIZE, STONE_SIZE))
    settings_bg_image = safe_load(SETTINGS_BG_PATH, (SCREEN_WIDTH, SCREEN_HEIGHT))
    shop_bg_image = safe_load(SHOP_BG_PATH, (SCREEN_WIDTH, SCREEN_HEIGHT))
    game_over_bg_image = safe_load(GAME_OVER_BG_PATH, (SCREEN_WIDTH, SCREEN_HEIGHT))
    if game_over_bg_image:
        print(f"Game Over BG Loaded: {GAME_OVER_BG_PATH}")
    else:
        print(f"Failed to load Game Over BG: {GAME_OVER_BG_PATH}")

    TILE_IMAGES.clear()
    for i in range(len(TILE_COLORS)):
        path = get_path(f'tile_{i}.png')
        img = safe_load(path, (TILE_SIZE, TILE_SIZE))
        TILE_IMAGES.append(img)

    SPECIAL_TILE_IMAGE = safe_load(get_path('tile_special.png'), (TILE_SIZE, TILE_SIZE))

def play_music():
    try:
        pygame.mixer.init()
        if os.path.exists(BG_MUSIC_PATH) and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(BG_MUSIC_PATH)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)
            print("Music Playing")
    except Exception as e: print(f"Music Error: {e}")

# ---------- Drawing Helpers ----------
def is_point_in_circle(point, center, radius):
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return (dx*dx + dy*dy) <= (radius*radius)

def draw_menu_effect(surf, rect, is_hover, is_click):
    if not is_hover and not is_click: return 
    effect_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    if is_click: pygame.draw.rect(effect_surf, (255, 255, 255, 150), effect_surf.get_rect(), border_radius=12)
    elif is_hover:
        pygame.draw.rect(effect_surf, (255, 215, 0, 50), effect_surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (255, 215, 0), rect, 2, border_radius=12)
    surf.blit(effect_surf, rect.topleft)

def draw_button(surf, rect, text, hover=False, font_color=WHITE, bg_color=(66, 165, 245), hover_color=(100, 181, 246)):
    color = hover_color if hover else bg_color
    pygame.draw.rect(surf, color, rect, border_radius=12)
    pygame.draw.rect(surf, font_color, rect, 3, border_radius=12)
    txt = large_font.render(text, True, font_color)
    surf.blit(txt, txt.get_rect(center=rect.center))

def draw_lock_icon(surf, center):
    x, y = center
    pygame.draw.rect(surf, (50, 50, 50), (x - 10, y - 8, 20, 18), border_radius=3)
    pygame.draw.arc(surf, (50, 50, 50), (x - 8, y - 20, 16, 20), 0, 3.14, 3)

def draw_level_button_on_stone(surf, rect, is_locked, stars_earned, hover=False):
    if stone_button_image: surf.blit(stone_button_image, rect.topleft)
    else:
        color = (100, 100, 100) if not is_locked else (70, 70, 70)
        pygame.draw.circle(surf, color, rect.center, rect.width//2)
        pygame.draw.circle(surf, (50, 50, 50), rect.center, rect.width//2, 3)

    if is_locked:
        draw_lock_icon(surf, rect.center)
    else:
        if hover:
            radius = rect.width // 2
            glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 215, 0, 80), (radius + 10, radius + 10), radius + 5)
            surf.blit(glow_surf, (rect.x - 10, rect.y - 10))
            pygame.draw.circle(surf, (255, 215, 0), rect.center, radius, 3)
        if stars_earned > 0:
            for i in range(stars_earned):
                sx = rect.centerx - 10 + (i * 10)
                sy = rect.bottom + 5
                pygame.draw.circle(surf, GOLD, (sx, sy), 4)

def grid_to_pixel(r, c):
    return OFFSET_X + c * TILE_SIZE, OFFSET_Y + r * TILE_SIZE

def pixel_to_grid(x, y):
    col = int((x - OFFSET_X) // TILE_SIZE)
    row = int((y - OFFSET_Y) // TILE_SIZE)
    return row, col