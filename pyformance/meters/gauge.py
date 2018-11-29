from .base_metric import BaseMetric


class Gauge(BaseMetric):

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
        "A subclass of Gauge should implement this method"
        raise NotImplementedError()


class CallbackGauge(Gauge):

    """
    A Gauge reading for a given callback
    """

    def __init__(self, callback, key, tags=None):
        "constructor expects a callable"
        super(CallbackGauge, self).__init__(key, tags)
        self.callback = callback

    def get_value(self):
        "returns the result of callback which is executed each time"
        return self.callback()


class SimpleGauge(Gauge):

    """
    A gauge which holds values with simple getter- and setter-interface
    """

    def __init__(self, key, value=float("nan"), tags=None):
        "constructor accepts initial value"
        super(SimpleGauge, self).__init__(key, tags)
        self._value = value

    def get_value(self):
        "getter returns current value"
        return self._value

    def set_value(self, value):
        "setter changes current value"
        # XXX: add locking?
        self._value = value
