import pygame
import math
import random
from game.settings import *


class Particle:
    def __init__(self, x, y, color=None, speed=None, lifetime=None, size=None):
        self.x = x
        self.y = y
        self.color = color or random.choice(PARTICLE_COLORS)
        angle = random.uniform(0, 2 * math.pi)
        spd = speed or random.uniform(1.5, 4.5)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.lifetime = lifetime or random.randint(20, 45)
        self.age = 0
        self.size = size or random.uniform(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        self.age += 1

    def draw(self, surface):
        alpha = max(0, 1 - self.age / self.lifetime)
        r, g, b = self.color[:3]
        s = max(1, self.size * alpha)
        glow_surf = pygame.Surface((int(s * 6), int(s * 6)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (r, g, b, int(50 * alpha)),
                           (int(s * 3), int(s * 3)), int(s * 3))
        pygame.draw.circle(glow_surf, (r, g, b, int(180 * alpha)),
                           (int(s * 3), int(s * 3)), int(s * 1.5))
        pygame.draw.circle(glow_surf, (min(255, r + 80), min(255, g + 80), min(255, b + 80), int(255 * alpha)),
                           (int(s * 3), int(s * 3)), int(s * 0.6))
        surface.blit(glow_surf, (self.x - s * 3, self.y - s * 3))

    @property
    def alive(self):
        return self.age < self.lifetime


class TrailSegment:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 100
        self.size = BLOCK * 0.35

    def update(self):
        self.alpha -= 3.5
        self.size *= 0.96

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((int(self.size * 3), int(self.size * 3)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*SNAKE_HEAD[:3], int(max(0, self.alpha))),
                               (int(self.size * 1.5), int(self.size * 1.5)), int(self.size * 1.5))
            surface.blit(s, (self.x + BLOCK // 2 - self.size * 1.5,
                             self.y + BLOCK // 2 - self.size * 1.5))

    @property
    def alive(self):
        return self.alpha > 0


class BGParticle:

    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.size = random.uniform(0.5, 2.0)
        self.speed = random.uniform(0.1, 0.4)
        self.alpha = random.randint(15, 50)
        self.color = random.choice([(0, 255, 120), (0, 180, 255), (120, 80, 255)])

    def update(self):
        self.y -= self.speed
        if self.y < -5:
            self.y = HEIGHT + 5
            self.x = random.uniform(0, WIDTH)

    def draw(self, surface):
        s = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha),
                           (int(self.size * 2), int(self.size * 2)), int(self.size * 2))
        surface.blit(s, (self.x, self.y))


class Renderer:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SnakeRL")
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.SysFont(FONT_NAME, FONT_SIZE_LARGE, bold=True)
        self.font_med = pygame.font.SysFont(FONT_NAME, FONT_SIZE_MEDIUM, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, FONT_SIZE_SMALL)
        self.font_tiny = pygame.font.SysFont(FONT_NAME, FONT_SIZE_TINY)

        self.particles = []
        self.trails = []
        self.bg_particles = [BGParticle() for _ in range(35)]

        self.tick = 0
        self.screen_flash = 0
        self.screen_flash_color = (255, 255, 255)
        self.score_popup = None
        self.score_display = 0          
        self.score_target = 0

        self._scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 3):
            pygame.draw.line(self._scanline_surf, (0, 0, 0, 12), (0, y), (WIDTH, y))

    def draw_background(self):
        self.screen.fill(BG_COLOR)

        grid_alpha = int(18 + 6 * math.sin(self.tick * 0.02))
        for x in range(0, WIDTH, BLOCK):
            pygame.draw.line(self.screen, (*GRID_COLOR[:3],), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, BLOCK):
            pygame.draw.line(self.screen, (*GRID_COLOR[:3],), (0, y), (WIDTH, y))


        edge_size = 3
        edge_alpha = int(40 + 20 * math.sin(self.tick * 0.03))
        edge_surf = pygame.Surface((WIDTH, edge_size), pygame.SRCALPHA)
        edge_surf.fill((*SNAKE_HEAD[:3], edge_alpha))
        self.screen.blit(edge_surf, (0, 0))
        self.screen.blit(edge_surf, (0, HEIGHT - edge_size))
        edge_v = pygame.Surface((edge_size, HEIGHT), pygame.SRCALPHA)
        edge_v.fill((*SNAKE_HEAD[:3], edge_alpha))
        self.screen.blit(edge_v, (0, 0))
        self.screen.blit(edge_v, (WIDTH - edge_size, 0))


        for bp in self.bg_particles:
            bp.update()
            bp.draw(self.screen)

    #Snake 

    def draw_snake(self, snake_pixels, direction):
        n = len(snake_pixels)
        if n == 0:
            return

        if n > 1:
            tail = snake_pixels[-1]
            self.trails.append(TrailSegment(tail[0], tail[1]))

        for i in range(n - 1, -1, -1):
            px, py = snake_pixels[i]
            t = 1 - (i / max(n - 1, 1))  
            r = int(SNAKE_BODY_END[0] + (SNAKE_BODY_START[0] - SNAKE_BODY_END[0]) * t)
            g = int(SNAKE_BODY_END[1] + (SNAKE_BODY_START[1] - SNAKE_BODY_END[1]) * t)
            b = int(SNAKE_BODY_END[2] + (SNAKE_BODY_START[2] - SNAKE_BODY_END[2]) * t)

            if i < n - 1:
                next_px, next_py = snake_pixels[i + 1]
                mid_x = (px + next_px) / 2
                mid_y = (py + next_py) / 2

                if abs(px - next_px) <= BLOCK and abs(py - next_py) <= BLOCK:
                    conn_rect = pygame.Rect(int(mid_x) + 2, int(mid_y) + 2, BLOCK - 4, BLOCK - 4)
                    pygame.draw.rect(self.screen, (r, g, b), conn_rect, border_radius=3)

            rect = pygame.Rect(px + 1, py + 1, BLOCK - 2, BLOCK - 2)
            pygame.draw.rect(self.screen, (r, g, b), rect, border_radius=5)

            highlight = pygame.Rect(px + 3, py + 3, BLOCK // 3, BLOCK // 3)
            pygame.draw.rect(self.screen, (min(255, r + 60), min(255, g + 60), min(255, b + 60)),
                             highlight, border_radius=2)

            if i == 0:
                glow_size = BLOCK * 3.0
                glow_surf = pygame.Surface((int(glow_size), int(glow_size)), pygame.SRCALPHA)
                glow_alpha = int(35 + 15 * math.sin(self.tick * 0.1))
                pygame.draw.circle(glow_surf, (*SNAKE_HEAD[:3], glow_alpha),
                                   (int(glow_size // 2), int(glow_size // 2)),
                                   int(glow_size // 2))
                self.screen.blit(glow_surf, (px + BLOCK // 2 - glow_size // 2,
                                             py + BLOCK // 2 - glow_size // 2))

                pygame.draw.rect(self.screen, SNAKE_HEAD, rect, border_radius=6)

                shine = pygame.Rect(px + 3, py + 3, BLOCK // 2.5, BLOCK // 2.5)
                pygame.draw.rect(self.screen, (min(255, SNAKE_HEAD[0] + 80),
                                               min(255, SNAKE_HEAD[1] + 80),
                                               min(255, SNAKE_HEAD[2] + 80)),
                                 shine, border_radius=3)

                self._draw_eyes(px, py, direction)

    def _draw_eyes(self, px, py, direction):
        cx, cy = px + BLOCK // 2, py + BLOCK // 2
        dx, dy = direction if direction != (0, 0) else (1, 0)

        perp_x, perp_y = -dy, dx
        eye_offset = 4
        pupil_shift = 2

        for side in (-1, 1):
            ex = cx + perp_x * eye_offset * side
            ey = cy + perp_y * eye_offset * side

            pygame.draw.circle(self.screen, (220, 240, 255), (int(ex), int(ey)), 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(ex), int(ey)), 2)
            pygame.draw.circle(self.screen, (10, 10, 10),
                               (int(ex + dx * pupil_shift), int(ey + dy * pupil_shift)), 1)


    def draw_food(self, food_pixel):
        fx, fy = food_pixel
        center = (fx + BLOCK // 2, fy + BLOCK // 2)

        pulse = math.sin(self.tick * 0.08) * 0.35 + 1.0
        glow_r = int(BLOCK * 1.2 * pulse)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        glow_alpha = int(30 + 20 * math.sin(self.tick * 0.08))
        pygame.draw.circle(glow_surf, (*FOOD_COLOR[:3], glow_alpha),
                           (glow_r, glow_r), glow_r)
        self.screen.blit(glow_surf, (center[0] - glow_r, center[1] - glow_r))

        pulse2 = math.sin(self.tick * 0.08 + 1.5) * 0.25 + 0.8
        glow_r2 = int(BLOCK * 0.9 * pulse2)
        glow_surf2 = pygame.Surface((glow_r2 * 2, glow_r2 * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf2, (*FOOD_COLOR[:3], int(glow_alpha * 0.5)),
                           (glow_r2, glow_r2), glow_r2)
        self.screen.blit(glow_surf2, (center[0] - glow_r2, center[1] - glow_r2))

        for k in range(4):
            angle = self.tick * 0.04 + k * (math.pi / 2)
            rx = center[0] + int(math.cos(angle) * BLOCK * 0.6)
            ry = center[1] + int(math.sin(angle) * BLOCK * 0.6)
            dot_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, (*FOOD_COLOR[:3], 120), (3, 3), 3)
            self.screen.blit(dot_surf, (rx - 3, ry - 3))

        inner_size = int(BLOCK * 0.38 * (0.9 + 0.1 * math.sin(self.tick * 0.12)))
        pygame.draw.circle(self.screen, FOOD_COLOR, center, inner_size + 1)
        pygame.draw.circle(self.screen, (255, 150, 160), center, max(1, inner_size // 2))
        pygame.draw.circle(self.screen, (255, 220, 220), (center[0] - 1, center[1] - 2), max(1, inner_size // 4))


    def draw_powerup(self, px, py, kind):
        center = (px + BLOCK // 2, py + BLOCK // 2)
        color_map = {"speed": POWERUP_SPEED, "shield": POWERUP_SHIELD, "double": POWERUP_DOUBLE}
        icon_map = {"speed": ">>", "shield": "O", "double": "x2"}
        color = color_map.get(kind, POWERUP_SPEED)

        pulse = math.sin(self.tick * 0.1) * 0.3 + 1.0
        gr = int(BLOCK * 1.3 * pulse)
        gs = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*color, 40), (gr, gr), gr)
        self.screen.blit(gs, (center[0] - gr, center[1] - gr))

        angle = self.tick * 0.05
        pts = []
        for k in range(4):
            a = angle + k * (math.pi / 2)
            pts.append((center[0] + int(math.cos(a) * BLOCK * 0.45),
                        center[1] + int(math.sin(a) * BLOCK * 0.45)))
        pygame.draw.polygon(self.screen, color, pts)
        inner_pts = [(int(p[0] * 0.7 + center[0] * 0.3), int(p[1] * 0.7 + center[1] * 0.3)) for p in pts]
        pygame.draw.polygon(self.screen, (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60)),
                            inner_pts)

        icon = icon_map.get(kind, "?")
        txt = self.font_tiny.render(icon, True, (255, 255, 255))
        self.screen.blit(txt, (center[0] - txt.get_width() // 2,
                               center[1] - txt.get_height() // 2))


    def draw_obstacles(self, obstacle_pixels):
        for ox, oy in obstacle_pixels:
            rect = pygame.Rect(ox + 2, oy + 2, BLOCK - 4, BLOCK - 4)
            pygame.draw.rect(self.screen, OBSTACLE_COLOR, rect, border_radius=3)
            pygame.draw.rect(self.screen, (60, 60, 80), pygame.Rect(ox + 5, oy + 5, BLOCK - 10, BLOCK - 10), 1, border_radius=2)
            pygame.draw.line(self.screen, (100, 100, 120),
                             (ox + 5, oy + 5), (ox + BLOCK - 5, oy + BLOCK - 5), 1)
            pygame.draw.line(self.screen, (100, 100, 120),
                             (ox + BLOCK - 5, oy + 5), (ox + 5, oy + BLOCK - 5), 1)


    def spawn_eat_particles(self, x, y, count=18):
        for _ in range(count):
            c = random.choice([FOOD_COLOR, (255, 215, 0), (255, 255, 255)])
            self.particles.append(Particle(x + BLOCK // 2, y + BLOCK // 2, color=c,
                                           speed=random.uniform(2, 5)))

    def spawn_death_particles(self, snake_pixels):
        for px, py in snake_pixels[:12]:
            for _ in range(8):
                self.particles.append(
                    Particle(px + BLOCK // 2, py + BLOCK // 2,
                             color=random.choice(PARTICLE_COLORS),
                             speed=random.uniform(2, 7),
                             lifetime=random.randint(30, 60)))

    def spawn_powerup_particles(self, x, y, color):
        for _ in range(14):
            self.particles.append(Particle(x + BLOCK // 2, y + BLOCK // 2, color=color,
                                           speed=random.uniform(1.5, 4)))

    def update_particles(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]
        for t in self.trails:
            t.update()
        self.trails = [t for t in self.trails if t.alive]

    def draw_particles(self):
        for t in self.trails:
            t.draw(self.screen)
        for p in self.particles:
            p.draw(self.screen)


    def draw_hud(self, score, level, high_score, combo=0, active_effects=None):
        self.score_target = score
        if self.score_display < self.score_target:
            self.score_display += max(1, (self.score_target - self.score_display) // 3)
        elif self.score_display > self.score_target:
            self.score_display = self.score_target

        bar = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 180))
        self.screen.blit(bar, (0, 0))

        pygame.draw.line(self.screen, (*SNAKE_HEAD[:3], ), (0, 40), (WIDTH, 40), 1)

        score_txt = self.font_small.render(f"SCORE  {int(self.score_display)}", True, TEXT_PRIMARY)
        self.screen.blit(score_txt, (16, 8))

        lvl_txt = self.font_small.render(f"LVL {level}", True, TEXT_ACCENT)
        self.screen.blit(lvl_txt, (WIDTH // 2 - lvl_txt.get_width() // 2, 8))

        hs_txt = self.font_small.render(f"BEST  {high_score}", True, TEXT_SECONDARY)
        self.screen.blit(hs_txt, (WIDTH - hs_txt.get_width() - 16, 8))

        if combo > 1:
            combo_str = f"COMBO x{combo}!"
            combo_txt = self.font_small.render(combo_str, True, POWERUP_DOUBLE)
            cx = WIDTH // 2 - combo_txt.get_width() // 2

            glow_s = pygame.Surface((combo_txt.get_width() + 20, combo_txt.get_height() + 10), pygame.SRCALPHA)
            glow_s.fill((*POWERUP_DOUBLE[:3], 30))
            self.screen.blit(glow_s, (cx - 10, 38))
            self.screen.blit(combo_txt, (cx, 44))

        if active_effects:
            x_off = 16
            for eff in active_effects:
                color_map = {"speed": POWERUP_SPEED, "shield": POWERUP_SHIELD, "double": POWERUP_DOUBLE, "magnet": MAGNET_COLOR}
                c = color_map.get(eff, TEXT_ACCENT)

                pill = pygame.Surface((60, 22), pygame.SRCALPHA)
                pill.fill((*c[:3], 50))
                self.screen.blit(pill, (x_off - 4, HEIGHT - 28))
                et = self.font_tiny.render(eff.upper(), True, c)
                self.screen.blit(et, (x_off, HEIGHT - 26))
                x_off += et.get_width() + 20

        if self.score_popup:
            txt, sx, sy, frames = self.score_popup
            alpha = max(0, int(255 * frames / 30))
            pop = self.font_med.render(txt, True, TEXT_ACCENT)
            pop.set_alpha(alpha)
            self.screen.blit(pop, (sx, sy - (30 - frames) * 2))
            self.score_popup = (txt, sx, sy, frames - 1)
            if frames <= 0:
                self.score_popup = None

    def show_score_popup(self, text, x, y):
        self.score_popup = (text, x, y, 30)

    def trigger_flash(self, frames=6, color=None):
        self.screen_flash = frames
        self.screen_flash_color = color or SNAKE_HEAD

    def draw_flash(self):
        if self.screen_flash > 0:
            alpha = int(70 * (self.screen_flash / 6))
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((*self.screen_flash_color[:3], alpha))
            self.screen.blit(flash, (0, 0))
            self.screen_flash -= 1


    def draw_scanlines(self):
        self.screen.blit(self._scanline_surf, (0, 0))


    def draw_magnet_hud(self, magnet_active, magnet_cooldown, level=1):
        bar_w, bar_h = 120, 14
        bx = WIDTH - bar_w - 16
        by = HEIGHT - 24

        bg = pygame.Surface((bar_w + 4, bar_h + 4), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        self.screen.blit(bg, (bx - 2, by - 2))

        if level < MAGNET_UNLOCK_LEVEL:

            pygame.draw.rect(self.screen, (40, 40, 55), (bx, by, bar_w, bar_h), border_radius=3)
            label = self.font_tiny.render(f"MAGNET (LVL {MAGNET_UNLOCK_LEVEL})", True, (80, 80, 100))
        
        elif magnet_active > 0:

            frac = magnet_active / MAGNET_DURATION
            fill_w = int(bar_w * frac)
            pygame.draw.rect(self.screen, MAGNET_COLOR, (bx, by, fill_w, bar_h), border_radius=3)
            label = self.font_tiny.render("MAGNET", True, (255, 255, 255))
        
        elif magnet_cooldown > 0:
            frac = 1 - (magnet_cooldown / MAGNET_COOLDOWN)
            fill_w = int(bar_w * frac)
            pygame.draw.rect(self.screen, (80, 80, 100), (bx, by, bar_w, bar_h), border_radius=3)
            pygame.draw.rect(self.screen, (100, 120, 150), (bx, by, fill_w, bar_h), border_radius=3)
            label = self.font_tiny.render("COOLDOWN", True, TEXT_SECONDARY)
        
        else:
            ready_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            ready_surf.fill((*MAGNET_COLOR[:3], 60))
            self.screen.blit(ready_surf, (bx, by))
            pygame.draw.rect(self.screen, MAGNET_COLOR, (bx, by, bar_w, bar_h), 1, border_radius=3)
            label = self.font_tiny.render("[W] MAGNET", True, MAGNET_COLOR)

        self.screen.blit(label, (bx + bar_w // 2 - label.get_width() // 2,
                                  by - 1))


    def draw_start_menu(self, high_score):
        self.draw_background()

        glow_alpha = int(30 + 20 * math.sin(self.tick * 0.04))
        title = self.font_large.render("SnakeRL", True, SNAKE_HEAD)
        title_x = WIDTH // 2 - title.get_width() // 2
        title_y = HEIGHT // 5
        glow_w, glow_h = title.get_width() + 80, title.get_height() + 40
        gs = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(gs, (*SNAKE_HEAD[:3], glow_alpha), (0, 0, glow_w, glow_h))
        self.screen.blit(gs, (title_x - 40, title_y - 20))

        self.screen.blit(title, (title_x, title_y))


        line_w = 200
        line_y = HEIGHT // 5 + 80
        pygame.draw.line(self.screen, (*TEXT_ACCENT[:3],),
                         (WIDTH // 2 - line_w // 2, line_y), (WIDTH // 2 + line_w // 2, line_y), 1)

        if high_score > 0:
            hs = self.font_small.render(f"HIGH SCORE: {high_score}", True, POWERUP_DOUBLE)
            self.screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, HEIGHT // 2 - 10))

        alpha = int(160 + 90 * math.sin(self.tick * 0.06))
        options = [
            ("[ ENTER ]  Play Game", TEXT_PRIMARY),
            ("[ A ]  Watch AI Play", TEXT_PRIMARY),
            ("[ Q ]  Quit", TEXT_SECONDARY),
        ]
        y_start = HEIGHT // 2 + 35
        for i, (text, color) in enumerate(options):
            opt = self.font_small.render(text, True, color)
            if i < 2:
                opt.set_alpha(alpha)
            self.screen.blit(opt, (WIDTH // 2 - opt.get_width() // 2, y_start + i * 40))

        ctrl = self.font_tiny.render("Arrow Keys = Move  |  P = Pause  |  W = Magnet", True, TEXT_SECONDARY)
        self.screen.blit(ctrl, (WIDTH // 2 - ctrl.get_width() // 2, HEIGHT - 45))

        ver = self.font_tiny.render("v2.0", True, (60, 60, 80))
        self.screen.blit(ver, (WIDTH - 45, HEIGHT - 25))

        self.draw_scanlines()

    def draw_game_over(self, score, high_score, is_new_record):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("GAME OVER", True, TEXT_DANGER)
        glow_w = title.get_width() + 40
        glow_h = title.get_height() + 20
        gs = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(gs, (*TEXT_DANGER[:3], 25), (0, 0, glow_w, glow_h))
        self.screen.blit(gs, (WIDTH // 2 - glow_w // 2, HEIGHT // 4 - 10))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        if is_new_record:
            rec_alpha = int(180 + 70 * math.sin(self.tick * 0.1))
            rec = self.font_med.render("NEW HIGH SCORE!", True, POWERUP_DOUBLE)
            rec.set_alpha(rec_alpha)
            self.screen.blit(rec, (WIDTH // 2 - rec.get_width() // 2, HEIGHT // 4 + 75))

        card_w, card_h = 280, 100
        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card.fill((20, 20, 40, 200))
        pygame.draw.rect(card, (*TEXT_ACCENT[:3], 80), (0, 0, card_w, card_h), 1, border_radius=8)
        self.screen.blit(card, (WIDTH // 2 - card_w // 2, HEIGHT // 2 - 10))

        sc = self.font_med.render(f"Score: {score}", True, TEXT_PRIMARY)
        self.screen.blit(sc, (WIDTH // 2 - sc.get_width() // 2, HEIGHT // 2))
        hs = self.font_small.render(f"Best: {high_score}", True, TEXT_SECONDARY)
        self.screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, HEIGHT // 2 + 45))

        alpha = int(160 + 90 * math.sin(self.tick * 0.06))
        r1 = self.font_small.render("[ ENTER ]  Play Again", True, TEXT_ACCENT)
        r2 = self.font_small.render("[ Q ]  Quit", True, TEXT_SECONDARY)
        r1.set_alpha(alpha)
        self.screen.blit(r1, (WIDTH // 2 - r1.get_width() // 2, HEIGHT // 2 + 120))
        self.screen.blit(r2, (WIDTH // 2 - r2.get_width() // 2, HEIGHT // 2 + 160))

        self.draw_scanlines()

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("PAUSED", True, TEXT_ACCENT)
        glow_w = title.get_width() + 40
        glow_h = title.get_height() + 20
        gs = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(gs, (*TEXT_ACCENT[:3], 20), (0, 0, glow_w, glow_h))
        self.screen.blit(gs, (WIDTH // 2 - glow_w // 2, HEIGHT // 2 - 70))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))

        alpha = int(160 + 90 * math.sin(self.tick * 0.06))
        r1 = self.font_small.render("[ ENTER ]  Resume", True, TEXT_PRIMARY)
        r2 = self.font_small.render("[ Q ]  Back to Menu", True, TEXT_SECONDARY)
        r1.set_alpha(alpha)
        self.screen.blit(r1, (WIDTH // 2 - r1.get_width() // 2, HEIGHT // 2 + 20))
        self.screen.blit(r2, (WIDTH // 2 - r2.get_width() // 2, HEIGHT // 2 + 60))

        self.draw_scanlines()


    def draw_ai_label(self, episode_info=None):
        bar = pygame.Surface((WIDTH, 32), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 180))
        self.screen.blit(bar, (0, HEIGHT - 32))
        pygame.draw.line(self.screen, (*POWERUP_SPEED[:3],), (0, HEIGHT - 32), (WIDTH, HEIGHT - 32), 1)

        txt = "AI PLAYING"
        if episode_info:
            txt += f"  |  {episode_info}"
        txt += "  |  Press Q to return"
        label = self.font_tiny.render(txt, True, TEXT_SECONDARY)
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT - 26))


    def update(self):
        self.tick += 1
        self.update_particles()

    def flip(self):
        pygame.display.flip()

    def tick_clock(self, fps):
        self.clock.tick(fps)

    def quit(self):
        pygame.quit()