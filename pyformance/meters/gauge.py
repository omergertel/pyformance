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


class CallbackGauge(Gauge):

    """
    A Gauge reading for a given callback
    """

    def __init__(self, callback):
        super(CallbackGauge, self).__init__()
        self.callback = callback

    def get_value(self):
        return self.callback()

    
class SimpleGauge(Gauge):
    """
    A gauge which holds values with simple getter- and setter-interface
    """
    
    def __init__(self, value=float("nan")):
        super(SimpleGauge, self).__init__()
        self._value = value

    def get_value(self):
        return self._value

    def set_value(self, value):
        # XXX: add locking?
        self._value = value
