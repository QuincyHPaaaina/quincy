"""
Geometry Dash — auto-running cube jumper!
Press SPACE or click to jump. Reach the end!
"""

import pygame
import math
import array
import random
import sys

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash")
clock = pygame.time.Clock()
FPS = 60

# --- Constants ---
PLAYER_SCR_X = 160
GROUND_Y     = HEIGHT - 90
CUBE_W       = 36
CUBE_H       = 36
GRAVITY      = 0.65
JUMP_FORCE   = -13.5
SPEED        = 5.5
LEVEL_LEN    = 10000

# --- Colors ---
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GOLD   = (255, 215, 0)
GRAY   = (140, 140, 170)
RED    = (255, 80, 80)

BG_PALETTES = [
    [(18, 8, 48),  (55, 18, 90)],
    [(8, 25, 65),  (18, 70, 130)],
    [(48, 8, 48),  (90, 22, 85)],
    [(8, 48, 25),  (18, 95, 55)],
]
GROUND_COL  = (40, 42, 65)
GROUND_TOP  = (75, 80, 120)
GRID_COL    = (55, 55, 80)
SPIKE_COL   = (255, 75, 75)
SPIKE_DARK  = (190, 20, 20)
SPIKE_LT    = (255, 160, 160)
BLOCK_COL   = (65, 135, 255)
BLOCK_DARK  = (25, 75, 185)
BLOCK_LT    = (145, 195, 255)
CUBE_COL    = (75, 225, 95)
CUBE_DARK   = (35, 155, 55)
CUBE_LT     = (185, 255, 195)
PART_COLS   = [
    (255,80,80),(255,205,40),(80,225,100),
    (80,185,255),(255,120,200),(205,255,100),
]

# --- Fonts ---
font_big   = pygame.font.SysFont("Arial", 48, bold=True)
font_med   = pygame.font.SysFont("Arial", 28, bold=True)
font_small = pygame.font.SysFont("Arial", 20)

# --- Parallax background buildings (pre-generated, fixed seed) ---
def _make_bg_buildings():
    rng = random.Random(777)
    out = []
    for x in range(0, LEVEL_LEN + 2000, 130):
        h = rng.randint(45, 160)
        w = rng.randint(32, 85)
        out.append((x, w, h))
    return out
BG_BUILDINGS = _make_bg_buildings()

# --- Sounds ---
def make_jump_sound():
    sr, dur = 44100, 0.09
    s = array.array("h")
    for i in range(int(sr * dur)):
        t = i / sr
        fade = max(0, 1 - t / dur)
        freq = 480 + 280 * (t / dur)
        s.append(int(0.25 * 32767 * fade * math.sin(2*math.pi*freq*t)))
    return pygame.mixer.Sound(buffer=s)

def make_death_sound():
    sr, dur = 44100, 0.25
    s = array.array("h")
    rng = random.Random(42)
    for i in range(int(sr * dur)):
        t = i / sr
        fade = max(0, 1 - t / dur) ** 0.5
        s.append(int(0.45 * 32767 * fade * rng.uniform(-1, 1)))
    return pygame.mixer.Sound(buffer=s)

def make_win_sound():
    sr = 44100
    s = array.array("h")
    for freq, dur in [(523,.08),(659,.08),(784,.08),(1047,.08),(1319,.30)]:
        for i in range(int(sr * dur)):
            t = i / sr
            fade = max(0, 1 - t / dur)
            s.append(int(0.22 * 32767 * fade * math.sin(2*math.pi*freq*t)))
    return pygame.mixer.Sound(buffer=s)

