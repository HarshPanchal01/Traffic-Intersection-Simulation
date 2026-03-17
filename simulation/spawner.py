import numpy as np

class Spawner:
    def __init__(self, rate):
        # Arrival rate parameter for Poisson distribution (vehicles per second)
        self.rate = rate 
        self.timer = 0.0
        self.time_to_next = self._get_next_time()
        
    def _get_next_time(self):
        # Using the inverse CDF method for exponential distribution from the lecture
        # F^{-1}(x) = -1/lambda * ln(1 - U)
        U = np.random.random()
        # Prevent math domain error
        if U == 1.0: U = 0.999
        return - (1.0 / self.rate) * np.log(1.0 - U)

    def update(self, dt):
        self.timer += dt
        spawned = []
        while self.timer >= self.time_to_next:
            self.timer -= self.time_to_next
            # Pick a random direction
            direction = np.random.choice(['N', 'S', 'E', 'W'])
            # Pick a random turn with weighted probabilities
            turn = np.random.choice(['straight', 'left', 'right'], p=[0.6, 0.2, 0.2])
            lane = 'left' if turn == 'left' else 'right'
            # Pick a random vehicle type
            vehicle_type = np.random.choice(['car', 'small_car', 'bus', 'truck'], p=[0.55, 0.20, 0.10, 0.15])
            spawned.append((direction, turn, lane, vehicle_type))
            self.time_to_next = self._get_next_time()
        return spawned
