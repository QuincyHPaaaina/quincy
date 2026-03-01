"""
Flappy Bird - by Quincy!
Press SPACE to flap. Dodge the pipes. Have fun!
"""

import pygame
import random
import sys
import math
import array
import os
import datetime

# --- Setup ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

WIDTH = 400
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# --- Colors ---
SKY_BLUE = (135, 206, 235)
SKY_TOP = (100, 180, 255)
GREEN = (34, 177, 76)
LIGHT_GREEN = (80, 210, 110)
DARK_GREEN = (20, 140, 50)
PIPE_HIGHLIGHT = (100, 220, 130)
YELLOW = (255, 220, 50)
DARK_YELLOW = (220, 180, 20)
LIGHT_YELLOW = (255, 245, 150)
ORANGE = (255, 165, 0)
DARK_ORANGE = (200, 120, 0)
RED = (255, 80, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 90, 43)
DARK_BROWN = (100, 60, 25)
LIGHT_BROWN = (180, 130, 70)
CLOUD_WHITE = (245, 250, 255)
CLOUD_SHADOW = (200, 220, 240)

# Night mode colors
NIGHT_SKY_TOP = (10, 10, 40)
NIGHT_SKY_BOTTOM = (30, 30, 80)
NIGHT_GREEN = (15, 100, 40)
NIGHT_LIGHT_GREEN = (40, 130, 60)
NIGHT_DARK_GREEN = (8, 70, 25)
NIGHT_PIPE_HIGHLIGHT = (50, 140, 70)
NIGHT_BROWN = (80, 50, 25)
NIGHT_DARK_BROWN = (50, 30, 12)
NIGHT_LIGHT_BROWN = (110, 70, 35)
MOON_YELLOW = (255, 245, 200)
MOON_SHADOW = (220, 210, 170)
STAR_WHITE = (255, 255, 230)

# Auto night mode — checks your computer's clock!
# Night = 7pm to 7am, Day = 7am to 7pm
# You can still press N to toggle manually
hour = datetime.datetime.now().hour
night_mode = hour >= 19 or hour < 7

# --- Fonts ---
big_font = pygame.font.SysFont("Arial", 60, bold=True)
medium_font = pygame.font.SysFont("Arial", 30, bold=True)
small_font = pygame.font.SysFont("Arial", 22)

# --- Bird settings ---
BIRD_X = 80
BIRD_RADIUS = 18
GRAVITY = 0.45
FLAP_POWER = -7.5

# --- Pipe settings ---
PIPE_WIDTH = 55
PIPE_GAP = 160
PIPE_SPEED = 3
PIPE_SPAWN_TIME = 90  # frames between new pipes (1.5 seconds at 60 FPS)

# --- Ground ---
GROUND_HEIGHT = 50


