import pygame
import random
import math
import sys
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Office Chaos – Clean Edition")
clock = pygame.time.Clock()

# =====================
# FILE PATHS
# =====================
# Figure out where the script is located,
# then build paths to the assets and sounds folders.
BASE = os.path.dirname(__file__)
ASSETS = os.path.join(BASE, "assets")
SOUNDS = os.path.join(ASSETS, "sounds")

# =====================
# LOAD & RESIZE ASSETS
# =====================
# Helper function so we don’t repeat scaling logic everywhere.
def load_scaled(path, size):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, size)

# Standard sizes so everything looks consistent
CHAIR_SIZE = (70, 70)
MANAGER_SIZE = (95, 95)
ITEM_SIZE = (45, 45)

# Load images
chair_img = load_scaled(os.path.join(ASSETS, "chair.png"), CHAIR_SIZE)
manager_img = load_scaled(os.path.join(ASSETS, "manager.png"), MANAGER_SIZE)
coffee_img = load_scaled(os.path.join(ASSETS, "coffee.png"), ITEM_SIZE)
email_img = load_scaled(os.path.join(ASSETS, "email.png"), ITEM_SIZE)
duck_img = load_scaled(os.path.join(ASSETS, "rubber_duck.png"), ITEM_SIZE)

# Load sounds
coffee_sound = pygame.mixer.Sound(os.path.join(SOUNDS, "coffee.wav"))
email_sound = pygame.mixer.Sound(os.path.join(SOUNDS, "email.wav"))
duck_sound = pygame.mixer.Sound(os.path.join(SOUNDS, "rubber_duck.wav"))
manager_sound = pygame.mixer.Sound(os.path.join(SOUNDS, "manager.wav"))

font = pygame.font.SysFont("arial", 26)

# =====================
# BACKGROUND (procedurally drawn)
# =====================
# Instead of using a static image,
# we draw a soft gradient + grid for a clean office vibe.
def draw_background(surface):
    top_color = (240, 244, 255)
    bottom_color = (255, 240, 248)

    # Vertical gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = top_color[0] * (1 - ratio) + bottom_color[0] * ratio
        g = top_color[1] * (1 - ratio) + bottom_color[1] * ratio
        b = top_color[2] * (1 - ratio) + bottom_color[2] * ratio
        pygame.draw.line(surface, (int(r), int(g), int(b)), (0, y), (WIDTH, y))

    # Subtle grid to give it a “floor tiles” feel
    grid_color = (210, 215, 235)
    grid_size = 80

    for x in range(0, WIDTH, grid_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, HEIGHT), 1)

    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(surface, grid_color, (0, y), (WIDTH, y), 1)

    # Soft glow in the corners for extra polish
    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pygame.draw.circle(glow, (255, 200, 220, 40), (0, 0), 300)
    pygame.draw.circle(glow, (200, 255, 220, 40), (WIDTH, 0), 300)
    pygame.draw.circle(glow, (220, 220, 255, 40), (0, HEIGHT), 300)
    pygame.draw.circle(glow, (255, 240, 200, 40), (WIDTH, HEIGHT), 300)

    surface.blit(glow, (0, 0))

