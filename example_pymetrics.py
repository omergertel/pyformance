import datetime
import os
import threading
import gc
import multiprocessing

try:
    import resource
except ImportError:
    resource = None
    # windows
    import psutil

from pyformance import global_registry

    

class Collector(object):
    # TODO: use meters and histograms instead of gauges if possible

    def __init__(self, registry=None):
        if registry is None:
            registry = global_registry()
        self.registry = registry
        self._memory_usage = 0
        
    def collect_memory(self):
        if resource:
            usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        else:
            process = psutil.Process(os.getpid())
            usage = process.get_memory_info()[0] / float(2 ** 20)
        increase = usage - self._memory_usage
        self._memory_usage = usage
        self.registry.gauge("python.memory.usage").set_value(usage)
        self.registry.gauge("python.memory.increase").set_value(increase)
    
    def collect_threads(self):
        counter = 0
        alive = 0
        daemon = 0
        for thread in threading.enumerate():
            counter +=1
            if thread.isDaemon():
                daemon += 1
            if thread.isAlive():
                alive += 1
        #switch_interval = sys.getcheckinterval()
        self.registry.gauge("python.thread.count").set_value(counter)
        self.registry.gauge("python.thread.daemon").set_value(daemon)
        self.registry.gauge("python.thread.alive").set_value(alive)
    
    def collect_garbage(self):
        (count0, count1, count2) = gc.get_count()
        (threshold0, threshold1, threshold2) = gc.get_threshold()
        object_count = len(gc.get_objects())
        referrers_count = len(gc.get_referrers())
        referents_count = len(gc.get_referents())
        self.registry.gauge("python.gc.collection.count0").set_value(count0)
        self.registry.gauge("python.gc.collection.count1").set_value(count1)
        self.registry.gauge("python.gc.collection.count2").set_value(count2)
        self.registry.gauge("python.gc.objects.count").set_value(object_count)
        self.registry.gauge("python.gc.referrers.count").set_value(referrers_count)
        self.registry.gauge("python.gc.referents.count").set_value(referents_count)
    
    def collect_processes(self):
        counter = 0
        alive = 0
        daemon = 0
        for proc in multiprocessing.active_children():
            counter += 1
            if proc.is_alive():
                alive += 1
            if proc.daemon:
                daemon += 1
        self.registry.gauge("python.processes.count").set_value(counter)
        self.registry.gauge("python.processes.alive").set_value(alive)
        self.registry.gauge("python.processes.daemon").set_value(daemon)
    
        
    def collect(self):
        self.collect_memory()
        self.collect_garbage()
        self.collect_threads()
        self.collect_processes()

    
    
if __name__ == "__main__":
    from pyformance.reporters import ConsoleReporter
    reporter = ConsoleReporter()
    col = Collector()
    col.collect()
    reporter.report_now()
