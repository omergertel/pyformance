from . import Histogram, Meter
import time

class Timer(object):
    def __init__(self, clock = time):
        super(Timer, self).__init__()
        self.meter = Meter(clock)
        self.hist = Histogram(clock)
        
    def get_counter(self):
        return self.hist.get_counter()
    
    def get_sum(self):
        return self.hist.get_sum()
    
    def get_max(self):
        return self.hist.get_max()
    
    def get_min(self):
        return self.hist.get_min()
    
    def get_mean(self):
        return self.hist.get_mean()
    
    def get_stddev(self):
        return self.hist.get_stddev()
    
    def get_var(self):
        return self.hist.get_var()
    
    def get_one_minute_rate(self):
        return self.meter.get_one_minute_rate()
    
    def get_five_minute_rate(self):
        return self.meter.get_five_minute_rate()
    
    def get_fifteen_minute_rate(self):
        return self.meter.get_fifteen_minute_rate()
    
    def _update(self, seconds):
        if seconds>=0:
            self.hist.add(seconds)
            self.meter.mark()
    
    def time(self):
        return TimerContext(self, self.meter.clock)
    
    def clear(self):
        self.hist.clear()
        self.meter.clear()
    
class TimerContext(object):
    def __init__(self, timer, clock):
        super(TimerContext, self).__init__()
        self.clock = clock
        self.timer = timer
        self.start_time = self.clock.time()
        
    def stop(self):
        elapsed = self.clock.time() - self.start_time
        self.timer._update(elapsed)
        return elapsed
    
    def __enter__(self):
        pass
    
    def __exit__(self, t, v, tb):
        self.stop()