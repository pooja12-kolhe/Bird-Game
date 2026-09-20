import pygame
import random
import sys

pygame.init()

# ------------------------
# Window
# ------------------------
WIDTH = 500
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()

# ------------------------
# Fonts
# ------------------------
title_font = pygame.font.SysFont("Arial", 55, bold=True)
font = pygame.font.SysFont("Arial", 35)
small_font = pygame.font.SysFont("Arial", 25)

# ------------------------
# Colors
# ------------------------
DAY = (135,206,235)
NIGHT = (25,25,60)
GREEN = (0,180,0)
DARK_GREEN = (0,120,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
YELLOW = (255,255,0)
ORANGE = (255,180,0)

background = DAY

# ------------------------
# Bird
# ------------------------
bird_x = 100
bird_y = HEIGHT//2
bird_radius = 20

gravity = 0.18
velocity = 0
jump = -8

# ------------------------
# Pipe
# ------------------------
pipe_width = 80
pipe_gap = 180
pipe_speed = 5

pipe_x = WIDTH
pipe_height = random.randint(150,450)

score = 0
passed = False

# ------------------------
# Ground
# ------------------------
ground_height = 60

# ------------------------
# Button
# ------------------------
start_button = pygame.Rect(170,320,160,60)

game_started = False
game_over = False

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if not game_started:

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_started = True

        elif not game_over:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    velocity = jump

    if game_started and not game_over:

        velocity += gravity
        bird_y += velocity

        pipe_x -= pipe_speed

        if pipe_x < -pipe_width:
            pipe_x = WIDTH
            pipe_height = random.randint(120,420)
            passed = False

        if pipe_x + pipe_width < bird_x and not passed:
            score += 1
            passed = True

    screen.fill(background)


    if not game_started:

        title = title_font.render("FLAPPY BIRD",True,BLACK)
        screen.blit(title,(60,170))

        pygame.draw.rect(screen,GREEN,start_button,border_radius=10)

        txt = font.render("START",True,WHITE)
        screen.blit(txt,(203,333))

    else:

        # Bird
        pygame.draw.circle(screen,YELLOW,(bird_x,int(bird_y)),bird_radius)

        pygame.draw.circle(screen,BLACK,(108,int(bird_y)-6),3)

        # Top Pipe
        pygame.draw.rect(screen,GREEN,(pipe_x,0,pipe_width,pipe_height))

        pygame.draw.rect(screen,DARK_GREEN,
                         (pipe_x-5,pipe_height-20,pipe_width+10,20))

        # Bottom Pipe
        pygame.draw.rect(screen,GREEN,
                         (pipe_x,
                          pipe_height+pipe_gap,
                          pipe_width,
                          HEIGHT))

        pygame.draw.rect(screen,DARK_GREEN,
                         (pipe_x-5,
                          pipe_height+pipe_gap,
                          pipe_width+10,
                          20))

        # Ground
        pygame.draw.rect(screen,(200,170,80),
                         (0,HEIGHT-ground_height,WIDTH,ground_height))

        score_text = font.render(f"Score : {score}",True,BLACK)
        screen.blit(score_text,(20,20))

    pygame.display.update()

pygame.quit()
sys.exit()