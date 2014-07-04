# -*- coding: utf-8 -*-
"""
Carbon is the network daemon to collect metrics for Graphite
"""
import socket

from .reporter import Reporter

DEFAULT_CARBON_SERVER = '0.0.0.0'
DEFAULT_CARBON_PORT = 2003


class CarbonReporter(Reporter):
    
    def __init__(self, registry, reporting_interval, prefix="", 
                 server=DEFAULT_CARBON_SERVER, port=DEFAULT_CARBON_PORT, socket_factory=socket.socket,
                 clock=None):
        super(CarbonReporter, self).__init__(registry, reporting_interval, clock)            
        self.prefix = prefix
        self.server = server
        self.port = port
        self.socket_factory = socket_factory

    def report_now(self, registry=None, timestamp=None):
        metrics = self._collect_metrics(registry or self.registry, timestamp)
        if metrics:
            # XXX: keep connection open or use UDP?
            sock = self.socket_factory()
            sock.connect((CARBON_SERVER, CARBON_PORT))
            sock.sendall(metrics)
            sock.close()
            
    def _collect_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(self.clock.time()))
        metrics = registry.dump_metrics()
        metrics_data = []
        for key in metrics.keys():
            for value_key in metrics[key].keys():
                metricLine = "%s%s.%s %s %s\n" % (self.prefix, key, value_key, metrics[key][value_key], timestamp)
                metrics_data.append(metricLine)
        return ''.join(metrics_data)


