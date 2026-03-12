class TrafficLightSystem:
    def __init__(self, ns_green=10.0, ns_yellow=3.0, ew_green=10.0, ew_yellow=3.0):
        self.ns_green = ns_green
        self.ns_yellow = ns_yellow
        self.ew_green = ew_green
        self.ew_yellow = ew_yellow
        
        # States: NS_GREEN, NS_YELLOW, EW_GREEN, EW_YELLOW
        self.state = "NS_GREEN"
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt
        
        if self.state == "NS_GREEN" and self.timer >= self.ns_green:
            self.state = "NS_YELLOW"
            self.timer -= self.ns_green
        elif self.state == "NS_YELLOW" and self.timer >= self.ns_yellow:
            self.state = "EW_GREEN"
            self.timer -= self.ns_yellow
        elif self.state == "EW_GREEN" and self.timer >= self.ew_green:
            self.state = "EW_YELLOW"
            self.timer -= self.ew_green
        elif self.state == "EW_YELLOW" and self.timer >= self.ew_yellow:
            self.state = "NS_GREEN"
            self.timer -= self.ew_yellow

    @property
    def ns_state(self):
        if self.state == "NS_GREEN": return "GREEN"
        if self.state == "NS_YELLOW": return "YELLOW"
        return "RED"

    @property
    def ew_state(self):
        if self.state == "EW_GREEN": return "GREEN"
        if self.state == "EW_YELLOW": return "YELLOW"
        return "RED"
