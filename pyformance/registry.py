import re
from time import time
from .meters import Counter, Histogram, Meter, Timer

class MetricsRegistry(object):
    """
    A single interface used to gather metrics on a service. It keeps track of
    all the relevant Counters, Meters, Histograms, and Timers. It does not have
    a reference back to its service. The service would create a
    L{MetricsRegistry} to manage all of its metrics tools.
    """
    def __init__(self, clock=time):
        """
        Creates a new L{MetricsRegistry} instance.
        """
        self._timers = {}
        self._meters = {}
        self._counters = {}
        self._histograms = {}
        self._gauges = {}
        self._clock = clock

    def counter(self, key):
        """
        Gets a counter based on a key, creates a new one if it does not exist.

        @param key: name of the metric
        @type key: C{str}

        @return: L{Counter}
        """
        if key not in self._counters:
            self._counters[key] = Counter()
        return self._counters[key]

    def histogram(self, key):
        """
        Gets a histogram based on a key, creates a new one if it does not exist.

        @param key: name of the metric
        @type key: C{str}

        @return: L{Histogram}
        """
        if key not in self._histograms:
            self._histograms[key] = Histogram()
        return self._histograms[key]

    def gauge(self, key, gauge = None):
        if key not in self._gauges:
            self._gauges[key] = gauge
        return self._gauges[key]

    def meter(self, key):
        """
        Gets a meter based on a key, creates a new one if it does not exist.

        @param key: name of the metric
        @type key: C{str}

        @return: L{Meter}
        """
        if key not in self._meters:
            self._meters[key] = Meter()
        return self._meters[key]

    def timer(self, key):
        """
        Gets a timer based on a key, creates a new one if it does not exist.

        @param key: name of the metric
        @type key: C{str}

        @return: L{Timer}
        """
        if key not in self._timers:
            self._timers[key] = Timer()
        return self._timers[key]

    def clear(self):
        self._meters.clear()
        self._counters.clear()
        self._gauges.clear()
        self._timers.clear()
        self._histograms.clear()

    def _get_counter_metrics(self, key):
        if key in self._counters:
            counter = self._counters[key]
            return {"count": counter.get_count()}
        return {}

    def _get_histogram_metrics(self, key):
        if key in self._histograms:
            histogram = self._histograms[key]
            snapshot = histogram.get_snapshot()
            res = {"avg": histogram.get_mean(),
                   "count": histogram.get_count(),
                   "max": histogram.get_max(),
                   "min": histogram.get_min(),
                   "std_dev": histogram.get_stddev(),
                   "75_percentile": snapshot.get_75th_percentile(),
                   "95_percentile": snapshot.get_95th_percentile(),
                   "99_percentile": snapshot.get_99th_percentile(),
                   "999_percentile": snapshot.get_999th_percentile()}
            return res
        return {}

    def _get_meter_metrics(self, key):
        if key in self._meters:
            meter = self._meters[key]
            res = {"15m_rate": meter.get_fifteen_minute_rate(),
                   "5m_rate": meter.get_five_minute_rate(),
                   "1m_rate": meter.get_one_minute_rate(),
                   "mean_rate": meter.get_mean_rate()}
            return res
        return {}

    def _get_timer_metrics(self, key):
        if key in self._timers:
            timer = self._timers[key]
            snapshot = timer.get_snapshot()
            res = {"avg": timer.get_mean(),
                   "count": timer.get_count(),
                   "max": timer.get_max(),
                   "min": timer.get_min(),
                   "std_dev": timer.get_stddev(),
                   "15m_rate": timer.get_fifteen_minute_rate(),
                   "5m_rate": timer.get_five_minute_rate(),
                   "1m_rate": timer.get_one_minute_rate(),
                   "mean_rate": timer.get_mean_rate(),
                   "75_percentile": snapshot.get_75th_percentile(),
                   "95_percentile": snapshot.get_95th_percentile(),
                   "99_percentile": snapshot.get_99th_percentile(),
                   "999_percentile": snapshot.get_999th_percentile()}
            return res
        return {}

    def get_metrics(self, key):
        """
        Gets all the metrics for a specified key.

        @param key: name of the metric
        @type key: C{str}

        @return: C{dict}
        """
        metrics = {}
        for getter in (self._get_counter_metrics, self._get_histogram_metrics,
                       self._get_meter_metrics, self._get_timer_metrics):
            metrics.update(getter(key))
        return metrics

    def dump_metrics(self):
        """
        Formats all of the metrics and returns them as a dict.

        @return: C{list} of C{dict} of metrics
        """
        metrics = {}
        for metric_type in (self._counters, 
                            self._histograms,
                            self._meters, 
                            self._timers):
            for key in metric_type.keys():
                metrics[key] = self.get_metrics(key)
                
        return metrics

