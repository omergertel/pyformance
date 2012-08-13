import math
from threading import Lock
import random
import time

class ExpWeightedMovingAvg(object):
    """
    An exponentially-weighted moving average.
    """
    INTERVAL = 5.0 # seconds
    SECONDS_PER_MINUTE = 60.0
    
    def __init__(self, minutes):
        super(ExpWeightedMovingAvg, self).__init__()
        self.alpha = self._calc_alpha(minutes)
        self.uncounted = 0
        self.rate = -1
        
    def get_rate(self):
        if self.rate >= 0:
            return self.rate
        return 0
    
    def add(self, value):
        self.uncounted = self.uncounted + value
        
    def tick(self):
        rate = self.uncounted / ExpWeightedMovingAvg.INTERVAL
        self.uncounted = 0
        if self.rate < 0:
            self.rate = rate
        else:
            self.rate = self.rate + (self.alpha * (rate - self.rate))
    
    def _calc_alpha(self, minutes):
        return 1 - math.exp(-ExpWeightedMovingAvg.INTERVAL / ExpWeightedMovingAvg.SECONDS_PER_MINUTE / minutes);
    
class ExpDecayingSample(object):
    DEFAULT_SIZE = 1028
    DEFAULT_ALPHA = 0.015
    RESCALE_THREASHOLD = 3600.0 # 1 hour
    
    def __init__(self, size=DEFAULT_SIZE, alpha=DEFAULT_ALPHA, clock=time):
        super(ExpDecayingSample, self).__init__()
        self.clock = clock
        self.size = size
        self.alpha = alpha
        self.clear()
        
    def clear(self):
        self.values = {}
        self.counter = 0
        self.start_time = self.clock.time()
        self.next_time = self.clock.time() + ExpDecayingSample.RESCALE_THREASHOLD
        
    def get_size(self):
        return self.counter if self.counter < self.size else self.size
    
    def update(self, value):
        self._rescale_if_necessary()
        priority = self._weight(self.clock.time() - self.start_time) / random.random()
        new_counter = self.counter + 1
        self.counter = new_counter
       
        if new_counter <= self.size:
            self.values[priority] = value
        else:
            first = self.values.iterkeys().next()
            if first < priority:
                if not priority in self.values:
                    del self.values[first]
                self.values[priority] = value
    
    def _rescale_if_necessary(self):
        if self.clock.time() >= self.next_time:
            self._rescale()
            
    def _rescale(self):
        self.next_time = self.clock.time() + ExpDecayingSample.RESCALE_THREASHOLD
        old_start_time = self.start_time
        self.start_time = self.clock.time()
        for key, val in self.values.items():
            del self.values[key]
            self.values[key * math.exp(-self.alpha * (self.start_time - old_start_time))] = val
        self.counter = len(self.values)
        
    def _weight(self, value):
        return math.exp(self.alpha * value)
        
    def get_snapshot(self):
        return Snapshot(self.values.values())
    
class Snapshot(object):
    MEDIAN = 0.5
    P75_Q = 0.75
    P95_Q = 0.95
    P99_Q = 0.99
    P999_Q = 0.999
    
    def __init__(self, values):
        super(Snapshot, self).__init__()
        self.values = values
        self.values.sort()
        
    def get_size(self):
        return len(self.values)
        
    def get_median(self):
        return self.get_percentile(Snapshot.MEDIAN)
    
    def get_75th_percentile(self):
        return self.get_percentile(Snapshot.P75_Q)
    
    def get_95th_percentile(self):
        return self.get_percentile(Snapshot.P95_Q)
    
    def get_99th_percentile(self):
        return self.get_percentile(Snapshot.P99_Q)
    
    def get_999th_percentile(self):
        return self.get_percentile(Snapshot.P999_Q)
    
    def get_percentile(self, percentile):
        if percentile < 0 or percentile > 1:
            raise ValueError("{} is not in [0..1]".format(percentile))
        length = len(self.values)
        if length==0:
            return 0
        pos = percentile * (length + 1)
        if pos<1:
            return self.values[0]
        if pos>=length:
            return self.values[-1]
        lower = self.values[int(pos)-1]
        upper = self.values[int(pos)]
        return lower + (pos-int(pos))*(upper-lower)