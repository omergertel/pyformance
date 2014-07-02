import time
from threading import Thread, Event
from pyformance.registry import _global_registry

class Reporter(object):
    
    def __init__(self, registry=None, reporting_interval=30):
        self.registry = registry or _global_registry
        self.reporting_interval = reporting_interval
        self._stopped = Event()
        self._loop_thread = Thread(target=self._loop)
        self._loop_thread.setDaemon(True)
        
    def start(self):
        self._loop_thread.start()
        
    def stop(self):
        self._stopped.set()
    
    def _loop(self):
        while not self._stopped.is_set():
            self.send_metrics_now(self.registry)
            time.sleep(self.reporting_interval)

    def send_metrics_now(self, registry=None):
        raise NotImplementedError(self.send_metrics_now)