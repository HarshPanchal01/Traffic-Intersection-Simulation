import pygame
import sys
from simulation.car import Car
from simulation.traffic_light import TrafficLightSystem
from simulation.spawner import Spawner

# Set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRASS_COLOR = (34, 139, 34)
ROAD_COLOR = (50, 50, 50)
YELLOW_LINE = (255, 204, 0)

WIDTH, HEIGHT = 800, 800
ROAD_WIDTH = 160

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
    
    # Draw stop lines
    # North (cars coming from north, stop line on the right side of the road)
    pygame.draw.line(screen, WHITE, (center_x - ROAD_WIDTH // 2, center_y - ROAD_WIDTH // 2), (center_x, center_y - ROAD_WIDTH // 2), 4)
    # South (cars coming from south)
    pygame.draw.line(screen, WHITE, (center_x, center_y + ROAD_WIDTH // 2), (center_x + ROAD_WIDTH // 2, center_y + ROAD_WIDTH // 2), 4)
    # West (cars coming from west)
    pygame.draw.line(screen, WHITE, (center_x - ROAD_WIDTH // 2, center_y), (center_x - ROAD_WIDTH // 2, center_y + ROAD_WIDTH // 2), 4)
    # East (cars coming from east)
    pygame.draw.line(screen, WHITE, (center_x + ROAD_WIDTH // 2, center_y - ROAD_WIDTH // 2), (center_x + ROAD_WIDTH // 2, center_y), 4)

def draw_traffic_lights(screen, traffic_lights):
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    def get_color(state):
        if state == "GREEN": return GREEN
        if state == "YELLOW": return YELLOW
        return RED

    ns_color = get_color(traffic_lights.ns_state)
    ew_color = get_color(traffic_lights.ew_state)
    
    radius = 12
    offset_x = ROAD_WIDTH // 2 + 20
    offset_y = ROAD_WIDTH // 2 + 20
    
    # Draw light housing (black rectangles)
    pygame.draw.rect(screen, BLACK, (center_x - offset_x - radius - 2, center_y + offset_y - radius - 2, radius*2 + 4, radius*2 + 4)) # South approaching
    pygame.draw.rect(screen, BLACK, (center_x + offset_x - radius - 2, center_y - offset_y - radius - 2, radius*2 + 4, radius*2 + 4)) # North approaching
    pygame.draw.rect(screen, BLACK, (center_x - offset_x - radius - 2, center_y - offset_y - radius - 2, radius*2 + 4, radius*2 + 4)) # West approaching
    pygame.draw.rect(screen, BLACK, (center_x + offset_x - radius - 2, center_y + offset_y - radius - 2, radius*2 + 4, radius*2 + 4)) # East approaching
    
    # North approaching (NS light) - top-right
    pygame.draw.circle(screen, ns_color, (center_x + offset_x, center_y - offset_y), radius)
    # South approaching (NS light) - bottom-left
    pygame.draw.circle(screen, ns_color, (center_x - offset_x, center_y + offset_y), radius)
    
    # West approaching (EW light) - top-left
    pygame.draw.circle(screen, ew_color, (center_x - offset_x, center_y - offset_y), radius)
    # East approaching (EW light) - bottom-right
    pygame.draw.circle(screen, ew_color, (center_x + offset_x, center_y + offset_y), radius)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Traffic Intersection Simulation")
    
    # clock object that ensures animation has the same speed on all machines
    clock = pygame.time.Clock()

    traffic_lights = TrafficLightSystem()
    spawner = Spawner(rate=0.5) # 0.5 cars per second
    
    cars = {'N': [], 'S': [], 'E': [], 'W': []}
    
    start_positions = {
        'N': (360, 0),
        'S': (440, 800),
        'E': (800, 360),
        'W': (0, 440)
    }

    print('--------------------------------')
    print('Usage:')
    print('Press (q) to stop the simulation')
    print('--------------------------------')

    running = True
    while running:
        # Calculate delta time in seconds
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        # Update logic
        traffic_lights.update(dt)
        
        # Spawner logic
        new_cars = spawner.update(dt)
        for direction in new_cars:
            if not cars[direction] or cars[direction][-1].state[0] > 60.0:
                cars[direction].append(Car(direction, start_positions[direction]))

        # Update cars
        for direction in ['N', 'S', 'E', 'W']:
            if direction in ['N', 'S']:
                light_state = traffic_lights.ns_state
            else:
                light_state = traffic_lights.ew_state
                
            for i, car in enumerate(cars[direction]):
                dist_ahead = None
                if i > 0:
                    dist_ahead = cars[direction][i-1].state[0] - car.state[0]
                    
                car.update(dt, light_state, dist_ahead)

        # Remove cars that have left the screen
        for direction in ['N', 'S', 'E', 'W']:
            cars[direction] = [car for car in cars[direction] if car.state[0] < 900.0]

        # Draw environment
        draw_intersection(screen)
        draw_traffic_lights(screen, traffic_lights)
        
        # Draw cars
        for direction in ['N', 'S', 'E', 'W']:
            for car in cars[direction]:
                car.draw(screen)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
