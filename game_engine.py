import pygame
import random
from collections import deque
from settings import *
import utils
from components import Tile

class Game:
    def __init__(self, level_id, mode="moves"):
        self.level_id = level_id
        self.rows, self.cols = GRID_ROWS, GRID_COLS
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.score, self.selected = 0, None
        self.animating = False
        self.anim_queue = deque()
        self.mode = mode
        self.start_time = pygame.time.get_ticks()
        self.last_special_time = pygame.time.get_ticks()
        self.double_score = False
        self.extra_time = 0
        self.bg_img = utils.game_background_image
        
        self.moves_left = MOVES_LIMIT
        
        # Activate Extra Moves
        if utils.extra_moves_active:
            print("Boost Activated: +5 Moves!")
            self.moves_left += ITEM_MOVE_BONUS
            utils.extra_moves_active = False
            utils.save_data()
        
        self.match_chain_count = 0
        self.swap_reverting = False
        self.session_coins = 0

        self.populate_initial()

        self.paused = False
        self.settings_btn_rect = pygame.Rect(SCREEN_WIDTH - 80, 20, 60, 60)
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.pause_continue_btn = pygame.Rect(cx - 120, cy - 40, 240, 60)
        self.pause_menu_btn = pygame.Rect(cx - 120, cy + 40, 240, 60)

    def populate_initial(self):
        for r in range(self.rows):
            for c in range(self.cols):
                kind = random.randrange(len(TILE_COLORS))
                self.grid[r][c] = Tile(kind, r, c)
        initial_matches = self.find_matches()
        attempts = 0
        while initial_matches and attempts < 5:
            for match in initial_matches:
                for (mr, mc) in match:
                    self.grid[mr][mc] = Tile(random.randrange(len(TILE_COLORS)), mr, mc)
            attempts += 1
            initial_matches = self.find_matches()

    def spawn_special(self):
        now = pygame.time.get_ticks()
        if now - self.last_special_time >= SPECIAL_SPAWN_RATE:
            self.last_special_time = now
            wildcards_count = sum(
                1 for r in range(self.rows) for c in range(self.cols) 
                if self.grid[r][c] and self.grid[r][c].wildcard
            )
            if wildcards_count >= 3: return
            tries = 0
            while tries < 20:
                tries += 1
                r = random.randint(0, self.rows - 1)
                c = random.randint(0, self.cols - 1)
                if self.grid[r][c] and not self.grid[r][c].wildcard:
                    self.grid[r][c] = Tile(0, r, c, wildcard=True)
                    break

    def check_group_match(self, tiles):
        colors = {t.kind for t in tiles if not t.wildcard}
        if len(colors) > 1: return False
        return True

    def find_matches(self):
        matches = []
        # Horizontal
        for r in range(self.rows):
            for c in range(self.cols - 2):
                group = [self.grid[r][c], self.grid[r][c+1], self.grid[r][c+2]]
                if any(t is None for t in group): continue
                if self.check_group_match(group):
                    match_set = [(r, c), (r, c+1), (r, c+2)]
                    group_obj = group[:]
                    k = c + 3
                    while k < self.cols:
                        t_next = self.grid[r][k]
                        if t_next is None: break
                        ref_kind = -1
                        for t in group_obj:
                            if not t.wildcard:
                                ref_kind = t.kind; break
                        if t_next.wildcard or (ref_kind != -1 and t_next.kind == ref_kind) or ref_kind == -1:
                            match_set.append((r, k))
                            group_obj.append(t_next)
                            k += 1
                        else: break
                    matches.append(match_set)

        # Vertical
        for c in range(self.cols):
            for r in range(self.rows - 2):
                group = [self.grid[r][c], self.grid[r+1][c], self.grid[r+2][c]]
                if any(t is None for t in group): continue
                if self.check_group_match(group):
                    match_set = [(r, c), (r+1, c), (r+2, c)]
                    group_obj = group[:]
                    k = r + 3
                    while k < self.rows:
                        t_next = self.grid[k][c]
                        if t_next is None: break
                        ref_kind = -1
                        for t in group_obj:
                            if not t.wildcard:
                                ref_kind = t.kind; break
                        if t_next.wildcard or (ref_kind != -1 and t_next.kind == ref_kind) or ref_kind == -1:
                            match_set.append((k, c))
                            group_obj.append(t_next)
                            k += 1
                        else: break
                    matches.append(match_set)
        return matches

    def remove_matches(self, matches):
        for match in matches:
            coords = list(dict.fromkeys(match))
            has_wildcard = any(self.grid[r][c] and self.grid[r][c].wildcard for r, c in coords)
            gain = 10 * len(coords)
            if self.double_score: gain *= 2
            self.score += gain
            if has_wildcard: self.session_coins += random.randint(2, 4)
            for r, c in coords:
                if 0 <= r < self.rows and 0 <= c < self.cols: self.grid[r][c] = None

    def collapse_columns(self):
        for c in range(self.cols):
            stack = [self.grid[r][c] for r in range(self.rows) if self.grid[r][c] is not None]
            missing = self.rows - len(stack)
            new_tiles = []
            for i in range(missing):
                start_row = -missing + i
                t = Tile(random.randrange(len(TILE_COLORS)), start_row, c)
                t.anim_x, t.anim_y = utils.grid_to_pixel(start_row, c)
                new_tiles.append(t)
            new_stack = new_tiles + stack
            for r in range(self.rows):
                t = new_stack[r]
                t.set_grid(r, c)
                self.grid[r][c] = t

    def swap_tiles(self, a, b, animate=True):
        (ar, ac), (br, bc) = a, b
        self.grid[ar][ac], self.grid[br][bc] = self.grid[br][bc], self.grid[ar][ac]
        if self.grid[ar][ac]: self.grid[ar][ac].set_grid(ar, ac)
        if self.grid[br][bc]: self.grid[br][bc].set_grid(br, bc)
        if animate:
            self.animating = True
            self.anim_queue.append(("check_matches", None))

    def are_adjacent(self, a, b):
        ar, ac = a; br, bc = b
        return abs(ar - br) + abs(ac - bc) == 1

    def handle_click(self, pos):
        if self.paused:
            if self.pause_continue_btn.collidepoint(pos): self.paused = False
            elif self.pause_menu_btn.collidepoint(pos): return "quit_to_menu"
            return 
        if self.settings_btn_rect.collidepoint(pos):
            self.paused = True
            return
        if self.animating or self.moves_left <= 0: return
        
        x, y = pos
        if not (OFFSET_X <= x < OFFSET_X + BOARD_WIDTH and OFFSET_Y <= y < OFFSET_Y + BOARD_HEIGHT): return
        r, c = utils.pixel_to_grid(x, y)
        if not (0 <= r < self.rows and 0 <= c < self.cols): return

        if self.selected is None:
            self.selected = (r, c)
            if self.grid[r][c]: self.grid[r][c].selected = True
            return
        sr, sc = self.selected
        if (r, c) == (sr, sc):
            if self.grid[sr][sc]: self.grid[sr][sc].selected = False
            self.selected = None
            return
        if self.are_adjacent((sr, sc), (r, c)):
            if self.grid[sr][sc]: self.grid[sr][sc].selected = False
            self.grid[sr][sc], self.grid[r][c] = self.grid[r][c], self.grid[sr][sc]
            if self.grid[sr][sc]: self.grid[sr][sc].set_grid(sr, sc)
            if self.grid[r][c]: self.grid[r][c].set_grid(r, c)
            self.animating = True
            self.anim_queue.append(("validate_swap", ((sr, sc), (r, c))))
            self.selected = None
            return
        if self.grid[sr][sc]: self.grid[sr][sc].selected = False
        self.selected = (r, c)
        if self.grid[r][c]: self.grid[r][c].selected = True

    def _process_one_action(self):
        if not self.anim_queue:
            if self.animating: self.animating = False
            return
        action, data = self.anim_queue.popleft()
        if action == "check_matches":
            matches = self.find_matches()
            if matches:
                self.remove_matches(matches)
                self.collapse_columns()
                self.animating = True
                self.anim_queue.append(("check_matches", None))
                self.match_chain_count += 1
                if self.match_chain_count > 30:
                    self.anim_queue.clear(); self.animating = False; self.match_chain_count = 0
            else:
                self.match_chain_count = 0; self.animating = False
        elif action == "validate_swap":
            a, b = data
            matches = self.find_matches()
            if matches:
                self.moves_left -= 1
                self.remove_matches(matches)
                self.collapse_columns()
                self.animating = True
                self.anim_queue.append(("check_matches", None))
                self.match_chain_count = 1
            else:
                (ar, ac), (br, bc) = a, b
                self.grid[ar][ac], self.grid[br][bc] = self.grid[br][bc], self.grid[ar][ac]
                if self.grid[ar][ac]: self.grid[ar][ac].set_grid(ar, ac)
                if self.grid[br][bc]: self.grid[br][bc].set_grid(br, bc)
                self.animating = True
                self.anim_queue.append(("finish_swap_back", None))
        elif action == "finish_swap_back":
            self.animating = False

    def update(self, dt):
        if self.paused: return
        self.spawn_special()
        if self.moves_left <= 0 and not self.animating and not self.anim_queue: return "gameover"
        any_anim = False
        for r in range(self.rows):
            for c in range(self.cols):
                t = self.grid[r][c]
                if t:
                    t.update_animation(dt)
                    if abs(t.anim_x - t.target_x) > 0.5 or abs(t.anim_y - t.target_y) > 0.5: any_anim = True
        if any_anim: return
        if self.anim_queue: self._process_one_action()
        else: self.animating = False

    def draw_star_bar(self, surf):
        bar_w, bar_h = 400, 30
        bar_x, bar_y = (SCREEN_WIDTH - bar_w) // 2, 20
        pygame.draw.rect(surf, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=15)
        max_score = STAR_SCORES[2]
        fill_w = min(1.0, self.score / max_score) * bar_w
        if fill_w > 0: pygame.draw.rect(surf, GOLD, (bar_x, bar_y, fill_w, bar_h), border_radius=15)
        pygame.draw.rect(surf, WHITE, (bar_x, bar_y, bar_w, bar_h), 3, border_radius=15)
        for i, target in enumerate(STAR_SCORES):
            mx = bar_x + (target / max_score) * bar_w
            pygame.draw.line(surf, WHITE, (mx, bar_y), (mx, bar_y + bar_h), 2)
            star_color = GOLD if self.score >= target else GRAY_LOCK
            pygame.draw.circle(surf, star_color, (int(mx), bar_y + bar_h + 10), 8)

    def draw(self, surf):
        if self.bg_img: surf.blit(self.bg_img, (0, 0))
        else: surf.fill(BG_COLOR)

        board_w = self.cols * TILE_SIZE
        board_h = self.rows * TILE_SIZE
        board_surf = pygame.Surface((board_w, board_h), pygame.SRCALPHA)
        board_surf.fill((0, 0, 0, 50)) 
        for i in range(self.cols + 1): pygame.draw.line(board_surf, (255, 255, 255, 30), (i * TILE_SIZE, 0), (i * TILE_SIZE, board_h))
        for i in range(self.rows + 1): pygame.draw.line(board_surf, (255, 255, 255, 30), (0, i * TILE_SIZE), (board_w, i * TILE_SIZE))
        surf.blit(board_surf, (OFFSET_X, OFFSET_Y))

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]: self.grid[r][c].draw(surf)

        mouse_pos = pygame.mouse.get_pos()
        if not self.paused:
            is_hover = self.settings_btn_rect.collidepoint(mouse_pos)
            is_click = pygame.mouse.get_pressed()[0] and is_hover
            utils.draw_menu_effect(surf, self.settings_btn_rect, is_hover, is_click)
            icon_color = WHITE if not is_hover else GOLD
            line_x = self.settings_btn_rect.x + 12; line_w = self.settings_btn_rect.width - 24
            for i in range(3): pygame.draw.line(surf, icon_color, (line_x, self.settings_btn_rect.y + 18 + i*12), (line_x + line_w, self.settings_btn_rect.y + 18 + i*12), 4)

        # Draw UI at TOP
        score_txt = utils.large_font.render(f"Score: {self.score}", True, WHITE)
        surf.blit(score_txt, (20, 20))

        moves_txt = utils.large_font.render(f"Moves: {self.moves_left}", True, (100, 255, 255))
        surf.blit(moves_txt, (SCREEN_WIDTH // 2 - 50, 70))

        coin_txt = utils.large_font.render(f"Coins: {utils.player_coins + self.session_coins}", True, GOLD)
        surf.blit(coin_txt, (SCREEN_WIDTH - 200, 80))

        self.draw_star_bar(surf)

        if self.paused:
            if utils.settings_bg_image: surf.blit(utils.settings_bg_image, (0, 0))
            else:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150)); surf.blit(overlay, (0, 0))
            
            is_cont_hover = self.pause_continue_btn.collidepoint(mouse_pos)
            is_cont_click = pygame.mouse.get_pressed()[0] and is_cont_hover
            utils.draw_menu_effect(surf, self.pause_continue_btn, is_cont_hover, is_cont_click)
            is_menu_hover = self.pause_menu_btn.collidepoint(mouse_pos)
            is_menu_click = pygame.mouse.get_pressed()[0] and is_menu_hover
            utils.draw_menu_effect(surf, self.pause_menu_btn, is_menu_hover, is_menu_click)