def make_bg_music():
    sr  = 44100
    bpm = 130
    spb = 60 / bpm          # seconds per beat
    beat_samples = int(sr * spb)
    total = beat_samples * 8   # 8-beat loop
    buf = array.array("h", [0] * total)

    def add_tone(freq, start_s, dur_s, vol=0.12, square=False):
        start = int(start_s * sr)
        dur   = int(dur_s   * sr)
        fade  = max(1, int(sr * 0.015))
        for i in range(dur):
            pos = start + i
            if pos >= total:
                break
            t   = i / sr
            env = min(1.0, min(i, dur - i) / fade)
            v   = (1.0 if math.sin(2*math.pi*freq*t) > 0 else -1.0) * 0.45 if square else math.sin(2*math.pi*freq*t)
            buf[pos] = max(-32767, min(32767, buf[pos] + int(vol * 32767 * env * v)))

    # Upbeat arpeggio melody
    arp = [
        (523,0.00),(659,0.25),(784,0.50),(1047,0.75),
        (880,1.00),(784,1.25),(659,1.50),(523,1.75),
        (587,2.00),(740,2.25),(880,2.50),(1047,2.75),
        (880,3.00),(740,3.25),(587,3.50),(523,3.75),
        (440,4.00),(523,4.25),(659,4.50),(784,4.75),
        (659,5.00),(523,5.25),(440,5.50),(392,5.75),
        (523,6.00),(659,6.25),(784,6.50),(880,6.75),
        (1047,7.00),(880,7.25),(784,7.50),(659,7.75),
    ]
    for freq, bp in arp:
        add_tone(freq, bp * spb, spb * 0.22, vol=0.10)

    # Bass line (square wave)
    bass = [(130,0),(130,1),(165,2),(165,3),(110,4),(110,5),(146,6),(146,7)]
    for freq, b in bass:
        add_tone(freq, b * spb, spb * 0.65, vol=0.15, square=True)

    # Kick drum every beat
    for b in range(8):
        s0 = int(b * spb * sr)
        for i in range(int(sr * 0.09)):
            if s0 + i >= total: break
            t = i / sr
            val = int(0.28 * 32767 * math.exp(-t*30) * math.sin(2*math.pi*100*math.exp(-t*40)*t))
            buf[s0 + i] = max(-32767, min(32767, buf[s0 + i] + val))

    # Hi-hat every half-beat
    rng2 = random.Random(99)
    for h in range(16):
        s0 = int(h * spb * sr / 2)
        for i in range(int(sr * 0.03)):
            if s0 + i >= total: break
            t   = i / sr
            val = int(0.07 * 32767 * math.exp(-t*80) * rng2.uniform(-1, 1))
            buf[s0 + i] = max(-32767, min(32767, buf[s0 + i] + val))

    return pygame.mixer.Sound(buffer=buf)

jump_sound  = make_jump_sound()
death_sound = make_death_sound()
win_sound   = make_win_sound()
bg_music    = make_bg_music()
bg_music.play(-1)   # loop forever

# --- Level ---
SPIKE_W, SPIKE_H = 32, 32
BLOCK_W, BLOCK_H = 60, 60

OBSTACLES = [
    # Section 1 — warmup
    ("spike", 750), ("spike", 1150), ("spike", 1550), ("spike", 1595),
    ("spike", 2050),
    ("block", 2350),
    ("spike", 2700), ("spike", 2745), ("spike", 3100), ("spike", 3145), ("spike", 3190),
    ("block", 3500),
    # Section 2
    ("spike", 3850), ("spike", 3895), ("spike", 3940),
    ("spike", 4350), ("spike", 4395),
    ("spike", 4800),
    ("block", 5100),
    ("spike", 5400), ("spike", 5445), ("spike", 5490), ("spike", 5535),
    ("spike", 5950), ("spike", 5995),
    ("block", 6300),
    # Section 3
    ("spike", 6600), ("spike", 6645), ("spike", 6690),
    ("spike", 7100), ("spike", 7145), ("spike", 7190), ("spike", 7235),
    ("block", 7550),
    ("spike", 7850), ("spike", 7895), ("spike", 7940),
    ("spike", 8350), ("spike", 8395), ("spike", 8440), ("spike", 8485),
    ("block", 8800),
    # Final stretch
    ("spike", 9050), ("spike", 9095), ("spike", 9140), ("spike", 9185), ("spike", 9230),
    ("spike", 9550), ("spike", 9595), ("spike", 9640), ("spike", 9685), ("spike", 9730),
]

