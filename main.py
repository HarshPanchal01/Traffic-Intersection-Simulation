import pygame
import sys
import datetime
import cv2
import numpy as np
import os
from simulation.car import Car
from simulation.traffic_light import TrafficLightSystem
from simulation.spawner import Spawner

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

def draw_intersection(screen):
    # Fill background with grass
    screen.fill(GRASS_COLOR)
    
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # Draw roads
    # Vertical road
    pygame.draw.rect(screen, ROAD_COLOR, (center_x - ROAD_WIDTH // 2, 0, ROAD_WIDTH, HEIGHT))
    # Horizontal road
    pygame.draw.rect(screen, ROAD_COLOR, (0, center_y - ROAD_WIDTH // 2, WIDTH, ROAD_WIDTH))
    
    # Draw road markings
    # Vertical double yellow line
    pygame.draw.line(screen, YELLOW_LINE, (center_x - 2, 0), (center_x - 2, center_y - ROAD_WIDTH // 2), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x + 2, 0), (center_x + 2, center_y - ROAD_WIDTH // 2), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x - 2, center_y + ROAD_WIDTH // 2), (center_x - 2, HEIGHT), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x + 2, center_y + ROAD_WIDTH // 2), (center_x + 2, HEIGHT), 2)
    
    # Horizontal double yellow line
    pygame.draw.line(screen, YELLOW_LINE, (0, center_y - 2), (center_x - ROAD_WIDTH // 2, center_y - 2), 2)
    pygame.draw.line(screen, YELLOW_LINE, (0, center_y + 2), (center_x - ROAD_WIDTH // 2, center_y + 2), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x + ROAD_WIDTH // 2, center_y - 2), (WIDTH, center_y - 2), 2)
    pygame.draw.line(screen, YELLOW_LINE, (center_x + ROAD_WIDTH // 2, center_y + 2), (WIDTH, center_y + 2), 2)
    
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

    draw_dashed_line(screen, WHITE, (center_x - 50, 0), (center_x - 50, center_y - ROAD_WIDTH // 2), 2)
    draw_dashed_line(screen, WHITE, (center_x + 50, 0), (center_x + 50, center_y - ROAD_WIDTH // 2), 2)
    draw_dashed_line(screen, WHITE, (center_x - 50, center_y + ROAD_WIDTH // 2), (center_x - 50, HEIGHT), 2)
    draw_dashed_line(screen, WHITE, (center_x + 50, center_y + ROAD_WIDTH // 2), (center_x + 50, HEIGHT), 2)
    
    draw_dashed_line(screen, WHITE, (0, center_y - 50), (center_x - ROAD_WIDTH // 2, center_y - 50), 2)
    draw_dashed_line(screen, WHITE, (0, center_y + 50), (center_x - ROAD_WIDTH // 2, center_y + 50), 2)
    draw_dashed_line(screen, WHITE, (center_x + ROAD_WIDTH // 2, center_y - 50), (WIDTH, center_y - 50), 2)
    draw_dashed_line(screen, WHITE, (center_x + ROAD_WIDTH // 2, center_y + 50), (WIDTH, center_y + 50), 2)
    
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

    arrow_offset = ROAD_WIDTH // 2 + 50

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
    # North (cars coming from north, stop line on the right side of the road)
    pygame.draw.line(screen, WHITE, (center_x - ROAD_WIDTH // 2, center_y - ROAD_WIDTH // 2), (center_x, center_y - ROAD_WIDTH // 2), 4)
    # South (cars coming from south)
    pygame.draw.line(screen, WHITE, (center_x, center_y + ROAD_WIDTH // 2), (center_x + ROAD_WIDTH // 2, center_y + ROAD_WIDTH // 2), 4)
    # West (cars coming from west)
    pygame.draw.line(screen, WHITE, (center_x - ROAD_WIDTH // 2, center_y), (center_x - ROAD_WIDTH // 2, center_y + ROAD_WIDTH // 2), 4)
    # East (cars coming from east)
    pygame.draw.line(screen, WHITE, (center_x + ROAD_WIDTH // 2, center_y - ROAD_WIDTH // 2), (center_x + ROAD_WIDTH // 2, center_y), 4)

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
    offset_y = ROAD_WIDTH // 2 + 12
    offset_x = ROAD_WIDTH // 2 + 12
    
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Traffic Intersection Simulation")
    
    # clock object that ensures animation has the same speed on all machines
    clock = pygame.time.Clock()
    
    # Load assets
    tl_box_img = pygame.image.load('assets/tl_box.png').convert_alpha()

    traffic_lights = TrafficLightSystem()
    spawner = Spawner(rate=0.5) # 0.5 cars per second
    
    cars = {'N': [], 'S': [], 'E': [], 'W': []}
    
    running = True
    is_paused = False
    
    # Start recording automatically
    is_recording = True
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"simulation_{timestamp}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_filename, fourcc, 60.0, (WIDTH, HEIGHT))
    print(f"Recording started: {video_filename}")
    
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
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"snapshot_{timestamp}.png"
                    pygame.image.save(screen, filename)
                    print(f"Snapshot saved: {filename}")

        if not is_paused:
            # Update logic
            traffic_lights.update(dt)
            
            # Spawner logic
            new_cars = spawner.update(dt)
            for direction, turn, lane in new_cars:
                lane_cars = [c for c in cars[direction] if c.lane == lane]
                if not lane_cars or lane_cars[-1].state[0] > 60.0:
                    cars[direction].append(Car(direction, turn, lane))

            # Update cars
            for direction in ['N', 'S', 'E', 'W']:
                if direction in ['N', 'S']:
                    light_state = traffic_lights.ns_state
                else:
                    light_state = traffic_lights.ew_state
                    
                for i, car in enumerate(cars[direction]):
                    # Find distance to car ahead IN THE SAME LANE
                    dist_ahead = None
                    lane_cars_ahead = [c for c in cars[direction][:i] if c.lane == car.lane]
                    if lane_cars_ahead:
                        dist_ahead = lane_cars_ahead[-1].state[0] - car.state[0]
                        
                    must_yield_left = False
                    can_right_on_red = False
                    
                    if car.turn == 'left':
                        opposing_dir = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                        for opp_car in cars[opposing_dir]:
                            if opp_car.turn in ['straight', 'right']:
                                # If light is yellow or red, opposing cars before the stop line will stop.
                                if light_state in ['YELLOW', 'RED'] and opp_car.state[0] < 320:
                                    continue
                                    
                                # If opposing car is in intersection
                                if 320 <= opp_car.state[0] < 450:
                                    must_yield_left = True
                                    break
                                # If opposing car is approaching and moving fast enough to be a threat
                                elif opp_car.state[0] < 320:
                                    # Calculate time for opposing car to reach intersection
                                    v_opp = opp_car.state[1]
                                    if v_opp > 0.1:
                                        time_to_intersect = (320 - opp_car.state[0]) / v_opp
                                        # If it will reach the intersection in the next 3.5 seconds, yield
                                        if time_to_intersect < 3.5:
                                            must_yield_left = True
                                            break
                                    
                    if car.turn == 'right' and light_state == 'RED':
                        cross_left_dir = {'N':'E', 'S':'W', 'E':'S', 'W':'N'}[direction]
                        opposing_dir = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                        
                        is_safe = True
                        for cross_car in cars[cross_left_dir]:
                            if cross_car.turn in ['straight', 'left']:
                                if 320 < cross_car.state[0] < 480:
                                    is_safe = False
                                    break
                                elif 150 < cross_car.state[0] <= 320 and cross_car.state[1] > 2.0:
                                    is_safe = False
                                    break
                        if is_safe:
                            for opp_car in cars[opposing_dir]:
                                if opp_car.turn == 'left':
                                    if 320 < opp_car.state[0] < 450:
                                        is_safe = False
                                        break
                                    elif 200 < opp_car.state[0] <= 320 and opp_car.state[1] > 2.0:
                                        is_safe = False
                                        break
                        can_right_on_red = is_safe
                        
                    car.update(dt, light_state, dist_ahead, must_yield_left, can_right_on_red)

            # Remove cars that have left the screen
            for direction in ['N', 'S', 'E', 'W']:
                cars[direction] = [car for car in cars[direction] if car.state[0] < 900.0]

        # Draw environment
        draw_intersection(screen)
        draw_traffic_lights(screen, traffic_lights, tl_box_img)
        
        # Draw cars
        for direction in ['N', 'S', 'E', 'W']:
            for car in cars[direction]:
                car.draw(screen)
        
        # Draw legend
        draw_legend(screen)
        
        pygame.display.flip()
        
        # Save frame to video if recording
        if is_recording and video_writer:
            # Convert Pygame surface to OpenCV image (RGB -> BGR)
            frame_data = pygame.surfarray.array3d(screen)
            frame_data = np.transpose(frame_data, (1, 0, 2))
            frame_data = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)
            video_writer.write(frame_data)

    if video_writer:
        video_writer.release()
        print(f"Video saved: {video_filename}")
        
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
