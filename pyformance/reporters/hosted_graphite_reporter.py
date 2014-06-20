# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import urllib2
import base64
import time

from twisted.internet import reactor  # XXX: does this import trigger something or can it removed?
from twisted.internet import task

from pyformance.meters import Counter, Histogram, Meter, Timer
from pyformance.registry import MetricsRegistry


class HostedGraphiteReporter(object):

    def __init__(self, registry, reporting_interval, hosted_graphite_api_key, url="https://hostedgraphite.com/api/v1/sink"):
        self.url = url
        self.api_key = hosted_graphite_api_key
        loop = task.LoopingCall(self.send_metrics_now, registry)
        loop.start(reporting_interval)

    def send_metrics_now(self, registry):
        metrics = self.get_metrics(registry)
        if metrics:
            try:
                request = urllib2.Request(self.url, metrics)
                request.add_header("Authorization", "Basic %s" %
                                   base64.encodestring(self.api_key).strip())
                result = urllib2.urlopen(request)
            except Exception as e:
                print(e, file=sys.stderr)

    def get_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(time.time()))
        metrics = registry.dump_metrics()
        metrics_data = []
        for key in metrics.keys():
            for value_key in metrics[key].keys():
                metricLine = "%s.%s %s %s\n" % (key, value_key, metrics[key][value_key], timestamp)
                metrics_data.append(metricLine)
        return ''.join(metrics_data)
