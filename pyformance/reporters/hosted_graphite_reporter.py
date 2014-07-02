# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import urllib2
import base64
import time

from pyformance.meters import Counter, Histogram, Meter, Timer
from pyformance.registry import MetricsRegistry
from .reporter import Reporter


class HostedGraphiteReporter(Reporter)

    def __init__(self, hosted_graphite_api_key, registry=None, reporting_interval=10, url="https://hostedgraphite.com/api/v1/sink"):
        super(HostedGraphiteReporter, self).__init__(registry, reporting_interval)
        self.url = url
        self.api_key = hosted_graphite_api_key

    def send_metrics_now(self, registry=None):
        metrics = self._collect_metrics(registry or self._registry)
        if metrics:
            try:
                # XXX: better use http-keepalive/pipelining somehow?
                request = urllib2.Request(self.url, metrics)
                request.add_header("Authorization", "Basic %s" %
                                   base64.encodestring(self.api_key).strip())
                result = urllib2.urlopen(request)
            except Exception as e:
                print(e, file=sys.stderr)

    def _collect_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(time.time()))
        metrics = registry.dump_metrics()
        metrics_data = []
        for key in metrics.keys():
            for value_key in metrics[key].keys():
                metric_line = "%s.%s %s %s\n" % (key, value_key, metrics[key][value_key], timestamp)
                metrics_data.append(metric_line)
        return ''.join(metrics_data)
