from threading import Lock
from stats import ExpWeightedMovingAvg, ExpDecayingSample
import sys
import math
import time

class Gauge(object):
    """
    A base class for reading of a particular.
    
    For example, to instrument a queue depth:
    
    class QueueLengthGaguge(Gauge):
        def __init__(self, queue):
            super(QueueGaguge, self).__init__()
            self.queue = queue
        
        def get_value(self):
            return len(self.queue)
    
    """
    def get_value(self):
        raise NotImplementedError()
    
class CallBackGauge(Gauge):
    """
    A Gauge reading for a given callback
    """
    def __init__(self, callback):
        super(CallBackGauge, self).__init__()
        self.callback = callback
        
    def get_value(self):
        return self.callback()

class Counter(object):
    """
    An incrementing and decrementing metric
    """
    def __init__(self):
        super(Counter, self).__init__()
        self.lock = Lock()
        self.counter = 0
        
    def inc(self, val=1):
        with self.lock:
            self.counter = self.counter + val
        
    def dec(self, val=1):
        self.inc(-val)
        
    def get_count(self):
        return self.counter
    
    def clear(self):
        with self.lock:
            self.counter = 0

class Meter(object):
    """
    A meter metric which measures mean throughput and one-, five-, and fifteen-minute
    exponentially-weighted moving average throughputs.
    """
    TICK_INTERVAL = 5.0 # seconds
    def __init__(self, clock = time):
        super(Meter, self).__init__()
        self.clock = clock
        self.lock = Lock()
        self.start_time = self.last_tick = self.clock.time()
        self.counter = 0.0
        self.m1rate = ExpWeightedMovingAvg(minutes=1)
        self.m5rate = ExpWeightedMovingAvg(minutes=5)
        self.m15rate = ExpWeightedMovingAvg(minutes=15)
               
    def get_one_minute_rate(self):
        self._tick_if_necessary()
        return self.m1rate.get_rate()
    
    def get_five_minute_rate(self):
        self._tick_if_necessary()
        return self.m5rate.get_rate()
    
    def get_fifteen_minute_rate(self):
        self._tick_if_necessary()
        return self.m15rate.get_rate()
    
    def _tick_if_necessary(self):
        new_tick = self.clock.time()
        age = new_tick - self.last_tick
        if age > Meter.TICK_INTERVAL:
            with self.lock:
                self.last_tick = new_tick
            required_ticks = int(age/Meter.TICK_INTERVAL)
            for i in xrange(required_ticks):
                self.tick()
                
    def tick(self):
        self.m1rate.tick()
        self.m5rate.tick()
        self.m15rate.tick()
        
    def mark(self, value=1):
        self._tick_if_necessary()
        with self.lock:
            self.counter = self.counter + value
            self.m1rate.add(value)
            self.m5rate.add(value)
            self.m15rate.add(value)
    
    def get_count(self):
        return self.counter
    
    def get_mean_rate(self):
        if self.counter==0:
            return 0;
        elapsed = self.clock.time() - self.start_time
        return self.counter / elapsed;

    def _convertNsRate(self, ratePerNs):
        return ratePerNs;

class Histogram(object):
    def __init__(self, size=ExpDecayingSample.DEFAULT_SIZE, alpha=ExpDecayingSample.DEFAULT_ALPHA, clock = time):
        super(Histogram, self).__init__()
        self.lock = Lock()
        self.clock = clock
        self.sample = ExpDecayingSample(size, alpha, clock)
        self.clear()

    def add(self,value):
        with self.lock:
            self.sample.update(value)
            self.counter = self.counter+1
            self.max = value if value>self.max else self.max
            self.min = value if value<self.min else self.min
            self.sum = self.sum + value
            self._update_var(value)
            
    def clear(self):
        with self.lock:
            self.sample.clear()
            self.counter = 0.0
            self.min = sys.maxint
            self.max = -sys.maxint - 1
            self.sum = 0.0
            self.var = [-1.0,0.0]
    
    def get_count(self):
        return self.counter
    
    def get_sum(self):
        return self.sum
    
    def get_max(self):
        return self.max
    
    def get_min(self):
        return self.min
    
    def get_mean(self):
        if self.counter > 0:
            return self.sum / self.counter
        return 0
    
    def get_stddev(self):
        if self.counter > 0:
            return math.sqrt(self.get_var())
        return 0
    
    def get_var(self):
        if self.counter > 1:
            return self.var[1] / (self.counter -1)
        return 0
    
    def get_snapshot(self):
        return self.sample.get_snapshot()
    
    def _update_var(self, value):
        old_m, old_s = self.var
        new_m, new_s = [0.0,0.0]
        if old_m == -1:
            new_m = value
        else:
            new_m = old_m + ((value-old_m) / self.counter)
            new_s = old_s + ((value-old_m) * (value - new_m))
        self.var = [new_m, new_s]
                
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