# --- Sounds (generated with math — no files needed!) ---
def make_sound(frequency, duration, volume=0.3):
    """Create a simple beep sound from a frequency and duration."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    samples = array.array("h")  # signed 16-bit integers
    for i in range(num_samples):
        t = i / sample_rate
        # Fade out so it doesn't click at the end
        fade = max(0, 1 - t / duration)
        value = int(volume * 32767 * fade * math.sin(2 * math.pi * frequency * t))
        samples.append(value)
    return pygame.mixer.Sound(buffer=samples)


def make_score_sound():
    """Two quick rising notes — ding ding!"""
    sample_rate = 44100
    samples = array.array("h")
    # First note (E5 = 659 Hz) for 0.08 seconds
    for i in range(int(sample_rate * 0.08)):
        t = i / sample_rate
        fade = max(0, 1 - t / 0.08)
        value = int(0.3 * 32767 * fade * math.sin(2 * math.pi * 659 * t))
        samples.append(value)
    # Second note (A5 = 880 Hz) for 0.12 seconds
    for i in range(int(sample_rate * 0.12)):
        t = i / sample_rate
        fade = max(0, 1 - t / 0.12)
        value = int(0.3 * 32767 * fade * math.sin(2 * math.pi * 880 * t))
        samples.append(value)
    return pygame.mixer.Sound(buffer=samples)


def make_game_over_sound():
    """A sad descending tone."""
    sample_rate = 44100
    duration = 0.5
    samples = array.array("h")
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        fade = max(0, 1 - t / duration)
        # Frequency drops from 400 Hz down to 150 Hz
        freq = 400 - 500 * t
        value = int(0.3 * 32767 * fade * math.sin(2 * math.pi * freq * t))
        samples.append(value)
    return pygame.mixer.Sound(buffer=samples)


flap_sound = make_sound(500, 0.08)       # short high blip
score_sound = make_score_sound()          # happy ding ding
game_over_sound = make_game_over_sound()  # sad descending tone
seed_sound = make_sound(900, 0.12, 0.25) # high sparkly blip for seeds

SEED_RADIUS = 8
ALMOND_TAN = (210, 175, 120)
ALMOND_DARK = (160, 120, 70)
ALMOND_LIGHT = (235, 210, 170)
ALMOND_RIDGE = (185, 150, 95)


seed_spin = 0


def rotate_point(px, py, cx, cy, angle):
    """Rotate point (px, py) around center (cx, cy) by angle in radians."""
    dx = px - cx
    dy = py - cy
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a)


def draw_seed(x, y):
    """Draw an almond that spins in full 360s."""
    global seed_spin
    seed_spin += 1

    angle = seed_spin * 0.06  # rotation angle, keeps going around

    # Almond shape — pointed oval made of polygon points
    # Build the shape at (0,0) then rotate and move to (x, y)
    hw = SEED_RADIUS  # half width
    hh = int(SEED_RADIUS * 1.4)  # half height (taller)

    # Almond outline points — oval with pointy top and bottom
    points = []
    num_points = 16
    for i in range(num_points):
        t = (i / num_points) * 2 * math.pi
        # Egg/almond shape: pointier at top and bottom
        px = math.cos(t) * hw
        py = math.sin(t) * hh
        # Make top and bottom pointier
        if abs(math.sin(t)) > 0.7:
            squeeze = 0.6
            px *= squeeze
        # Rotate the point
        rx, ry = rotate_point(px + x, py + y, x, y, angle)
        points.append((rx, ry))

    # Shadow (slightly offset)
    shadow_points = [(px + 2, py + 2) for px, py in points]
    pygame.draw.polygon(screen, ALMOND_DARK, shadow_points)

    # Main almond body
    pygame.draw.polygon(screen, ALMOND_TAN, points)

    # Ridge line down the middle (rotates with the almond)
    ridge_top = rotate_point(x, y - hh + 3, x, y, angle)
    ridge_bot = rotate_point(x, y + hh - 3, x, y, angle)
    pygame.draw.line(screen, ALMOND_RIDGE, ridge_top, ridge_bot, 2)

    # Highlight on one side (rotates too)
    hl_top = rotate_point(x - hw * 0.3, y - hh + 4, x, y, angle)
    hl_bot = rotate_point(x - hw * 0.3, y + hh - 4, x, y, angle)
    pygame.draw.line(screen, ALMOND_LIGHT, hl_top, hl_bot, 3)

    # Outline
    pygame.draw.polygon(screen, ALMOND_DARK, points, 2)

    # Sparkle stays on top
    pygame.draw.circle(screen, WHITE, (x + 3, y - 4), 2)

# --- High score (saved to a file so it remembers!) ---
HIGH_SCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.txt")


def load_high_score():
    """Load the high score from file. Returns 0 if no file yet."""
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    """Save a new high score to file."""
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))


high_score = load_high_score()


wing_frame = 0  # counts up each frame so the wing flaps

# Pre-generate cloud positions so they stay consistent
cloud_positions = [(60, 50, 1.0), (200, 100, 0.7), (330, 40, 0.85), (140, 150, 0.6)]
cloud_scroll = 0

# Pre-generate star positions
random.seed(42)
star_positions = [(random.randint(0, WIDTH), random.randint(0, HEIGHT - GROUND_HEIGHT - 50),
                   random.uniform(0.5, 2.5)) for _ in range(60)]
random.seed()  # reset to random
star_twinkle = 0


def draw_sky():
    """Draw a gradient sky with clouds (day) or stars and moon (night)."""
    global cloud_scroll, star_twinkle

    if night_mode:
        # Night gradient
        for row in range(HEIGHT - GROUND_HEIGHT):
            ratio = row / (HEIGHT - GROUND_HEIGHT)
            r = int(NIGHT_SKY_TOP[0] + (NIGHT_SKY_BOTTOM[0] - NIGHT_SKY_TOP[0]) * ratio)
            g = int(NIGHT_SKY_TOP[1] + (NIGHT_SKY_BOTTOM[1] - NIGHT_SKY_TOP[1]) * ratio)
            b = int(NIGHT_SKY_TOP[2] + (NIGHT_SKY_BOTTOM[2] - NIGHT_SKY_TOP[2]) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, row), (WIDTH, row))

        # Stars that twinkle
        star_twinkle += 1
        for sx, sy, size in star_positions:
            brightness = 0.5 + 0.5 * math.sin(star_twinkle * 0.03 + sx * 0.1 + sy * 0.2)
            alpha = int(255 * brightness)
            r = int(size * 1.2)
            star_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, (255, 255, 230, alpha), (r, r), r)
            screen.blit(star_surf, (sx - r, sy - r))

        # Moon
        pygame.draw.circle(screen, MOON_YELLOW, (WIDTH - 60, 60), 30)
        pygame.draw.circle(screen, MOON_SHADOW, (WIDTH - 55, 55), 28, 2)
        # Moon crater details
        pygame.draw.circle(screen, MOON_SHADOW, (WIDTH - 70, 55), 5)
        pygame.draw.circle(screen, MOON_SHADOW, (WIDTH - 55, 70), 4)
        pygame.draw.circle(screen, MOON_SHADOW, (WIDTH - 48, 52), 3)
        # Moon glow
        glow_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 245, 200, 30), (50, 50), 45)
        screen.blit(glow_surf, (WIDTH - 110, 10))
    else:
        # Day gradient
        for row in range(HEIGHT - GROUND_HEIGHT):
            ratio = row / (HEIGHT - GROUND_HEIGHT)
            r = int(SKY_TOP[0] + (SKY_BLUE[0] - SKY_TOP[0]) * ratio)
            g = int(SKY_TOP[1] + (SKY_BLUE[1] - SKY_TOP[1]) * ratio)
            b = int(SKY_TOP[2] + (SKY_BLUE[2] - SKY_TOP[2]) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, row), (WIDTH, row))

        # Clouds drift slowly to the left
        cloud_scroll -= 0.3
        for cx, cy, size in cloud_positions:
            x = (cx + cloud_scroll) % (WIDTH + 80) - 40
            draw_cloud(int(x), cy, size)


def draw_cloud(x, y, size):
    """Draw a fluffy cloud made of overlapping circles."""
    s = size
    # Shadow underneath
    pygame.draw.circle(screen, CLOUD_SHADOW, (x, int(y + 4 * s)), int(22 * s))
    pygame.draw.circle(screen, CLOUD_SHADOW, (int(x + 20 * s), int(y + 6 * s)), int(18 * s))
    pygame.draw.circle(screen, CLOUD_SHADOW, (int(x - 18 * s), int(y + 5 * s)), int(16 * s))
    # Main cloud puffs
    pygame.draw.circle(screen, CLOUD_WHITE, (x, int(y)), int(22 * s))
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x + 20 * s), int(y + 2 * s)), int(18 * s))
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x - 18 * s), int(y + 2 * s)), int(16 * s))
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x + 8 * s), int(y - 10 * s)), int(16 * s))
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x - 8 * s), int(y - 8 * s)), int(14 * s))
    # Bright highlight on top
    pygame.draw.circle(screen, WHITE, (int(x + 5 * s), int(y - 12 * s)), int(8 * s))


def draw_bird(y):
    """Draw a cute detailed yellow bird with flapping wings."""
    global wing_frame
    wing_frame += 1
    by = int(y)

    # Tail feathers (behind body)
    tail_points = [
        (BIRD_X - BIRD_RADIUS + 2, by),
        (BIRD_X - BIRD_RADIUS - 12, by - 8),
        (BIRD_X - BIRD_RADIUS - 8, by),
        (BIRD_X - BIRD_RADIUS - 14, by + 6),
    ]
    pygame.draw.polygon(screen, DARK_ORANGE, tail_points)

    # Body shadow
    pygame.draw.circle(screen, DARK_YELLOW, (BIRD_X, by + 2), BIRD_RADIUS)
    # Main body
    pygame.draw.circle(screen, YELLOW, (BIRD_X, by), BIRD_RADIUS)
    # Body outline
    pygame.draw.circle(screen, DARK_YELLOW, (BIRD_X, by), BIRD_RADIUS, 2)
    # Belly (lighter oval)
    pygame.draw.ellipse(screen, LIGHT_YELLOW, (BIRD_X - 10, by + 2, 20, 14))

    # Wing — drawn on top of body, flaps up and down every 8 frames
    wing_flap = (wing_frame // 8) % 2
    if wing_flap == 0:
        # Wing up
        wing_points = [
            (BIRD_X - 2, by + 2),
            (BIRD_X - 8, by - 18),
            (BIRD_X - 22, by - 10),
        ]
    else:
        # Wing down
        wing_points = [
            (BIRD_X - 2, by + 2),
            (BIRD_X - 8, by + 16),
            (BIRD_X - 22, by + 8),
        ]
    pygame.draw.polygon(screen, ORANGE, wing_points)
    pygame.draw.polygon(screen, DARK_ORANGE, wing_points, 2)  # wing outline

    # Eye (white part)
    pygame.draw.circle(screen, WHITE, (BIRD_X + 8, by - 5), 7)
    pygame.draw.circle(screen, BLACK, (BIRD_X + 8, by - 5), 7, 1)  # eye outline
    # Pupil
    pygame.draw.circle(screen, BLACK, (BIRD_X + 10, by - 5), 3)
    # Eye shine
    pygame.draw.circle(screen, WHITE, (BIRD_X + 9, by - 7), 2)

    # Beak (two parts for top and bottom)
    top_beak = [
        (BIRD_X + BIRD_RADIUS - 2, by - 2),
        (BIRD_X + BIRD_RADIUS + 14, by + 2),
        (BIRD_X + BIRD_RADIUS - 2, by + 4),
    ]
    bottom_beak = [
        (BIRD_X + BIRD_RADIUS - 2, by + 4),
        (BIRD_X + BIRD_RADIUS + 10, by + 5),
        (BIRD_X + BIRD_RADIUS - 2, by + 9),
    ]
    pygame.draw.polygon(screen, ORANGE, top_beak)
    pygame.draw.polygon(screen, RED, bottom_beak)

    # Cheek blush
    pygame.draw.circle(screen, (255, 180, 150), (BIRD_X + 2, by + 8), 5)


def get_pipe_colors():
    """Return pipe colors based on day/night mode."""
    if night_mode:
        return NIGHT_GREEN, NIGHT_PIPE_HIGHLIGHT, NIGHT_DARK_GREEN, NIGHT_LIGHT_GREEN
    return GREEN, PIPE_HIGHLIGHT, DARK_GREEN, LIGHT_GREEN


def draw_pipe_section(x, top, height):
    """Draw one pipe section with 3D shading."""
    if height <= 0:
        return
    pc_main, pc_highlight, pc_dark, pc_light = get_pipe_colors()
    # Main pipe body
    pygame.draw.rect(screen, pc_main, (x, top, PIPE_WIDTH, height))
    # Left highlight stripe (light)
    pygame.draw.rect(screen, pc_highlight, (x + 4, top, 8, height))
    # Right shadow stripe (dark)
    pygame.draw.rect(screen, pc_dark, (x + PIPE_WIDTH - 10, top, 10, height))
    # Left edge line
    pygame.draw.line(screen, pc_dark, (x, top), (x, top + height), 2)
    # Right edge line
    pygame.draw.line(screen, pc_dark, (x + PIPE_WIDTH, top), (x + PIPE_WIDTH, top + height), 2)


def draw_pipe_rim(x, top):
    """Draw a pipe rim/lip with 3D shading."""
    pc_main, pc_highlight, pc_dark, pc_light = get_pipe_colors()
    rim_w = PIPE_WIDTH + 8
    rim_x = x - 4
    pygame.draw.rect(screen, pc_main, (rim_x, top, rim_w, 22))
    # Highlight on top edge
    pygame.draw.rect(screen, pc_light, (rim_x + 2, top + 2, rim_w - 4, 6))
    # Shadow on bottom edge
    pygame.draw.rect(screen, pc_dark, (rim_x, top + 16, rim_w, 6))
    # Outline
    pygame.draw.rect(screen, pc_dark, (rim_x, top, rim_w, 22), 2)


def draw_pipe(x, gap_y, gap_size):
    """Draw a pair of detailed green pipes with a gap centered at gap_y."""
    top_height = gap_y - gap_size // 2
    bottom_top = gap_y + gap_size // 2

    # Top pipe body + rim
    draw_pipe_section(x, 0, top_height - 22)
    draw_pipe_rim(x, top_height - 22)

    # Bottom pipe rim + body
    draw_pipe_rim(x, bottom_top)
    draw_pipe_section(x, bottom_top + 22, HEIGHT - bottom_top - 22 - GROUND_HEIGHT)


ground_scroll = 0
grass_time = 0


def draw_ground(speed=3):
    """Draw the ground with scrolling, wavy grass and dirt layers."""
    global ground_scroll, grass_time
    ground_scroll = (ground_scroll + speed) % 12
    grass_time += 1

    ground_y = HEIGHT - GROUND_HEIGHT
    # Pick colors based on mode
    c_brown = NIGHT_BROWN if night_mode else BROWN
    c_dark_brown = NIGHT_DARK_BROWN if night_mode else DARK_BROWN
    c_light_brown = NIGHT_LIGHT_BROWN if night_mode else LIGHT_BROWN
    c_green = NIGHT_GREEN if night_mode else GREEN
    c_light_green = NIGHT_LIGHT_GREEN if night_mode else LIGHT_GREEN
    c_dark_green = NIGHT_DARK_GREEN if night_mode else DARK_GREEN
    # Dirt
    pygame.draw.rect(screen, c_brown, (0, ground_y + 10, WIDTH, GROUND_HEIGHT - 10))
    # Darker dirt stripes
    pygame.draw.rect(screen, c_dark_brown, (0, ground_y + 30, WIDTH, 8))
    pygame.draw.rect(screen, c_light_brown, (0, ground_y + 18, WIDTH, 4))
    # Grass layer on top
    pygame.draw.rect(screen, c_green, (0, ground_y, WIDTH, 12))
    pygame.draw.rect(screen, c_light_green, (0, ground_y, WIDTH, 5))
    # Scrolling wavy grass tufts
    for gx in range(-12, WIDTH + 12, 8):
        sx = gx - ground_scroll
        # Each blade sways using sin — offset by position so they wave like a crowd
        sway = math.sin(grass_time * 0.08 + gx * 0.15) * 4
        height1 = 6 + math.sin(grass_time * 0.06 + gx * 0.2) * 2
        height2 = 5 + math.sin(grass_time * 0.07 + gx * 0.25) * 1.5
        pygame.draw.line(screen, c_dark_green,
                         (sx, ground_y),
                         (sx - 3 + sway, ground_y - height1), 2)
        pygame.draw.line(screen, c_green,
                         (sx + 4, ground_y),
                         (sx + 7 + sway, ground_y - height2), 2)


def check_collision(bird_y, pipes):
    """Check if the bird hit a pipe or the ground/ceiling."""
    # Hit the ground or ceiling?
    if bird_y + BIRD_RADIUS >= HEIGHT - GROUND_HEIGHT or bird_y - BIRD_RADIUS <= 0:
        return True

    # Hit a pipe?
    for pipe_x, gap_y, _scored, gap_size in pipes:
        # Is the bird horizontally overlapping the pipe?
        if BIRD_X + BIRD_RADIUS > pipe_x and BIRD_X - BIRD_RADIUS < pipe_x + PIPE_WIDTH:
            # Is the bird outside the gap?
            if bird_y - BIRD_RADIUS < gap_y - gap_size // 2 or bird_y + BIRD_RADIUS > gap_y + gap_size // 2:
                return True

    return False


def show_start_screen():
    """Show the title screen before the game starts."""
    draw_sky()
    draw_ground()

    title = big_font.render("Flappy Bird", True, WHITE)
    shadow = big_font.render("Flappy Bird", True, BLACK)
    screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 2, 142))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 140))

    # Draw a bird in the middle
    draw_bird(300)

    hint = medium_font.render("Press SPACE to play!", True, WHITE)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 420))

    pygame.display.flip()

    # Wait for SPACE
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        clock.tick(FPS)


def show_game_over(score):
    """Show the game over screen."""
    global high_score
    new_best = score > high_score
    if new_best:
        high_score = score
        save_high_score(high_score)

    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    game_over_text = big_font.render("Game Over!", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 160))

    score_text = medium_font.render(f"Score: {score}", True, YELLOW)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 260))

    best_text = medium_font.render(f"Best: {high_score}", True, ORANGE)
    screen.blit(best_text, (WIDTH // 2 - best_text.get_width() // 2, 310))

    if new_best:
        new_best_text = medium_font.render("NEW BEST!", True, (255, 50, 50))
        screen.blit(new_best_text, (WIDTH // 2 - new_best_text.get_width() // 2, 360))

    restart_text = small_font.render("Press SPACE to play again", True, WHITE)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 420))

    pygame.display.flip()

    # Wait for SPACE
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        clock.tick(FPS)


def get_difficulty(score):
    """Return pipe gap, pipe speed, and spawn time based on score.
    Starts easy and gets harder as you score more!"""
    # Gap shrinks: 200 -> 130 (smaller gap = harder)
    gap = max(130, 200 - score * 5)
    # Speed increases: 2.5 -> 5.5 (faster = harder)
    speed = min(5.5, 2.5 + score * 0.2)
    # Pipes spawn faster: 100 -> 55 frames (less time between pipes = harder)
    spawn_time = max(55, 100 - score * 3)
    return gap, speed, spawn_time


def show_paused():
    """Draw the pause overlay on top of the current frame."""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(120)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    pause_text = big_font.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 230))

    hint_text = small_font.render("Press P to continue", True, WHITE)
    screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 310))

    pygame.display.flip()


def game():
    """Run one round of the game. Returns the final score."""
    global night_mode
    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipes = []  # Each pipe is [x_position, gap_center_y, scored, gap_size]
    score = 0
    pipe_timer = 0
    pipe_count = 0  # counts pipes spawned, for seed timing
    seeds = []  # Each seed is [x, y, collected]
    paused = False
    trail = []  # list of past bird (x, y) positions

    invincible = False

    running = True
    while running:
        # --- Difficulty scales with score ---
        current_gap, current_speed, current_spawn_time = get_difficulty(score)

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        show_paused()
                if event.key == pygame.K_n:
                    night_mode = not night_mode
                if event.key == pygame.K_0:
                    invincible = not invincible
                if not paused and event.key == pygame.K_SPACE:
                    bird_velocity = FLAP_POWER
                    flap_sound.play()

        # If paused, skip updating and drawing — just wait
        if paused:
            clock.tick(FPS)
            continue

        # --- Update ---
        # Bird trail — remember recent positions
        trail.append((BIRD_X, bird_y))
        if len(trail) > 15:
            trail.pop(0)

        # Bird physics
        bird_velocity += GRAVITY
        bird_y += bird_velocity

        # Invincible — bounce off floor and ceiling instead of dying
        if invincible:
            if bird_y + BIRD_RADIUS >= HEIGHT - GROUND_HEIGHT:
                bird_y = HEIGHT - GROUND_HEIGHT - BIRD_RADIUS
                bird_velocity = -abs(bird_velocity) * 0.8
            if bird_y - BIRD_RADIUS <= 0:
                bird_y = BIRD_RADIUS
                bird_velocity = abs(bird_velocity) * 0.8

        # Spawn new pipes
        pipe_timer += 1
        if pipe_timer >= current_spawn_time:
            pipe_timer = 0
            pipe_count += 1
            gap_y = random.randint(120, HEIGHT - GROUND_HEIGHT - 120)
            pipes.append([WIDTH, gap_y, False, current_gap])

            # Spawn a seed every 3 pipes — floating in the gap
            if pipe_count % 3 == 0:
                seed_y = gap_y + random.randint(-current_gap // 4, current_gap // 4)
                seeds.append([WIDTH + PIPE_WIDTH // 2, seed_y, False])

        # Move pipes to the left
        for pipe in pipes:
            pipe[0] -= current_speed

        # Move seeds to the left (same speed as pipes)
        for seed in seeds:
            seed[0] -= current_speed

        # Check if bird collects a seed
        for seed in seeds:
            if not seed[2]:
                dx = BIRD_X - seed[0]
                dy = bird_y - seed[1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < BIRD_RADIUS + SEED_RADIUS:
                    seed[2] = True
                    score += 1
                    seed_sound.play()

        # Score — bird passed the pipe's right edge
        for pipe in pipes:
            if pipe[0] + PIPE_WIDTH < BIRD_X and not pipe[2]:
                score += 1
                pipe[2] = True
                score_sound.play()

        # Remove pipes and seeds that went off screen
        pipes = [p for p in pipes if p[0] > -PIPE_WIDTH]
        seeds = [s for s in seeds if s[0] > -SEED_RADIUS * 2 and not s[2]]

        # Check collisions (skip if invincible!)
        if not invincible and check_collision(bird_y, pipes):
            game_over_sound.play()
            return score

        # --- Draw ---
        draw_sky()

        # Pipes
        for pipe_x, gap_y, _scored, gap_size in pipes:
            draw_pipe(int(pipe_x), gap_y, gap_size)

        # Seeds
        for seed in seeds:
            if not seed[2]:
                draw_seed(int(seed[0]), int(seed[1]))

        # Ground (scrolls at same speed as pipes)
        draw_ground(current_speed)

        # Bird trail — fading circles stretching out behind the bird
        for i, (tx, ty) in enumerate(trail):
            # Older = more faded, smaller, and further left
            progress = (i + 1) / len(trail)
            alpha = int(180 * progress)
            radius = max(3, int(BIRD_RADIUS * progress * 0.6))
            # Spread dots out to the left behind the bird
            offset_x = (len(trail) - i) * 4
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (255, 220, 50, alpha), (radius, radius), radius)
            screen.blit(trail_surface, (int(tx) - radius - offset_x, int(ty) - radius))

        # Bird
        draw_bird(bird_y)

        # Score display
        score_surface = big_font.render(str(score), True, WHITE)
        score_shadow = big_font.render(str(score), True, BLACK)
        screen.blit(score_shadow, (WIDTH // 2 - score_shadow.get_width() // 2 + 2, 32))
        screen.blit(score_surface, (WIDTH // 2 - score_surface.get_width() // 2, 30))

        # Invincible indicator
        if invincible:
            inv_font = pygame.font.SysFont("Arial", 18, bold=True)
            inv_text = inv_font.render("INVINCIBLE!", True, (255, 80, 220))
            screen.blit(inv_text, (WIDTH // 2 - inv_text.get_width() // 2, 70))

        pygame.display.flip()
        clock.tick(FPS)


# --- Main loop ---
show_start_screen()
while True:
    final_score = game()
    show_game_over(final_score)
