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

WIDTH, HEIGHT = 800, 800

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

        # Clear the background
        screen.fill(BLACK)
        
        # TODO: Update and draw simulation components
        
        pygame.display.flip()
        
        # 60 fps
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
