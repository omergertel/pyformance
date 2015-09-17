# -*- coding: utf-8 -*-
import socket
import sys
import struct
import pickle
import contextlib
from six import iteritems

from .reporter import Reporter

DEFAULT_CARBON_SERVER = '0.0.0.0'
DEFAULT_CARBON_PORT = 2003


class CarbonReporter(Reporter):

    """
    Carbon is the network daemon to collect metrics for Graphite
    """

    def __init__(self, registry=None, reporting_interval=5, prefix="",
                 server=DEFAULT_CARBON_SERVER, port=DEFAULT_CARBON_PORT, socket_factory=socket.socket,
                 clock=None, pickle_protocol=False):
        super(CarbonReporter, self).__init__(registry, reporting_interval, clock)
        self.prefix = prefix
        self.server = server
        self.port = port
        self.socket_factory = socket_factory
        self.pickle_protocol = pickle_protocol

    def report_now(self, registry=None, timestamp=None):
        metrics = self._collect_metrics(registry or self.registry, timestamp)
        if metrics:
            # TODO: keep connection open 
            with contextlib.closing(self.socket_factory()) as sock:
                sock.connect((self.server, self.port))
                sock.sendall(metrics)

    def _collect_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(self.clock.time()))
        metrics = registry.dump_metrics()
        if self.pickle_protocol:
            payload = pickle.dumps([
                ("%s%s.%s" % (self.prefix, metric_name, metic_key), (timestamp, metric_value))
                for metric_name, metric in iteritems(metrics)
                for metic_key, metric_value in iteritems(metric)
            ])
            header = struct.pack("!L", len(payload))
            return header + payload
        else:
            metrics_data = []
            for metric_name, metric in iteritems(metrics):
                for metic_key, metric_value in iteritems(metric):
                    metricLine = "%s%s.%s %s %s\n" % (
                        self.prefix, metric_name, metic_key, metric_value, timestamp)
                    metrics_data.append(metricLine)
            result = ''.join(metrics_data)
            if sys.version_info[0] > 2:
                return result.encode()
            return result

    
class UdpCarbonReporter(CarbonReporter):
    
    """
    The default CarbonReporter uses TCP.
    This sub-class uses UDP instead which might be unreliable but it is faster
    """
    
    def report_now(self, registry=None, timestamp=None):
        metrics = self._collect_metrics(registry or self.registry, timestamp)
        if metrics:
            with contextlib.closing(self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
                sock.sendto(metrics, (self.server, self.port))
