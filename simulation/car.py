import numpy as np

class Car:
    def __init__(self, start_pos, velocity):
        self.pos = np.array(start_pos, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.max_speed = 15.0
        self.acceleration = 2.0
        self.braking = 4.0
        
    def update(self, dt):
        # TODO: Kinematics logic and car following model goes here
        pass
