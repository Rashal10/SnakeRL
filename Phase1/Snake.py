import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 600, 400
BLOCK = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RL Snake Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
font = pygame.font.SysFont("bahnschrift", 25)

try:
    apple_img = pygame.image.load("apple.png").convert_alpha()
    apple_img = pygame.transform.scale(apple_img, (BLOCK, BLOCK))
except pygame.error:
    print("Error: apple.png not found. Please place apple.png in the same directory.")
    pygame.quit()
    quit()

HS_FILE = "highscore.txt"
if os.path.exists(HS_FILE):
    with open(HS_FILE, "r") as f:
        HIGH_SCORE = int(f.read().strip() or "0")
else:
    HIGH_SCORE = 0

def message(msg, color, pos):
    mesg = font.render(msg, True, color)
    screen.blit(mesg, pos)

def draw_checkered_background():
    color1 = (255, 255, 204)  # light yellow
    color2 = (255, 204, 153)  # light orange
    tile_size = 40
    for y in range(0, HEIGHT, tile_size):
        for x in range(0, WIDTH, tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            if (x // tile_size + y // tile_size) % 2 == 0:
                pygame.draw.rect(screen, color1, rect)
            else:
                pygame.draw.rect(screen, color2, rect)

TONGUE_FRAMES = [0, 1]

def draw_snake_with_tongue(snake_list, tongue_state, direction):
    for i, pos in enumerate(snake_list):
        x, y = pos
        rect = pygame.Rect(x, y, BLOCK, BLOCK)

        if i == len(snake_list) - 1:
            pygame.draw.rect(screen, (0, 100, 0), rect, border_radius=8)
            eye_r = 2
            offset_x = 5
            offset_y = 5
            pygame.draw.circle(screen, WHITE, (x + offset_x, y + offset_y), eye_r)
            pygame.draw.circle(screen, WHITE, (x + BLOCK - offset_x, y + offset_y), eye_r)

            if tongue_state == 1:
                tongue_length = BLOCK // 2
                if direction == (BLOCK, 0): 
                    start = (x + BLOCK, y + BLOCK // 2)
                    end = (x + BLOCK + tongue_length, y + BLOCK // 2)
                elif direction == (-BLOCK, 0):  
                    start = (x, y + BLOCK // 2)
                    end = (x - tongue_length, y + BLOCK // 2)
                elif direction == (0, -BLOCK):  
                    start = (x + BLOCK // 2, y)
                    end = (x + BLOCK // 2, y - tongue_length)
                else: 
                    start = (x + BLOCK // 2, y + BLOCK)
                    end = (x + BLOCK // 2, y + BLOCK + tongue_length)

                pygame.draw.line(screen, (255, 0, 0), start, end, 2)

        else:
            pygame.draw.rect(screen, (34, 139, 34), rect, border_radius=6)

def gameLoop():
    global HIGH_SCORE

    game_over = False
    game_close = False

    x = WIDTH // 2
    y = HEIGHT // 2
    dx = 0
    dy = 0

    snake_list = []
    length_of_snake = 1

    foodx = round(random.randrange(0, WIDTH - BLOCK) / BLOCK) * BLOCK
    foody = round(random.randrange(0, HEIGHT - BLOCK) / BLOCK) * BLOCK

    score = 0
    level = 1
    speed = 10

    tongue_state = 0
    direction = (0, 0)

    while not game_over:

        while game_close:
            screen.fill(WHITE)
            message("You Lost! Press C-Play Again or Q-Quit", (255, 0, 0), (WIDTH / 8, HEIGHT / 3))
            pygame.display.update()

            if score > HIGH_SCORE:
                HIGH_SCORE = score
                with open(HS_FILE, "w") as f:
                    f.write(str(HIGH_SCORE))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_close = False
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK, 0
                    direction = (dx, dy); tongue_state = 1
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK, 0
                    direction = (dx, dy); tongue_state = 1
                elif event.key == pygame.K_UP and dy == 0:
                    dy, dx = -BLOCK, 0
                    direction = (0, -BLOCK); tongue_state = 1
                elif event.key == pygame.K_DOWN and dy == 0:
                    dy, dx = BLOCK, 0
                    direction = (0, BLOCK); tongue_state = 1

        x += dx
        y += dy

        if x >= WIDTH: x = 0
        elif x < 0: x = WIDTH - BLOCK
        if y >= HEIGHT: y = 0
        elif y < 0: y = HEIGHT - BLOCK

        draw_checkered_background()
        screen.blit(apple_img, (foodx, foody))

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        draw_snake_with_tongue(snake_list, tongue_state, direction)
        message(f"Score: {score}  Level: {level}  High Score: {HIGH_SCORE}", BLACK, (10, 10))
        pygame.display.update()

        if x == foodx and y == foody:
            score += 1
            length_of_snake += 1
            foodx = round(random.randrange(0, WIDTH - BLOCK) / BLOCK) * BLOCK
            foody = round(random.randrange(0, HEIGHT - BLOCK) / BLOCK) * BLOCK
            level = score // 5 + 1
            speed = 10 + level * 2

        tongue_state = TONGUE_FRAMES[(TONGUE_FRAMES.index(tongue_state) + 1) % len(TONGUE_FRAMES)]

        clock.tick(speed)

    if score > HIGH_SCORE:
        HIGH_SCORE = score
        with open(HS_FILE, "w") as f:
            f.write(str(HIGH_SCORE))

    pygame.quit()
    quit()

gameLoop()
