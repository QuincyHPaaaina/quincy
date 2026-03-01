"""
Pi Quiz — how many digits of π can you remember?
Type the digits after 3. one at a time.
Press H for a hint if you're stuck!
"""

import pygame
import math
import array
import random
import os
import sys

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

WIDTH, HEIGHT = 700, 560
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("π Quiz")
clock = pygame.time.Clock()
FPS = 60

# First 200 digits of pi after the decimal point
PI_DIGITS = (
    "14159265358979323846264338327950288419716939937510"
    "58209749445923078164062862089986280348253421170679"
    "82148086513282306647093844609550582231725359408128"
    "48111745028410270193852110555964462294895493038196"
)

# --- Colors ---
BG_TOP      = (18, 8, 48)
BG_BOTTOM   = (45, 18, 75)
GOLD        = (255, 215, 0)
GOLD_DIM    = (160, 120, 0)
WHITE       = (255, 255, 255)
GRAY        = (150, 150, 175)
BLACK       = (0, 0, 0)
GREEN       = (80, 220, 100)
RED_COL     = (255, 80, 80)
HINT_BLUE   = (100, 190, 255)
STAR_COLOR  = (200, 200, 230)
CONFETTI_COLORS = [
    (255, 80,  80),  (255, 210, 0),  (80,  220, 100),
    (80, 180, 255),  (255, 110, 200),(200, 255, 100),
]

# --- Fonts ---
font_big    = pygame.font.SysFont("Arial",      48, bold=True)
font_med    = pygame.font.SysFont("Arial",      30, bold=True)
font_small  = pygame.font.SysFont("Arial",      20)
font_digit  = pygame.font.SysFont("Courier New",30, bold=True)  # monospace


