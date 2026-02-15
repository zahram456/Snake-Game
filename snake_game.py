import pygame
import random
import sys
import os
import math
# python "d:/My projects/Snake game/snake_game.py"

# ---------------- INITIALIZATION ----------------
pygame.init()

WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 20
MIN_WIDTH, MIN_HEIGHT = 640, 480
HIGH_SCORE_FILE = "high_score.txt"
POWERUP_DURATION = 6.0
POWERUP_SPAWN_SCORE_STEP = 70

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

# Colors (bright yellow theme)
WHITE = (250, 248, 230)
BLACK = (18, 16, 8)
YELLOW = (255, 218, 90)
YELLOW_DARK = (200, 160, 40)
ORANGE = (255, 170, 60)
ORANGE_DARK = (210, 120, 40)
BLUE = (90, 140, 210)
BG_DARK = (36, 30, 10)
BG_LIGHT = (52, 44, 18)
BG_MID = (70, 58, 22)
GRID = (84, 72, 30)
ACCENT = (255, 230, 120)
POWERUP_COLORS = {
    "slow": (120, 200, 255),
    "magnet": (255, 180, 120),
    "shield": (200, 255, 150),
    "double": (255, 240, 120),
}

# Fonts
font = pygame.font.SysFont("arial", 30)
big_font = pygame.font.SysFont("arial", 60)

# ---------------- FUNCTIONS ----------------
def draw_text(text, font, color, x, y):
    screen.blit(font.render(text, True, color), (x, y))

def draw_centered(text, font, color, y):
    surface = font.render(text, True, color)
    x = (WIDTH - surface.get_width()) // 2
    screen.blit(surface, (x, y))

