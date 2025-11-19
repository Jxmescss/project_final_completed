import pygame
import colorsys
from settings import *
import utils

def get_rainbow_color():
    t = pygame.time.get_ticks() / 500.0
    r, g, b = colorsys.hsv_to_rgb(t % 1, 0.8, 1)
    return (int(r*255), int(g*255), int(b*255))

# <<< ต้องมี Class นี้ และชื่อต้องเขียนแบบนี้เป๊ะๆ >>>
class MenuButton:
    def __init__(self, rect, action, text):
        self.rect = rect
        self.action = action
        self.text = text

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            return self.action
        return None

class Tile:
    def __init__(self, kind, row, col, wildcard=False):
        self.kind = kind
        self.row, self.col = row, col
        self.wildcard = wildcard 
        self.selected = False
        self.anim_x, self.anim_y = utils.grid_to_pixel(row, col)
        self.target_x, self.target_y = self.anim_x, self.anim_y

    def draw(self, surf):
        x, y = int(self.anim_x), int(self.anim_y)
        
        if self.wildcard:
            neon_color = get_rainbow_color()
            glow = pygame.Surface((TILE_SIZE + 30, TILE_SIZE + 30), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*neon_color, 100), (TILE_SIZE//2 + 15, TILE_SIZE//2 + 15), TILE_SIZE//2 + 8)
            surf.blit(glow, (x - 15, y - 15))

            if utils.SPECIAL_TILE_IMAGE:
                surf.blit(utils.SPECIAL_TILE_IMAGE, (x, y))
            else:
                cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                radius = TILE_SIZE // 2 - 6
                pygame.draw.circle(surf, WHITE, (cx, cy), radius)
                pygame.draw.circle(surf, neon_color, (cx, cy), radius, 4)
        else:
            tile_img = None
            if utils.TILE_IMAGES and self.kind < len(utils.TILE_IMAGES) and utils.TILE_IMAGES[self.kind]:
                tile_img = utils.TILE_IMAGES[self.kind]

            if tile_img:
                surf.blit(tile_img, (x, y))
            else:
                cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                radius = TILE_SIZE // 2 - 6
                color = TILE_COLORS[self.kind % len(TILE_COLORS)]
                pygame.draw.circle(surf, color, (cx, cy), radius)
        
        if self.selected:
            cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
            radius = TILE_SIZE // 2 - 6
            pygame.draw.circle(surf, WHITE, (cx, cy), radius + 3, 3)

    def update_animation(self, dt):
        speed = 12.0 * dt
        self.anim_x += (self.target_x - self.anim_x) * speed
        self.anim_y += (self.target_y - self.anim_y) * speed

    def set_grid(self, row, col):
        self.row, self.col = row, col
        self.target_x, self.target_y = utils.grid_to_pixel(row, col)