# --- Particles ---
class Particle:
    def __init__(self, x, y):
        self.x    = float(x)
        self.y    = float(y)
        self.vx   = random.uniform(-6, 6)
        self.vy   = random.uniform(-9, -1)
        self.col  = random.choice(PART_COLS)
        self.size = random.randint(4, 9)
        self.life = random.randint(30, 55)
        self.max_life = self.life

    def update(self):
        self.vy += 0.4
        self.x  += self.vx
        self.y  += self.vy
        self.life -= 1

    def draw(self, surface):
        a = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.col, a), (0, 0, self.size*2, self.size*2))
        surface.blit(s, (int(self.x)-self.size, int(self.y)-self.size))


# --- Drawing helpers ---
def draw_cube(surface, scr_x, y_bottom, angle, squash=False, stretch=False):
    y_top  = y_bottom - CUBE_H
    cx_mid = scr_x + CUBE_W // 2
    cy_mid = y_top  + CUBE_H // 2

    # Soft glow halo behind cube
    for gr, ga in [(30, 18), (22, 30), (14, 50)]:
        gs = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*CUBE_COL, ga), (gr, gr), gr)
        surface.blit(gs, (cx_mid - gr, cy_mid - gr))

    sz  = CUBE_W + 20
    off = (sz - CUBE_W) // 2
    cs  = pygame.Surface((sz, sz), pygame.SRCALPHA)

    # Main body
    pygame.draw.rect(cs, CUBE_COL,  (off, off, CUBE_W, CUBE_H), border_radius=5)
    # Top highlight strip
    pygame.draw.rect(cs, CUBE_LT,   (off+2, off+2, CUBE_W-4, 9),  border_radius=4)
    # Bottom shadow strip
    pygame.draw.rect(cs, CUBE_DARK, (off+2, off+CUBE_H-9, CUBE_W-4, 7), border_radius=3)
    # Left bright edge
    pygame.draw.line(cs, CUBE_LT, (off+2, off+2), (off+2, off+CUBE_H-2), 2)

    # Face
    icx, icy = off + CUBE_W//2, off + CUBE_H//2
    # Eyes
    for ex in (icx - 5, icx + 5):
        pygame.draw.circle(cs, WHITE,       (ex, icy - 4), 4)
        pygame.draw.circle(cs, (20, 20, 20),(ex + 1, icy - 3), 2)   # pupil
        pygame.draw.circle(cs, WHITE,       (ex + 2, icy - 5), 1)   # shine
    # Smile arc
    pygame.draw.arc(cs, (20, 20, 20),
                    pygame.Rect(icx - 7, icy + 1, 14, 9), math.pi, 0, 3)
    pygame.draw.arc(cs, WHITE,
                    pygame.Rect(icx - 6, icy + 2, 12, 8), math.pi, 0, 2)

    # Outer outline (dark then bright)
    pygame.draw.rect(cs, CUBE_DARK, (off,   off,   CUBE_W,   CUBE_H),   2, border_radius=5)
    pygame.draw.rect(cs, CUBE_LT,   (off+1, off+1, CUBE_W-2, CUBE_H-2), 1, border_radius=4)

    # Squash / stretch before rotation
    if squash:
        cs = pygame.transform.scale(cs, (int(sz * 1.28), int(sz * 0.76)))
    elif stretch:
        cs = pygame.transform.scale(cs, (int(sz * 0.82), int(sz * 1.24)))

    rotated = pygame.transform.rotate(cs, -angle)
    surface.blit(rotated, (cx_mid - rotated.get_width()//2,
                            cy_mid - rotated.get_height()//2))


def draw_spike(surface, sx):
    mid  = sx + SPIKE_W // 2
    tip_y = GROUND_Y - SPIKE_H

    # Red glow at base
    gs = pygame.Surface((SPIKE_W + 20, 22), pygame.SRCALPHA)
    pygame.draw.ellipse(gs, (*SPIKE_COL, 45), (0, 4, SPIKE_W + 20, 16))
    surface.blit(gs, (sx - 10, GROUND_Y - 11))

    # Main spike body
    outer = [(sx, GROUND_Y), (sx + SPIKE_W, GROUND_Y), (mid, tip_y)]
    pygame.draw.polygon(surface, SPIKE_COL, outer)

    # Brighter inner core triangle
    core = [(sx + 6, GROUND_Y - 4), (sx + SPIKE_W - 6, GROUND_Y - 4), (mid, tip_y + 10)]
    pygame.draw.polygon(surface, SPIKE_LT, core)

    # Dark outline
    pygame.draw.polygon(surface, SPIKE_DARK, outer, 2)

    # Glowing tip dot
    tip_gs = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.circle(tip_gs, (*SPIKE_LT, 180), (7, 7), 7)
    surface.blit(tip_gs, (mid - 7, tip_y - 5))


def draw_block(surface, sx):
    by = GROUND_Y - BLOCK_H

    # Glow behind block
    gs = pygame.Surface((BLOCK_W + 20, BLOCK_H + 20), pygame.SRCALPHA)
    pygame.draw.rect(gs, (*BLOCK_COL, 35), (0, 0, BLOCK_W + 20, BLOCK_H + 20), border_radius=6)
    surface.blit(gs, (sx - 10, by - 10))

    # Right shadow strip (3D depth)
    pygame.draw.rect(surface, BLOCK_DARK, (sx + BLOCK_W - 7, by + 7, 7, BLOCK_H))
    # Bottom shadow strip
    pygame.draw.rect(surface, BLOCK_DARK, (sx + 7, by + BLOCK_H - 7, BLOCK_W, 7))

    # Main face
    pygame.draw.rect(surface, BLOCK_COL, (sx, by, BLOCK_W - 7, BLOCK_H - 7))
    # Top highlight
    pygame.draw.rect(surface, BLOCK_LT,  (sx + 2, by + 2, BLOCK_W - 11, 10))
    # Left bright edge
    pygame.draw.line(surface, BLOCK_LT,  (sx + 2, by + 2), (sx + 2, by + BLOCK_H - 9), 2)

    # Inner inset frame
    pygame.draw.rect(surface, BLOCK_DARK, (sx + 7, by + 16, BLOCK_W - 21, BLOCK_H - 30), 2)

    # Rivet corners with bright centre
    for rx, ry in [(sx+7, by+7), (sx+BLOCK_W-14, by+7),
                   (sx+7, by+BLOCK_H-14), (sx+BLOCK_W-14, by+BLOCK_H-14)]:
        pygame.draw.circle(surface, BLOCK_DARK, (rx, ry), 5)
        pygame.draw.circle(surface, BLOCK_LT,   (rx, ry), 2)

    # Circuit lines inside frame
    pygame.draw.line(surface, BLOCK_DARK,
                     (sx + 7,  by + BLOCK_H // 2 - 4),
                     (sx + BLOCK_W - 14, by + BLOCK_H // 2 - 4), 1)
    pygame.draw.line(surface, BLOCK_DARK,
                     (sx + BLOCK_W // 2 - 4, by + 16),
                     (sx + BLOCK_W // 2 - 4, by + BLOCK_H - 16), 1)

    # Bright outer outline
    pygame.draw.rect(surface, BLOCK_LT, (sx, by, BLOCK_W - 7, BLOCK_H - 7), 2)


def draw_finish_line(surface, camera_x, frame=0):
    fx = int(LEVEL_LEN - camera_x)
    if not (-60 < fx < WIDTH + 60):
        return
    pulse = abs(math.sin(frame * 0.07))

    # Outer glow column
    for gw, ga in [(40, 12), (28, 22), (18, 35)]:
        gs = pygame.Surface((gw, 140), pygame.SRCALPHA)
        gs.fill((*GOLD, int(ga * (0.6 + pulse * 0.4))))
        surface.blit(gs, (fx - gw//2 + 15, GROUND_Y - 140))

    # Checkered flag
    for row in range(9):
        for col in range(2):
            shade = WHITE if (row + col) % 2 == 0 else (40, 40, 40)
            pygame.draw.rect(surface, shade,
                             (fx + col*15, GROUND_Y - 135 + row*15, 15, 15))

    # Gold border with animated brightness
    bc = int(180 + 75 * pulse)
    pygame.draw.rect(surface, (bc, bc, 0), (fx, GROUND_Y - 135, 30, 135), 3)

    # "FINISH" text floating above
    fs = font_small.render("FINISH!", True, GOLD)
    surface.blit(fs, (fx + 15 - fs.get_width()//2, GROUND_Y - 165))


def get_bg_colors(world_x):
    t   = max(0, min(1, world_x / LEVEL_LEN)) * (len(BG_PALETTES)-1)
    i   = min(int(t), len(BG_PALETTES)-2)
    f   = t - i
    top    = tuple(int(BG_PALETTES[i][0][c]*(1-f)+BG_PALETTES[i+1][0][c]*f) for c in range(3))
    bottom = tuple(int(BG_PALETTES[i][1][c]*(1-f)+BG_PALETTES[i+1][1][c]*f) for c in range(3))
    return top, bottom


def draw_background(world_x, pulse, camera_x):
    top, bot = get_bg_colors(world_x)
    if pulse > 0:
        top = tuple(min(255, int(c * (1 + pulse*0.35))) for c in top)
        bot = tuple(min(255, int(c * (1 + pulse*0.35))) for c in bot)
    for y in range(0, GROUND_Y, 4):
        t = y / GROUND_Y
        r = int(top[0]*(1-t)+bot[0]*t)
        g = int(top[1]*(1-t)+bot[1]*t)
        b = int(top[2]*(1-t)+bot[2]*t)
        pygame.draw.rect(screen, (r, g, b), (0, y, WIDTH, 4))

    # Parallax buildings (scroll at 30% of camera speed)
    for bx, bw, bh in BG_BUILDINGS:
        sx = int(bx - camera_x * 0.3)
        if sx < -100 or sx > WIDTH + 100:
            continue
        by = GROUND_Y - bh
        # Silhouette slightly lighter than background
        sc = tuple(min(255, c + 18) for c in bot)
        pygame.draw.rect(screen, sc, (sx, by, bw, bh))
        # Lit windows
        for wy in range(by + 8, GROUND_Y - 8, 18):
            for wx in range(sx + 5, sx + bw - 5, 15):
                if (wx * 3 + wy * 7) % 5 != 0:
                    wc = tuple(min(255, c + 55) for c in sc)
                    pygame.draw.rect(screen, wc, (wx, wy, 7, 9))

    # Scrolling grid lines
    for gx in range(0, WIDTH + 60, 60):
        lx = gx - (camera_x % 60)
        pygame.draw.line(screen, GRID_COL, (int(lx), 0), (int(lx), GROUND_Y), 1)
    for gy in range(0, GROUND_Y, 60):
        pygame.draw.line(screen, GRID_COL, (0, gy), (WIDTH, gy), 1)
    # Bright dots at grid intersections
    for gx in range(0, WIDTH + 60, 60):
        lx = gx - (camera_x % 60)
        for gy in range(0, GROUND_Y, 60):
            pygame.draw.circle(screen, (80, 80, 110), (int(lx), gy), 2)


def draw_ground(camera_x=0, pulse=0):
    pygame.draw.rect(screen, GROUND_COL, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    # Fixed tile pattern (no scrolling)
    tile_w = 42
    for tx in range(0, WIDTH + tile_w, tile_w):
        idx = tx // tile_w
        alt = tuple(min(255, c + (10 if idx % 2 == 0 else 0)) for c in GROUND_COL)
        pygame.draw.rect(screen, alt, (tx, GROUND_Y + 4, tile_w - 1, HEIGHT - GROUND_Y - 4))
    # Bright glowing top line
    glow_r = min(255, int(GROUND_TOP[0] + pulse * 80))
    glow_g = min(255, int(GROUND_TOP[1] + pulse * 80))
    glow_b = min(255, int(GROUND_TOP[2] + pulse * 80))
    pygame.draw.line(screen, (glow_r, glow_g, glow_b), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
    pygame.draw.line(screen, GROUND_TOP, (0, GROUND_Y + 3), (WIDTH, GROUND_Y + 3), 1)


def draw_progress(world_x):
    prog  = max(0, min(1, world_x / LEVEL_LEN))
    bw, bh, bx, by = WIDTH-40, 8, 20, 12
    pygame.draw.rect(screen, (50,50,70), (bx, by, bw, bh), border_radius=4)
    if prog > 0:
        pygame.draw.rect(screen, GOLD, (bx, by, int(bw*prog), bh), border_radius=4)
    pygame.draw.rect(screen, GRAY, (bx, by, bw, bh), 1, border_radius=4)
    pct = font_small.render(f"{int(prog*100)}%", True, WHITE)
    screen.blit(pct, (WIDTH-20-pct.get_width(), 8))


# --- Screens ---
def show_start_screen():
    frame = 0
    while True:
        frame += 1
        draw_background(0, math.sin(frame*0.05)*0.4+0.4, 0)
        draw_ground()
        draw_cube(screen, WIDTH//2 - CUBE_W//2, GROUND_Y, 0, squash=False, stretch=False)

        title = font_big.render("Geometry Dash", True, GOLD)
        screen.blit(title, (WIDTH//2-title.get_width()//2, 90))
        sub = font_med.render("Press SPACE or click to jump!", True, WHITE)
        screen.blit(sub, (WIDTH//2-sub.get_width()//2, 160))
        tip = font_small.render("Avoid all spikes and blocks — reach the end!", True, GRAY)
        screen.blit(tip, (WIDTH//2-tip.get_width()//2, 210))
        go = font_med.render("Press SPACE to start", True, WHITE)
        screen.blit(go, (WIDTH//2-go.get_width()//2, 380))

        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE: return
            if event.type == pygame.MOUSEBUTTONDOWN: return


def show_death_screen(attempt, pct_reached, particles):
    timer = 0
    while True:
        timer += 1
        draw_background(0, 0, 0)
        draw_ground()
        for p in particles:
            p.update(); p.draw(screen)
        particles = [p for p in particles if p.life > 0]

        t1 = font_big.render("You crashed!", True, RED)
        screen.blit(t1, (WIDTH//2-t1.get_width()//2, HEIGHT//2-70))
        t2 = font_med.render(f"Reached {pct_reached}% — Attempt {attempt}", True, GRAY)
        screen.blit(t2, (WIDTH//2-t2.get_width()//2, HEIGHT//2))
        if timer > 30:
            t3 = font_med.render("Press SPACE to try again", True, WHITE)
            screen.blit(t3, (WIDTH//2-t3.get_width()//2, HEIGHT//2+55))

        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE and timer > 30: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if timer > 30: return


def show_win_screen(attempt):
    confetti, timer = [], 0
    while True:
        timer += 1
        draw_background(LEVEL_LEN, 0, LEVEL_LEN - PLAYER_SCR_X)
        draw_ground()
        if timer % 3 == 0:
            confetti.append(Particle(random.randint(0, WIDTH), -5))
        for c in confetti:
            c.vy = min(c.vy + 0.2, 6); c.x += c.vx; c.y += c.vy; c.life -= 1
            if 0 < c.y < HEIGHT: pygame.draw.rect(screen, c.col, (int(c.x), int(c.y), c.size, c.size))
        confetti = [c for c in confetti if c.life > 0 and c.y < HEIGHT+20]

        t1 = font_big.render("YOU WIN!!!", True, GOLD)
        screen.blit(t1, (WIDTH//2-t1.get_width()//2, HEIGHT//2-75))
        t2 = font_med.render(f"Completed in {attempt} attempt{'s' if attempt>1 else ''}!", True, WHITE)
        screen.blit(t2, (WIDTH//2-t2.get_width()//2, HEIGHT//2))
        t3 = font_med.render("Press SPACE to play again", True, GRAY)
        screen.blit(t3, (WIDTH//2-t3.get_width()//2, HEIGHT//2+55))

        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE: return


# --- Main game ---
def game(attempt):
    world_x      = 0.0
    y_bottom     = float(GROUND_Y)
    vy           = 0.0
    on_ground    = True
    angle        = 0.0
    pulse        = 0.0
    pulse_timer  = 0
    trail        = []
    land_timer   = 0   # squash on landing
    jump_timer   = 0   # stretch on jump
    frame        = 0

    while True:
        jump_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE: jump_pressed = True
            if event.type == pygame.MOUSEBUTTONDOWN: jump_pressed = True

        if jump_pressed and on_ground:
            vy = JUMP_FORCE
            on_ground = False
            jump_timer = 8
            jump_sound.play()

        world_x  += SPEED
        vy       += GRAVITY
        y_bottom += vy
        was_in_air = not on_ground
        if y_bottom >= GROUND_Y:
            y_bottom  = GROUND_Y
            vy        = 0.0
            if was_in_air:
                land_timer = 8   # squash on landing
            on_ground = True
        else:
            on_ground = False

        if land_timer > 0: land_timer -= 1
        if jump_timer > 0: jump_timer -= 1
        frame += 1
        # Only flip while in the air — snap flat on landing
        if not on_ground:
            angle += 9.0        # ~360° over a full jump arc
        else:
            angle = round(angle / 360) * 360  # snap to upright
        pulse_timer += 1
        if pulse_timer >= 45:
            pulse_timer = 0
            pulse = 1.0
        pulse *= 0.85

        camera_x = world_x - PLAYER_SCR_X
        y_top    = y_bottom - CUBE_H

        trail.append((PLAYER_SCR_X + CUBE_W//2, int(y_bottom - CUBE_H//2)))
        if len(trail) > 12:
            trail.pop(0)

        # Win
        if world_x >= LEVEL_LEN:
            win_sound.play()
            return "win", 100

        # Collision
        p_rect = pygame.Rect(PLAYER_SCR_X+5, int(y_top)+5, CUBE_W-10, CUBE_H-10)
        hit = False
        for otype, ox in OBSTACLES:
            sx = ox - camera_x
            if sx < -80 or sx > WIDTH+20:
                continue
            if otype == "spike":
                srect = pygame.Rect(sx+5, GROUND_Y-SPIKE_H+6, SPIKE_W-10, SPIKE_H-7)
                if p_rect.colliderect(srect):
                    hit = True; break
            elif otype == "block":
                brect = pygame.Rect(sx+2, GROUND_Y-BLOCK_H+2, BLOCK_W-4, BLOCK_H-4)
                if p_rect.colliderect(brect):
                    hit = True; break

        if hit:
            death_sound.play()
            pct = int(world_x / LEVEL_LEN * 100)
            px  = PLAYER_SCR_X + CUBE_W//2
            py  = int(y_bottom - CUBE_H//2)
            particles = [Particle(px, py) for _ in range(24)]
            show_death_screen(attempt, pct, particles)
            return "dead", pct

        # Draw
        draw_background(world_x, pulse, camera_x)

        # Glowing trail (outer glow + inner core)
        for i, (tx, ty) in enumerate(trail):
            prog = (i + 1) / len(trail)
            a    = int(170 * prog)
            r    = max(2, int(CUBE_W * 0.32 * prog))
            # Outer glow
            gs = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*CUBE_COL, a // 4), (0, 0, r*4, r*4), border_radius=4)
            screen.blit(gs, (tx - r*2, ty - r*2))
            # Inner core
            ts = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.rect(ts, (*CUBE_COL, a), (0, 0, r*2, r*2), border_radius=3)
            screen.blit(ts, (tx - r, ty - r))

        for otype, ox in OBSTACLES:
            sx = ox - camera_x
            if -80 < sx < WIDTH+20:
                if otype == "spike": draw_spike(screen, sx)
                elif otype == "block": draw_block(screen, sx)

        draw_finish_line(screen, camera_x, frame)
        draw_ground(camera_x, pulse)
        draw_cube(screen, PLAYER_SCR_X, y_bottom, angle,
                  squash=land_timer > 0, stretch=jump_timer > 0)
        draw_progress(world_x)

        att_txt = font_small.render(f"Attempt {attempt}", True, GRAY)
        screen.blit(att_txt, (20, 28))

        pygame.display.flip()
        clock.tick(FPS)


# --- Run ---
show_start_screen()
attempt = 1
while True:
    result, pct = game(attempt)
    if result == "win":
        show_win_screen(attempt)
        attempt = 1
    else:
        attempt += 1
