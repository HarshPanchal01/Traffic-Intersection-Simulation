import pygame
import sys
import datetime
import imageio
import numpy as np
import argparse
import math
from simulation.vehicle import Vehicle
from simulation.traffic_light import TrafficLightSystem
from simulation.spawner import Spawner
from analytics.metrics import MetricsManager

# Set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (204, 50, 50)
GREEN = (45, 201, 55)
BLUE = (0, 0, 255)
YELLOW = (231, 180, 22)
GRASS_COLOR = (34, 139, 34)
ROAD_COLOR = (50, 50, 50)
YELLOW_LINE = (255, 204, 0)

WIDTH, HEIGHT = 800, 800
ROAD_WIDTH = 200

BUILDING_COLORS = [
    (140, 140, 140), # Gray
    (160, 150, 140), # Beige
    (130, 140, 150), # Blue-gray
    (150, 130, 130)  # Brick
]

BUILDINGS = [
    # Top-Left (UI area) - No buildings here, just grass
    # Top-Right (UI area) - No buildings here, just grass
    
    # Bottom-Left
    (30, 530, 150, 110, BUILDING_COLORS[2], 'ac_units'),
    (200, 530, 70, 240, BUILDING_COLORS[3], 'helipad'),
    (40, 660, 140, 110, BUILDING_COLORS[0], 'hospital'),
    
    # Bottom-Right
    (530, 530, 110, 110, BUILDING_COLORS[1], 'solar_panels'),
    (660, 530, 110, 240, BUILDING_COLORS[2], 'skylight'),
    (530, 660, 110, 110, BUILDING_COLORS[3], 'ac_units'),
]

TREES = [
    # Top-Left Park (shifted up to avoid sidewalk at bottom edge)
    (30, 80), (210, 50), (100, 40), (260, 100), (50, 210),
    (250, 180), (70, 250), (160, 260), (220, 240), (30, 140),
    # Top-Right Park
    (580, 180), (640, 130), (720, 200), (600, 240), (670, 260), (760, 160),
    (620, 70), (740, 90), (690, 120), (560, 100)
]

