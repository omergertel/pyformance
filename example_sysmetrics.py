#!/usr/bin/env python
import os
import platform
import socket
import time
import json

import psutil

from pyformance import global_registry


class Collector(object):
    # TODO: use meters and histograms instead of gauges if possible

    def __init__(self, registry=None):
        if registry is None:
            registry = global_registry()
        self.registry = registry

    def collect_disk_io(self, whitelist=[]):
        stats = psutil.disk_io_counters(perdisk=True)
        for entry, stat in stats.iteritems():
            if not whitelist or entry in whitelist:
                for k, v in stat._asdict().iteritems():
                    self.registry.gauge("disk-%s.%s" % (entry, k)).set_value(v)
                    
    def collect_network_io(self, whitelist=[]):
        stats = psutil.network_io_counters(pernic=True)
        for entry, stat in stats.iteritems():
            if not whitelist or entry in whitelist:
                for k, v in stat._asdict().iteritems():
                    self.registry.gauge("nic-%s.%s" % (entry.replace(" ", "_"), k)).set_value(v)

    def collect_cpu_times(self, whitelist=[]):
        stats = psutil.cpu_times(percpu=True)
        for entry, stat in enumerate(stats):
            if not whitelist or entry in whitelist:
                for k, v in stat._asdict().iteritems():
                    self.registry.gauge("cpu%d.%s" % (entry, k)).set_value(v)

    def collect_phymem_usage(self):
        stats = psutil.phymem_usage()
        for k, v in stats._asdict().iteritems():
            self.registry.gauge("phymem.%s" % k).set_value(v)

    def collect_swap_usage(self):
        stats = psutil.swap_memory()
        for k, v in stats._asdict().iteritems():
            self.registry.gauge("swap.%s" % k).set_value(v)
        
    def collect_virtmem_usage(self):
        stats = psutil.virtmem_usage()
        for k, v in stats._asdict().iteritems():
            self.registry.gauge("virtmem.%s" % k).set_value(v)    
            
    def collect_uptime(self):
        uptime = int(time.time()) - int(psutil.BOOT_TIME)
        self.registry.gauge("uptime").set_value(uptime)

    def collect_disk_usage(self, whitelist=[]):
        for partition in psutil.disk_partitions():
            if not whitelist or partition.mountpoint in whitelist or partition.device in whitelist:
                usage = psutil.disk_usage(partition.mountpoint)
                if platform.system() == "Windows":
                    disk_name = "-" + \
                        partition.mountpoint.replace("\\", "").replace(":", "")
                else:
                    disk_name = partition.mountpoint.replace("/", "-")
                    if disk_name == "-":
                        disk_name = "-root"
                self.registry.gauge("df%s.total" % disk_name).set_value(usage.total)
                self.registry.gauge("df%s.used" % disk_name).set_value(usage.used)
                self.registry.gauge("df%s.free" % disk_name).set_value(usage.free)

    def collect_loadavgs(self):
        loadavgs = os.getloadavg()
        self.registry.gauge('loadavg_1min').set_value(loadavgs[0])
        self.registry.gauge('loadavg_5min').set_value(loadavgs[1])
        self.registry.gauge('loadavg_15min').set_value(loadavgs[2])

    def collect(self):
        self.collect_disk_io()
        self.collect_cpu_times()
        self.collect_uptime()
        self.collect_network_io()
        self.collect_phymem_usage()
        self.collect_virtmem_usage()
        self.collect_swap_usage()
        self.collect_disk_usage()
        self.collect_loadavgs()

        
if __name__ == "__main__":
    from pyformance.reporters import ConsoleReporter
    reporter = ConsoleReporter()
    col = Collector()
    col.collect()
    reporter.report_now()
