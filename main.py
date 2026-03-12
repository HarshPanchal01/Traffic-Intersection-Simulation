import pygame
import sys
from simulation.car import Car
from simulation.traffic_light import TrafficLight
from simulation.spawner import Spawner

# Set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Traffic Intersection Simulation")
    
    # clock object that ensures animation has the same speed on all machines
    clock = pygame.time.Clock()

    print('--------------------------------')
    print('Usage:')
    print('Press (q) to stop the simulation')
    print('--------------------------------')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        # Draw environment
        draw_intersection(screen)
        
        # TODO: Update and draw simulation components
        
        pygame.display.flip()
        
        # 60 fps
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
