import numpy as np
from scipy.integrate import ode
import pygame

class Car:
    def __init__(self, direction, start_pos):
        self.direction = direction # 'N', 'S', 'E', 'W'
        
        # State: [position_1d, velocity_1d]
        self.state = [0.0, 15.0] # start at 0 local distance, initial speed 15
        
        self.start_pos = np.array(start_pos, dtype=float)
        
        # Scale: pixels are our meters for simplicity, so speeds/accels are in px/s or px/s^2.
        # But let's assume 1 pixel = 1 meter, so 15 m/s = 54 km/h (reasonable city speed).
        self.max_speed = 40.0
        self.acceleration = 15.0
        self.braking = 30.0
        self.t = 0.0
        
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_initial_value(self.state, self.t)
        
        # Dimensions for drawing
        self.length = 40
        self.width = 20
        # Random car color
        self.color = (np.random.randint(50, 255), np.random.randint(50, 255), np.random.randint(50, 255))
        
    def f(self, t, state, a):
        x, v = state
        return [v, a]

    def get_2d_position(self):
        pos_1d = self.state[0]
        if self.direction == 'N': # Coming from North, moving South (+y)
            return [self.start_pos[0], self.start_pos[1] + pos_1d]
        elif self.direction == 'S': # Coming from South, moving North (-y)
            return [self.start_pos[0], self.start_pos[1] - pos_1d]
        elif self.direction == 'E': # Coming from East, moving West (-x)
            return [self.start_pos[0] - pos_1d, self.start_pos[1]]
        elif self.direction == 'W': # Coming from West, moving East (+x)
            return [self.start_pos[0] + pos_1d, self.start_pos[1]]

    def update(self, dt, light_state, distance_to_car_ahead):
        v = self.state[1]
        
        # Distance to stop line.
        # Intersection is at center (400, 400), road width is 160.
        # If car starts at edge of screen (0 or 800), distance to stop line is 320.
        dist_to_stop_line = 320.0 - self.state[0]
        
        a = 0.0
        braking_dist = (v**2) / (2 * self.braking) if v > 0 else 0.0
        
        stopping_for_light = False
        # Stop for RED or YELLOW if we are before the stop line and can stop safely
        if light_state in ['RED', 'YELLOW'] and dist_to_stop_line > 0:
            if dist_to_stop_line <= braking_dist + 15.0: # 15m buffer to stop line
                stopping_for_light = True
                
        stopping_for_car = False
        if distance_to_car_ahead is not None:
            if distance_to_car_ahead <= braking_dist + self.length + 20.0: # Safe following distance
                stopping_for_car = True
                
        if stopping_for_car or stopping_for_light:
            a = -self.braking
            # Bring to a complete stop gracefully if very close and very slow
            if v <= 1.0 and ((stopping_for_light and dist_to_stop_line < 20.0) or (stopping_for_car and distance_to_car_ahead < self.length + 25.0)):
                a = 0.0
                self.state[1] = 0.0 # fully stopped
        else:
            if v < self.max_speed:
                a = self.acceleration
            else:
                a = 0.0 # cruising
                
        # Prevent moving backward
        if v < 0.0 and a < 0.0:
            a = 0.0
            self.state[1] = 0.0
            
        self.solver.set_f_params(a)
        if self.solver.successful():
            self.solver.integrate(self.t + dt)
            self.t += dt
            self.state = self.solver.y
            
            # Prevent negative velocity
            if self.state[1] < 0:
                self.state[1] = 0.0

    def draw(self, screen):
        cx, cy = self.get_2d_position()
        # Create a surface for the car
        if self.direction in ['N', 'S']:
            rect = pygame.Rect(0, 0, self.width, self.length)
        else:
            rect = pygame.Rect(0, 0, self.length, self.width)
            
        rect.center = (cx, cy)
        pygame.draw.rect(screen, self.color, rect)
