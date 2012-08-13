import time, random, math
from .snapshot import Snapshot

class ExpDecayingSample(object):
    """
    An exponentially-decaying random sample of longs. Uses Cormode et al's
    forward-decaying priority reservoir sampling method to produce a
    statistically representative sample, exponentially biased towards newer
    entries.

    @see: <a href="http://www.research.att.com/people/Cormode_Graham/library/publications/CormodeShkapenyukSrivastavaXu09.pdf">
          Cormode et al. Forward Decay: A Practical Time Decay Model for
          Streaming Systems. ICDE '09: Proceedings of the 2009 IEEE
          International Conference on Data Engineering (2009)</a>
    """
    DEFAULT_SIZE = 1028
    DEFAULT_ALPHA = 0.015
    RESCALE_THREASHOLD = 3600.0 # 1 hour
    
    def __init__(self, size=DEFAULT_SIZE, alpha=DEFAULT_ALPHA, clock=time):
        """
        Creates a new L{ExponentiallyDecayingSample}.

        @type size: C{int}
        @param size: the number of samples to keep in the sampling reservoir
        @type alpha: C{float}
        @param alpha: the exponential decay factor; the higher this is, the more
                      biased the sample will be towards newer values
        @type clock: C{function}
        @param clock: the function used to return the current time, default to
                      seconds since the epoch; to be used with other time
                      units, or with the twisted clock for our testing purposes
        """
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
        """
        Adds a value to the sample.

        @type value: C{int} or C{float}
        @param value: the value to be added
        """
        if self.size==0:
            return
        self._rescale_if_necessary()
        priority = self._weight(self.clock.time() - self.start_time) / random.random()
        new_counter = self.counter + 1
        self.counter = new_counter
       
        if new_counter <= self.size:
            self.values[priority] = value
        else:
            first = min(self.values)
            if first < priority:
                if priority not in self.values:
                    self.values[priority] = value
                    while first not in self.values:
                        first = min(self.values)
                    del self.values[first]
    
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