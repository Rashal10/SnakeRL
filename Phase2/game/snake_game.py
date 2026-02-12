import pygame
import random
import os
import sys

from game.settings import *
from game.renderer import Renderer


class PowerUp:
    def __init__(self, grid_pos, kind):
        self.grid_pos = grid_pos       
        self.kind = kind               
        self.lifetime = POWERUP_DURATION

    @property
    def pixel_pos(self):
        return (self.grid_pos[0] * BLOCK, self.grid_pos[1] * BLOCK)

    def tick(self):
        self.lifetime -= 1

    @property
    def alive(self):
        return self.lifetime > 0


class SnakeGame:
    HS_FILE = "highscore.txt"

    def __init__(self):
        self.renderer = Renderer()
        self.high_score = self._load_high_score()


    def _load_high_score(self):
        if os.path.exists(self.HS_FILE):
            try:
                with open(self.HS_FILE, "r") as f:
                    return int(f.read().strip() or "0")
            except ValueError:
                return 0
        return 0

    def _save_high_score(self):
        with open(self.HS_FILE, "w") as f:
            f.write(str(self.high_score))


    def run(self):
        """Show start menu, then launch selected mode."""
        while True:
            choice = self._start_menu()
            if choice == "play":
                self._play_loop()
            elif choice == "ai":
                self._ai_watch()
            elif choice == "quit":
                break
        self.renderer.quit()

    def _start_menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "play"
                    if event.key == pygame.K_a:
                        return "ai"
                    if event.key == pygame.K_q:
                        return "quit"

            self.renderer.draw_start_menu(self.high_score)
            self.renderer.update()
            self.renderer.flip()
            self.renderer.tick_clock(FPS)


    def _play_loop(self):
        cx, cy = COLS // 2, ROWS // 2
        snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        direction = DIR_RIGHT
        score = 0
        level = 1
        speed = GAME_SPEED

        food = self._random_empty(snake, [])
        obstacles = []
        powerup = None

        combo = 0
        combo_timer = 0
        speed_boost_timer = 0
        shield_count = 0
        double_points_timer = 0
        active_effects = []

        magnet_active = 0       
        magnet_cooldown = 0     
        food_float = None     

        paused = False
        game_over = False
        move_timer = 0

        while True:
            dt = self.renderer.clock.tick(FPS)
            move_timer += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.renderer.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if game_over:
                        if event.key == pygame.K_RETURN:
                            return   
                        if event.key == pygame.K_q:
                            self.renderer.quit()
                            sys.exit()
                        continue

                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        paused = not paused
                    if paused:
                        if event.key == pygame.K_RETURN:
                            paused = False   
                        if event.key == pygame.K_q:
                            return          
                        continue
                    if event.key == pygame.K_w:
                        if level >= MAGNET_UNLOCK_LEVEL and magnet_active == 0 and magnet_cooldown == 0:
                            magnet_active = MAGNET_DURATION
                            food_float = (float(food[0]), float(food[1]))
                            if "magnet" not in active_effects:
                                active_effects.append("magnet")

                    if event.key == pygame.K_LEFT and direction != DIR_RIGHT:
                        direction = DIR_LEFT
                    elif event.key == pygame.K_RIGHT and direction != DIR_LEFT:
                        direction = DIR_RIGHT
                    elif event.key == pygame.K_UP and direction != DIR_DOWN:
                        direction = DIR_UP
                    elif event.key == pygame.K_DOWN and direction != DIR_UP:
                        direction = DIR_DOWN

            if paused:
                self.renderer.draw_background()
                self._draw_game_state(snake, food, obstacles, powerup, direction,
                                      score, level, combo, active_effects)
                self.renderer.draw_pause()
                self.renderer.update()
                self.renderer.draw_scanlines()
                self.renderer.flip()
                continue

            if game_over:
                self.renderer.draw_background()
                self._draw_game_state(snake, food, obstacles, powerup, direction,
                                      score, level, combo, active_effects)
                self.renderer.draw_particles()
                is_new = score >= self.high_score and score > 0
                self.renderer.draw_game_over(score, self.high_score, is_new)
                self.renderer.update()
                self.renderer.draw_scanlines()
                self.renderer.flip()
                continue

            effective_speed = speed + (5 if speed_boost_timer > 0 else 0)
            tick_interval = 1000 / effective_speed 

            if move_timer < tick_interval:
                if magnet_active > 0:
                    magnet_active -= 1
                    if food_float is None:
                        food_float = (float(food[0]), float(food[1]))
                    hx, hy = float(snake[0][0]), float(snake[0][1])
                    fx, fy = food_float
                    food_float = (fx + (hx - fx) * 0.08, fy + (hy - fy) * 0.08)
                    if abs(food_float[0] - hx) < 1.0 and abs(food_float[1] - hy) < 1.0:
                        food_px = (food[0] * BLOCK, food[1] * BLOCK)
                        self.renderer.spawn_eat_particles(food_px[0], food_px[1])
                        self.renderer.trigger_flash()
                        pts = 2 if double_points_timer > 0 else 1
                        combo += 1
                        combo_timer = COMBO_WINDOW
                        if combo > 1:
                            pts += combo
                        score += pts
                        self.renderer.show_score_popup(f"+{pts}", food_px[0], food_px[1] - 10)
                        snake.insert(0, snake[0])  
                        new_level = score // LEVEL_UP_SCORE + 1
                        if new_level > level:
                            level = new_level
                            speed = GAME_SPEED + level
                        food = self._random_empty(snake, obstacles)
                        food_float = (float(food[0]), float(food[1]))
                    else:
                        new_food = (round(food_float[0]) % COLS, round(food_float[1]) % ROWS)
                        if new_food not in snake and new_food not in obstacles:
                            food = new_food
                    if magnet_active == 0:
                        magnet_cooldown = MAGNET_COOLDOWN
                        food_float = None
                        if "magnet" in active_effects:
                            active_effects.remove("magnet")
                elif magnet_cooldown > 0:
                    magnet_cooldown -= 1

                self.renderer.draw_background()
                self._draw_game_state(snake, food, obstacles, powerup, direction,
                                      score, level, combo, active_effects)
                self.renderer.draw_particles()
                self.renderer.draw_flash()
                self.renderer.draw_hud(score, level, self.high_score, combo, active_effects)
                self.renderer.draw_magnet_hud(magnet_active, magnet_cooldown, level)
                self.renderer.update()
                self.renderer.draw_scanlines()
                self.renderer.flip()
                continue

            move_timer = 0

            head = snake[0]
            dx, dy = direction
            new_head = (head[0] + dx, head[1] + dy)

            new_head = (new_head[0] % COLS, new_head[1] % ROWS)

            if new_head in snake[1:]:
                if shield_count > 0:
                    shield_count -= 1
                    if "shield" in active_effects and shield_count == 0:
                        active_effects.remove("shield")
                else:
                    game_over = True
                    self._on_death(snake, score)
                    continue

            if new_head in obstacles:
                if shield_count > 0:
                    shield_count -= 1
                    obstacles.remove(new_head)
                    if "shield" in active_effects and shield_count == 0:
                        active_effects.remove("shield")
                else:
                    game_over = True
                    self._on_death(snake, score)
                    continue

            snake.insert(0, new_head)

            ate_food = new_head == food
            if ate_food:
                points = 1
                if double_points_timer > 0:
                    points = 2

                if combo_timer > 0:
                    combo += 1
                    points += combo
                else:
                    combo = 1
                combo_timer = COMBO_WINDOW

                score += points
                self.renderer.spawn_eat_particles(new_head[0] * BLOCK, new_head[1] * BLOCK)
                self.renderer.trigger_flash()
                self.renderer.show_score_popup(f"+{points}", new_head[0] * BLOCK, new_head[1] * BLOCK - 10)

                level = score // LEVEL_UP_SCORE + 1
                speed = GAME_SPEED + level * 2

                if level >= OBSTACLE_START_LEVEL:
                    target = min((level - OBSTACLE_START_LEVEL + 1) * 2, MAX_OBSTACLES)
                    while len(obstacles) < target:
                        obs = self._random_empty(snake, obstacles + [food])
                        if obs:
                            obstacles.append(obs)

                food = self._random_empty(snake, obstacles)
                food_float = None  
            else:
                snake.pop()

            if magnet_active > 0:
                magnet_active -= 1
                if food_float is None:
                    food_float = (float(food[0]), float(food[1]))
                hx, hy = float(snake[0][0]), float(snake[0][1])
                fx, fy = food_float
                food_float = (fx + (hx - fx) * 0.08, fy + (hy - fy) * 0.08)
                if abs(food_float[0] - hx) < 1.0 and abs(food_float[1] - hy) < 1.0:
                    food_px = (food[0] * BLOCK, food[1] * BLOCK)
                    self.renderer.spawn_eat_particles(food_px[0], food_px[1])
                    self.renderer.trigger_flash()
                    pts = 2 if double_points_timer > 0 else 1
                    combo += 1
                    combo_timer = COMBO_WINDOW
                    if combo > 1:
                        pts += combo
                    score += pts
                    self.renderer.show_score_popup(f"+{pts}", food_px[0], food_px[1] - 10)
                    snake.insert(0, snake[0])
                    new_level = score // LEVEL_UP_SCORE + 1
                    if new_level > level:
                        level = new_level
                        speed = GAME_SPEED + level
                    food = self._random_empty(snake, obstacles)
                    food_float = (float(food[0]), float(food[1]))
                else:
                    new_food = (round(food_float[0]) % COLS, round(food_float[1]) % ROWS)
                    if new_food not in snake and new_food not in obstacles:
                        food = new_food
                if magnet_active == 0:
                    magnet_cooldown = MAGNET_COOLDOWN
                    food_float = None
                    if "magnet" in active_effects:
                        active_effects.remove("magnet")
            elif magnet_cooldown > 0:
                magnet_cooldown -= 1

            if combo_timer > 0:
                combo_timer -= 1
                if combo_timer == 0:
                    combo = 0

            if powerup is None and random.random() < POWERUP_SPAWN_CHANCE:
                kind = random.choice(["speed", "shield", "double"])
                pos = self._random_empty(snake, obstacles + [food])
                if pos:
                    powerup = PowerUp(pos, kind)

            if powerup:
                powerup.tick()
                if not powerup.alive:
                    powerup = None
                elif new_head == powerup.grid_pos:
                    self._activate_powerup(powerup, active_effects)
                    if powerup.kind == "speed":
                        speed_boost_timer = SPEED_BOOST_DURATION
                    elif powerup.kind == "shield":
                        shield_count = SHIELD_HITS
                    elif powerup.kind == "double":
                        double_points_timer = DOUBLE_POINTS_DURATION
                    powerup = None

            if speed_boost_timer > 0:
                speed_boost_timer -= 1
                if speed_boost_timer == 0 and "speed" in active_effects:
                    active_effects.remove("speed")
            if double_points_timer > 0:
                double_points_timer -= 1
                if double_points_timer == 0 and "double" in active_effects:
                    active_effects.remove("double")

            self.renderer.draw_background()
            self._draw_game_state(snake, food, obstacles, powerup, direction,
                                  score, level, combo, active_effects)
            self.renderer.draw_particles()
            self.renderer.draw_flash()
            self.renderer.draw_hud(score, level, self.high_score, combo, active_effects)
            self.renderer.draw_magnet_hud(magnet_active, magnet_cooldown, level)
            self.renderer.update()
            self.renderer.draw_scanlines()
            self.renderer.flip()


    def _ai_watch(self):
        """Load trained model and let it play."""
        from game.snake_env import SnakeEnv

        agent = None
        has_model = False
        try:
            import torch
            from rl.agent import DQNAgent
            agent = DQNAgent()
            model_path = os.path.join("models", "snake_dqn.pth")
            if os.path.exists(model_path):
                agent.load(model_path)
                agent.epsilon = 0  
                has_model = True
            else:
                agent = None
        except ImportError:
            pass

        env = SnakeEnv(wall_kill=True)
        state = env.reset()
        speed = GAME_SPEED + 5
        games_played = 0
        prev_score = 0
        death_pause = 0           
        prev_food = env.food     

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.renderer.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        speed = min(60, speed + 3)
                    if event.key == pygame.K_MINUS:
                        speed = max(5, speed - 3)

            if death_pause > 0:
                death_pause -= 1
                self.renderer.draw_background()
                self.renderer.draw_particles()
                self.renderer.draw_hud(prev_score, env.level, self.high_score)
                info_str = f"Game #{games_played}  |  Speed: {speed}"
                if not has_model:
                    info_str += "  |  NO MODEL (random)"
                self.renderer.draw_ai_label(info_str)
                self.renderer.draw_scanlines()
                self.renderer.update()
                self.renderer.flip()
                self.renderer.tick_clock(FPS)

                if death_pause == 0:
                    state = env.reset()
                    prev_food = env.food
                    self.renderer.score_display = 0
                continue

            if agent:
                action = agent.get_action(state)
            else:
                action = random.randint(0, 2)

            old_score = env.score
            state, reward, done, info = env.step(action)

            if env.score > old_score:
                food_px = (prev_food[0] * BLOCK, prev_food[1] * BLOCK)
                self.renderer.spawn_eat_particles(food_px[0], food_px[1])
                self.renderer.trigger_flash()
                self.renderer.show_score_popup(f"+{env.score - old_score}",
                                               food_px[0], food_px[1] - 10)
            prev_food = env.food

            if done:
                games_played += 1
                prev_score = info["score"]
                if prev_score > self.high_score:
                    self.high_score = prev_score
                    self._save_high_score()

                self.renderer.spawn_death_particles(env.get_snake_pixels())
                self.renderer.trigger_flash(frames=10, color=TEXT_DANGER)
                death_pause = 45 
                continue

            self.renderer.draw_background()
            self.renderer.draw_obstacles(env.get_obstacle_pixels())
            self.renderer.draw_food(env.get_food_pixel())
            self.renderer.draw_snake(env.get_snake_pixels(), env.direction)
            self.renderer.draw_particles()
            self.renderer.draw_flash()
            self.renderer.draw_hud(env.score, env.level, self.high_score)

            info_str = f"Game #{games_played + 1}  |  Speed: {speed}  |  +/- to change"
            if not has_model:
                info_str = f"NO TRAINED MODEL (random)  |  Run: python train.py"
            self.renderer.draw_ai_label(info_str)
            self.renderer.draw_scanlines()
            self.renderer.update()
            self.renderer.flip()
            self.renderer.tick_clock(speed)


    def _draw_game_state(self, snake, food, obstacles, powerup, direction,
                         score, level, combo, active_effects):
        obs_pixels = [(o[0] * BLOCK, o[1] * BLOCK) for o in obstacles]
        self.renderer.draw_obstacles(obs_pixels)
        self.renderer.draw_food((food[0] * BLOCK, food[1] * BLOCK))
        if powerup:
            px, py = powerup.pixel_pos
            self.renderer.draw_powerup(px, py, powerup.kind)
        snake_pixels = [(s[0] * BLOCK, s[1] * BLOCK) for s in snake]
        self.renderer.draw_snake(snake_pixels, direction)

    def _random_empty(self, snake, extra_occupied):
        occupied = set(snake) | set(extra_occupied)
        attempts = 0
        while attempts < 500:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in occupied:
                return pos
            attempts += 1
        return (0, 0)

    def _on_death(self, snake, score):
        snake_pixels = [(s[0] * BLOCK, s[1] * BLOCK) for s in snake]
        self.renderer.spawn_death_particles(snake_pixels)
        if score > self.high_score:
            self.high_score = score
            self._save_high_score()

    def _activate_powerup(self, powerup, active_effects):
        px, py = powerup.pixel_pos
        color_map = {"speed": POWERUP_SPEED, "shield": POWERUP_SHIELD, "double": POWERUP_DOUBLE}
        self.renderer.spawn_powerup_particles(px, py, color_map[powerup.kind])
        if powerup.kind not in active_effects:
            active_effects.append(powerup.kind)