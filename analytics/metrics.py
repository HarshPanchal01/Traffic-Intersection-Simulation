class Metrics:
    def __init__(self):
        self.wait_times = []
        self.queue_lengths = []
        self.throughput = 0
        
    def record_wait_time(self, time):
        self.wait_times.append(time)
        
    def record_queue_length(self, length):
        self.queue_lengths.append(length)