def draw_ac(screen, ax, ay, size, t):
    import math
    pygame.draw.rect(screen, (180, 180, 180), (ax, ay, size, size))
    center = (ax + size//2, ay + size//2)
    radius = size//2 - 2
    pygame.draw.circle(screen, (50, 50, 50), center, radius)
    angle = t * 10 # Rotation speed
    x1 = center[0] + (radius-1) * math.cos(angle)
    y1 = center[1] + (radius-1) * math.sin(angle)
    x2 = center[0] - (radius-1) * math.cos(angle)
    y2 = center[1] - (radius-1) * math.sin(angle)
    x3 = center[0] + (radius-1) * math.cos(angle + math.pi/2)
    y3 = center[1] + (radius-1) * math.sin(angle + math.pi/2)
    x4 = center[0] - (radius-1) * math.cos(angle + math.pi/2)
    y4 = center[1] - (radius-1) * math.sin(angle + math.pi/2)
    pygame.draw.line(screen, (200, 200, 200), (x1, y1), (x2, y2), 2)
    pygame.draw.line(screen, (200, 200, 200), (x3, y3), (x4, y4), 2)

def draw_buildings_and_parks(screen, t=0.0):
    # Draw Pond and Benches in Top-Left Park (centered)
    pond_cx, pond_cy = 140, 160
    pygame.draw.ellipse(screen, (70, 130, 180), (pond_cx - 40, pond_cy - 25, 80, 50)) # Pond
    pygame.draw.ellipse(screen, (100, 160, 210), (pond_cx - 35, pond_cy - 20, 70, 40)) # Pond inner
    
    # Bench Top
    pygame.draw.rect(screen, (139, 69, 19), (pond_cx - 10, pond_cy - 40, 20, 8))
    pygame.draw.rect(screen, (105, 50, 10), (pond_cx - 8, pond_cy - 43, 16, 3))
    # Bench Bottom
    pygame.draw.rect(screen, (139, 69, 19), (pond_cx - 10, pond_cy + 32, 20, 8))
    pygame.draw.rect(screen, (105, 50, 10), (pond_cx - 8, pond_cy + 40, 16, 3))
    # Bench Left
    pygame.draw.rect(screen, (139, 69, 19), (pond_cx - 50, pond_cy - 10, 8, 20))
    pygame.draw.rect(screen, (105, 50, 10), (pond_cx - 53, pond_cy - 8, 3, 16))
    # Bench Right
    pygame.draw.rect(screen, (139, 69, 19), (pond_cx + 42, pond_cy - 10, 8, 20))
    pygame.draw.rect(screen, (105, 50, 10), (pond_cx + 50, pond_cy - 8, 3, 16))
    
    # Draw Trees
    for tx, ty in TREES:
        # Tree shadow
        pygame.draw.circle(screen, (25, 100, 25), (tx+3, ty+3), 18)
        # Tree canopy
        pygame.draw.circle(screen, (34, 110, 34), (tx, ty), 18)
        pygame.draw.circle(screen, (40, 130, 40), (tx-4, ty-4), 12)

    for b in BUILDINGS:
        x, y, w, h, color = b[:5]
        detail = b[5] if len(b) > 5 else None
        
        # Base building shadow/outline
        pygame.draw.rect(screen, (50, 50, 50), (x+5, y+5, w, h))
        # Base building
        pygame.draw.rect(screen, color, (x, y, w, h))
        # Roof border
        pygame.draw.rect(screen, (70, 70, 70), (x, y, w, h), 3)
        # Inner roof detail (adds depth)
        inner_color = (max(color[0]-20, 0), max(color[1]-20, 0), max(color[2]-20, 0))
        pygame.draw.rect(screen, inner_color, (x+8, y+8, w-16, h-16))
        pygame.draw.rect(screen, (80, 80, 80), (x+8, y+8, w-16, h-16), 2)
        # Decorations
        if detail == 'helipad':
            cx, cy = x + w//2, y + h//2
            pygame.draw.circle(screen, (100, 100, 100), (cx, cy), 15)
            pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 15, 2)
            pygame.draw.line(screen, (255, 255, 255), (cx-5, cy-8), (cx-5, cy+8), 3)
            pygame.draw.line(screen, (255, 255, 255), (cx+5, cy-8), (cx+5, cy+8), 3)
            pygame.draw.line(screen, (255, 255, 255), (cx-5, cy), (cx+5, cy), 3)
        elif detail == 'hospital':
            cx, cy = x + w//2, y + h//2
            pygame.draw.rect(screen, (255, 255, 255), (cx-12, cy-12, 24, 24))
            pygame.draw.rect(screen, (220, 50, 50), (cx-3, cy-9, 6, 18))
            pygame.draw.rect(screen, (220, 50, 50), (cx-9, cy-3, 18, 6))
        elif detail == 'ac_units':
            # Cluster of AC units
            draw_ac(screen, x+20, y+20, 14, t)
            draw_ac(screen, x+40, y+20, 14, t)
            draw_ac(screen, x+20, y+40, 14, t)
            draw_ac(screen, x+40, y+40, 14, t)
        elif detail == 'solar_panels':
            # Detailed solar panel grid
            for px in range(x+20, x+w-30, 22):
                for py in range(y+20, y+h-30, 28):
                    pygame.draw.rect(screen, (20, 40, 80), (px, py, 18, 24)) # Dark blue base
                    pygame.draw.rect(screen, (150, 150, 150), (px, py, 18, 24), 2) # Silver frame
                    pygame.draw.line(screen, (80, 120, 180), (px+3, py+2), (px+15, py+2), 1) # Glare lines
                    pygame.draw.line(screen, (80, 120, 180), (px+3, py+8), (px+15, py+8), 1)
                    pygame.draw.line(screen, (80, 120, 180), (px+3, py+14), (px+15, py+14), 1)
                    pygame.draw.line(screen, (80, 120, 180), (px+3, py+20), (px+15, py+20), 1)
        elif detail == 'skylight':
            pygame.draw.rect(screen, (170, 200, 220), (x+w//2-15, y+20, 30, h-40))
            pygame.draw.rect(screen, (220, 240, 255), (x+w//2-12, y+23, 24, h-46))
            for ly in range(y+30, y+h-20, 15):
                pygame.draw.line(screen, (150, 180, 200), (x+w//2-15, ly), (x+w//2+14, ly), 2)



def draw_intersection(screen, t=0.0):
    # Fill background with grass
    screen.fill(GRASS_COLOR)
    
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # Draw sidewalks
    SIDEWALK_COLOR = (160, 160, 160)
    SIDEWALK_LINE = (130, 130, 130)
    SIDEWALK_WIDTH = ROAD_WIDTH + 40
    
    # Vertical sidewalk base
    pygame.draw.rect(screen, SIDEWALK_COLOR, (center_x - SIDEWALK_WIDTH // 2, 0, SIDEWALK_WIDTH, HEIGHT))
    # Horizontal sidewalk base
    pygame.draw.rect(screen, SIDEWALK_COLOR, (0, center_y - SIDEWALK_WIDTH // 2, WIDTH, SIDEWALK_WIDTH))
    
    # Sidewalk paving lines (grid pattern)
    for i in range(0, HEIGHT, 20):
        # Vertical sidewalk lines
        pygame.draw.line(screen, SIDEWALK_LINE, (center_x - SIDEWALK_WIDTH // 2, i), (center_x - ROAD_WIDTH // 2, i))
        pygame.draw.line(screen, SIDEWALK_LINE, (center_x + ROAD_WIDTH // 2, i), (center_x + SIDEWALK_WIDTH // 2, i))
    for i in range(0, WIDTH, 20):
        # Horizontal sidewalk lines
        pygame.draw.line(screen, SIDEWALK_LINE, (i, center_y - SIDEWALK_WIDTH // 2), (i, center_y - ROAD_WIDTH // 2))
        pygame.draw.line(screen, SIDEWALK_LINE, (i, center_y + ROAD_WIDTH // 2), (i, center_y + SIDEWALK_WIDTH // 2))
    
    # Outer curb lines
    pygame.draw.line(screen, (120, 120, 120), (center_x - SIDEWALK_WIDTH // 2, 0), (center_x - SIDEWALK_WIDTH // 2, HEIGHT), 2)
    pygame.draw.line(screen, (120, 120, 120), (center_x + SIDEWALK_WIDTH // 2, 0), (center_x + SIDEWALK_WIDTH // 2, HEIGHT), 2)
    pygame.draw.line(screen, (120, 120, 120), (0, center_y - SIDEWALK_WIDTH // 2), (WIDTH, center_y - SIDEWALK_WIDTH // 2), 2)
    pygame.draw.line(screen, (120, 120, 120), (0, center_y + SIDEWALK_WIDTH // 2), (WIDTH, center_y + SIDEWALK_WIDTH // 2), 2)

    # Draw buildings and parks
    draw_buildings_and_parks(screen, t)
    
    # Draw roads
    # Vertical road
    pygame.draw.rect(screen, ROAD_COLOR, (center_x - ROAD_WIDTH // 2, 0, ROAD_WIDTH, HEIGHT))
    # Horizontal road
    pygame.draw.rect(screen, ROAD_COLOR, (0, center_y - ROAD_WIDTH // 2, WIDTH, ROAD_WIDTH))
    
    # Draw road markings
    # Vertical double yellow line
    pygame.draw.line(screen, YELLOW_LINE, (center_x - 2, 0), (center_x - 2, center_y - (ROAD_WIDTH // 2 + 30)), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x + 2, 0), (center_x + 2, center_y - (ROAD_WIDTH // 2 + 30)), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x - 2, center_y + (ROAD_WIDTH // 2 + 30)), (center_x - 2, HEIGHT), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x + 2, center_y + (ROAD_WIDTH // 2 + 30)), (center_x + 2, HEIGHT), 2)
    
    # Horizontal double yellow line
    pygame.draw.line(screen, YELLOW_LINE, (0, center_y - 2), (center_x - (ROAD_WIDTH // 2 + 30), center_y - 2), 2)
    pygame.draw.line(screen, YELLOW_LINE, (0, center_y + 2), (center_x - (ROAD_WIDTH // 2 + 30), center_y + 2), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x + (ROAD_WIDTH // 2 + 30), center_y - 2), (WIDTH, center_y - 2), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x + (ROAD_WIDTH // 2 + 30), center_y + 2), (WIDTH, center_y + 2), 2)
    
    # Draw lane dividers (dashed white lines)
    def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=10):
        x1, y1 = start_pos
        x2, y2 = end_pos
        if x1 == x2:
            ycoords = [y for y in range(min(y1, y2), max(y1, y2), dash_length)]
            for i in range(0, len(ycoords) - 1, 2):
                pygame.draw.line(surface, color, (x1, ycoords[i]), (x1, ycoords[i+1]), width)
        elif y1 == y2:
            xcoords = [x for x in range(min(x1, x2), max(x1, x2), dash_length)]
            for i in range(0, len(xcoords) - 1, 2):
                pygame.draw.line(surface, color, (xcoords[i], y1), (xcoords[i+1], y1), width)

    draw_dashed_line(screen, WHITE, (center_x - 50, 0), (center_x - 50, center_y - (ROAD_WIDTH // 2 + 30)), 2)
    draw_dashed_line(screen, WHITE, (center_x + 50, 0), (center_x + 50, center_y - (ROAD_WIDTH // 2 + 30)), 2)
    draw_dashed_line(screen, WHITE, (center_x - 50, center_y + (ROAD_WIDTH // 2 + 30)), (center_x - 50, HEIGHT), 2)
    draw_dashed_line(screen, WHITE, (center_x + 50, center_y + (ROAD_WIDTH // 2 + 30)), (center_x + 50, HEIGHT), 2)
    
    draw_dashed_line(screen, WHITE, (0, center_y - 50), (center_x - (ROAD_WIDTH // 2 + 30), center_y - 50), 2)
    draw_dashed_line(screen, WHITE, (0, center_y + 50), (center_x - (ROAD_WIDTH // 2 + 30), center_y + 50), 2)
    draw_dashed_line(screen, WHITE, (center_x + (ROAD_WIDTH // 2 + 30), center_y - 50), (WIDTH, center_y - 50), 2)
    draw_dashed_line(screen, WHITE, (center_x + (ROAD_WIDTH // 2 + 30), center_y + 50), (WIDTH, center_y + 50), 2)
    
    # Draw left turn arrows in the left lanes
    def draw_left_arrow(surface, pos, angle):
        large_surf = pygame.Surface((100, 150), pygame.SRCALPHA)
        # Draw arc ring (thickness 16). Outer radius 50, inner 34.
        pygame.draw.circle(large_surf, WHITE, (40, 66), 50, 16)
        # Erase bottom and left
        large_surf.fill((0,0,0,0), (0, 66, 100, 100))
        large_surf.fill((0,0,0,0), (0, 0, 40, 150))
        
        # Draw stem
        pygame.draw.rect(large_surf, WHITE, (74, 66, 16, 50))
        # Draw head
        pygame.draw.polygon(large_surf, WHITE, [(40, 0), (0, 24), (40, 48)])
        
        arrow_surface = pygame.transform.smoothscale(large_surf, (20, 30))
        rotated_arrow = pygame.transform.rotate(arrow_surface, angle)
        rect = rotated_arrow.get_rect(center=pos)
        surface.blit(rotated_arrow, rect)

    # Draw straight/right combined arrows in the right lanes
    def draw_straight_right_arrow(surface, pos, angle):
        large_surf = pygame.Surface((100, 150), pygame.SRCALPHA)
        # Draw arc ring
        pygame.draw.circle(large_surf, WHITE, (70, 100), 48, 16)
        # Erase right and bottom
        large_surf.fill((0,0,0,0), (70, 0, 30, 150))
        large_surf.fill((0,0,0,0), (0, 100, 100, 50))
        
        # Stem
        pygame.draw.rect(large_surf, WHITE, (22, 40, 16, 85))
        # Straight head
        pygame.draw.polygon(large_surf, WHITE, [(6, 40), (30, 0), (54, 40)])
        # Right head
        pygame.draw.polygon(large_surf, WHITE, [(70, 40), (100, 60), (70, 80)])
        
        arrow_surface = pygame.transform.smoothscale(large_surf, (20, 30))
        rotated_arrow = pygame.transform.rotate(arrow_surface, angle)
        rect = rotated_arrow.get_rect(center=pos)
        surface.blit(rotated_arrow, rect)

    arrow_offset = ROAD_WIDTH // 2 + 80

    # Southbound (North incoming) lanes
    draw_left_arrow(screen, (center_x - 25, center_y - arrow_offset), 180)
    draw_straight_right_arrow(screen, (center_x - 75, center_y - arrow_offset), 180)
    
    # Northbound (South incoming) lanes
    draw_left_arrow(screen, (center_x + 25, center_y + arrow_offset), 0)
    draw_straight_right_arrow(screen, (center_x + 75, center_y + arrow_offset), 0)
    
    # Eastbound (West incoming) lanes
    draw_left_arrow(screen, (center_x - arrow_offset, center_y + 25), -90)
    draw_straight_right_arrow(screen, (center_x - arrow_offset, center_y + 75), -90)
    
    # Westbound (East incoming) lanes
    draw_left_arrow(screen, (center_x + arrow_offset, center_y - 25), 90)
    draw_straight_right_arrow(screen, (center_x + arrow_offset, center_y - 75), 90)

    # Draw stop lines
    # North (vehicles coming from north, stop line on the right side of the road)
    pygame.draw.line(screen, WHITE, (center_x - ROAD_WIDTH // 2, center_y - (ROAD_WIDTH // 2 + 30)), (center_x, center_y - (ROAD_WIDTH // 2 + 30)), 4)
    # South (vehicles coming from south)
    pygame.draw.line(screen, WHITE, (center_x, center_y + (ROAD_WIDTH // 2 + 30)), (center_x + ROAD_WIDTH // 2, center_y + (ROAD_WIDTH // 2 + 30)), 4)
    # West (vehicles coming from west)
    pygame.draw.line(screen, WHITE, (center_x - (ROAD_WIDTH // 2 + 30), center_y), (center_x - (ROAD_WIDTH // 2 + 30), center_y + ROAD_WIDTH // 2), 4)
    # East (vehicles coming from east)
    pygame.draw.line(screen, WHITE, (center_x + (ROAD_WIDTH // 2 + 30), center_y - ROAD_WIDTH // 2), (center_x + (ROAD_WIDTH // 2 + 30), center_y), 4)

    # Draw crosswalks (zebra lines) in the 30-pixel free space
    def draw_crosswalk_y(screen, y_pos, x_center, width):
        stripe_w = 8
        stripe_h = 24
        spacing = 16
        start_x = x_center - width // 2 + spacing // 2
        for x in range(start_x, x_center + width // 2, spacing):
            pygame.draw.rect(screen, WHITE, (x, y_pos - stripe_h // 2, stripe_w, stripe_h))

    def draw_crosswalk_x(screen, x_pos, y_center, height):
        stripe_w = 24
        stripe_h = 8
        spacing = 16
        start_y = y_center - height // 2 + spacing // 2
        for y in range(start_y, y_center + height // 2, spacing):
            pygame.draw.rect(screen, WHITE, (x_pos - stripe_w // 2, y, stripe_w, stripe_h))

    # Center of the 30-pixel band
    cw_offset = ROAD_WIDTH // 2 + 15

    # North crosswalk
    draw_crosswalk_y(screen, center_y - cw_offset, center_x, ROAD_WIDTH)
    # South crosswalk
    draw_crosswalk_y(screen, center_y + cw_offset, center_x, ROAD_WIDTH)
    # West crosswalk
    draw_crosswalk_x(screen, center_x - cw_offset, center_y, ROAD_WIDTH)
    # East crosswalk
    draw_crosswalk_x(screen, center_x + cw_offset, center_y, ROAD_WIDTH)

def draw_traffic_lights(screen, traffic_lights, tl_box_img):
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    def get_color(state):
        if state == "GREEN": return GREEN
        if state == "YELLOW": return YELLOW
        return RED

    ns_color = get_color(traffic_lights.ns_state)
    ew_color = get_color(traffic_lights.ew_state)
    
    radius = 8
    
    # Optional glow effect for lights
    def draw_light(surface, img, color, pos, angle):
        # Rotate the box image
        rotated_img = pygame.transform.rotate(img, angle)
        rect = rotated_img.get_rect(center=pos)
        surface.blit(rotated_img, rect.topleft)
        
        # Calculate light position based on angle
        if angle == 0: # Facing up
            light_pos = (pos[0], pos[1])
        elif angle == 180: # Facing down
            light_pos = (pos[0], pos[1])
        elif angle == 90: # Facing left
            light_pos = (pos[0], pos[1])
        else: # Facing right
            light_pos = (pos[0], pos[1])
            
        # Draw a subtle glow
        glow_surf = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 80), (radius*2, radius*2), radius*1.5)
        surface.blit(glow_surf, (light_pos[0]-radius*2, light_pos[1]-radius*2))
        
        # Draw the solid light
        pygame.draw.circle(surface, color, light_pos, radius)
    
    # Position them near the stop lines on the yellow line separator
    offset_y = (ROAD_WIDTH // 2 + 30) + 12
    offset_x = (ROAD_WIDTH // 2 + 30) + 12
    
    # North approaching (NS light) - Stop line is at top, so light is at top, facing North (0 degrees)
    draw_light(screen, tl_box_img, ns_color, (center_x, center_y - offset_y), 0)
    
    # South approaching (NS light) - Stop line is at bottom, facing South (180 degrees)
    draw_light(screen, tl_box_img, ns_color, (center_x, center_y + offset_y), 180)
    
    # West approaching (EW light) - Stop line is left, facing West (90 degrees)
    draw_light(screen, tl_box_img, ew_color, (center_x - offset_x, center_y), 90)
    
    # East approaching (EW light) - Stop line is right, facing East (-90 degrees)
    draw_light(screen, tl_box_img, ew_color, (center_x + offset_x, center_y), -90)

def draw_legend(screen):
    font = pygame.font.SysFont("courier new", 16)

    lines = [
        "controls:",
        "q: quit & save",
        "p: pause",
        "r: resume",
        "s: snapshot"
    ]
    
    # Semi-transparent background
    legend_width = 160
    legend_height = len(lines) * 22 + 10
    overlay = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (10, 10))
    
    for i, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        screen.blit(text, (20, 20 + i * 22))

def draw_stats(screen, active_vehicles, collision_count, sim_time, metrics):
    font = pygame.font.SysFont("courier new", 16)

    # Format time as MM:SS.ss
    minutes = int(sim_time // 60)
    seconds = sim_time % 60
    time_str = f"{minutes:02d}:{seconds:05.2f}"

    lines = [
        "simulation details:",
        f"time: {time_str}",
        f"active vehicles: {active_vehicles}",
        f"total collisions: {collision_count}",
        f"avg wait: {metrics.get_avg_wait_time():.1f}s",
        f"throughput: {metrics.get_throughput(sim_time):.1f} vehicles/min",
        f"max queue: {metrics.max_queue_length}"
    ]
    
    # Semi-transparent background
    stats_width = 330
    stats_height = len(lines) * 22 + 10
    overlay = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (WIDTH - stats_width - 10, 10))

    for i, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        screen.blit(text, (WIDTH - stats_width, 20 + i * 22))
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Traffic Intersection Simulation")
    
    # clock object that ensures animation has the same speed on all machines
    clock = pygame.time.Clock()
    
    # Load assets
    tl_box_img = pygame.image.load('assets/tl_box.png').convert_alpha()

    traffic_lights = TrafficLightSystem()
    spawner = Spawner(rate=0.5) # 0.5 vehicles per second
    
    vehicles = {'N': [], 'S': [], 'E': [], 'W': []}
    
    running = True
    is_paused = False
    total_sim_time = 0.0
    metrics = MetricsManager()
    
    # Start recording automatically
    is_recording = True
    timestamp = datetime.datetime.now().strftime("%b%d_%Y_%I%M%p").lower()
    video_filename = f"simulation_{timestamp}.mp4"
    video_writer = imageio.get_writer(video_filename, fps=60.0)
    print(f"Recording started: {video_filename}")
    
    collision_count = 0
    collided_pairs = set()

    while running:
        # Calculate delta time in seconds
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_p:
                    is_paused = True
                elif event.key == pygame.K_r:
                    is_paused = False
                elif event.key == pygame.K_s:
                    # Capture snapshot
                    timestamp = datetime.datetime.now().strftime("%b%d_%Y_%I%M%p").lower()
                    filename = f"snapshot_{timestamp}.png"
                    pygame.image.save(screen, filename)
                    print(f"Snapshot saved: {filename}")

        if not is_paused:
            total_sim_time += dt
            # Update logic
            traffic_lights.update(dt)
            
            # Spawner logic
            new_vehicles = spawner.update(dt)
            for direction, turn, lane, vehicle_type in new_vehicles:
                lane_vehicles = [c for c in vehicles[direction] if c.lane == lane]
                if not lane_vehicles or lane_vehicles[-1].state[0] > 50.0:
                    vehicles[direction].append(Vehicle(direction, turn, lane, vehicle_type))

            # Update vehicles
            all_vehicles = []
            for direction in ['N', 'S', 'E', 'W']:
                if direction in ['N', 'S']:
                    light_state = traffic_lights.ns_state
                else:
                    light_state = traffic_lights.ew_state
                    
                for i, vehicle in enumerate(vehicles[direction]):
                    # Find the closest vehicle ahead, including those from other directions that merged.
                    # We calculate the distance purely in 1D along the track (state[0]) because 
                    # 2D Euclidean distance cuts corners on curves, causing false collision readings.
                    min_dist_ahead = float('inf')
                    
                    lane_vehicles_ahead = [c for c in vehicles[direction][:i] if c.lane == vehicle.lane]
                    if lane_vehicles_ahead:
                        vehicle_ahead = lane_vehicles_ahead[-1]
                        # 1D Distance = Position of car ahead - Position of current car - their half lengths
                        d = vehicle_ahead.state[0] - vehicle.state[0] - (vehicle.length / 2) - (vehicle_ahead.length / 2)
                        if d > 0 and d < min_dist_ahead:
                            min_dist_ahead = d

                    pos1 = vehicle.get_world_pos()
                    _, _, _, rx, ry = vehicle.trajectory.get_position_and_angle(vehicle.state[0])
                    dx_dir, dy_dir = ry, -rx
                    
                    for other_dir in ['N', 'S', 'E', 'W']:
                        if other_dir == direction: continue
                        for ov in vehicles[other_dir]:
                            if ov.state[0] > 300: # Has started turning / merged
                                pos2 = ov.get_world_pos()
                                dx = pos2[0] - pos1[0]
                                dy = pos2[1] - pos1[1]
                                
                                _, _, _, ov_rx, ov_ry = ov.trajectory.get_position_and_angle(ov.state[0])
                                ov_dx_dir, ov_dy_dir = ov_ry, -ov_rx
                                
                                # Only follow cars heading in roughly the same direction (dot product > 0.5)
                                if (dx_dir * ov_dx_dir + dy_dir * ov_dy_dir) > 0.5:
                                    forward_dist = dx * dx_dir + dy * dy_dir
                                    if forward_dist > 0:
                                        lateral_dist = abs(dx * rx + dy * ry)
                                        if lateral_dist < 15.0:
                                            d = forward_dist - (vehicle.length / 2) - (ov.length / 2)
                                            if d > 0 and d < min_dist_ahead:
                                                min_dist_ahead = d
                                            
                    dist_ahead = min_dist_ahead if min_dist_ahead != float('inf') else None
                        
                    must_yield_left = False
                    can_right_on_red = False
                    
                    if vehicle.turn == 'left':
                        opposing_dir = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                        for opp_vehicle in vehicles[opposing_dir]:
                            if opp_vehicle.turn in ['straight', 'right']:
                                # If light is yellow or red, opposing vehicles before the stop line will stop.
                                if light_state in ['YELLOW', 'RED'] and opp_vehicle.state[0] < 270:
                                    continue
                                    
                                # If opposing vehicle is in intersection and before the midpoint (center)
                                if 270 <= opp_vehicle.state[0] < 450:
                                    must_yield_left = True
                                    break
                                # If opposing vehicle is approaching and moving fast enough to be a threat
                                elif opp_vehicle.state[0] < 270:
                                    # Calculate time for opposing vehicle to reach intersection
                                    v_opp = opp_vehicle.state[1]
                                    if v_opp > 0.1:
                                        time_to_intersect = (270 - opp_vehicle.state[0]) / v_opp
                                        # If it will reach the intersection in the next 5.5 seconds, yield
                                        if time_to_intersect < 5.5:
                                            must_yield_left = True
                                            break
                                    
                    if vehicle.turn == 'right' and light_state == 'RED':
                        cross_left_dir = {'N':'E', 'S':'W', 'E':'S', 'W':'N'}[direction]
                        opposing_dir = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                        
                        is_safe = True
                        for cross_vehicle in vehicles[cross_left_dir]:
                            if cross_vehicle.turn in ['straight', 'left']:
                                if 250 < cross_vehicle.state[0] < 500:
                                    is_safe = False
                                    break
                                elif cross_vehicle.state[0] <= 250 and cross_vehicle.state[1] > 0.1:
                                    time_to_intersect = (270 - cross_vehicle.state[0]) / cross_vehicle.state[1]
                                    if time_to_intersect < 5.0:
                                        is_safe = False
                                        break
                        if is_safe:
                            for opp_vehicle in vehicles[opposing_dir]:
                                if opp_vehicle.turn == 'left':
                                    if 250 < opp_vehicle.state[0] < 500:
                                        is_safe = False
                                        break
                                    elif opp_vehicle.state[0] <= 250 and opp_vehicle.state[1] > 0.1:
                                        time_to_intersect = (270 - opp_vehicle.state[0]) / opp_vehicle.state[1]
                                        if time_to_intersect < 5.0:
                                            is_safe = False
                                            break
                        can_right_on_red = is_safe
                        
                    cross_traffic_blocking = False
                    if vehicle.state[0] < 270:
                        cross_dirs = ['E', 'W'] if direction in ['N', 'S'] else ['N', 'S']
                        for c_dir in cross_dirs:
                            for cv in vehicles[c_dir]:
                                if 300 < cv.state[0] < 500 and cv.state[1] < 15.0:
                                    # If crossing traffic is in the intersection and moving somewhat slowly, don't enter
                                    cross_traffic_blocking = True
                                    break
                            if cross_traffic_blocking:
                                break
                        
                    vehicle.update(dt, light_state, dist_ahead, must_yield_left, can_right_on_red, cross_traffic_blocking)
                    all_vehicles.append(vehicle)

            # Collision detection (using 2D Euclidean distance)
            # Modeling vehicles approximately as bounding circles. 
            # If the distance between the centers is less than the threshold, it is a collision.
            for i in range(len(all_vehicles)):
                for j in range(i + 1, len(all_vehicles)):
                    car1 = all_vehicles[i]
                    car2 = all_vehicles[j]

                    pos1 = car1.get_world_pos()
                    pos2 = car2.get_world_pos()

                    # Distance formula: d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
                    dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

                    if dist < 30.0:
                        pair_id = tuple(sorted((id(car1), id(car2))))
                        if pair_id not in collided_pairs:
                            collision_count += 1
                            collided_pairs.add(pair_id)
                            print(f"[{total_sim_time:06.2f}s] Collision detected! {car1.direction}-{car1.turn} (pos:{car1.state[0]:.1f}) vs {car2.direction}-{car2.turn} (pos:{car2.state[0]:.1f})")

            # Update Metrics
            metrics.update_max_queue(vehicles)

            # Remove vehicles that have left the screen
            for direction in ['N', 'S', 'E', 'W']:
                for vehicle in vehicles[direction]:
                    if vehicle.state[0] >= 850.0:
                        collided_pairs = {p for p in collided_pairs if id(vehicle) not in p}
                        # Record metrics for finished vehicle
                        metrics.add_completed_vehicle(vehicle)
                vehicles[direction] = [vehicle for vehicle in vehicles[direction] if vehicle.state[0] < 850.0]

        # Draw environment
        draw_intersection(screen, total_sim_time)
        draw_traffic_lights(screen, traffic_lights, tl_box_img)
        
        # Draw vehicles
        active_count = 0
        for direction in ['N', 'S', 'E', 'W']:
            for vehicle in vehicles[direction]:
                vehicle.draw(screen)
                # Only count vehicles whose centers are actually on screen
                if 0 <= vehicle.state[0] <= 800:
                    active_count += 1
        
        # Draw legends and stats
        draw_legend(screen)
        draw_stats(screen, active_count, collision_count, total_sim_time, metrics)
        
        pygame.display.flip()
        
        # Save frame to video if recording
        if is_recording and video_writer:
            # Convert Pygame surface to imageio image format
            frame_data = pygame.surfarray.array3d(screen)
            frame_data = np.transpose(frame_data, (1, 0, 2))
            video_writer.append_data(frame_data)

    if video_writer:
        video_writer.close()
        print(f"Video saved: {video_filename}")
        
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Traffic Intersection Simulation')
    parser.add_argument('--headless', action='store_true', help='Run headless experiments without GUI')
    args = parser.parse_args()

    if args.headless:
        import run_experiments
        run_experiments.main()
    else:
        main()
