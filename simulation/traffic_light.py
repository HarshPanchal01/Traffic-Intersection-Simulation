class TrafficLight:
    def __init__(self, green_time=30, yellow_time=5, red_time=35):
        self.green_time = green_time
        self.yellow_time = yellow_time
        self.red_time = red_time
        self.state = "RED"
        self.timer = 0.0
        
    def update(self, dt):
        self.timer += dt
        # TODO: State machine logic goes here
        pass
