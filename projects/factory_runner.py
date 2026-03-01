"""
Factory Runner — a side-scrolling platformer set in a factory!
Collect coins, jump on platforms, and avoid obstacles.

Arrow keys to move, SPACE to jump.
Press SPACE again in the air for a DOUBLE JUMP!
Stomp robots by landing on their heads.
"""

import pygame
import math
import array
import random
import os

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# --- Screen setup ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Factory Runner")
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
BG_DARK       = (40, 42, 48)
METAL_GRAY    = (130, 135, 140)
METAL_LIGHT   = (170, 175, 180)
METAL_DARK    = (80, 85, 92)
RIVET         = (90, 92, 96)
CONCRETE      = (100, 100, 105)
PIPE_COLOR    = (80, 85, 90)
GEAR_COLOR    = (70, 73, 78)
ORANGE_GLOW   = (200, 110, 40)
GOLD          = (255, 215, 0)
GOLD_DARK     = (200, 165, 0)
SKIN          = (240, 200, 160)
SHIRT         = (50, 120, 200)
PANTS         = (60, 60, 80)
SHOE          = (50, 40, 35)
HARD_HAT      = (230, 190, 40)
WHITE         = (255, 255, 255)
RED           = (200, 50, 50)
STEAM_WHITE   = (200, 205, 210)
BARREL_BROWN  = (120, 70, 30)
BARREL_STRIPE = (80, 50, 20)
# New colors
LASER_RED     = (255, 30, 30)
CRATE_TAN     = (160, 110, 55)
CRATE_DARK    = (110, 70, 25)
ROBOT_BODY    = (100, 108, 120)
ROBOT_DARK    = (65, 70, 80)
ROBOT_EYE     = (80, 220, 100)
BLUE_PLAT     = (60, 140, 210)
BLUE_PLAT_LT  = (110, 185, 240)
FINISH_GREEN  = (60, 220, 80)
HEART_RED     = (220, 50, 50)
LAVA_DARK     = (100, 15, 0)
LAVA_RED      = (190, 30, 10)
LAVA_ORANGE   = (255, 110, 0)
LAVA_YELLOW   = (255, 220, 50)
LAVA_BRIGHT   = (255, 240, 160)
DARK_BLUE     = (30, 70, 150)

# --- Fonts ---
font_big   = pygame.font.SysFont("Arial", 48, bold=True)
font_med   = pygame.font.SysFont("Arial", 32, bold=True)
font_small = pygame.font.SysFont("Arial", 22)


# ============================================================
#  SOUNDS
# ============================================================
def make_sound(frequency, duration, volume=0.3):
    sample_rate = 44100
    samples = array.array("h")
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        fade = max(0, 1 - t / duration)
        samples.append(int(volume * 32767 * fade * math.sin(2 * math.pi * frequency * t)))
    return pygame.mixer.Sound(buffer=samples)