# ============================================================
#  SOUNDS
# ============================================================
def make_correct_sound():
    sr = 44100
    samples = array.array("h")
    for freq, dur in [(880, 0.06), (1100, 0.12)]:
        for i in range(int(sr * dur)):
            t = i / sr
            fade = max(0, 1 - t / dur)
            samples.append(int(0.25 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)

def make_wrong_sound():
    sr = 44100
    dur = 0.28
    samples = array.array("h")
    for i in range(int(sr * dur)):
        t = i / sr
        fade = max(0, 1 - t / dur)
        freq = 220 - 100 * (t / dur)
        samples.append(int(0.35 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)

def make_hint_sound():
    sr = 44100
    samples = array.array("h")
    for freq, dur in [(660, 0.05), (440, 0.09)]:
        for i in range(int(sr * dur)):
            t = i / sr
            fade = max(0, 1 - t / dur)
            samples.append(int(0.2 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)

correct_sound = make_correct_sound()
wrong_sound   = make_wrong_sound()
hint_sound    = make_hint_sound()


def make_auto_sound():
    """Rapid ascending arpeggio — cheat code activated!"""
    sr = 44100
    samples = array.array("h")
    notes = [523, 659, 784, 1047, 1319, 1568, 2093]
    for freq in notes:
        dur = 0.055
        for i in range(int(sr * dur)):
            t = i / sr
            fade = max(0, 1 - t / dur)
            samples.append(int(0.22 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)


auto_sound = make_auto_sound()


# ============================================================
#  HIGH SCORE
# ============================================================
HS_FILE = os.path.join(os.path.dirname(__file__), "pi_highscore.txt")

def load_high_score():
    try:
        with open(HS_FILE) as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_high_score(score):
    with open(HS_FILE, "w") as f:
        f.write(str(score))


# ============================================================
#  CONFETTI
# ============================================================
class Confetti:
    def __init__(self, x, y):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = random.uniform(-6, 6)
        self.vy    = random.uniform(-9, -2)
        self.color = random.choice(CONFETTI_COLORS)
        self.size  = random.randint(5, 11)
        self.rot   = random.uniform(0, 360)
        self.rot_v = random.uniform(-10, 10)
        self.life  = random.randint(45, 75)
        self.max_life = self.life

    def update(self):
        self.vy  += 0.35
        self.x   += self.vx
        self.y   += self.vy
        self.vx  *= 0.98
        self.rot += self.rot_v
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.color, alpha), (0, 0, self.size, self.size))
        rotated = pygame.transform.rotate(s, self.rot)
        surface.blit(rotated, (int(self.x) - rotated.get_width() // 2,
                               int(self.y) - rotated.get_height() // 2))


# ============================================================
#  DRAWING HELPERS
# ============================================================
def draw_background(frame):
    # Gradient background
    for y in range(0, HEIGHT, 4):
        t = y / HEIGHT
        r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
        pygame.draw.rect(screen, (r, g, b), (0, y, WIDTH, 4))

    # Faint giant π watermark
    pi_surf = font_big.render("π", True, (55, 30, 95))
    big_pi = pygame.transform.scale(pi_surf,
                                    (pi_surf.get_width() * 3, pi_surf.get_height() * 3))
    screen.blit(big_pi, (WIDTH // 2 - big_pi.get_width() // 2,
                          HEIGHT // 2 - big_pi.get_height() // 2 - 10))

    # Twinkling stars
    random.seed(99)
    for _ in range(50):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT)
        bright = int(80 + 70 * math.sin(frame * 0.04 + sx * 0.07 + sy * 0.05))
        pygame.draw.circle(screen, (bright, bright, bright + 20), (sx, sy), 1)
    random.seed()


DIGITS_PER_ROW = 20
DIGIT_W        = 28
ROW_LEFT       = WIDTH // 2 - DIGITS_PER_ROW * DIGIT_W // 2
DIGITS_START_Y = 135
ROW_HEIGHT     = 40
MAX_ROWS       = 3   # show at most 3 rows of digits on screen


def draw_digits_area(typed_digits, hinted_set, flash_color,
                     hint_show, hint_char, score, high_score):
    # Header: π = 3.
    header = font_big.render("π  =  3.", True, GOLD)
    screen.blit(header, (WIDTH // 2 - header.get_width() // 2, 62))

    # Which digits to display (last MAX_ROWS * DIGITS_PER_ROW)
    max_show = MAX_ROWS * DIGITS_PER_ROW
    offset   = max(0, len(typed_digits) - max_show)
    display  = typed_digits[offset:]

    for i, ch in enumerate(display):
        x = ROW_LEFT + (i % DIGITS_PER_ROW) * DIGIT_W
        y = DIGITS_START_Y + (i // DIGITS_PER_ROW) * ROW_HEIGHT
        real_idx = i + offset
        color = HINT_BLUE if real_idx in hinted_set else WHITE
        d_surf = font_digit.render(ch, True, color)
        screen.blit(d_surf, (x, y))

    # Cursor position
    cur_i = len(display)
    cur_x = ROW_LEFT + (cur_i % DIGITS_PER_ROW) * DIGIT_W
    cur_y = DIGITS_START_Y + (cur_i // DIGITS_PER_ROW) * ROW_HEIGHT

    # Blinking underline cursor
    if pygame.time.get_ticks() % 900 < 500:
        pygame.draw.rect(screen, GOLD, (cur_x, cur_y + 28, DIGIT_W - 4, 3))

    # Big centred hint popup
    if hint_show > 0:
        alpha = min(220, hint_show * 5)

        # Dark semi-transparent backdrop panel
        panel_w, panel_h = 320, 160
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((10, 5, 35, alpha))
        px = WIDTH  // 2 - panel_w // 2
        py = HEIGHT // 2 - panel_h // 2
        screen.blit(panel, (px, py))

        # Glowing border
        border_color = (*HINT_BLUE, alpha)
        border_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, border_color,
                         (0, 0, panel_w, panel_h), 4, border_radius=12)
        screen.blit(border_surf, (px, py))

        # "Hint!" label
        label_font  = pygame.font.SysFont("Arial", 22, bold=True)
        label_surf  = label_font.render("H I N T", True, HINT_BLUE)
        label_s     = pygame.Surface(label_surf.get_size(), pygame.SRCALPHA)
        label_s.blit(label_surf, (0, 0))
        label_s.set_alpha(alpha)
        screen.blit(label_s, (WIDTH // 2 - label_surf.get_width() // 2, py + 14))

        # The big digit in the centre
        big_font_hint = pygame.font.SysFont("Courier New", 90, bold=True)
        d_surf = big_font_hint.render(hint_char, True, WHITE)
        d_s    = pygame.Surface(d_surf.get_size(), pygame.SRCALPHA)
        d_s.blit(d_surf, (0, 0))
        d_s.set_alpha(alpha)
        screen.blit(d_s, (WIDTH // 2 - d_surf.get_width() // 2, py + 44))

    # Score bar
    score_txt = font_med.render(f"Digits: {score}   Best: {high_score}", True, WHITE)
    screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT - 95))

    # Controls hint
    ctrl = font_small.render("Press 0–9 to type a digit     H = hint", True, GRAY)
    screen.blit(ctrl, (WIDTH // 2 - ctrl.get_width() // 2, HEIGHT - 55))

    # Green/red flash overlay
    if flash_color:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*flash_color, 55))
        screen.blit(overlay, (0, 0))


# ============================================================
#  SCREENS
# ============================================================
def show_start_screen():
    frame = 0
    while True:
        frame += 1
        draw_background(frame)

        title = font_big.render("π  Quiz", True, GOLD)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 90))

        sub = font_med.render("Type the digits of pi — how many can you get?", True, WHITE)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 170))

        preview = font_digit.render("3 . 1 4 1 5 9 2 6 5 3 ...", True, GRAY)
        screen.blit(preview, (WIDTH // 2 - preview.get_width() // 2, 250))

        hint_note = font_small.render("Tip: press H during the game for a hint!", True, HINT_BLUE)
        screen.blit(hint_note, (WIDTH // 2 - hint_note.get_width() // 2, 330))

        start = font_med.render("Press SPACE to start!", True, WHITE)
        screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 420))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()


def show_game_over(score, high_score, typed_digits, correct_digit, confetti_list):
    new_best = score > 0 and score >= high_score
    frame = 0
    while True:
        frame += 1
        draw_background(frame)

        for c in confetti_list:
            c.update()
            c.draw(screen)
        confetti_list = [c for c in confetti_list if c.life > 0]

        title_color = GOLD if new_best else RED_COL
        title_text  = "NEW BEST! 🎉" if new_best else "WRONG!"
        title_surf  = font_big.render(title_text, True, title_color)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 70))

        if score == 1:
            result = f"You got 1 digit right!"
        else:
            result = f"You got {score} digits right!"
        r_surf = font_med.render(result, True, WHITE)
        screen.blit(r_surf, (WIDTH // 2 - r_surf.get_width() // 2, 150))

        next_d = font_med.render(f"The next digit was:  {correct_digit}", True, HINT_BLUE)
        screen.blit(next_d, (WIDTH // 2 - next_d.get_width() // 2, 210))

        # Show what they got (up to 40 chars)
        if typed_digits:
            shown = "".join(typed_digits[:40])
            label = font_small.render("You typed:  3." + shown + ("…" if len(typed_digits) > 40 else ""), True, GRAY)
            screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 280))

        best_txt = font_small.render(f"Best: {high_score} digits", True, GOLD_DIM)
        screen.blit(best_txt, (WIDTH // 2 - best_txt.get_width() // 2, 330))

        again = font_med.render("Press SPACE to try again", True, WHITE)
        screen.blit(again, (WIDTH // 2 - again.get_width() // 2, 430))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()


# ============================================================
#  MAIN GAME
# ============================================================
def game():
    high_score    = load_high_score()
    typed_digits  = []
    hinted_set    = set()    # indices of digits revealed by hint
    score         = 0
    confetti_list = []
    flash_color   = None
    flash_timer   = 0
    hint_show     = 0        # frames left to show the hint digit
    hint_char     = ""
    frame         = 0
    shake         = 0

    running = True
    while running:
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                # Number key pressed
                if event.unicode in "0123456789":
                    expected = PI_DIGITS[score] if score < len(PI_DIGITS) else "?"
                    if event.unicode == expected:
                        # Correct!
                        typed_digits.append(event.unicode)
                        score += 1
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                        correct_sound.play()
                        flash_color = (80, 220, 100)
                        flash_timer = 10
                        # Confetti burst
                        for _ in range(28):
                            confetti_list.append(Confetti(
                                WIDTH // 2 + random.randint(-80, 80),
                                HEIGHT // 2 - 20
                            ))
                    else:
                        # Wrong!
                        wrong_sound.play()
                        shake = 14
                        # Draw one last frame with red flash, then game over
                        flash_color = (255, 60, 60)
                        draw_background(frame)
                        for c in confetti_list:
                            c.draw(screen)
                        draw_digits_area(typed_digits, hinted_set, flash_color,
                                         hint_show, hint_char, score, high_score)
                        pygame.display.flip()
                        pygame.time.delay(350)
                        show_game_over(score, high_score, typed_digits,
                                       expected, confetti_list)
                        return  # back to outer loop for restart

                # Hint key
                if event.key == pygame.K_h:
                    if score < len(PI_DIGITS) and hint_show == 0:
                        hint_char = PI_DIGITS[score]
                        hint_show = 100   # ~1.7 seconds
                        hinted_set.add(score)
                        hint_sound.play()

                # Z — auto-type the next 100 digits!
                if event.key == pygame.K_z:
                    count = min(100, len(PI_DIGITS) - score)
                    for j in range(count):
                        typed_digits.append(PI_DIGITS[score + j])
                        hinted_set.add(score + j)   # show them in blue
                    score += count
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    auto_sound.play()
                    flash_color = HINT_BLUE
                    flash_timer = 18
                    for _ in range(80):
                        confetti_list.append(Confetti(
                            random.randint(0, WIDTH),
                            random.randint(HEIGHT // 4, HEIGHT * 3 // 4)
                        ))

        # Update timers
        if flash_timer > 0:
            flash_timer -= 1
            if flash_timer == 0:
                flash_color = None
        if hint_show > 0:
            hint_show -= 1
        if shake > 0:
            shake -= 1

        for c in confetti_list:
            c.update()
        confetti_list = [c for c in confetti_list if c.life > 0]

        # Draw
        sx = random.randint(-shake, shake) if shake > 0 else 0
        sy = random.randint(-shake // 2, shake // 2) if shake > 0 else 0
        if shake > 0:
            screen.fill(BLACK)
        draw_background(frame)

        for c in confetti_list:
            c.draw(screen)

        draw_digits_area(typed_digits, hinted_set, flash_color,
                         hint_show, hint_char, score, high_score)

        if shake > 0:
            # Render to temp surface and offset it for shake effect
            pass

        pygame.display.flip()
        clock.tick(FPS)


# ============================================================
#  RUN
# ============================================================
show_start_screen()
while True:
    game()
