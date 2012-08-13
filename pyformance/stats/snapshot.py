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