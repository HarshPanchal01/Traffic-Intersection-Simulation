import numpy as np

class Spawner:
    def __init__(self, rate):
        """
        Initializes the vehicle spawner.
        
        Args:
            rate (float): The arrival rate parameter (lambda) for the Poisson distribution representing vehicles per second.
        """
        self.rate = rate 
        self.timer = 0.0
        self.time_to_next = self._get_next_time()
        
    def _get_next_time(self):
        """
        Calculates the time until the next vehicle arrives.
        
        Uses the Inverse Transform Sampling method to generate exponentially distributed 
        time intervals. This models a Poisson process, simulating natural traffic 
        clustering and gaps.
        
        Mathematical Formulation:
        The Cumulative Distribution Function (CDF) of an exponential distribution is:
            F(x) = 1 - e^(-lambda * x)
        
        Setting U = F(x), where U is a uniform random variable in [0, 1), we can 
        solve for x (the time until the next event):
            U = 1 - e^(-lambda * x)
            e^(-lambda * x) = 1 - U
            -lambda * x = ln(1 - U)
            x = -(1 / lambda) * ln(1 - U)
            
        Returns:
            float: Time in seconds until the next vehicle spawns.
        """
        U = np.random.random()
        # Prevent math domain error for log(0) if U exactly equals 1.0
        if U == 1.0: U = 0.999
        return - (1.0 / self.rate) * np.log(1.0 - U)

    def update(self, dt):
        """
        Advances the spawner's timer by dt and returns any vehicles that should 
        spawn during this time step.
        """
        self.timer += dt
        spawned = []
        
        while self.timer >= self.time_to_next:
            self.timer -= self.time_to_next
            
            # Randomly distribute traffic across the 4 cardinal directions
            direction = np.random.choice(['N', 'S', 'E', 'W'])
            
            # Weighted probabilities for turning behavior
            # Most vehicles go straight (60%), some turn left (20%) or right (20%)
            turn = np.random.choice(['straight', 'left', 'right'], p=[0.6, 0.2, 0.2])
            
            # Assign lane based on turn intention
            lane = 'left' if turn == 'left' else 'right'
            
            # Randomly determine vehicle type with realistic proportions
            vehicle_type = np.random.choice(['car', 'small_car', 'bus', 'truck'], p=[0.55, 0.20, 0.10, 0.15])
            
            spawned.append((direction, turn, lane, vehicle_type))
            
            # Calculate time for the *next* vehicle arrival
            self.time_to_next = self._get_next_time()
            
        return spawned
