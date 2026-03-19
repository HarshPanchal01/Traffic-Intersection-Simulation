import numpy as np

class TrafficLightSystem:
    def __init__(self, ns_green=10.0, ns_yellow=3.0, ew_green=10.0, ew_yellow=3.0):
        self.ns_green = ns_green
        self.ns_yellow = ns_yellow
        self.ew_green = ew_green
        self.ew_yellow = ew_yellow
        
        # States: NS_GREEN, NS_YELLOW, ALL_RED_NS, EW_GREEN, EW_YELLOW, ALL_RED_EW
        self.state = "NS_GREEN"
        self.timer = 0.0
        self.current_all_red_time = 0.0

    def _get_random_all_red_time(self):
        """
        Returns a random all-red clearance phase time between 1.0 and 3.0 seconds.
        This provides a realistic buffer between crossing light changes to prevent T-bone collisions.
        """
        return np.random.uniform(1.0, 3.0)

    def update(self, dt):
        """
        Updates the state machine based on the elapsed time (dt).
        """
        self.timer += dt
        
        if self.state == "NS_GREEN" and self.timer >= self.ns_green:
            self.state = "NS_YELLOW"
            self.timer -= self.ns_green
        elif self.state == "NS_YELLOW" and self.timer >= self.ns_yellow:
            self.state = "ALL_RED_NS"
            self.timer -= self.ns_yellow
            self.current_all_red_time = self._get_random_all_red_time()
        elif self.state == "ALL_RED_NS" and self.timer >= self.current_all_red_time:
            self.state = "EW_GREEN"
            self.timer -= self.current_all_red_time
        elif self.state == "EW_GREEN" and self.timer >= self.ew_green:
            self.state = "EW_YELLOW"
            self.timer -= self.ew_green
        elif self.state == "EW_YELLOW" and self.timer >= self.ew_yellow:
            self.state = "ALL_RED_EW"
            self.timer -= self.ew_yellow
            self.current_all_red_time = self._get_random_all_red_time()
        elif self.state == "ALL_RED_EW" and self.timer >= self.current_all_red_time:
            self.state = "NS_GREEN"
            self.timer -= self.current_all_red_time

    @property
    def ns_state(self):
        """ Returns the simple GREEN/YELLOW/RED state for the North/South direction. """
        if self.state == "NS_GREEN": return "GREEN"
        if self.state == "NS_YELLOW": return "YELLOW"
        return "RED" # Applies for ALL_RED_NS, EW_GREEN, EW_YELLOW, ALL_RED_EW

    @property
    def ew_state(self):
        """ Returns the simple GREEN/YELLOW/RED state for the East/West direction. """
        if self.state == "EW_GREEN": return "GREEN"
        if self.state == "EW_YELLOW": return "YELLOW"
        return "RED" # Applies for ALL_RED_EW, NS_GREEN, NS_YELLOW, ALL_RED_NS
