__import__('pkg_resources').declare_namespace(__name__)

from .meters import Counter, Histogram, Timer, Meter
   
class MetricsRegistry(object):
    def __init__(self):
        super(MetricsRegistry, self).__init__()
        self._meters = {}
        
    def add(self, metric_name, meter):
        if meter is not None:
            self._meters[metric_name]=meter
        return meter
    
    def get(self, metric_name):
        return self._meters[metric_name]

class MetricName(object):
    def __init__(self, cls, name, scope):
        self.cls = cls
        self.name = name
        self.scope = scope
        self._hash = (self.cls.__name__ + '.' + self.name).__hash__()
    
    def __hash__(self, *args, **kwargs):
        return self._hash
    
registry = MetricsRegistry()

def add_metric(cls, name, metric, scope=None):
    return registry.add(MetricName(cls, name, scope), metric)

def add_meter(cls, name, scope=None):
    return add_metric(cls, name, Meter(), scope)

def add_counter(cls, name, scope=None):
    return add_metric(cls, name, Counter(), scope)

def add_histogram(cls, name, scope=None):
    return add_metric(cls, name, Histogram(), scope)

def add_timer(cls, name, scope=None):
    return add_metric(cls, name, Timer(), scope)
