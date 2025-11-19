import pygame
import sys
from settings import *
import utils
from components import MenuButton, Tile
from game_engine import Game

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MATCH ADVENTURE")
clock = pygame.time.Clock()

# Load Assets
utils.load_all_images()
utils.load_data()

# --- Menu Buttons ---
try:
    menu_bg_img = pygame.image.load(MENU_BG_PATH).convert_alpha()
    menu_bg_img = pygame.transform.scale(menu_bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except: menu_bg_img = None

btn_w, btn_h = 270, 75
center_x = SCREEN_WIDTH // 2 - (btn_w // 2)
menu_buttons = [
    MenuButton(pygame.Rect(center_x, 490, btn_w, btn_h), "play", "PLAY"),
    MenuButton(pygame.Rect(center_x, 580, btn_w, btn_h), "shop", "SHOP"),
    MenuButton(pygame.Rect(center_x, 670, btn_w, btn_h), "quit", "EXIT")
]

# ---------- Scenes ----------
def show_gameover(score, stars):
    while True:
        mouse = pygame.mouse.get_pos()
        if utils.game_over_bg_image:
            screen.blit(utils.game_over_bg_image, (0, 0))
        else:
            screen.fill(BG_COLOR)
            title_surf = utils.title_font.render("GAME OVER", True, GOLD)
            screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 200)))
        
        if not utils.game_over_bg_image:
            score_surf = utils.large_font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, 300)))
            star_txt = utils.large_font.render(f"Stars: {stars}", True, GOLD)
            screen.blit(star_txt, star_txt.get_rect(center=(SCREEN_WIDTH // 2, 350)))
        
        back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 120, 450, 240, 60)
        is_back_hover = back_btn.collidepoint(mouse)
        is_back_click = pygame.mouse.get_pressed()[0] and is_back_hover
        
        utils.draw_menu_effect(screen, back_btn, is_back_hover, is_back_click)
        if not utils.game_over_bg_image:
             utils.draw_button(screen, back_btn, "Back to Menu", is_back_hover)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(mouse): return
        pygame.display.flip()
        clock.tick(FPS)

def run_game_loop(level_id):
    game = Game(level_id)
    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = game.handle_click(event.pos)
                if action == "quit_to_menu": return 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: game.reset()
                elif event.key == pygame.K_ESCAPE: game.paused = not game.paused

        result = game.update(dt)
        game.draw(screen)
        pygame.display.flip()
        
        if result == "gameover":
            stars_earned = 0
            if game.score >= STAR_SCORES[2]: stars_earned = 3
            elif game.score >= STAR_SCORES[1]: stars_earned = 2
            elif game.score >= STAR_SCORES[0]: stars_earned = 1
            
            utils.player_coins += game.session_coins
            
            if stars_earned == 3:
                utils.level_stars[level_id] = 3
                utils.save_data()
                return # Auto return to unlock next
            else:
                utils.level_stars[level_id] = max(utils.level_stars[level_id], stars_earned)
                utils.save_data()
                show_gameover(game.score, stars_earned)
            break

def level_selection_screen():
    level_bg_img = None
    try:
        level_bg_img = pygame.transform.scale(pygame.image.load(LEVEL_SELECT_BG_PATH).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    except: 
        level_bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        level_bg_img.fill(LEVEL_BG_COLOR)

    stone_w, stone_h = STONE_SIZE, STONE_SIZE
    stone_radius = stone_w // 2
    back_btn = pygame.Rect(SCREEN_WIDTH - 190, SCREEN_HEIGHT - 90, 160, 60)
    base_x = 597 

    lock_status = {
        "level_3": False, 
        "level_2": utils.level_stars["level_3"] < 3,
        "level_1": utils.level_stars["level_2"] < 3
    }
    level_buttons = [
        (pygame.Rect(base_x, 190, stone_w, stone_h), "level_1"),
        (pygame.Rect(base_x, 390, stone_w, stone_h), "level_2"),
        (pygame.Rect(base_x, 590, stone_w, stone_h), "level_3"),
    ]

    while True:
        mouse = pygame.mouse.get_pos()
        screen.blit(level_bg_img, (0, 0))
        
        for rect, lvl_id in level_buttons:
            is_locked = lock_status[lvl_id]
            stars = utils.level_stars[lvl_id]
            is_hover = utils.is_point_in_circle(mouse, rect.center, stone_radius) and not is_locked
            utils.draw_level_button_on_stone(screen, rect, is_locked, stars, is_hover)
            
        is_back_hover = back_btn.collidepoint(mouse)
        is_back_click = pygame.mouse.get_pressed()[0] and is_back_hover
        utils.draw_menu_effect(screen, back_btn, is_back_hover, is_back_click)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if back_btn.collidepoint(mouse): return
                for rect, lvl_id in level_buttons:
                    if utils.is_point_in_circle(mouse, rect.center, stone_radius) and not lock_status[lvl_id]:
                        run_game_loop(lvl_id)
                        lock_status["level_2"] = utils.level_stars["level_3"] < 3
                        lock_status["level_1"] = utils.level_stars["level_2"] < 3
                        return 
        pygame.display.flip(); clock.tick(FPS)

def shop_screen():
    back_btn = pygame.Rect(SCREEN_WIDTH - 180, 30, 160, 60)
    item_size, gap = 150, 225
    total_width = (item_size * 3) + (gap * 2)
    start_x = (SCREEN_WIDTH - total_width) // 2
    start_y = SCREEN_HEIGHT // 2 
    shop_items = [pygame.Rect(start_x + (item_size+gap)*i, start_y, item_size, item_size) for i in range(3)]

    while True:
        mouse = pygame.mouse.get_pos()
        if utils.shop_bg_image: screen.blit(utils.shop_bg_image, (0, 0))
        else: screen.fill((20, 20, 20))
        
        is_back_hover = back_btn.collidepoint(mouse)
        is_back_click = pygame.mouse.get_pressed()[0] and is_back_hover
        utils.draw_menu_effect(screen, back_btn, is_back_hover, is_back_click)

        for i, item_rect in enumerate(shop_items):
            is_item_hover = item_rect.collidepoint(mouse)
            is_item_click = pygame.mouse.get_pressed()[0] and is_item_hover
            utils.draw_menu_effect(screen, item_rect, is_item_hover, is_item_click)
            
            if i == 0:
                status = "READY" if utils.extra_moves_active else f"{ITEM_MOVE_PRICE}C"
                color = GREEN_BUY if utils.extra_moves_active else WHITE
                txt = utils.font.render(status, True, color)
                screen.blit(txt, (item_rect.centerx - txt.get_width()//2, item_rect.bottom + 5))
                t = utils.font.render("+5 Moves", True, GOLD)
                screen.blit(t, (item_rect.centerx - t.get_width()//2, item_rect.top - 25))
            
            elif i == 1:
                status = "OWNED" if utils.is_music_unlocked else f"{ITEM_MUSIC_PRICE}C"
                color = GREEN_BUY if utils.is_music_unlocked else WHITE
                txt = utils.font.render(status, True, color)
                screen.blit(txt, (item_rect.centerx - txt.get_width()//2, item_rect.bottom + 5))
                t = utils.font.render("Music", True, GOLD)
                screen.blit(t, (item_rect.centerx - t.get_width()//2, item_rect.top - 25))

        coin_txt = utils.large_font.render(f"Total Coins: {utils.player_coins}", True, GOLD)
        screen.blit(coin_txt, coin_txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if back_btn.collidepoint(mouse): return
                
                # Buy Moves
                if shop_items[0].collidepoint(mouse):
                    if not utils.extra_moves_active:
                        if utils.player_coins >= ITEM_MOVE_PRICE:
                            utils.player_coins -= ITEM_MOVE_PRICE
                            utils.extra_moves_active = True
                            utils.save_data()
                
                # Buy Music
                elif shop_items[1].collidepoint(mouse):
                    if not utils.is_music_unlocked:
                        if utils.player_coins >= ITEM_MUSIC_PRICE:
                            utils.player_coins -= ITEM_MUSIC_PRICE
                            utils.is_music_unlocked = True
                            utils.save_data()
                            utils.play_music()

        pygame.display.flip(); clock.tick(FPS)

def main_menu_loop():
    current_click = None
    while True:
        if menu_bg_img: screen.blit(menu_bg_img, (0, 0))
        else: screen.fill(BG_COLOR)
        mouse = pygame.mouse.get_pos()
        hovered_button = None
        for btn in menu_buttons:
            if btn.rect.collidepoint(mouse): hovered_button = btn; break
        if pygame.mouse.get_pressed()[0]: current_click = hovered_button
        else: current_click = None
        for btn in menu_buttons:
            is_hover = (btn == hovered_button) and (btn != current_click)
            is_click = (btn == current_click)
            utils.draw_menu_effect(screen, btn.rect, is_hover, is_click)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for btn in menu_buttons:
                    action = btn.handle_click(event.pos)
                    if action == "play": level_selection_screen()
                    elif action == "shop": shop_screen()
                    elif action == "quit": pygame.quit(); sys.exit()
        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__":
    main_menu_loop()