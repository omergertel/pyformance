from . import Histogram, Meter
from blinker import Namespace
import time

timer_signals = Namespace()
call_too_long = timer_signals.signal("call_too_long")

class Timer(object):
    def __init__(self, threshold = None, clock = time):
        super(Timer, self).__init__()
        self.meter = Meter(clock=clock)
        self.hist = Histogram(clock=clock)
        self.threshold = threshold
        
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
    
    def time(self, **kwargs):
        """
        Parameters will be sent to signal, if fired.
        """
        return TimerContext(self, self.meter.clock, **kwargs)
    
    def clear(self):
        self.hist.clear()
        self.meter.clear()
    
class TimerContext(object):
    def __init__(self, timer, clock, **kwargs):
        super(TimerContext, self).__init__()
        self.clock = clock
        self.timer = timer
        self.start_time = self.clock.time()
        self.kwargs = kwargs
        
    def stop(self):
        elapsed = self.clock.time() - self.start_time
        self.timer._update(elapsed)
        if self.timer.threshold and self.timer.threshold < elapsed:
            call_too_long.send(self.timer, elapsed=elapsed, **self.kwargs)
        return elapsed
    
    def __enter__(self):
        pass
    
    def __exit__(self, t, v, tb):
        self.stop()