def make_coin_sound():
    sample_rate = 44100
    samples = array.array("h")
    for freq, dur in [(1318, 0.06), (1568, 0.10)]:
        for i in range(int(sample_rate * dur)):
            t = i / sample_rate
            fade = max(0, 1 - t / dur)
            samples.append(int(0.25 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)


def make_game_over_sound():
    sample_rate = 44100
    duration = 0.6
    samples = array.array("h")
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        fade = max(0, 1 - t / duration)
        freq = 440 - 500 * t
        samples.append(int(0.3 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)


def make_stomp_sound():
    """Rising boing when stomping a robot."""
    sample_rate = 44100
    duration = 0.15
    samples = array.array("h")
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        fade = max(0, 1 - t / duration)
        freq = 200 + 600 * (t / duration)   # pitch rises
        samples.append(int(0.3 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)


def make_win_sound():
    """Happy fanfare."""
    sample_rate = 44100
    samples = array.array("h")
    for freq, dur in [(523, 0.10), (659, 0.10), (784, 0.10), (1047, 0.30)]:
        for i in range(int(sample_rate * dur)):
            t = i / sample_rate
            fade = max(0, 1 - t / dur)
            samples.append(int(0.25 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)


jump_sound       = make_sound(600, 0.10)
double_jump_sound = make_sound(800, 0.08, 0.2)
coin_sound       = make_coin_sound()
game_over_sound  = make_game_over_sound()
stomp_sound      = make_stomp_sound()
win_sound        = make_win_sound()
hurt_sound        = make_sound(180, 0.20, 0.4)


def make_checkpoint_sound():
    """Rising three-note chime when you hit a checkpoint."""
    sample_rate = 44100
    samples = array.array("h")
    for freq, dur in [(880, 0.08), (1100, 0.08), (1320, 0.18)]:
        for i in range(int(sample_rate * dur)):
            t = i / sample_rate
            fade = max(0, 1 - t / dur)
            samples.append(int(0.25 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)


checkpoint_sound  = make_checkpoint_sound()


def make_1up_sound():
    """Happy 4-note jingle for getting an extra life."""
    sample_rate = 44100
    samples = array.array("h")
    for freq, dur in [(523, 0.08), (659, 0.08), (784, 0.08), (1047, 0.22)]:
        for i in range(int(sample_rate * dur)):
            t = i / sample_rate
            fade = max(0, 1 - t / dur)
            samples.append(int(0.28 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)


oneup_sound = make_1up_sound()


def make_meow_sound():
    """Silly meow — rises then falls."""
    sample_rate = 44100
    samples = array.array("h")
    # rising part
    for i in range(int(sample_rate * 0.12)):
        t = i / sample_rate
        fade = max(0, 1 - t / 0.12)
        freq = 600 + 400 * (t / 0.12)
        samples.append(int(0.3 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    # falling part
    for i in range(int(sample_rate * 0.18)):
        t = i / sample_rate
        fade = max(0, 1 - t / 0.18)
        freq = 1000 - 500 * (t / 0.18)
        samples.append(int(0.25 * 32767 * fade * math.sin(2 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=samples)


meow_sound = make_meow_sound()


# ============================================================
#  LEVEL CONSTANTS
# ============================================================
GROUND_Y      = HEIGHT - 50
GROUND_HEIGHT = 50
LEVEL_END_X   = 4800   # where the finish line lives


# ============================================================
#  PLATFORM CLASS  (supports moving platforms!)
# ============================================================
class Platform:
    def __init__(self, x, y, w, ptype,
                 moves=False, x_min=None, x_max=None, speed=2.0):
        self.x      = float(x)
        self.y      = y
        self.w      = w
        self.ptype  = ptype        # "girder", "conveyor", or "moving"
        self.moves  = moves
        self.x_min  = float(x_min) if x_min is not None else float(x)
        self.x_max  = float(x_max) if x_max is not None else float(x)
        self.speed  = speed
        self.dir    = 1
        self.prev_x = float(x)

    def update(self):
        self.prev_x = self.x
        if self.moves:
            self.x += self.speed * self.dir
            if self.x <= self.x_min:
                self.x = self.x_min
                self.dir = 1
            elif self.x + self.w >= self.x_max:
                self.x = self.x_max - self.w
                self.dir = -1

    @property
    def dx(self):
        """How far the platform moved this frame."""
        return self.x - self.prev_x


# ============================================================
#  ENEMY CLASS
# ============================================================
class Enemy:
    def __init__(self, x, y, x_min, x_max, speed=1.3):
        self.x          = float(x)
        self.y          = float(y)   # top of enemy
        self.w          = 24
        self.h          = 32
        self.x_min      = float(x_min)
        self.x_max      = float(x_max)
        self.speed      = speed
        self.dir         = 1
        self.alive       = True
        self.walk_timer  = 0.0
        self.blink_timer = random.randint(0, 150)   # offset so they don't all blink together

    def update(self):
        self.x += self.speed * self.dir
        if self.x <= self.x_min or self.x + self.w >= self.x_max:
            self.dir *= -1
        self.walk_timer  += 0.18
        self.blink_timer  = (self.blink_timer + 1) % 160   # blink every ~2.7 seconds

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surface, camera_x, player_x=None):
        sx = self.x - camera_x
        if sx < -50 or sx > WIDTH + 50:
            return
        sy  = self.y
        cx  = sx + self.w // 2

        # "!" alert bubble when player is nearby
        if player_x is not None and abs(player_x - (self.x + self.w // 2)) < 220:
            bx = int(cx) - 8
            by = int(sy) - 26
            pygame.draw.rect(surface, WHITE, (bx, by, 16, 16), border_radius=3)
            pygame.draw.rect(surface, ORANGE_GLOW, (bx, by, 16, 16), border_radius=3, width=2)
            surface.blit(font_small.render("!", True, ORANGE_GLOW), (bx + 5, by))

        # Antenna (bobs up and down while walking)
        antenna_bob = int(math.sin(self.walk_timer * 2) * 1.5)
        pygame.draw.line(surface, ROBOT_DARK,
                         (int(cx), int(sy) - 2),
                         (int(cx), int(sy) - 9 + antenna_bob), 2)
        # Antenna tip pulses between green and yellow
        tip_color = ROBOT_EYE if (int(self.walk_timer * 3) % 2 == 0) else GOLD
        pygame.draw.circle(surface, tip_color, (int(cx), int(sy) - 10 + antenna_bob), 3)

        # Head box
        pygame.draw.rect(surface, ROBOT_BODY,
                         (int(cx) - 10, int(sy), 20, 14), border_radius=3)

        # Eye — blinks every ~2.7 seconds (last 5 frames of the 160-frame cycle)
        ex = int(cx) + (4 if self.dir > 0 else -4)
        blinking = self.blink_timer > 155
        if blinking:
            pygame.draw.line(surface, ROBOT_DARK,
                             (ex - 4, int(sy) + 6), (ex + 4, int(sy) + 6), 2)
        else:
            pygame.draw.rect(surface, ROBOT_DARK,
                             (ex - 5, int(sy) + 3, 10, 6), border_radius=2)
            pygame.draw.ellipse(surface, ROBOT_EYE,
                                (ex - 3, int(sy) + 4, 6, 4))

        # Body
        pygame.draw.rect(surface, ROBOT_DARK,
                         (int(cx) - 8, int(sy) + 14, 16, 13))

        # Chest LED — pulses
        led_pulse = 0.5 + 0.5 * math.sin(self.walk_timer * 0.8)
        led_r = int(2 + led_pulse * 1.5)
        led_g = int(80 + led_pulse * 175)
        pygame.draw.circle(surface, (0, led_g, 50),
                           (int(cx), int(sy) + 20), led_r)

        # Arms — swing opposite to legs
        arm_swing = int(math.sin(self.walk_timer) * 5)
        arm_y = int(sy) + 17
        pygame.draw.line(surface, ROBOT_BODY,
                         (int(cx) - 8, arm_y),
                         (int(cx) - 14 - arm_swing, arm_y + 7), 2)
        pygame.draw.line(surface, ROBOT_BODY,
                         (int(cx) + 8, arm_y),
                         (int(cx) + 14 + arm_swing, arm_y + 7), 2)

        # Legs (walk animation)
        lo = int(math.sin(self.walk_timer) * 4)
        pygame.draw.line(surface, ROBOT_BODY,
                         (int(cx) - 4, int(sy) + 27),
                         (int(cx) - 4 + lo, int(sy) + 34), 3)
        pygame.draw.line(surface, ROBOT_BODY,
                         (int(cx) + 4, int(sy) + 27),
                         (int(cx) + 4 - lo, int(sy) + 34), 3)


# ============================================================
#  FALLING CRATE CLASS
# ============================================================
class FallingCrate:
    def __init__(self, x, y):
        self.x       = float(x)
        self.y       = float(y)
        self.w       = 32
        self.h       = 32
        self.vy      = 0.0
        self.falling = False
        self.landed  = False
        self.shake   = 0      # rumble intensity when about to drop

    def update(self, player_x):
        cx = self.x + self.w // 2
        dist = abs(player_x - cx)

        if not self.falling and not self.landed:
            if dist < 180:
                self.shake = 3
            if dist < 90:
                self.falling = True
                self.shake   = 0

        if self.falling and not self.landed:
            self.vy += 0.9
            self.y  += self.vy
            if self.y + self.h >= GROUND_Y:
                self.y      = float(GROUND_Y - self.h)
                self.vy     = 0
                self.landed = True

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surface, camera_x):
        sx = self.x - camera_x
        if sx < -50 or sx > WIDTH + 50:
            return
        wobble = random.randint(-self.shake, self.shake) if self.shake else 0
        rx, ry = int(sx) + wobble, int(self.y)

        # Body
        pygame.draw.rect(surface, CRATE_TAN, (rx, ry, self.w, self.h))
        # Boards
        for oy in (10, 22):
            pygame.draw.line(surface, CRATE_DARK, (rx, ry + oy),
                             (rx + self.w, ry + oy), 2)
        for ox in (10, 22):
            pygame.draw.line(surface, CRATE_DARK, (rx + ox, ry),
                             (rx + ox, ry + self.h), 2)
        # X brace
        pygame.draw.line(surface, CRATE_DARK,
                         (rx + 2, ry + 2), (rx + self.w - 2, ry + self.h - 2), 1)
        pygame.draw.line(surface, CRATE_DARK,
                         (rx + self.w - 2, ry + 2), (rx + 2, ry + self.h - 2), 1)
        pygame.draw.rect(surface, CRATE_DARK, (rx, ry, self.w, self.h), 2)

        # Warning triangle if shaking
        if self.shake and not self.falling:
            pygame.draw.polygon(surface, ORANGE_GLOW,
                                [(rx + 16, ry - 20),
                                 (rx + 7,  ry - 5),
                                 (rx + 25, ry - 5)])
            warn = font_small.render("!", True, WHITE)
            surface.blit(warn, (rx + 13, ry - 18))


# ============================================================
#  LEVEL DATA
# ============================================================
# ============================================================
#  CHECKPOINT CLASS
# ============================================================
class Checkpoint:
    """A flag pole the player runs through to save their spot."""
    def __init__(self, x, platform_y):
        self.x          = float(x)
        self.platform_y = platform_y   # top surface of the platform it sits on
        self.pole_top   = platform_y - 55
        self.activated  = False
        self.glow       = 0            # countdown for the flash when activated

    @property
    def respawn_x(self):
        return self.x + 40            # land just to the right of the flag

    @property
    def respawn_y(self):
        return float(self.platform_y - 50)   # player.h = 50

    def update(self, player_x):
        """Activate when player walks past. Returns True on first activation."""
        if self.glow > 0:
            self.glow -= 1
        if not self.activated and player_x > self.x:
            self.activated = True
            self.glow      = 90
            return True
        return False

    def draw(self, surface, camera_x, frame):
        sx = self.x - camera_x
        if sx < -60 or sx > WIDTH + 60:
            return

        pole_bottom = self.platform_y
        pole_top    = self.pole_top

        # Pole
        pygame.draw.line(surface, METAL_GRAY,
                         (int(sx), int(pole_top)), (int(sx), int(pole_bottom)), 3)

        # Flag
        if self.activated:
            flag_color = FINISH_GREEN
            wave = math.sin(frame * 0.12) * 7
        else:
            flag_color = (160, 160, 160)
            wave = 0

        flag_pts = [
            (sx,            pole_top),
            (sx + 26 + wave, pole_top + 10),
            (sx + 26,        pole_top + 20),
            (sx,             pole_top + 20),
        ]
        pygame.draw.polygon(surface, flag_color, flag_pts)
        pygame.draw.polygon(surface, METAL_DARK if self.activated else RIVET,
                            flag_pts, 1)

        # "CP" label on the pole base
        label = font_small.render("CP", True,
                                  FINISH_GREEN if self.activated else METAL_LIGHT)
        surface.blit(label, (int(sx) - 10, int(pole_bottom) - 18))

        # Flash burst when just activated
        if self.glow > 60:
            alpha  = (self.glow - 60) * 6
            radius = (90 - self.glow) * 3 + 10
            gs = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (100, 255, 100, min(255, alpha)),
                               (radius, radius), radius)
            surface.blit(gs, (int(sx) - radius, int(pole_top) - radius))


def make_level():
    platforms = [
        # --- Easy start ---
        Platform(250, 450, 180, "girder"),
        Platform(500, 380, 160, "girder"),
        Platform(350, 300, 140, "conveyor"),
        Platform(700, 340, 180, "girder"),
        Platform(900, 280, 150, "girder"),
        # First moving platform — gentle introduction
        Platform(1080, 400, 120, "moving",
                 moves=True, x_min=980, x_max=1250, speed=1.8),
        # --- Middle section ---
        Platform(1300, 340, 140, "girder"),
        Platform(1500, 260, 180, "girder"),
        Platform(1200, 180, 120, "girder"),
        Platform(1700, 380, 200, "conveyor"),
        Platform(1900, 300, 140, "girder"),
        Platform(2050, 360, 100, "moving",
                 moves=True, x_min=1980, x_max=2200, speed=2.2),
        # --- Hard section ---
        Platform(2300, 340, 100, "conveyor"),
        Platform(2500, 260, 140, "girder"),
        Platform(2660, 360, 90, "moving",
                 moves=True, x_min=2600, x_max=2860, speed=2.8),
        Platform(2900, 300, 120, "girder"),
        Platform(3100, 200, 180, "conveyor"),
        Platform(3300, 350, 140, "girder"),
        Platform(3460, 270, 80, "moving",
                 moves=True, x_min=3400, x_max=3660, speed=3.2),
        Platform(3700, 420, 200, "girder"),
        Platform(3900, 340, 140, "conveyor"),
        Platform(4060, 240, 90, "moving",
                 moves=True, x_min=3990, x_max=4220, speed=2.5),
        Platform(4300, 380, 180, "girder"),
        Platform(4500, 300, 140, "girder"),
    ]

    coins = [
        (200, GROUND_Y - 40),
        (300, 410), (370, 410),
        (560, 340), (405, 260),
        (770, 300), (965, 240),
        (1170, 360), (1360, 300),
        (1565, 220), (1265, 140),
        (1790, 340), (1965, 260),
        (2170, 380), (2355, 300),
        (2565, 220), (2760, 340),
        (2960, 260), (3165, 160),
        (3365, 310), (3565, 240),
        (3765, 380), (3965, 300),
        (4165, 200), (4365, 340),
        (4565, 260),
    ]

    # Regular obstacles: (x, y, type)
    obstacles = [
        (450,  GROUND_Y - 30, "barrel"),
        (800,  GROUND_Y - 30, "gear"),
        (1050, GROUND_Y - 30, "barrel"),
        (1450, GROUND_Y - 30, "steam"),
        (1650, GROUND_Y - 30, "gear"),
        (2000, GROUND_Y - 30, "barrel"),
        (2250, GROUND_Y - 30, "gear"),
        (2600, GROUND_Y - 30, "steam"),
        (2850, GROUND_Y - 30, "barrel"),
        (3050, GROUND_Y - 30, "gear"),
        (3400, GROUND_Y - 30, "steam"),
        (3650, GROUND_Y - 30, "barrel"),
        (3850, GROUND_Y - 30, "gear"),
        (4050, GROUND_Y - 30, "steam"),
        (4400, GROUND_Y - 30, "barrel"),
    ]

    # Lasers: (x, y, length)
    lasers = [
        (580,  GROUND_Y - 75, 90),
        (1380, 225,            100),
        (2100, GROUND_Y - 75, 80),
        (2780, 265,            90),
        (3480, GROUND_Y - 75, 85),
        (4180, 315,            100),
    ]

    # Enemies: (x, y_top, patrol_min, patrol_max)
    enemies = [
        Enemy(740,  340 - 32, 700,  880),    # Platform(700,  340, 180)
        Enemy(1350, 340 - 32, 1300, 1440),  # Platform(1300, 340, 140)
        Enemy(1580, 260 - 32, 1500, 1680),  # Platform(1500, 260, 180)
        Enemy(2330, 340 - 32, 2300, 2400),  # Platform(2300, 340, 100)
        Enemy(2930, 300 - 32, 2900, 3020),  # Platform(2900, 300, 120)
        Enemy(3160, 200 - 32, 3100, 3280),  # Platform(3100, 200, 180)
        Enemy(3780, 420 - 32, 3700, 3900),  # Platform(3700, 420, 200)
        Enemy(4370, 380 - 32, 4300, 4480),  # Platform(4300, 380, 180)
    ]

    # Falling crates: (x, start_y)
    crates = [
        FallingCrate(760,  100),
        FallingCrate(1360, 80),
        FallingCrate(2440, 110),
        FallingCrate(3220, 75),
        FallingCrate(4010, 100),
    ]

    # Checkpoints — placed on top of solid platforms roughly every 1000 units
    checkpoints = [
        Checkpoint(920,  280),   # Platform(900,  280, 150)
        Checkpoint(1920, 300),   # Platform(1900, 300, 140)
        Checkpoint(2920, 300),   # Platform(2900, 300, 120)
        Checkpoint(3920, 340),   # Platform(3900, 340, 140)
    ]

    # Mac n cheese bowls — rare extra life pickups!
    mac_n_cheese = [
        (650,  300),   # on the high girder early on
        (1460, 210),
        (2460, 270),
        (3260, 185),
        (4110, 290),
    ]

    return platforms, coins, obstacles, lasers, enemies, crates, checkpoints, mac_n_cheese


def make_decorations():
    decorations = []
    for x in range(0, 5300, 300):
        kind = random.choice(["pipe_v", "pipe_h", "gear_bg"])
        y = random.randint(50, HEIGHT - 150)
        decorations.append((x + random.randint(0, 200), y, kind))
    return decorations


# ============================================================
#  PLAYER
# ============================================================
class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x          = 310.0   # centre of the first platform (x=250, w=180)
        self.y          = 400.0   # on top of the first platform (y=450 - h=50)
        self.w          = 28
        self.h          = 50
        self.vx         = 0.0
        self.vy         = 0.0
        self.on_ground    = False
        self.on_lava      = False
        self.jumps_left   = 2
        self.walk_timer   = 0.0
        self.facing_right = True
        self.invincible   = 0
        self.visible      = True
        self.land_timer   = 0      # counts down after landing — drives dust puff

    def respawn(self, x, y):
        self.x          = float(x)
        self.y          = float(y)
        self.vx         = 0.0
        self.vy         = 0.0
        self.on_ground  = False
        self.on_lava    = False
        self.jumps_left = 2
        self.invincible = 120
        self.land_timer = 0

    def try_jump(self):
        """Called on SPACE keydown. Returns True if a jump happened."""
        if self.jumps_left <= 0:
            return False
        if self.jumps_left == 2:
            self.vy = -13.0
            jump_sound.play()
        else:
            self.vy = -11.0        # double jump is slightly weaker
            double_jump_sound.play()
        self.on_ground   = False
        self.jumps_left -= 1
        return True

    def take_hit(self):
        """Damage the player. Returns True if the hit landed (not invincible)."""
        if self.invincible > 0:
            return False
        hurt_sound.play()
        self.invincible = 120
        self.vy = -7
        self.vx = -4 if self.facing_right else 4
        return True

    def update(self, keys, platforms):
        # Invincibility flicker
        if self.invincible > 0:
            self.invincible -= 1
            self.visible = (self.invincible // 6) % 2 == 0
        else:
            self.visible = True

        # Horizontal movement (disabled briefly right after a hit)
        if self.invincible < 100:
            self.vx = 0.0
            if keys[pygame.K_LEFT]:
                self.vx = -4.5
                self.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.vx = 4.5
                self.facing_right = True

        # Gravity
        self.vy = min(self.vy + 0.7, 15.0)

        # Horizontal move + wall
        self.x = max(0.0, self.x + self.vx)

        # Vertical move
        self.y += self.vy

        # Ground — it's lava, so flag it instead of safely landing
        self.on_ground = False
        self.on_lava   = False
        if self.y + self.h >= GROUND_Y:
            self.y         = float(GROUND_Y - self.h)
            self.vy        = 0.0
            self.on_lava   = True   # touched the lava!

        # Platforms
        p_rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
        for plat in platforms:
            pr = pygame.Rect(int(plat.x), plat.y, plat.w, 20)
            if self.vy >= 0 and p_rect.colliderect(pr):
                # Only land when coming from above
                if self.y + self.h - self.vy <= plat.y + 6:
                    self.y         = float(plat.y - self.h)
                    self.vy        = 0.0
                    self.on_ground = True
                    self.jumps_left = 2
                    self.x        += plat.dx          # ride moving platforms
                    if plat.ptype == "conveyor":
                        self.x    += 1.5

        # Landing detection — trigger dust puff
        just_landed = self.on_ground and not getattr(self, '_was_on_ground', True)
        if just_landed:
            self.land_timer = 10
        if self.land_timer > 0:
            self.land_timer -= 1
        self._was_on_ground = self.on_ground

        # Walk animation
        if self.vx != 0 and self.on_ground:
            self.walk_timer += 0.2
        else:
            self.walk_timer = 0.0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surface, camera_x):
        if not self.visible:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y)

        # Squash on landing
        squash = self.land_timer > 6
        bw = 26 if squash else 22
        bh = 18 if squash else 26
        bx = sx + self.w // 2 - bw // 2
        by = sy + self.h - bh

        # Shadow under block
        pygame.draw.ellipse(surface, (20, 20, 20),
                            (bx + 2, by + bh - 4, bw, 6))

        # Main block body
        pygame.draw.rect(surface, SHIRT, (bx, by, bw, bh), border_radius=3)
        # Top highlight
        pygame.draw.rect(surface, (120, 160, 255), (bx + 2, by + 2, bw - 4, 4), border_radius=2)
        # Bottom shadow
        pygame.draw.rect(surface, DARK_BLUE, (bx + 2, by + bh - 5, bw - 4, 4), border_radius=2)
        # Outline
        pygame.draw.rect(surface, DARK_BLUE, (bx, by, bw, bh), 2, border_radius=3)

        # Face — scared eyes when falling fast, normal otherwise
        falling_fast = self.vy > 8
        cx = bx + bw // 2
        ey = by + bh // 2 - 2
        ed = 4 if self.facing_right else -4

        # Eyes
        eye_size = 4 if falling_fast else 3
        pygame.draw.circle(surface, WHITE, (cx + ed - 3, ey), eye_size)
        pygame.draw.circle(surface, WHITE, (cx + ed + 3, ey), eye_size)
        pupil_shift = 1 if self.facing_right else -1
        pygame.draw.circle(surface, (30, 30, 30), (cx + ed - 3 + pupil_shift, ey + (1 if falling_fast else 0)), eye_size - 1)
        pygame.draw.circle(surface, (30, 30, 30), (cx + ed + 3 + pupil_shift, ey + (1 if falling_fast else 0)), eye_size - 1)
        # Eye shines
        pygame.draw.circle(surface, WHITE, (cx + ed - 2 + pupil_shift, ey - 1), 1)
        pygame.draw.circle(surface, WHITE, (cx + ed + 4 + pupil_shift, ey - 1), 1)

        # Mouth
        mx = cx + ed - 4
        my = ey + 6
        if falling_fast:
            pygame.draw.circle(surface, (30, 30, 30), (mx + 4, my + 1), 3)
        else:
            pygame.draw.arc(surface, (30, 30, 30),
                            pygame.Rect(mx, my, 9, 5), math.pi, 0, 2)

        # Landing dust puffs
        if self.land_timer > 0:
            alpha = self.land_timer * 22
            spread = (10 - self.land_timer) * 3
            for side in (-1, 1):
                ds = pygame.Surface((14, 8), pygame.SRCALPHA)
                pygame.draw.ellipse(ds, (180, 155, 130, min(255, alpha)), (0, 0, 14, 8))
                surface.blit(ds, (cx + side * (8 + spread) - 7, sy + self.h - 4))

        # Double-jump sparkles
        if not self.on_ground and self.jumps_left > 0:
            t = pygame.time.get_ticks() * 0.005
            for i in range(4):
                a = t + i * (math.pi / 2)
                sx2 = int(cx + math.cos(a) * 14)
                sy2 = int(sy + self.h - 8 + math.sin(a) * 5)
                pygame.draw.circle(surface, (120, 200, 255), (sx2, sy2), 2)


# ============================================================
#  CAT COMPANION  (5% chance to spawn — gives 20 coins!)
# ============================================================
CAT_ORANGE  = (230, 130, 40)
CAT_STRIPE  = (180, 90, 20)
CAT_BELLY   = (255, 220, 170)
CAT_EAR     = (220, 100, 120)


class Cat:
    def __init__(self, player_x, player_y):
        # Start a little ways behind the player
        self.x     = float(player_x - 80)
        self.y     = float(player_y)
        self.alive = True
        self.collected = False
        self.facing_right = True
        self.walk_timer   = 0.0
        self.blink_timer  = 0
        self.collect_flash = 0   # counts down after collected

    def update(self, player_x, player_y):
        if self.collected:
            self.collect_flash -= 1
            return

        # Target: stay ~50px behind the player
        offset = -50 if self.facing_right else 50
        target_x = player_x + offset
        target_y = player_y + 10   # sit at about foot level

        dx = target_x - self.x
        dy = target_y - self.y

        # Smoothly follow — moves at about 55% of gap per second (lazy cat pace)
        self.x += dx * 0.045
        self.y += dy * 0.07

        # Face whichever way the player is
        self.facing_right = player_x > self.x
        self.walk_timer += abs(dx) * 0.005
        self.blink_timer += 1

    def get_rect(self):
        return pygame.Rect(int(self.x) - 14, int(self.y) - 18, 28, 28)

    def draw(self, surface, camera_x, frame):
        sx = int(self.x - camera_x)
        sy = int(self.y)
        if sx < -40 or sx > WIDTH + 40:
            return

        # Collect flash (coin burst effect)
        if self.collected:
            for i in range(8):
                a = i * (math.pi / 4) + frame * 0.2
                r = (10 - self.collect_flash) * 4
                cx2 = sx + int(math.cos(a) * r)
                cy2 = sy - 10 + int(math.sin(a) * r)
                pygame.draw.circle(surface, GOLD, (cx2, cy2), 3)
            return

        flip = -1 if self.facing_right else 1

        # Tail — curved arc behind the cat
        tail_pts = []
        for i in range(10):
            t = i / 9
            tx = sx + flip * int(12 + t * 14)
            ty = sy - int(math.sin(t * math.pi) * 14) + 4
            tail_pts.append((tx, ty))
        if len(tail_pts) > 1:
            pygame.draw.lines(surface, CAT_ORANGE, False, tail_pts, 4)
            pygame.draw.circle(surface, CAT_BELLY, tail_pts[-1], 4)

        # Body
        pygame.draw.ellipse(surface, CAT_ORANGE, (sx - 14, sy - 10, 28, 22))
        # Belly patch
        pygame.draw.ellipse(surface, CAT_BELLY, (sx - 7, sy - 5, 14, 14))
        # Stripes on body
        for i, off in enumerate([-5, 1, 7]):
            pygame.draw.line(surface, CAT_STRIPE,
                             (sx + off - 1, sy - 9), (sx + off + 1, sy + 4), 2)

        # Head
        pygame.draw.circle(surface, CAT_ORANGE, (sx + flip * (-6), sy - 18), 11)

        # Ears
        for ex, ey in [(sx + flip * (-14), sy - 27), (sx + flip * (-2), sy - 28)]:
            pygame.draw.polygon(surface, CAT_ORANGE,
                                [(ex, ey), (ex - flip * 3, ey + 9), (ex + flip * 3, ey + 9)])
            pygame.draw.polygon(surface, CAT_EAR,
                                [(ex, ey + 1), (ex - flip * 2, ey + 7), (ex + flip * 2, ey + 7)])

        # Eyes — blink every ~3 seconds
        blinking = self.blink_timer % 180 < 5
        ex_base = sx + flip * (-6)
        ey_base = sy - 20
        if blinking:
            pygame.draw.line(surface, CAT_STRIPE,
                             (ex_base - 4, ey_base), (ex_base - 1, ey_base), 2)
            pygame.draw.line(surface, CAT_STRIPE,
                             (ex_base + 1, ey_base), (ex_base + 4, ey_base), 2)
        else:
            pygame.draw.circle(surface, (60, 200, 60), (ex_base - 3, ey_base), 3)
            pygame.draw.circle(surface, (60, 200, 60), (ex_base + 3, ey_base), 3)
            pygame.draw.circle(surface, (20, 20, 20), (ex_base - 3, ey_base), 2)
            pygame.draw.circle(surface, (20, 20, 20), (ex_base + 3, ey_base), 2)
            pygame.draw.circle(surface, WHITE, (ex_base - 2, ey_base - 1), 1)
            pygame.draw.circle(surface, WHITE, (ex_base + 4, ey_base - 1), 1)

        # Nose + mouth
        pygame.draw.circle(surface, (220, 100, 130), (ex_base, ey_base + 5), 2)
        pygame.draw.arc(surface, CAT_STRIPE,
                        pygame.Rect(ex_base - 4, ey_base + 5, 5, 4), math.pi, 0, 1)
        pygame.draw.arc(surface, CAT_STRIPE,
                        pygame.Rect(ex_base, ey_base + 5, 5, 4), math.pi, 0, 1)

        # Whiskers
        for wy, wx1, wx2 in [(-1, -10, -4), (1, -10, -4), (-1, 3, 9), (1, 3, 9)]:
            pygame.draw.line(surface, (220, 220, 220),
                             (ex_base + wx1, ey_base + 4 + wy),
                             (ex_base + wx2, ey_base + 4 + wy), 1)

        # Legs — two pairs, animate by walk_timer
        leg_swing = math.sin(self.walk_timer) * 4
        for lx, phase in [(sx - 8, 0), (sx - 3, math.pi),
                          (sx + 3, math.pi), (sx + 8, 0)]:
            swing = int(math.sin(self.walk_timer + phase) * 3)
            pygame.draw.line(surface, CAT_ORANGE,
                             (lx, sy + 10), (lx + swing, sy + 18), 3)
            pygame.draw.circle(surface, CAT_BELLY, (lx + swing, sy + 18), 3)

        # Little "!" sparkle above cat to tell Quincy it's special
        if frame % 60 < 30:
            pygame.draw.line(surface, GOLD,
                             (sx + flip * (-6), sy - 34),
                             (sx + flip * (-6), sy - 29), 2)
            pygame.draw.circle(surface, GOLD, (sx + flip * (-6), sy - 27), 2)


# ============================================================
#  DRAWING HELPERS
# ============================================================
def draw_background(surface, camera_x, decorations):
    surface.fill(BG_DARK)
    for dx, dy, kind in decorations:
        sx = dx - camera_x * 0.3
        if sx < -120 or sx > WIDTH + 120:
            continue
        if kind == "pipe_v":
            pygame.draw.rect(surface, PIPE_COLOR, (sx, dy, 16, 120))
            pygame.draw.rect(surface, GEAR_COLOR, (sx - 4, dy, 24, 8))
            pygame.draw.rect(surface, GEAR_COLOR, (sx - 4, dy + 112, 24, 8))
        elif kind == "pipe_h":
            pygame.draw.rect(surface, PIPE_COLOR, (sx, dy, 120, 14))
            pygame.draw.rect(surface, GEAR_COLOR, (sx, dy - 3, 8, 20))
            pygame.draw.rect(surface, GEAR_COLOR, (sx + 112, dy - 3, 8, 20))
        elif kind == "gear_bg":
            gear_r = 20
            pygame.draw.circle(surface, GEAR_COLOR, (int(sx), int(dy)), gear_r)
            pygame.draw.circle(surface, BG_DARK, (int(sx), int(dy)), 8)
            for deg in range(0, 360, 45):
                a = math.radians(deg)
                tx = sx + math.cos(a) * (gear_r + 4)
                ty = dy + math.sin(a) * (gear_r + 4)
                pygame.draw.rect(surface, GEAR_COLOR, (tx - 4, ty - 4, 8, 8))


lava_time    = 0
lava_bubbles = []   # list of [x, age, phase]


def draw_ground_floor(surface, camera_x):
    """The floor is LAVA! Bubbling, glowing, dangerous lava."""
    global lava_time, lava_bubbles
    lava_time += 1

    # Dark rock base
    pygame.draw.rect(surface, LAVA_DARK, (0, GROUND_Y + 18, WIDTH, GROUND_HEIGHT - 18))
    # Dark red mid-layer
    pygame.draw.rect(surface, LAVA_RED,  (0, GROUND_Y + 8,  WIDTH, 14))

    # Wavy lava surface
    pts = [(0, HEIGHT)]
    for x in range(0, WIDTH + 4, 4):
        wave = (math.sin(lava_time * 0.05 + (x + camera_x) * 0.007) * 5
                + math.sin(lava_time * 0.03 + (x + camera_x) * 0.004) * 3)
        pts.append((x, int(GROUND_Y + wave)))
    pts.append((WIDTH, HEIGHT))
    pygame.draw.polygon(surface, LAVA_ORANGE, pts)

    # Bright hot streaks drifting across
    for i in range(8):
        sx = int((i * 110 - (lava_time * 1.5 + camera_x * 0.5)) % WIDTH)
        wave = math.sin(lava_time * 0.06 + i * 1.3) * 3
        slen = 35 + int(math.sin(lava_time * 0.04 + i) * 12)
        pygame.draw.ellipse(surface, LAVA_YELLOW,
                            (sx - slen // 2, int(GROUND_Y + wave) - 3, slen, 6))

    # Heat glow rising from the surface
    for row in range(14):
        alpha = max(0, 90 - row * 7)
        gs = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
        gs.fill((255, 80, 0, alpha))
        surface.blit(gs, (0, GROUND_Y - row))

    # Bubbles — pop up randomly and grow then burst
    if random.random() < 0.08:
        lava_bubbles.append([random.randint(10, WIDTH - 10), 0,
                              random.uniform(0, 6.28)])
    new_bubbles = []
    for bx, age, phase in lava_bubbles:
        age += 1
        if age <= 40:
            size  = max(1, int(min(age, 40 - age) * 0.35) + 1)
            wave  = math.sin(lava_time * 0.08 + phase) * 2
            by    = int(GROUND_Y + wave)
            color = LAVA_BRIGHT if age < 15 else LAVA_YELLOW
            pygame.draw.circle(surface, color, (int(bx), by - size), size, 1)
            if age >= 37:
                pygame.draw.circle(surface, LAVA_BRIGHT,
                                   (int(bx), by - size), size + 4, 1)
            new_bubbles.append([bx, age, phase])
    lava_bubbles = new_bubbles


def draw_platform(surface, plat, camera_x):
    sx = plat.x - camera_x
    if sx + plat.w < -10 or sx > WIDTH + 10:
        return
    y, w, h = plat.y, plat.w, 20
    if plat.ptype == "moving":
        pygame.draw.rect(surface, BLUE_PLAT, (sx, y, w, h))
        pygame.draw.line(surface, BLUE_PLAT_LT, (sx, y), (sx + w, y), 2)
        pygame.draw.line(surface, RIVET, (sx, y + h), (sx + w, y + h), 2)
        # Animated arrow showing direction
        cx2 = sx + w // 2
        d   = plat.dir
        pts = [(cx2 + 10 * d, y + h // 2),
               (cx2 - 6  * d, y + 4),
               (cx2 - 6  * d, y + h - 4)]
        pygame.draw.polygon(surface, BLUE_PLAT_LT, pts)
        for rx in range(int(sx) + 10, int(sx + w) - 5, 30):
            pygame.draw.circle(surface, RIVET, (rx, y + 5), 3)
    elif plat.ptype == "girder":
        pygame.draw.rect(surface, METAL_GRAY, (sx, y, w, h))
        pygame.draw.line(surface, METAL_LIGHT, (sx, y), (sx + w, y), 2)
        pygame.draw.line(surface, RIVET, (sx, y + h), (sx + w, y + h), 2)
        for rx in range(int(sx) + 10, int(sx + w) - 5, 30):
            pygame.draw.circle(surface, RIVET, (rx, y + 5), 3)
            pygame.draw.circle(surface, METAL_LIGHT, (rx - 1, y + 4), 1)
            pygame.draw.circle(surface, RIVET, (rx, y + h - 5), 3)
        pygame.draw.line(surface, RIVET, (sx + 2, y + 2), (sx + w - 2, y + h - 2), 1)
        pygame.draw.line(surface, RIVET, (sx + 2, y + h - 2), (sx + w - 2, y + 2), 1)
    else:  # conveyor
        pygame.draw.rect(surface, (60, 60, 65), (sx, y, w, h))
        pygame.draw.rect(surface, METAL_GRAY, (sx, y, w, h), 2)
        for rx in range(int(sx) + 8, int(sx + w) - 4, 16):
            pygame.draw.line(surface, (90, 90, 95), (rx, y + 3), (rx + 6, y + h - 3), 2)
        ax = sx + w // 2
        pygame.draw.polygon(surface, ORANGE_GLOW,
                            [(ax + 8, y + h // 2),
                             (ax - 2, y + 4),
                             (ax - 2, y + h - 4)])


def draw_coin(surface, x, y, camera_x, frame):
    sx = x - camera_x
    if sx < -20 or sx > WIDTH + 20:
        return
    hw = max(2, int(abs(math.sin(frame * 0.08)) * 10))
    pygame.draw.ellipse(surface, GOLD, (sx - hw, y - 10, hw * 2, 20))
    if hw > 4:
        pygame.draw.ellipse(surface, GOLD_DARK,
                            (sx - hw + 3, y - 7, hw * 2 - 6, 14), 2)
    if frame % 30 < 5:
        pygame.draw.line(surface, WHITE, (sx - 3, y - 14), (sx + 3, y - 14), 1)
        pygame.draw.line(surface, WHITE, (sx, y - 17), (sx, y - 11), 1)


def draw_mac_n_cheese(surface, x, y, camera_x, frame):
    sx = int(x - camera_x)
    if sx < -30 or sx > WIDTH + 30:
        return
    # Gentle bob up and down
    bob = int(math.sin(frame * 0.05) * 3)
    sy = y + bob

    # Bowl body (light gray)
    pygame.draw.ellipse(surface, (210, 210, 215), (sx - 16, sy + 10, 32, 16))
    # Bowl rim highlight
    pygame.draw.ellipse(surface, WHITE, (sx - 16, sy + 9, 32, 8))
    # Bowl outline
    pygame.draw.ellipse(surface, (150, 150, 155), (sx - 16, sy + 10, 32, 16), 2)

    # Cheesy filling (orange/yellow blob)
    pygame.draw.ellipse(surface, (255, 170, 30), (sx - 13, sy + 2, 26, 14))
    pygame.draw.ellipse(surface, (255, 210, 60), (sx - 10, sy + 3, 20, 9))

    # Little macaroni pieces (tiny C-shaped arcs)
    for px, py, rot in [(-6, 6, 0), (3, 4, 1), (-2, 9, 2), (5, 9, 3)]:
        arc_rect = pygame.Rect(sx + px - 3, sy + py - 3, 8, 6)
        start_a = rot * (math.pi / 2)
        pygame.draw.arc(surface, (220, 120, 10), arc_rect,
                        start_a, start_a + math.pi, 3)

    # Sparkle to make it look tempting
    if frame % 40 < 8:
        pygame.draw.line(surface, WHITE, (sx, sy - 5), (sx, sy - 10), 1)
        pygame.draw.line(surface, WHITE, (sx - 4, sy - 3), (sx + 4, sy - 3), 1)


def draw_obstacle(surface, x, y, otype, camera_x, frame):
    sx = x - camera_x
    if sx < -50 or sx > WIDTH + 50:
        return
    if otype == "barrel":
        pygame.draw.ellipse(surface, BARREL_BROWN, (sx - 15, y - 8, 30, 38))
        pygame.draw.rect(surface, BARREL_STRIPE, (sx - 15, y + 2, 30, 5))
        pygame.draw.rect(surface, BARREL_STRIPE, (sx - 15, y + 16, 30, 5))
        pygame.draw.line(surface, ORANGE_GLOW, (sx - 6, y + 6), (sx + 6, y + 14), 2)
        pygame.draw.line(surface, ORANGE_GLOW, (sx + 6, y + 6), (sx - 6, y + 14), 2)
    elif otype == "gear":
        r = 18
        ao = frame * 2
        pygame.draw.circle(surface, ORANGE_GLOW, (int(sx), int(y)), r)
        pygame.draw.circle(surface, BG_DARK, (int(sx), int(y)), 6)
        for i in range(8):
            a  = math.radians(ao + i * 45)
            tx = sx + math.cos(a) * (r + 3)
            ty = y  + math.sin(a) * (r + 3)
            pygame.draw.rect(surface, ORANGE_GLOW, (tx - 4, ty - 4, 8, 8))
    elif otype == "steam":
        pygame.draw.rect(surface, METAL_GRAY, (sx - 10, y + 10, 20, 20))
        pygame.draw.rect(surface, (50, 55, 60), (sx - 6, y + 10, 12, 4))
        phase = (frame % 60) / 60.0
        if phase < 0.7:
            for i in range(3):
                py_off = int(phase * 40 + i * 15)
                pr     = 6 + i * 2
                af     = max(0, 1 - py_off / 60)
                color  = tuple(int(c * af + BG_DARK[j] * (1 - af))
                               for j, c in enumerate(STEAM_WHITE))
                pygame.draw.circle(surface, color,
                                   (int(sx + math.sin(frame * 0.1 + i) * 4),
                                    int(y + 5 - py_off)), pr)


def get_obstacle_rect(x, y, otype):
    if otype == "barrel":
        return pygame.Rect(x - 12, y - 5, 24, 35)
    elif otype == "gear":
        return pygame.Rect(x - 16, y - 16, 32, 32)
    elif otype == "steam":
        return pygame.Rect(x - 6, y - 20, 12, 30)
    return pygame.Rect(x - 10, y - 10, 20, 20)


def draw_laser(surface, x, y, length, camera_x, frame):
    """Blinking horizontal laser beam."""
    sx = x - camera_x
    if sx + length < -20 or sx > WIDTH + 20:
        return

    on = (frame % 60) < 40

    # Emitter boxes at both ends (always visible)
    for ex in (sx, sx + length):
        pygame.draw.rect(surface, METAL_GRAY, (ex - 8, y - 8, 16, 16))
        pygame.draw.circle(surface, LASER_RED if on else RIVET,
                           (int(ex), int(y)), 5)

    if on:
        # Glowing beam layers
        for glow in range(5, 0, -1):
            alpha = 35 * glow
            gs = pygame.Surface((int(length), glow * 4), pygame.SRCALPHA)
            gs.fill((255, 30, 30, alpha))
            surface.blit(gs, (sx, y - glow * 2))
        # Core
        pygame.draw.line(surface, (255, 60, 60),  (sx, y), (sx + length, y), 3)
        pygame.draw.line(surface, (255, 200, 200), (sx, y), (sx + length, y), 1)


def laser_is_on(frame):
    return (frame % 60) < 40


def get_laser_rect(x, y, length):
    return pygame.Rect(x, y - 5, length, 10)


def draw_finish_line(surface, camera_x, frame):
    sx = LEVEL_END_X - camera_x
    if sx < -80 or sx > WIDTH + 80:
        return

    # Checkered pole
    for i in range(0, GROUND_Y, 20):
        color = WHITE if (i // 20) % 2 == 0 else (60, 60, 60)
        pygame.draw.rect(surface, color, (sx - 4, i, 8, 20))

    # Waving flag
    wave = math.sin(frame * 0.1) * 8
    pts  = [
        (sx + 4,      30),
        (sx + 34 + wave,  45),
        (sx + 64,     32 + wave * 0.5),
        (sx + 34 + wave * 0.5, 55),
        (sx + 4,      60),
    ]
    pygame.draw.polygon(surface, FINISH_GREEN, pts)
    pygame.draw.polygon(surface, (30, 180, 60), pts, 2)

    # "FINISH!" label
    label = font_med.render("FINISH!", True, GOLD)
    surface.blit(label, (sx - label.get_width() // 2, 68))


def draw_hud(surface, score, high_score, lives):
    # Coin + score
    pygame.draw.circle(surface, GOLD, (30, 30), 12)
    pygame.draw.circle(surface, GOLD_DARK, (30, 30), 9, 2)
    surface.blit(font_med.render(f"x {score}", True, WHITE), (48, 14))

    # Lives as red hearts
    for i in range(lives):
        hx = WIDTH - 36 - i * 32
        hy = 22
        # Simple heart from two circles + triangle
        pygame.draw.circle(surface, HEART_RED, (hx - 5, hy - 3), 7)
        pygame.draw.circle(surface, HEART_RED, (hx + 5, hy - 3), 7)
        pygame.draw.polygon(surface, HEART_RED,
                            [(hx - 11, hy + 1), (hx + 11, hy + 1), (hx, hy + 14)])

    # Best score (center top)
    hs = font_small.render(f"Best: {high_score}", True, METAL_LIGHT)
    surface.blit(hs, (WIDTH // 2 - hs.get_width() // 2, 10))


def draw_game_over(surface, score, high_score):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    surface.blit(ov, (0, 0))

    surface.blit(font_big.render("GAME OVER", True, ORANGE_GLOW),
                 font_big.render("GAME OVER", True, ORANGE_GLOW)
                 .get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))
    surface.blit(font_med.render(f"Coins: {score}", True, GOLD),
                 font_med.render(f"Coins: {score}", True, GOLD)
                 .get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    label = ("NEW BEST!", (100, 255, 100)) if score >= high_score \
            else (f"Best: {high_score}", METAL_LIGHT)
    surface.blit(font_med.render(label[0], True, label[1]),
                 font_med.render(label[0], True, label[1])
                 .get_rect(center=(WIDTH // 2, HEIGHT // 2 + 48)))
    surface.blit(font_small.render("Press SPACE to play again", True, WHITE),
                 font_small.render("Press SPACE to play again", True, WHITE)
                 .get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))


def draw_win_screen(surface, score, high_score, frame):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    surface.blit(ov, (0, 0))

    # Pulsing YOU WIN!
    p     = abs(math.sin(frame * 0.08))
    color = (int(80 + 175 * p), int(200 + 55 * p), 50)
    win   = font_big.render("YOU WIN!", True, color)
    shadow = font_big.render("YOU WIN!", True, BLACK)
    cx2   = WIDTH // 2
    surface.blit(shadow, shadow.get_rect(center=(cx2 + 3, HEIGHT // 2 - 80)))
    surface.blit(win,    win.get_rect(center=(cx2, HEIGHT // 2 - 83)))

    surface.blit(font_med.render(f"Coins collected: {score}", True, GOLD),
                 font_med.render(f"Coins collected: {score}", True, GOLD)
                 .get_rect(center=(cx2, HEIGHT // 2 - 10)))
    label = ("NEW BEST!", (100, 255, 100)) if score >= high_score \
            else (f"Best: {high_score}", METAL_LIGHT)
    surface.blit(font_med.render(label[0], True, label[1]),
                 font_med.render(label[0], True, label[1])
                 .get_rect(center=(cx2, HEIGHT // 2 + 36)))
    surface.blit(font_small.render("Press SPACE to play again", True, WHITE),
                 font_small.render("Press SPACE to play again", True, WHITE)
                 .get_rect(center=(cx2, HEIGHT // 2 + 92)))

    # Confetti
    random.seed(frame // 4)
    for _ in range(22):
        pygame.draw.circle(surface,
                           (random.randint(100, 255),
                            random.randint(100, 255),
                            random.randint(50, 255)),
                           (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                           random.randint(2, 5))
    random.seed()


# ============================================================
#  HIGH SCORE
# ============================================================
SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "factory_highscore.txt")


def load_high_score():
    try:
        with open(SCORE_FILE) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    with open(SCORE_FILE, "w") as f:
        f.write(str(score))


# ============================================================
#  MAIN
# ============================================================
def new_game():
    platforms, coins, obstacles, lasers, enemies, crates, checkpoints, mac_n_cheese = make_level()
    return {
        "player":          Player(),
        "platforms":       platforms,
        "coins":           coins,
        "coins_alive":     [True] * len(coins),
        "obstacles":       obstacles,
        "lasers":          lasers,
        "enemies":         enemies,
        "crates":          crates,
        "checkpoints":     checkpoints,
        "last_checkpoint": None,       # most recent activated checkpoint
        "decorations":     make_decorations(),
        "mac_n_cheese":    mac_n_cheese,
        "mac_alive":       [True] * len(mac_n_cheese),
        "cat":             Cat(310.0, 400.0) if random.random() < 0.05 else None,
        "score":           0,
        "lives":           3,
        "game_over":       False,
        "won":             False,
    }


def main():
    high_score = load_high_score()
    g = new_game()
    frame = 0

    running = True
    while running:
        frame += 1

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    if g["game_over"] or g["won"]:
                        g = new_game()
                        frame = 0
                    else:
                        g["player"].try_jump()

        player     = g["player"]
        platforms  = g["platforms"]
        coins      = g["coins"]
        coins_alive = g["coins_alive"]
        obstacles  = g["obstacles"]
        lasers     = g["lasers"]
        enemies     = g["enemies"]
        crates      = g["crates"]
        checkpoints = g["checkpoints"]

        if not g["game_over"] and not g["won"]:
            # --- Update ---
            for plat in platforms:
                plat.update()

            keys = pygame.key.get_pressed()
            player.update(keys, platforms)

            camera_x = max(0, player.x - WIDTH // 3)

            # Checkpoints
            for cp in checkpoints:
                if cp.update(player.x):
                    g["last_checkpoint"] = cp
                    checkpoint_sound.play()

            # Win condition
            if player.x >= LEVEL_END_X:
                g["won"] = True
                win_sound.play()
                if g["score"] > high_score:
                    high_score = g["score"]
                    save_high_score(high_score)

            # Coin collection
            p_rect = player.get_rect()
            for i, (cx2, cy) in enumerate(coins):
                if coins_alive[i] and \
                   p_rect.colliderect(pygame.Rect(cx2 - 10, cy - 10, 20, 20)):
                    coins_alive[i] = False
                    g["score"] += 1
                    coin_sound.play()

            # Mac n cheese collection — extra life!
            for i, (mx, my) in enumerate(g["mac_n_cheese"]):
                if g["mac_alive"][i] and \
                   p_rect.colliderect(pygame.Rect(mx - 16, my, 32, 26)):
                    g["mac_alive"][i] = False
                    g["lives"] = min(g["lives"] + 1, 9)
                    oneup_sound.play()

            # Lucky cat — follows you and gives 20 coins when touched!
            cat = g["cat"]
            if cat is not None:
                cat.update(player.x, player.y)
                if not cat.collected and p_rect.colliderect(cat.get_rect()):
                    cat.collected    = True
                    cat.collect_flash = 10
                    g["score"]       += 20
                    meow_sound.play()
                if cat.collected and cat.collect_flash <= 0:
                    g["cat"] = None   # fully gone after flash

            def hurt_player():
                """Deduct a life. Game over if none left."""
                nonlocal high_score
                if player.take_hit():
                    g["lives"] -= 1
                    if g["lives"] <= 0:
                        g["game_over"] = True
                        game_over_sound.play()
                        if g["score"] > high_score:
                            high_score = g["score"]
                            save_high_score(high_score)
                    else:
                        # Respawn at last checkpoint, or the very start
                        cp = g["last_checkpoint"]
                        if cp is not None:
                            player.respawn(cp.respawn_x, cp.respawn_y)
                        else:
                            player.respawn(310.0, 400.0)  # first platform

            # Regular obstacle collisions
            for ox, oy, otype in obstacles:
                if player.get_rect().inflate(-8, -8).colliderect(
                        get_obstacle_rect(ox, oy, otype)):
                    hurt_player()

            # Laser collisions
            if laser_is_on(frame):
                for lx, ly, ll in lasers:
                    if player.get_rect().inflate(-6, -6).colliderect(
                            get_laser_rect(lx, ly, ll)):
                        hurt_player()

            # Enemy collisions
            for enemy in enemies:
                if not enemy.alive:
                    continue
                enemy.update()
                e_rect = enemy.get_rect()
                p_rect = player.get_rect()
                if p_rect.colliderect(e_rect):
                    # Stomp: player falling and feet were above enemy head
                    if (player.vy > 1 and
                            player.y + player.h - player.vy <= e_rect.top + 12):
                        enemy.alive  = False
                        player.vy    = -10.0   # satisfying bounce!
                        g["score"] += 2
                        stomp_sound.play()
                    else:
                        hurt_player()

            # Falling crate collisions
            for crate in crates:
                crate.update(player.x)
                if crate.falling and \
                   player.get_rect().inflate(-6, -6).colliderect(crate.get_rect()):
                    hurt_player()

            # Touched the lava floor
            if player.on_lava:
                hurt_player()

            # Fell off the bottom of the screen
            if player.y > HEIGHT + 60:
                g["lives"] -= 1
                hurt_sound.play()
                if g["lives"] <= 0:
                    g["game_over"] = True
                    game_over_sound.play()
                    if g["score"] > high_score:
                        high_score = g["score"]
                        save_high_score(high_score)
                else:
                    cp = g["last_checkpoint"]
                    if cp is not None:
                        player.respawn(cp.respawn_x, cp.respawn_y)
                    else:
                        player.respawn(310.0, 400.0)

        else:
            camera_x = max(0, player.x - WIDTH // 3)

        # --- Draw ---
        draw_background(screen, camera_x, g["decorations"])
        draw_ground_floor(screen, camera_x)

        for plat in platforms:
            draw_platform(screen, plat, camera_x)

        for i, (cx2, cy) in enumerate(coins):
            if coins_alive[i]:
                draw_coin(screen, cx2, cy, camera_x, frame)

        for i, (mx, my) in enumerate(g["mac_n_cheese"]):
            if g["mac_alive"][i]:
                draw_mac_n_cheese(screen, mx, my, camera_x, frame)

        for ox, oy, otype in obstacles:
            draw_obstacle(screen, ox, oy, otype, camera_x, frame)

        for lx, ly, ll in lasers:
            draw_laser(screen, lx, ly, ll, camera_x, frame)

        for crate in crates:
            crate.draw(screen, camera_x)

        for enemy in enemies:
            if enemy.alive:
                enemy.draw(screen, camera_x, player.x)

        for cp in checkpoints:
            cp.draw(screen, camera_x, frame)

        draw_finish_line(screen, camera_x, frame)
        if g["cat"] is not None:
            g["cat"].draw(screen, camera_x, frame)
        player.draw(screen, camera_x)
        draw_hud(screen, g["score"], high_score, g["lives"])

        if g["game_over"]:
            draw_game_over(screen, g["score"], high_score)
        elif g["won"]:
            draw_win_screen(screen, g["score"], high_score, frame)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
