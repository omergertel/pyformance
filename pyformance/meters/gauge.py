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