class RegexRegistry(MetricsRegistry):
    """
    A single interface used to gather metrics on a service. This class uses a regex to combine
    measures that match a pattern. For example, if you have a REST API, instead of defining
    a timer for each method, you can use a regex to capture all API calls and group them.
    A pattern like '^/api/(?P<model>)/\d+/(?P<verb>)?$' will group and measure the following:
        /api/users/1 -> users
        /api/users/1/edit -> users/edit
        /api/users/2/edit -> users/edit
    """
    def __init__(self, pattern=None, clock=time):
        super(RegexRegistry, self).__init__(clock)
        if pattern is not None:
            self.pattern = re.compile(pattern)
        else:
            self.pattern = re.compile('^$')
    def _get_key(self, key):
        matches = self.pattern.match(key)
        if matches:
            key = '/'.join((v for v in matches.groups() if v))
        return key    
    def timer(self, key):
        return super(RegexRegistry, self).timer(self._get_key(key))
    def histogram(self, key):
        return super(RegexRegistry, self).histogram(self._get_key(key))
    def counter(self, key):
        return super(RegexRegistry, self).counter(self._get_key(key))
    def gauge(self, key, gauge=None):
        return super(RegexRegistry, self).gauge(self._get_key(key), gauge)
    def meter(self, key):
        return super(RegexRegistry, self).meter(self._get_key(key))

_global_registry = MetricsRegistry()

def counter(key):
    return _global_registry.counter(key)
def histogram(key):
    return _global_registry.histogram(key)
def meter(key):
    return _global_registry.meter(key)
def timer(key):
    return _global_registry.timer(key)
def dump_metrics():
    return _global_registry.dump_metrics()
def clear():
    return _global_registry.clear()

def count_calls(fn):
    """
    Decorator to track the number of times a function is called.

    @param fn: the function to be decorated
    @type fn: C{func}

    @return: the decorated function
    @rtype: C{func}
    """
    def wrapper(*args):
        counter("%s_calls" % fn.__name__).inc()
        try:
            fn(*args)
        except:
            raise
    return wrapper

def meter_calls(fn):
    """
    Decorator to the rate at which a function is called.

    @param fn: the function to be decorated
    @type fn: C{func}

    @return: the decorated function
    @rtype: C{func}
    """
    def wrapper(*args):
        meter("%s_calls" % fn.__name__).mark()
        try:
            fn(*args)
        except:
            raise
    return wrapper

def hist_calls(fn):
    """
    Decorator to check the distribution of return values of a function.

    @param fn: the function to be decorated
    @type fn: C{func}

    @return: the decorated function
    @rtype: C{func}
    """
    def wrapper(*args):
        _histogram = histogram("%s_calls" % fn.__name__)
        try:
            rtn = fn(*args)
            if type(rtn) in (int, float):
                _histogram.update(rtn)
        except:
            raise
    return wrapper

def time_calls(fn):
    """
    Decorator to time the execution of the function.

    @param fn: the function to be decorated
    @type fn: C{func}

    @return: the decorated function
    @rtype: C{func}
    """
    def wrapper(*args):
        _timer = timer("%s_calls" % fn.__name__)
        with _timer.time(fn=fn.__name__):
            fn(*args)
