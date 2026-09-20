import pygame
import random
import sys

pygame.init()


WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
FPS = 60



# Eagle colours
BIRD_BODY_COLOR = ( 80,  50,  20)   # dark brown body
BIRD_WING_COLOR = ( 50,  30,  10)   # darker brown wings
BIRD_BEAK_COLOR = (255, 180,   0)   # golden yellow beak
EAGLE_HEAD      = (255, 255, 255)   # white head
EAGLE_TAIL      = ( 255, 255, 255)  # white tail

# Stone pipe colours
STONE_LIGHT  = (160, 155, 150)   # light grey stone
STONE_MID    = (120, 115, 110)   # mid grey stone
STONE_DARK   = ( 80,  75,  70)   # dark grey stone
STONE_CRACK  = ( 60,  55,  50)   # crack lines


GRAVITY    = 0.30   # bird fall speed  — try 0.3 (easy) to 0.7 (hard)
FLAP_FORCE = -7     # flap strength    — try -10 (strong) to -6 (weak)
PIPE_SPEED = 3      # pipe move speed  — try 2 (slow) to 6 (fast)


PIPE_GAP   = 180    # try 120 (hard) to 220 (easy)
PIPE_WIDTH = 60
PIPE_FREQ  = 1800   # new pipe every X milliseconds — more distance between poles


DAY_SKY    = (135, 206, 235)   # light blue   ← change me
NIGHT_SKY  = ( 20,  20,  60)   # dark navy    ← change me
SUNSET_SKY = (255, 140,  60)   # orange-pink  ← change me

DAY_GROUND    = (210, 180, 140)
NIGHT_GROUND  = ( 60,  50,  40)
SUNSET_GROUND = (180, 100,  50)

WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
RED    = (220,  50,  50)
YELLOW = (255, 220,   0)

# ── Stars & Moon ─────────────────────────────────────────────
random.seed(99)
STARS = [(random.randint(0, WIDTH), random.randint(10, 480), random.choice([1, 1, 2])) for _ in range(80)]
random.seed()

