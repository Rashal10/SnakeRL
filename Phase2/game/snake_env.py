"""Gym-style Snake environment for RL training."""

import numpy as np
import random
from game.settings import (
    WIDTH, HEIGHT, BLOCK, COLS, ROWS,
    DIR_RIGHT, DIR_LEFT, DIR_UP, DIR_DOWN, CLOCKWISE,
    RL_STATE_SIZE, RL_MAX_STEPS,
    WALL_KILL, OBSTACLE_START_LEVEL, MAX_OBSTACLES, LEVEL_UP_SCORE,
)


class SnakeEnv:
    """RL-compatible Snake environment."""

    def __init__(self, render_mode=False, wall_kill=True):
        self.render_mode = render_mode
        self.wall_kill = wall_kill   # RL training uses walls for cleaner learning
        self.reset()

    def reset(self):
        """Reset and return initial state."""
        cx, cy = COLS // 2, ROWS // 2
        self.direction = DIR_RIGHT
        self.snake = [
            (cx, cy),
            (cx - 1, cy),
            (cx - 2, cy),
        ]
        self.score = 0
        self.level = 1
        self.steps_since_food = 0
        self.frame_iteration = 0
        self.obstacles = []
        self._place_food()
        return self._get_state()


    def step(self, action):
        """action: 0=straight, 1=right, 2=left → (state, reward, done, info)"""
        self.frame_iteration += 1
        self.steps_since_food += 1

        self._update_direction(action)

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if not self.wall_kill:
            new_head = (new_head[0] % COLS, new_head[1] % ROWS)

        done = False
        reward = 0

        if self._is_collision(new_head):
            done = True
            reward = -10
            return self._get_state(), reward, done, {"score": self.score}

        if self.steps_since_food > RL_MAX_STEPS * len(self.snake):
            done = True
            reward = -10
            return self._get_state(), reward, done, {"score": self.score}

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.steps_since_food = 0
            reward = 10
            self._update_level()
            self._place_food()
        else:
            self.snake.pop()
            old_dist = abs(head_x - self.food[0]) + abs(head_y - self.food[1])
            new_dist = abs(new_head[0] - self.food[0]) + abs(new_head[1] - self.food[1])
            if new_dist < old_dist:
                reward = 1
            else:
                reward = -1

        state = self._get_state()
        return state, reward, done, {"score": self.score}


    def _get_state(self):
        """
        11-dim state vector:
          [danger_straight, danger_right, danger_left,
           dir_left, dir_right, dir_up, dir_down,
           food_left, food_right, food_up, food_down]
        """
        head = self.snake[0]
        d = self.direction
        idx = CLOCKWISE.index(d)
        d_right = CLOCKWISE[(idx + 1) % 4]
        d_left = CLOCKWISE[(idx - 1) % 4]

        state = [
            # danger straight, right, left
            self._is_collision((head[0] + d[0], head[1] + d[1])),
            self._is_collision((head[0] + d_right[0], head[1] + d_right[1])),
            self._is_collision((head[0] + d_left[0], head[1] + d_left[1])),

            d == DIR_LEFT,
            d == DIR_RIGHT,
            d == DIR_UP,
            d == DIR_DOWN,

            # position of food 
            self.food[0] < head[0],   
            self.food[0] > head[0], 
            self.food[1] < head[1],
            self.food[1] > head[1], 
        ]
        return np.array(state, dtype=np.float32)

    #Helpers

    def _update_direction(self, action):
        """action: 0=straight, 1=right turn, 2=left turn"""
        idx = CLOCKWISE.index(self.direction)
        if action == 1:
            self.direction = CLOCKWISE[(idx + 1) % 4]
        elif action == 2:
            self.direction = CLOCKWISE[(idx - 1) % 4]

    def _is_collision(self, point):
        x, y = point
        if self.wall_kill:
            if x < 0 or x >= COLS or y < 0 or y >= ROWS:
                return True
        if point in self.snake[1:]:
            return True
        if point in self.obstacles:
            return True
        return False

    def _place_food(self):
        occupied = set(self.snake) | set(self.obstacles)
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in occupied:
                self.food = pos
                break

    def _update_level(self):
        self.level = self.score // LEVEL_UP_SCORE + 1
        if self.level >= OBSTACLE_START_LEVEL:
            target = min((self.level - OBSTACLE_START_LEVEL + 1) * 2, MAX_OBSTACLES)
            while len(self.obstacles) < target:
                self._place_obstacle()

    def _place_obstacle(self):
        occupied = set(self.snake) | set(self.obstacles) | {self.food}
        head = self.snake[0]
        safe_zone = set()
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                safe_zone.add((head[0] + dx, head[1] + dy))

        attempts = 0
        while attempts < 100:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in occupied and pos not in safe_zone:
                self.obstacles.append(pos)
                return
            attempts += 1

    #Pixel coordinates for rendering

    def get_snake_pixels(self):
        return [(x * BLOCK, y * BLOCK) for x, y in self.snake]

    def get_food_pixel(self):
        return (self.food[0] * BLOCK, self.food[1] * BLOCK)

    def get_obstacle_pixels(self):
        return [(x * BLOCK, y * BLOCK) for x, y in self.obstacles]