# =====================
# PLAYER (The Office Chair)
# =====================
class Player:
    def __init__(self):
        # Start in the middle of the screen
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

        # Movement physics
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 0.6          # acceleration strength
        self.friction = 0.90      # makes movement feel smooth
        self.max_speed = 7
        self.dash_power = 15
        self.dash_cd = 0          # dash cooldown timer
        self.angle = 0            # rotation angle
        self.freeze_timer = 0     # used when manager catches you

    def update(self):
        # If frozen (performance review...), don’t move
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            return

        keys = pygame.key.get_pressed()

        # Basic movement input
        if keys[pygame.K_LEFT]:
            self.vel_x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.vel_x += self.speed
        if keys[pygame.K_UP]:
            self.vel_y -= self.speed
        if keys[pygame.K_DOWN]:
            self.vel_y += self.speed

        # Dash mechanic (spacebar)
        if keys[pygame.K_SPACE] and self.dash_cd <= 0:
            direction = pygame.math.Vector2(self.vel_x, self.vel_y)
            if direction.length() > 0:
                direction = direction.normalize()
                self.vel_x += direction.x * self.dash_power
                self.vel_y += direction.y * self.dash_power
                self.dash_cd = 60  # 1 second cooldown at 60 FPS

        self.dash_cd -= 1

        # Clamp max speed so it doesn’t go crazy
        speed = math.hypot(self.vel_x, self.vel_y)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vel_x *= scale
            self.vel_y *= scale

        # Apply movement
        self.x += self.vel_x
        self.y += self.vel_y

        # Apply friction for smooth deceleration
        self.vel_x *= self.friction
        self.vel_y *= self.friction

        # Keep player inside screen bounds
        self.x = max(50, min(WIDTH - 50, self.x))
        self.y = max(50, min(HEIGHT - 50, self.y))

        # Rotate chair to match movement direction
        if speed > 0.1:
            self.angle = math.degrees(math.atan2(-self.vel_y, self.vel_x))

    def draw(self):
        rotated = pygame.transform.rotate(chair_img, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)

# =====================
# MANAGER (The Boss That Hunts You)
# =====================
class Manager:
    def __init__(self):
        # Spawn somewhere random (not too close to edges)
        self.x = random.randint(100, WIDTH-100)
        self.y = random.randint(100, HEIGHT-100)
        self.speed = 2.2

    def update(self, player):
        # Move toward the player if close enough
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 300:  # detection radius
            if dist != 0:
                self.x += dx/dist * self.speed
                self.y += dy/dist * self.speed

    def draw(self):
        rect = manager_img.get_rect(center=(self.x, self.y))
        screen.blit(manager_img, rect)

# =====================
# ITEMS (Coffee, Ducks, Emails)
# =====================
class Item:
    def __init__(self, kind):
        self.kind = kind
        self.x = random.randint(60, WIDTH-60)
        self.y = random.randint(60, HEIGHT-60)

    def draw(self):
        # Pick the right image depending on item type
        if self.kind == "coffee":
            rect = coffee_img.get_rect(center=(self.x, self.y))
            screen.blit(coffee_img, rect)
        elif self.kind == "email":
            rect = email_img.get_rect(center=(self.x, self.y))
            screen.blit(email_img, rect)
        elif self.kind == "duck":
            rect = duck_img.get_rect(center=(self.x, self.y))
            screen.blit(duck_img, rect)

# =====================
# GAME SETUP
# =====================
player = Player()
manager = Manager()
items = []
MAX_ITEMS = 8
score = 0

# Keep the office filled with items
def spawn_items():
    while len(items) < MAX_ITEMS:
        kind = random.choices(
            ["coffee", "duck", "email"],
            weights=[6, 3, 2],  # coffee most common
            k=1
        )[0]
        items.append(Item(kind))

# =====================
# MAIN GAME LOOP
# =====================
running = True
while running:
    clock.tick(60)  # lock at 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update()
    manager.update(player)
    spawn_items()

    # Check if player collects an item
    for item in items[:]:
        if math.hypot(player.x-item.x, player.y-item.y) < 40:
            if item.kind == "coffee":
                score += 5
                coffee_sound.play()
            elif item.kind == "duck":
                score += 10
                duck_sound.play()
            elif item.kind == "email":
                score -= 3
                email_sound.play()
            items.remove(item)

    # If manager catches you → penalty + freeze
    if math.hypot(player.x-manager.x, player.y-manager.y) < 60:
        manager_sound.play()
        score -= 15
        player.freeze_timer = 120  # 2 seconds freeze
        manager.x = random.randint(100, WIDTH-100)
        manager.y = random.randint(100, HEIGHT-100)

    # Draw everything
    draw_background(screen)

    for item in items:
        item.draw()

    manager.draw()
    player.draw()

    score_text = font.render(f"Score: {score}", True, (40, 40, 40))
    screen.blit(score_text, (20, 20))

    if player.freeze_timer > 0:
        freeze_text = font.render("PERFORMANCE REVIEW 😡", True, (200, 0, 0))
        screen.blit(freeze_text, (WIDTH//2 - 170, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()