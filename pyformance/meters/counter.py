from threading import Lock
from .base_metric import BaseMetric


class Counter(BaseMetric):

    """
    An incrementing and decrementing metric
    """

    def __init__(self, key, tags=None):
        super(Counter, self).__init__(key, tags)
        self.lock = Lock()
        self.counter = 0

    def inc(self, val=1):
        "increment counter by val (default is 1)"
        with self.lock:
            self.counter = self.counter + val

    def dec(self, val=1):
        "decrement counter by val (default is 1)"
        self.inc(-val)

    def get_count(self):
        "return current value of counter"
        return self.counter

    def clear(self):
        "reset counter to 0"
        with self.lock:
            self.counter = 0