def draw_background():
    # Gradient base
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        r = int(BG_DARK[0] * (1 - t) + BG_MID[0] * t)
        g = int(BG_DARK[1] * (1 - t) + BG_MID[1] * t)
        b = int(BG_DARK[2] * (1 - t) + BG_MID[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Soft diagonal grid lines
    for x in range(-HEIGHT, WIDTH, 50):
        pygame.draw.line(screen, BG_LIGHT, (x, 0), (x + HEIGHT, HEIGHT), 1)

    # Floating nodes
    for i in range(0, WIDTH, 140):
        pygame.draw.circle(screen, GRID, (i, (i * 3) % HEIGHT), 18, 1)

    # Subtle vignette
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (0, 0, 0, 70), (0, 0, WIDTH, HEIGHT), border_radius=24)
    screen.blit(vignette, (0, 0))

def draw_button(rect, label, is_active=False, is_hover=False):
    bg = (32, 46, 68)
    if is_active:
        bg = (48, 80, 120)
    if is_hover:
        bg = (60, 92, 140)
    pygame.draw.rect(screen, bg, rect, border_radius=8)
    pygame.draw.rect(screen, ACCENT, rect, 2, border_radius=8)
    text_surface = font.render(label, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_grid():
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

def draw_border():
    pygame.draw.rect(screen, ACCENT, (0, 0, WIDTH, HEIGHT), 3)

def draw_panel(rect, title=None, title_offset=0):
    pygame.draw.rect(screen, (20, 30, 46), rect, border_radius=12)
    pygame.draw.rect(screen, ACCENT, rect, 2, border_radius=12)
    if title:
        title_surface = font.render(title, True, ACCENT)
        title_rect = title_surface.get_rect(midtop=(rect.centerx, rect.top + 10 + title_offset))
        screen.blit(title_surface, title_rect)

def draw_snake(snake, t):
    if not snake:
        return
    head = snake[0]
    neck = snake[1] if len(snake) > 1 else (head[0] - BLOCK_SIZE, head[1])
    dx = head[0] - neck[0]
    dy = head[1] - neck[1]
    if dx == 0 and dy == 0:
        dx, dy = BLOCK_SIZE, 0
    # Normalize to unit direction (-1, 0, 1)
    dir_x = 0 if dx == 0 else int(dx / abs(dx))
    dir_y = 0 if dy == 0 else int(dy / abs(dy))

    # Head glow
    glow = pygame.Surface((BLOCK_SIZE * 2, BLOCK_SIZE * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 210, 80, 120), (BLOCK_SIZE, BLOCK_SIZE), BLOCK_SIZE)
    screen.blit(glow, (head[0] - BLOCK_SIZE // 2, head[1] - BLOCK_SIZE // 2))
    pygame.draw.rect(screen, YELLOW, (*head, BLOCK_SIZE, BLOCK_SIZE), border_radius=10)
    pygame.draw.rect(screen, YELLOW_DARK, (*head, BLOCK_SIZE, BLOCK_SIZE), 2, border_radius=10)

    # Eyes
    eye_offset_x = 5 * dir_x
    eye_offset_y = 5 * dir_y
    eye_base_x = head[0] + BLOCK_SIZE // 2 + eye_offset_x
    eye_base_y = head[1] + BLOCK_SIZE // 2 + eye_offset_y
    eye_side_dx = -dir_y * 5
    eye_side_dy = dir_x * 5
    pygame.draw.circle(screen, WHITE, (eye_base_x + eye_side_dx, eye_base_y + eye_side_dy), 3)
    pygame.draw.circle(screen, WHITE, (eye_base_x - eye_side_dx, eye_base_y - eye_side_dy), 3)
    pygame.draw.circle(screen, BLACK, (eye_base_x + eye_side_dx, eye_base_y + eye_side_dy), 1)
    pygame.draw.circle(screen, BLACK, (eye_base_x - eye_side_dx, eye_base_y - eye_side_dy), 1)

    # Tongue (flicker)
    if int(t * 6) % 2 == 0:
        tongue_len = 8
        tongue_x = head[0] + BLOCK_SIZE // 2 + dir_x * (BLOCK_SIZE // 2)
        tongue_y = head[1] + BLOCK_SIZE // 2 + dir_y * (BLOCK_SIZE // 2)
        tip_x = tongue_x + dir_x * tongue_len
        tip_y = tongue_y + dir_y * tongue_len
        pygame.draw.line(screen, ORANGE_DARK, (tongue_x, tongue_y), (tip_x, tip_y), 2)
        # Forked tip
        pygame.draw.line(screen, ORANGE_DARK, (tip_x, tip_y), (tip_x - dir_y * 3, tip_y + dir_x * 3), 2)
        pygame.draw.line(screen, ORANGE_DARK, (tip_x, tip_y), (tip_x + dir_y * 3, tip_y - dir_x * 3), 2)

    # Body with scale pattern
    for i, segment in enumerate(snake[1:], start=1):
        wiggle = int(2 * math.sin(t * 5 + i * 0.6))
        sx, sy = segment
        seg_rect = (sx + wiggle, sy - wiggle, BLOCK_SIZE, BLOCK_SIZE)
        shade = (YELLOW_DARK if i % 2 == 0 else YELLOW)
        pygame.draw.rect(screen, shade, seg_rect, border_radius=10)
        pygame.draw.rect(screen, YELLOW_DARK, seg_rect, 1, border_radius=10)
        # Scales
        scale_r = 3
        for ox, oy in ((6, 6), (14, 8), (10, 14)):
            pygame.draw.circle(screen, BG_LIGHT, (sx + wiggle + ox, sy - wiggle + oy), scale_r, 1)

def draw_food(food, t):
    cx = food[0] + BLOCK_SIZE // 2
    cy = food[1] + BLOCK_SIZE // 2
    pulse = 1.0 + 0.1 * math.sin(t * 6)
    radius = int((BLOCK_SIZE // 2 - 2) * pulse)
    # Glow
    glow = pygame.Surface((BLOCK_SIZE * 3, BLOCK_SIZE * 3), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 190, 80, 120), (BLOCK_SIZE * 3 // 2, BLOCK_SIZE * 3 // 2), BLOCK_SIZE)
    screen.blit(glow, (cx - BLOCK_SIZE * 3 // 2, cy - BLOCK_SIZE * 3 // 2))
    pygame.draw.circle(screen, ORANGE, (cx, cy), radius)
    # Orbiting sparkle
    orbit = int(BLOCK_SIZE * 0.55)
    sx = int(cx + orbit * math.cos(t * 5))
    sy = int(cy + orbit * math.sin(t * 5))
    pygame.draw.circle(screen, WHITE, (sx, sy), max(2, radius // 4))
    pygame.draw.circle(screen, WHITE, (cx - 3, cy - 3), max(2, radius // 3))

def draw_powerup(powerup, t):
    if not powerup:
        return
    kind, pos = powerup["kind"], powerup["pos"]
    cx = pos[0] + BLOCK_SIZE // 2
    cy = pos[1] + BLOCK_SIZE // 2
    pulse = 1.0 + 0.15 * math.sin(t * 6 + 1.2)
    radius = int((BLOCK_SIZE // 2 - 3) * pulse)
    color = POWERUP_COLORS.get(kind, WHITE)
    glow = pygame.Surface((BLOCK_SIZE * 3, BLOCK_SIZE * 3), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, 110), (BLOCK_SIZE * 3 // 2, BLOCK_SIZE * 3 // 2), BLOCK_SIZE)
    screen.blit(glow, (cx - BLOCK_SIZE * 3 // 2, cy - BLOCK_SIZE * 3 // 2))
    pygame.draw.circle(screen, color, (cx, cy), radius)
    pygame.draw.circle(screen, WHITE, (cx - 3, cy - 3), max(2, radius // 3))

def spawn_powerup(snake, hurdles, food):
    max_x, max_y = grid_limits()
    occupied = set(snake) | set(hurdles)
    if food:
        occupied.add(food)
    kinds = ["slow", "magnet", "shield", "double"]
    while True:
        pos = (random.randrange(0, max_x, BLOCK_SIZE),
               random.randrange(0, max_y, BLOCK_SIZE))
        if pos not in occupied:
            return {"kind": random.choice(kinds), "pos": pos}

def grid_limits():
    max_x = (WIDTH // BLOCK_SIZE) * BLOCK_SIZE
    max_y = (HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
    return max_x, max_y

def spawn_food(snake, hurdles):
    max_x, max_y = grid_limits()
    occupied = set(snake) | set(hurdles)
    while True:
        food = (random.randrange(0, max_x, BLOCK_SIZE),
                random.randrange(0, max_y, BLOCK_SIZE))
        if food not in occupied:
            return food

def generate_hurdles(mode_name, avoid_positions):
    if mode_name == "MEDIUM":
        count = 8
    elif mode_name == "HARD":
        count = 24
    else:
        return []
    max_x, max_y = grid_limits()
    hurdles = set()
    avoid = set(avoid_positions)
    while len(hurdles) < count:
        pos = (random.randrange(0, max_x, BLOCK_SIZE),
               random.randrange(0, max_y, BLOCK_SIZE))
        if pos not in avoid:
            hurdles.add(pos)
    return list(hurdles)

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip() or 0)
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))
    except OSError:
        pass

def update_high_score(score, high_score):
    if score > high_score:
        high_score = score
        save_high_score(high_score)
    return high_score

def exit_game():
    pygame.quit()
    sys.exit()

def game_over_screen(score, level, high_score, mouse_pos, buttons):
    draw_background()
    draw_grid()
    draw_border()
    draw_centered("GAME OVER", big_font, RED, HEIGHT // 2 - 140)
    draw_centered(f"Score: {score}", font, WHITE, HEIGHT // 2 - 30)
    draw_centered(f"High Score: {high_score}", font, ACCENT, HEIGHT // 2 + 10)
    draw_centered(f"Level: {level}", font, WHITE, HEIGHT // 2 + 50)
    draw_button(buttons["over_restart"], "Restart", is_active=False, is_hover=buttons["over_restart"].collidepoint(mouse_pos))
    draw_button(buttons["over_menu"], "Main Menu", is_active=False, is_hover=buttons["over_menu"].collidepoint(mouse_pos))
    draw_button(buttons["over_quit"], "Quit", is_active=False, is_hover=buttons["over_quit"].collidepoint(mouse_pos))
    pygame.display.update()

def start_screen(high_score, mode_name, mouse_pos, buttons):
    draw_background()
    draw_grid()
    draw_border()
    draw_centered("SNAKE", big_font, YELLOW, 50)

    mode_info = {
        "EASY": ["Relaxed speed", "Fewer obstacles", "Gentle scaling"],
        "MEDIUM": ["Balanced challenge", "Obstacles added", "Faster scaling"],
        "HARD": ["High speed", "Many obstacles", "Tough scaling"],
    }

    menu_panel = buttons["menu_panel"]
    draw_panel(menu_panel, title="Main Menu", title_offset=4)

    if menu_panel.left >= 320:
        info_panel = pygame.Rect(40, 180, max(260, (menu_panel.left - 70)), 260)
    else:
        info_panel = pygame.Rect(
            max(40, (WIDTH - 360) // 2),
            menu_panel.bottom + 16,
            min(360, WIDTH - 80),
            220,
        )
    draw_panel(info_panel, title="Mode Details")
    draw_text(f"Selected: {mode_name}", font, WHITE, info_panel.left + 20, info_panel.top + 60)
    lines = mode_info.get(mode_name, [])
    for i, line in enumerate(lines):
        draw_text(f"- {line}", font, WHITE, info_panel.left + 20, info_panel.top + 100 + i * 34)
    draw_text(f"High Score: {high_score}", font, ACCENT, info_panel.left + 20, info_panel.bottom - 50)

    tip_panel = pygame.Rect(info_panel.left, info_panel.bottom + 16, info_panel.width, 130)
    draw_panel(tip_panel, title="Controls")
    draw_text("Arrow Keys: Move", font, WHITE, tip_panel.left + 20, tip_panel.top + 55)
    draw_text("Buttons: Pause / Menu", font, WHITE, tip_panel.left + 20, tip_panel.top + 90)

    for name, rect in buttons["modes"].items():
        draw_button(
            rect,
            name,
            is_active=(name == mode_name),
            is_hover=rect.collidepoint(mouse_pos),
        )
    draw_button(buttons["start"], "Start", is_active=False, is_hover=buttons["start"].collidepoint(mouse_pos))
    draw_button(buttons["help"], "How To Play", is_active=False, is_hover=buttons["help"].collidepoint(mouse_pos))
    draw_button(buttons["quit"], "Quit", is_active=False, is_hover=buttons["quit"].collidepoint(mouse_pos))
    pygame.display.update()

def help_screen(mouse_pos, buttons):
    draw_background()
    draw_grid()
    draw_border()
    panel = pygame.Rect(120, 120, WIDTH - 240, HEIGHT - 260)
    draw_panel(panel, title="How To Play")
    text_y = panel.top + 70
    draw_text("Use Arrow Keys to move the snake.", font, WHITE, panel.left + 30, text_y)
    draw_text("Eat food to grow and gain points.", font, WHITE, panel.left + 30, text_y + 40)
    draw_text("Avoid walls, your tail, and obstacles.", font, WHITE, panel.left + 30, text_y + 80)
    draw_text("Use Pause/Resume buttons to control the game.", font, WHITE, panel.left + 30, text_y + 120)
    draw_text("Choose a mode on the main menu.", font, WHITE, panel.left + 30, text_y + 160)
    draw_button(buttons["back"], "Back", is_active=False, is_hover=buttons["back"].collidepoint(mouse_pos))
    pygame.display.update()

def main():
    global WIDTH, HEIGHT, screen

    difficulty = {
        "EASY": {"speed": 8, "level_step": 60, "speed_step": 2},
        "MEDIUM": {"speed": 10, "level_step": 50, "speed_step": 3},
        "HARD": {"speed": 13, "level_step": 40, "speed_step": 4},
    }

    def reset_game():
        snake = [(100, 100), (80, 100), (60, 100)]
        hurdles = generate_hurdles(mode_name, snake)
        direction = "RIGHT"
        food = spawn_food(snake, hurdles)
        score = 0
        level = 1
        speed = difficulty[mode_name]["speed"]
        powerup = None
        last_powerup_score = -1
        active = {"slow": 0.0, "magnet": 0.0, "shield": 0.0, "double": 0.0}
        return snake, direction, food, score, level, speed, hurdles, powerup, active, last_powerup_score

    mode_name = "MEDIUM"
    high_score = load_high_score()
    snake, direction, food, score, level, speed, hurdles, powerup, active, last_powerup_score = reset_game()

    def build_buttons():
        button_w, button_h = 160, 50
        gap = 20
        total_w = button_w * 3 + gap * 2
        pause_w, pause_h = 110, 36
        menu_w, menu_h = 90, 36
        stack_h = 55
        stack_gap = 12
        stack_total_h = stack_h * 3 + stack_gap * 2
        panel_w = max(total_w + 60, 520)
        panel_h = 30 + button_h + 24 + stack_total_h + 30
        panel_left = (WIDTH - panel_w) // 2
        panel_top = max(150, (HEIGHT - panel_h) // 2)

        start_x = panel_left + (panel_w - total_w) // 2
        mode_y = panel_top + 60
        stack_start_y = mode_y + button_h + 24
        return {
            "menu_panel": pygame.Rect(panel_left, panel_top, panel_w, panel_h),
            "modes": {
                "EASY": pygame.Rect(start_x, mode_y, button_w, button_h),
                "MEDIUM": pygame.Rect(start_x + button_w + gap, mode_y, button_w, button_h),
                "HARD": pygame.Rect(start_x + (button_w + gap) * 2, mode_y, button_w, button_h),
            },
            "start": pygame.Rect((WIDTH - 220) // 2, stack_start_y, 220, stack_h),
            "help": pygame.Rect((WIDTH - 220) // 2, stack_start_y + stack_h + stack_gap, 220, stack_h),
            "quit": pygame.Rect((WIDTH - 220) // 2, stack_start_y + (stack_h + stack_gap) * 2, 220, stack_h),
            "back": pygame.Rect((WIDTH - 180) // 2, HEIGHT - 120, 180, 50),
            "pause": pygame.Rect(WIDTH - pause_w - menu_w - 16, 12, pause_w, pause_h),
            "resume": pygame.Rect(WIDTH - pause_w - menu_w - 16, 12, pause_w, pause_h),
            "menu": pygame.Rect(WIDTH - menu_w - 8, 12, menu_w, menu_h),
            "over_restart": pygame.Rect((WIDTH - 220) // 2, HEIGHT // 2 + 120, 220, 55),
            "over_menu": pygame.Rect((WIDTH - 220) // 2, HEIGHT // 2 + 185, 220, 55),
            "over_quit": pygame.Rect((WIDTH - 220) // 2, HEIGHT // 2 + 250, 220, 55),
        }

    buttons = build_buttons()

    running = True
    game_state = "START"  # START, HELP, PLAYING, PAUSED, GAME_OVER

    while running:
        if game_state == "START":
            mouse_pos = pygame.mouse.get_pos()
            start_screen(high_score, mode_name, mouse_pos, buttons)
        elif game_state == "HELP":
            mouse_pos = pygame.mouse.get_pos()
            help_screen(mouse_pos, buttons)
        elif game_state == "GAME_OVER":
            mouse_pos = pygame.mouse.get_pos()
            game_over_screen(score, level, high_score, mouse_pos, buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            elif event.type == pygame.VIDEORESIZE:
                new_w = max(MIN_WIDTH, event.w)
                new_h = max(MIN_HEIGHT, event.h)
                WIDTH, HEIGHT = new_w, new_h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                buttons = build_buttons()
                hurdles = [h for h in hurdles if 0 <= h[0] < WIDTH and 0 <= h[1] < HEIGHT]
                if not (0 <= food[0] < WIDTH and 0 <= food[1] < HEIGHT):
                    food = spawn_food(snake, hurdles)
                if powerup and not (0 <= powerup["pos"][0] < WIDTH and 0 <= powerup["pos"][1] < HEIGHT):
                    powerup = None
                if any(seg[0] < 0 or seg[0] >= WIDTH or seg[1] < 0 or seg[1] >= HEIGHT for seg in snake):
                    game_state = "GAME_OVER"
            elif event.type == pygame.KEYDOWN:
                if game_state == "PLAYING":
                    if event.key == pygame.K_UP and direction != "DOWN":
                        direction = "UP"
                    elif event.key == pygame.K_DOWN and direction != "UP":
                        direction = "DOWN"
                    elif event.key == pygame.K_LEFT and direction != "RIGHT":
                        direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and direction != "LEFT":
                        direction = "RIGHT"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "START":
                    for name, rect in buttons["modes"].items():
                        if rect.collidepoint(event.pos):
                            mode_name = name
                    if buttons["start"].collidepoint(event.pos):
                        snake, direction, food, score, level, speed, hurdles, powerup, active, last_powerup_score = reset_game()
                        game_state = "PLAYING"
                    elif buttons["help"].collidepoint(event.pos):
                        game_state = "HELP"
                    elif buttons["quit"].collidepoint(event.pos):
                        exit_game()
                elif game_state == "HELP":
                    if buttons["back"].collidepoint(event.pos):
                        game_state = "START"
                elif game_state == "PLAYING":
                    if buttons["pause"].collidepoint(event.pos):
                        game_state = "PAUSED"
                    elif buttons["menu"].collidepoint(event.pos):
                        game_state = "START"
                elif game_state == "PAUSED":
                    if buttons["resume"].collidepoint(event.pos):
                        game_state = "PLAYING"
                    elif buttons["menu"].collidepoint(event.pos):
                        game_state = "START"
                elif game_state == "GAME_OVER":
                    if buttons["over_restart"].collidepoint(event.pos):
                        snake, direction, food, score, level, speed, hurdles, powerup, active, last_powerup_score = reset_game()
                        game_state = "PLAYING"
                    elif buttons["over_menu"].collidepoint(event.pos):
                        game_state = "START"
                    elif buttons["over_quit"].collidepoint(event.pos):
                        exit_game()

        if game_state == "PAUSED":
            mouse_pos = pygame.mouse.get_pos()
            t = pygame.time.get_ticks() / 1000.0
            draw_background()
            draw_grid()
            draw_border()
            draw_snake(snake, t)
            draw_food(food, t)
            draw_powerup(powerup, t)
            draw_text(f"Score: {score}", font, WHITE, 12, 10)
            draw_text(f"High: {high_score}", font, ACCENT, 12, 40)
            draw_text(f"Level: {level}", font, WHITE, 12, 70)
            draw_centered("PAUSED", big_font, BLUE, HEIGHT // 2 - 30)
            draw_button(buttons["resume"], "Resume", is_active=False, is_hover=buttons["resume"].collidepoint(mouse_pos))
            draw_button(buttons["menu"], "Menu", is_active=False, is_hover=buttons["menu"].collidepoint(mouse_pos))
            pygame.display.update()
            clock.tick(10)
            continue
        elif game_state != "PLAYING":
            clock.tick(10)
            continue

        # Move snake
        x, y = snake[0]
        if direction == "UP":
            y -= BLOCK_SIZE
        elif direction == "DOWN":
            y += BLOCK_SIZE
        elif direction == "LEFT":
            x -= BLOCK_SIZE
        elif direction == "RIGHT":
            x += BLOCK_SIZE

        new_head = (x, y)

        # Collision with walls or itself
        if (x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT or new_head in snake or new_head in hurdles):
            if active["shield"] > 0:
                # Consume shield instead of dying
                active["shield"] = 0
                game_state = "PLAYING"
            else:
                high_score = update_high_score(score, high_score)
                game_state = "GAME_OVER"
            continue

        snake.insert(0, new_head)

        # Food collision
        if new_head == food:
            points = 20 if active["double"] > 0 else 10
            score += points
            food = spawn_food(snake, hurdles)
            high_score = update_high_score(score, high_score)

            # Increase level every 50 points
            if score % difficulty[mode_name]["level_step"] == 0:
                level += 1
                speed += difficulty[mode_name]["speed_step"]
        else:
            snake.pop()

        # Powerup collection
        if powerup and new_head == powerup["pos"]:
            active[powerup["kind"]] = POWERUP_DURATION
            powerup = None

        # Magnet pulls food toward head by one tile
        if active["magnet"] > 0:
            hx, hy = snake[0]
            fx, fy = food
            if abs(hx - fx) + abs(hy - fy) <= BLOCK_SIZE * 6:
                step_x = BLOCK_SIZE if fx < hx else -BLOCK_SIZE if fx > hx else 0
                step_y = BLOCK_SIZE if fy < hy else -BLOCK_SIZE if fy > hy else 0
                candidate = (fx + step_x, fy + step_y)
                if candidate not in snake and candidate not in hurdles:
                    food = candidate

        # Tick active powerups and spawn new ones
        dt = clock.get_time() / 1000.0
        for k in active:
            if active[k] > 0:
                active[k] = max(0.0, active[k] - dt)
        if powerup is None and score > 0 and score % POWERUP_SPAWN_SCORE_STEP == 0 and score != last_powerup_score:
            powerup = spawn_powerup(snake, hurdles, food)
            last_powerup_score = score

        # ---------------- DRAWING ----------------
        mouse_pos = pygame.mouse.get_pos()
        t = pygame.time.get_ticks() / 1000.0
        draw_background()
        draw_grid()
        draw_border()
        draw_snake(snake, t)
        draw_food(food, t)
        draw_powerup(powerup, t)
        for h in hurdles:
            pygame.draw.rect(screen, BLUE, (*h, BLOCK_SIZE, BLOCK_SIZE), border_radius=6)
            pygame.draw.rect(screen, WHITE, (*h, BLOCK_SIZE, BLOCK_SIZE), 1, border_radius=6)

        draw_text(f"Score: {score}", font, WHITE, 12, 10)
        draw_text(f"High: {high_score}", font, ACCENT, 12, 40)
        draw_text(f"Level: {level}", font, WHITE, 12, 70)
        draw_text(f"Mode: {mode_name}", font, WHITE, 12, 100)
        active_list = [k for k, v in active.items() if v > 0]
        if active_list:
            draw_text(f"Power: {', '.join(active_list)}", font, WHITE, 12, 130)
        draw_button(buttons["pause"], "Pause", is_active=False, is_hover=buttons["pause"].collidepoint(mouse_pos))
        draw_button(buttons["menu"], "Menu", is_active=False, is_hover=buttons["menu"].collidepoint(mouse_pos))

        pygame.display.update()
        speed_factor = 0.6 if active["slow"] > 0 else 1.0
        clock.tick(speed * speed_factor)

# ---------------- RUN GAME ----------------
main()
