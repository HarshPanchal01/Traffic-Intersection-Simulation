import numpy as np

class MetricsManager:
    """
    Collects and processes performance metrics during the simulation.
    """
    def __init__(self):
        self.completed_wait_times = []
        self.total_vehicles_exited = 0
        self.max_queue_length = 0
        
        self.start_time = 0.0

    def add_completed_vehicle(self, vehicle):
        """
        Records the wait time of a vehicle that has successfully crossed 
        and exited the simulation bounds.
        """
        self.completed_wait_times.append(vehicle.wait_time)
        self.total_vehicles_exited += 1

    def update_max_queue(self, cars_dict):
        """
        Calculates the longest continuous line of stopped vehicles across all lanes.
        Vehicles are considered queued if their velocity is near zero and they 
        haven't crossed the stop line.
        """
        current_max = 0
        for direction in ['N', 'S', 'E', 'W']:
            # Count vehicles in each direction that are stationary before the stop line
            queue = [c for c in cars_dict[direction] if c.state[0] < 300.0 and c.state[1] < 0.1]
            current_max = max(current_max, len(queue))
        
        self.max_queue_length = max(self.max_queue_length, current_max)

    def get_avg_wait_time(self):
        """ Returns the global average wait time for all completed vehicles. """
        if not self.completed_wait_times:
            return 0.0
        return np.mean(self.completed_wait_times)

    def get_throughput(self, current_time):
        """ 
        Calculates throughput: the rate of vehicles successfully clearing the 
        intersection per minute.
        """
        if current_time <= 0:
            return 0.0
        # vehicles per minute
        return (self.total_vehicles_exited / current_time) * 60.0
