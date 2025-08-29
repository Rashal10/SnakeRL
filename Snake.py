import pygame
import random
import os

pygame.init()

# Game window
WIDTH, HEIGHT = 600, 400
BLOCK = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Wrap Around & Clock Snake")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
font = pygame.font.SysFont("bahnschrift", 25)

# Load apple image
try:
    apple_img = pygame.image.load("apple.png").convert_alpha()
    apple_img = pygame.transform.scale(apple_img, (BLOCK, BLOCK))
except pygame.error:
    print("Error: apple.png not found. Please place apple.png in the same directory.")
    pygame.quit()
    quit()

# High score file
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
    color1 = (200, 230, 201)  # light green
    color2 = (165, 214, 167)  # darker light green
    tile_size = 40
    for y in range(0, HEIGHT, tile_size):
        for x in range(0, WIDTH, tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            if (x // tile_size + y // tile_size) % 2 == 0:
                pygame.draw.rect(screen, color1, rect)
            else:
                pygame.draw.rect(screen, color2, rect)


def draw_clock_snake(snake_list):
    for i, pos in enumerate(snake_list):
        x, y = pos
        pygame.draw.circle(screen, (0, 128, 255), (x + BLOCK // 2, y + BLOCK // 2), BLOCK // 2 - 2)
        if i == len(snake_list) - 1:
            center = (x + BLOCK // 2, y + BLOCK // 2)
            # Hour hand
            pygame.draw.line(screen, (255, 255, 255), center, (center[0], center[1] - 6), 3)
            # Minute hand
            pygame.draw.line(screen, (255, 255, 255), center, (center[0] + 6, center[1]), 2)


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

    while not game_over:

        while game_close:
            screen.fill(WHITE)
            message("You Lost! Press C-Play Again or Q-Quit", (255, 0, 0), (WIDTH / 8, HEIGHT / 3))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    dx = -BLOCK
                    dy = 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx = BLOCK
                    dy = 0
                elif event.key == pygame.K_UP and dy == 0:
                    dy = -BLOCK
                    dx = 0
                elif event.key == pygame.K_DOWN and dy == 0:
                    dy = BLOCK
                    dx = 0

        x += dx
        y += dy

        # Wrap around screen edges
        if x >= WIDTH:
            x = 0
        elif x < 0:
            x = WIDTH - BLOCK

        if y >= HEIGHT:
            y = 0
        elif y < 0:
            y = HEIGHT - BLOCK

        draw_checkered_background()

        # Draw food (apple image)
        screen.blit(apple_img, (foodx, foody))

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check collision with itself
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        draw_clock_snake(snake_list)

        # Display score, level, high score
        message(f"Score: {score}  Level: {level}  High Score: {HIGH_SCORE}", BLACK, (10, 10))

        pygame.display.update()

        # Collision with food
        if x == foodx and y == foody:
            score += 1
            length_of_snake += 1
            foodx = round(random.randrange(0, WIDTH - BLOCK) / BLOCK) * BLOCK
            foody = round(random.randrange(0, HEIGHT - BLOCK) / BLOCK) * BLOCK

            # Update level every 5 points
            level = score // 5 + 1
            speed = 10 + level * 2

        clock.tick(speed)

    # Update high score file if needed
    if score > HIGH_SCORE:
        HIGH_SCORE = score
        with open(HS_FILE, "w") as f:
            f.write(str(HIGH_SCORE))

    pygame.quit()
    quit()


gameLoop()