def draw_stars_and_moon():
    tick = pygame.time.get_ticks()
    # twinkling stars
    for i, (sx, sy, sr) in enumerate(STARS):
        bright = int(160 + 95 * abs((tick // 600 + i * 31) % 20 - 10) / 10)
        pygame.draw.circle(screen, (bright, bright, min(255, bright + 20)), (sx, sy), sr)
    # moon body
    mx, my = 320, 65
    pygame.draw.circle(screen, (255, 248, 195), (mx, my), 28)
    # crescent shadow
    pygame.draw.circle(screen, NIGHT_SKY, (mx + 12, my - 5), 23)
    # moon glow
    glow = pygame.Surface((90, 90), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 245, 180, 35), (45, 45), 45)
    screen.blit(glow, (mx - 45, my - 45))


#  BIRD

BIRD_W, BIRD_H = 34, 24

def make_bird():
    return {"x": 80, "y": HEIGHT // 2, "vel": 0}

def draw_bird(bird):
    x, y = int(bird["x"]), int(bird["y"])
    # body — dark brown
    pygame.draw.ellipse(screen, BIRD_BODY_COLOR, (x + 4, y + 6, BIRD_W - 8, BIRD_H - 8))
    # left wing (top)
    pygame.draw.polygon(screen, BIRD_WING_COLOR,
                        [(x + 4,        y + 10),
                         (x,            y + 2),
                         (x + 14,       y + 8)])
    # right wing (bottom)
    pygame.draw.polygon(screen, BIRD_WING_COLOR,
                        [(x + 4,        y + 14),
                         (x,            y + 22),
                         (x + 14,       y + 16)])
    # white tail feathers
    pygame.draw.polygon(screen, EAGLE_TAIL,
                        [(x + 4,        y + 10),
                         (x,            y + 8),
                         (x,            y + 16)])
    # white head
    pygame.draw.circle(screen, EAGLE_HEAD, (x + BIRD_W - 8, y + 8), 7)
    # eye
    pygame.draw.circle(screen, BLACK, (x + BIRD_W - 6, y + 7), 2)
    # golden beak
    pygame.draw.polygon(screen, BIRD_BEAK_COLOR,
                        [(x + BIRD_W - 2, y + 9),
                         (x + BIRD_W + 8, y + 11),
                         (x + BIRD_W - 2, y + 14)])

def bird_rect(bird):
    return pygame.Rect(int(bird["x"]) + 4, int(bird["y"]) + 4, BIRD_W - 8, BIRD_H - 8)


#  PIPES

def make_pipe():
    top_h = random.randint(60, HEIGHT - PIPE_GAP - 60)
    return {"x": float(WIDTH), "top_h": top_h, "bot_y": top_h + PIPE_GAP, "scored": False}

def draw_stone_block(x, y, w, h):
    """Draw a single stone block with texture."""
    pygame.draw.rect(screen, STONE_MID,   (x, y, w, h))
    pygame.draw.rect(screen, STONE_LIGHT, (x, y, w, 4))           # top highlight
    pygame.draw.rect(screen, STONE_DARK,  (x, y + h - 4, w, 4))  # bottom shadow
    pygame.draw.rect(screen, STONE_DARK,  (x + w - 4, y, 4, h))  # right shadow
    # crack lines for stone texture
    pygame.draw.line(screen, STONE_CRACK, (x + w // 3, y + 4), (x + w // 3 - 3, y + h - 4), 1)
    pygame.draw.line(screen, STONE_CRACK, (x + w * 2 // 3, y + 4), (x + w * 2 // 3 + 2, y + h - 4), 1)

def draw_pipe(p):
    x = int(p["x"])
    block_h = 20   # height of each stone block segment

    # ── top stone pillar ────────────────────────────────────────
    for by in range(0, p["top_h"] - block_h, block_h):
        draw_stone_block(x, by, PIPE_WIDTH, block_h)
        pygame.draw.line(screen, STONE_DARK, (x, by + block_h - 1), (x + PIPE_WIDTH, by + block_h - 1), 1)
    # top cap (wider, chiselled stone)
    cap_x = x - 6
    cap_w = PIPE_WIDTH + 12
    pygame.draw.rect(screen, STONE_MID,   (cap_x,     p["top_h"] - block_h, cap_w, block_h))
    pygame.draw.rect(screen, STONE_LIGHT, (cap_x,     p["top_h"] - block_h, cap_w, 4))
    pygame.draw.rect(screen, STONE_DARK,  (cap_x,     p["top_h"] - 4,       cap_w, 4))
    pygame.draw.line(screen, STONE_CRACK, (cap_x + 8, p["top_h"] - block_h + 4),
                                          (cap_x + 8, p["top_h"] - 4), 1)
    pygame.draw.line(screen, STONE_CRACK, (cap_x + cap_w - 8, p["top_h"] - block_h + 4),
                                          (cap_x + cap_w - 8, p["top_h"] - 4), 1)

    # ── bottom stone pillar ──────────────────────────────────────
    for by in range(p["bot_y"] + block_h, HEIGHT, block_h):
        draw_stone_block(x, by, PIPE_WIDTH, block_h)
        pygame.draw.line(screen, STONE_DARK, (x, by + block_h - 1), (x + PIPE_WIDTH, by + block_h - 1), 1)
    # bottom cap
    pygame.draw.rect(screen, STONE_MID,   (cap_x,     p["bot_y"],           cap_w, block_h))
    pygame.draw.rect(screen, STONE_LIGHT, (cap_x,     p["bot_y"],           cap_w, 4))
    pygame.draw.rect(screen, STONE_DARK,  (cap_x,     p["bot_y"] + block_h - 4, cap_w, 4))
    pygame.draw.line(screen, STONE_CRACK, (cap_x + 8, p["bot_y"] + 4),
                                          (cap_x + 8, p["bot_y"] + block_h - 4), 1)
    pygame.draw.line(screen, STONE_CRACK, (cap_x + cap_w - 8, p["bot_y"] + 4),
                                          (cap_x + cap_w - 8, p["bot_y"] + block_h - 4), 1)

def pipe_rects(p):
    x = int(p["x"])
    return (pygame.Rect(x - 5, 0,          PIPE_WIDTH + 10, p["top_h"]),
            pygame.Rect(x - 5, p["bot_y"], PIPE_WIDTH + 10, HEIGHT - p["bot_y"]))


#  GROUND

GROUND_Y = HEIGHT - 60

def draw_ground(sky_mode):
    color = {"day": DAY_GROUND, "night": NIGHT_GROUND, "sunset": SUNSET_GROUND}[sky_mode]
    pygame.draw.rect(screen, color, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    darker = tuple(max(0, c - 50) for c in color)
    pygame.draw.rect(screen, darker, (0, GROUND_Y, WIDTH, 6))

# ============================================================
#  HUD
# ============================================================
font_big   = pygame.font.SysFont("Arial", 48, bold=True)
font_med   = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 20)

def draw_score(score):
    surf = font_big.render(str(score), True, WHITE)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 30))

def draw_hud_text(lines, y_start=160):
    for i, (text, font, color) in enumerate(lines):
        surf = font.render(text, True, color)
        screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y_start + i * 40))

# ============================================================
#  MAIN LOOP
# ============================================================
def main():
    sky_mode   = "day"
    bird       = make_bird()
    pipes      = []
    score      = 0
    high_score = 0
    alive      = True
    started    = False
    last_pipe  = pygame.time.get_ticks() - PIPE_FREQ

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                # Feature 4 — sky toggle
                if event.key == pygame.K_d:  sky_mode = "day"
                if event.key == pygame.K_n:  sky_mode = "night"
                if event.key == pygame.K_s:  sky_mode = "sunset"

                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if not alive:
                        bird      = make_bird()
                        pipes     = []
                        score     = 0
                        alive     = True
                        started   = False
                        last_pipe = now - PIPE_FREQ
                    else:
                        bird["vel"] = FLAP_FORCE
                        started = True

                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and alive:
                bird["vel"] = FLAP_FORCE
                started = True

        # ── Update ──────────────────────────────────────────────────────
        if alive and started:
            bird["vel"] += GRAVITY          # Feature 2 — gravity
            bird["y"]   += bird["vel"]

            if now - last_pipe > PIPE_FREQ:
                pipes.append(make_pipe())
                last_pipe = now

            for p in pipes:
                p["x"] -= PIPE_SPEED        # Feature 2 — pipe speed
                if not p["scored"] and p["x"] + PIPE_WIDTH < bird["x"]:
                    score += 1
                    high_score = max(score, high_score)
                    p["scored"] = True

            pipes = [p for p in pipes if p["x"] > -PIPE_WIDTH - 20]

            b_rect = bird_rect(bird)
            if bird["y"] + BIRD_H >= GROUND_Y or bird["y"] < 0:
                alive = False
            for p in pipes:
                for r in pipe_rects(p):
                    if b_rect.colliderect(r):
                        alive = False

        # ── Draw ────────────────────────────────────────────────────────
        sky_color = {"day": DAY_SKY, "night": NIGHT_SKY, "sunset": SUNSET_SKY}[sky_mode]
        screen.fill(sky_color)              # Feature 4 — background colour

        if sky_mode == "night":
            draw_stars_and_moon()

        for p in pipes:
            draw_pipe(p)

        draw_ground(sky_mode)
        draw_bird(bird)
        draw_score(score)

        if not started and alive:
            draw_hud_text([
                ("FLAPPY BIRD",               font_med,   WHITE),
                ("Space / Click to flap",     font_small, WHITE),
                ("D = Day  N = Night  S = Sunset", font_small, (220, 220, 220)),
            ])

        if not alive:
            draw_hud_text([
                ("GAME OVER",                 font_med,   RED),
                (f"Score  :  {score}",        font_small, WHITE),
                (f"Best   :  {high_score}",   font_small, YELLOW),
                ("Space to restart",          font_small, (220, 220, 220)),
            ])

        leg = font_small.render("D=Day  N=Night  S=Sunset  ESC=Quit", True, (180, 180, 180))
        screen.blit(leg, (WIDTH // 2 - leg.get_width() // 2, HEIGHT - 28))

        pygame.display.flip()

if __name__ == "__main__":
    main()
