import pygame
import csv
import sys
import os

# ================= CONFIGURATION =================
GRID_SIZE = 5          # Change this to 5, 9, etc.
CELL_SIZE = 60         # Pixel size of each cell
MARGIN = 200           # Right-side panel width
UI_MIN_HEIGHT = 500    # Minimum height to ensure UI fits

# Calculate Window Dimensions
GRID_PIXEL_SIZE = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = max(GRID_PIXEL_SIZE, UI_MIN_HEIGHT)
WINDOW_WIDTH = GRID_PIXEL_SIZE + MARGIN

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GRID_LINE_COLOR = (100, 100, 100)
INPUT_ACTIVE_COLOR = (0, 200, 255)
INPUT_PASSIVE_COLOR = (100, 100, 100)

# Palette for IDs 1-12
COLORS = [
    (0, 0, 0),       # 0: Empty
    (255, 0, 0),     # 1: Red
    (0, 255, 0),     # 2: Green
    (0, 0, 255),     # 3: Blue
    (255, 255, 0),   # 4: Yellow
    (255, 165, 0),   # 5: Orange
    (0, 255, 255),   # 6: Cyan
    (255, 0, 255),   # 7: Magenta
    (128, 0, 0),     # 8: Maroon
    (128, 128, 0),   # 9: Olive
    (0, 128, 0),     # 10: Dark Green
    (128, 0, 128),   # 11: Purple
    (0, 128, 128),   # 12: Teal
]

def get_color(id_num):
    if id_num < len(COLORS):
        return COLORS[id_num]
    import random
    random.seed(id_num)
    return (random.randint(50,255), random.randint(50,255), random.randint(50,255))

# ================= INITIALIZATION =================
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flow Free Level Generator")
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)

# Initialize Grid
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# State Variables
current_id = 1
status_message = "Ready"

# Text Input Variables
input_text = "level_01"
input_active = False
# We will calculate rect dynamically in draw_ui
input_rect = pygame.Rect(0, 0, 160, 32) 

def save_to_csv():
    filename = "./N = 5/"
    filename += input_text
    if not filename.endswith(".csv"):
        filename += ".csv"
    
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(grid)
        print(f"Successfully saved to {filename}")
        return f"Saved: {filename}"
    except Exception as e:
        print(f"Error saving: {e}")
        return "Error Saving!"

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            val = grid[row][col]
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, get_color(val), rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)
            if val > 0:
                text_surf = font.render(str(val), True, BLACK if sum(get_color(val)) > 400 else WHITE)
                text_rect = text_surf.get_rect(center=rect.center)
                screen.blit(text_surf, text_rect)

def draw_ui():
    # Sidebar Background (Full Height)
    ui_rect = pygame.Rect(GRID_PIXEL_SIZE, 0, MARGIN, WINDOW_HEIGHT)
    pygame.draw.rect(screen, (30, 30, 30), ui_rect)
    
    # Starting Y position for UI elements
    y_offset = 20
    x_start = GRID_PIXEL_SIZE + 20

    # 1. Selected ID and Color Preview
    screen.blit(small_font.render(f"Selected ID: {current_id}", True, WHITE), (x_start, y_offset))
    y_offset += 30
    preview_rect = pygame.Rect(x_start, y_offset, 40, 40)
    pygame.draw.rect(screen, get_color(current_id), preview_rect)
    y_offset += 50 # Add spacing after box

    # 2. Controls Text
    controls = [
        "Controls:",
        "Left Click: Paint",
        "Right Click: Erase",
        "Scroll: Change ID",
        "R: Reset Grid",
        "S: Save (if not typing)",
        "",
        "Filename:",
    ]

    for line in controls:
        surf = small_font.render(line, True, WHITE)
        screen.blit(surf, (x_start, y_offset))
        y_offset += 25 # Smaller line spacing

    # 3. Input Box (Dynamic Position)
    y_offset += 5 # Small padding
    input_rect.topleft = (x_start, y_offset)
    
    box_color = INPUT_ACTIVE_COLOR if input_active else INPUT_PASSIVE_COLOR
    pygame.draw.rect(screen, box_color, input_rect, 2)
    
    text_surface = small_font.render(input_text, True, WHITE)
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
    
    # 4. Status Message
    y_offset += 45
    status_surf = small_font.render(f"Status: {status_message}", True, (200, 200, 200))
    screen.blit(status_surf, (x_start, y_offset))

# ================= MAIN LOOP =================
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Mouse Click Handling ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                input_active = not input_active
            else:
                input_active = False
                
                # Check grid click only if not in input box
                if event.pos[0] < GRID_PIXEL_SIZE: 
                    mx, my = event.pos
                    col = mx // CELL_SIZE
                    row = my // CELL_SIZE
                    if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE:
                        if event.button == 1:
                            grid[row][col] = current_id
                        elif event.button == 3:
                            grid[row][col] = 0
        
        # --- Mouse Scroll Handling ---
        if event.type == pygame.MOUSEWHEEL:
            current_id += event.y
            if current_id < 1: current_id = 1

        # --- Keyboard Handling ---
        if event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    status_message = save_to_csv()
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if event.unicode.isalnum() or event.unicode in "_-.":
                        input_text += event.unicode
            else:
                if event.key == pygame.K_UP:
                    current_id += 1
                elif event.key == pygame.K_DOWN:
                    current_id = max(1, current_id - 1)
                elif event.key == pygame.K_r:
                    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                    status_message = "Grid Reset"
                elif event.key == pygame.K_s:
                    status_message = save_to_csv()

    # --- Mouse Painting ---
    if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
        mx, my = pygame.mouse.get_pos()
        # Ensure we are inside the grid and NOT hovering over the input box
        if mx < GRID_PIXEL_SIZE and not input_rect.collidepoint((mx, my)):
            col = mx // CELL_SIZE
            row = my // CELL_SIZE
            if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE:
                if pygame.mouse.get_pressed()[0]:
                    grid[row][col] = current_id
                else:
                    grid[row][col] = 0

    draw_grid()
    draw_ui()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()