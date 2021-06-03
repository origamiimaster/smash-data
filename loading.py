"""Loading bar code"""
import sys
import datetime
class LoadingBar:
    total = 0
    width = 40
    current = 0
    error = ""
    def __init__(self, total_intervals):
        self.total = total_intervals
    def add_error(self, error):
        self.error = error
    def print(self):
        string_to_print = "{0:.1f}%".format(100.0 * self.current / self.total) + "|"
        for i in range(self.width):
            if i < self.current*self.width / self.total:
                string_to_print += "█"
            else:
                string_to_print += '-'
        string_to_print += '|' + str(self.current) + "/" + str(self.total) + "(" + self.error + ")"
        sys.stdout.write("\b" * (len(string_to_print) + self.width))
        sys.stdout.write(string_to_print)
        sys.stdout.flush()
    def increment(self):
        self.current += 1
    def set(self, value):
        self.current = value

class Timer:
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.curr_time = datetime.datetime.now()
        self.total_events = 0
        self.time_passed = 0
    def update(self):
        self.total_events += 1
        self.curr_time = datetime.datetime.now()
        self.time_passed = self.curr_time - self.start_time
    def get_avg(self):
        if self.total_events == 0:
            return 0
        return self.time_passed / self.total_events
    def predict(self, future_events):
        return self.get_avg() * (future_events - self.total_events)
    def get_total(self):
        return self.time_passed

class TimingBar(Timer):
    def __init__(self, total_intervals):
        Timer.__init__(self)
        self.loader = LoadingBar(total_intervals)
    

if __name__ == "__main__":
    import time
    import random
    my_progress = LoadingBar(59674)
    my_progress.print()
    for _ in range(10):
        time.sleep(.1)
        my_progress.increment()
        my_progress.print()
    my_progress.add_error("TESTING ERROR")
    for _ in range(10):
        time.sleep(.1)
        my_progress.increment()
        my_progress.print()
    my_progress.add_error("WRONG")
    for _ in range(59000):
        time.sleep(.01)
        if random.random() > 0.5:
            my_progress.add_error(random.choice(["Error", " Something went wrong", "t", "afdsgf", ""]))
        my_progress.increment()
        my_progress.print()
