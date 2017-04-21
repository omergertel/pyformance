# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from .reporter import Reporter
import base64
import json

if sys.version_info[0] > 2:
    import urllib.request as urllib
    import urllib.error as urlerror
else:
    import urllib2 as urllib
    import urllib2 as urlerror


class OpenTSDBReporter(Reporter):
    """
    This reporter requires a tuple (application_name, write_key) to put data to opentsdb database
    """

    def __init__(self, application_name, write_key, url, registry=None, reporting_interval=10, clock=None, prefix="",
                 tags={}):
        super(OpenTSDBReporter, self).__init__(registry=registry,
                                               reporting_interval=reporting_interval,
                                               clock=clock)
        self.url = url
        self.application_name = application_name
        self.write_key = write_key
        self.prefix = prefix
        self.tags = tags or {}

    def report_now(self, registry=None, timestamp=None):
        metrics = self._collect_metrics(registry or self.registry, timestamp)
        if metrics:
            try:
                request = urllib.Request(self.url,
                                         data=json.dumps(metrics).encode("utf-8"),
                                         headers={'content-type': "application/json"})
                authentication_data = "{0}:{1}".format(self.application_name, self.write_key)
                auth_header = base64.b64encode(bytes(authentication_data.encode("utf-8")))
                request.add_header("Authorization", "Basic {0}".format(auth_header))
                urllib.urlopen(request)
            except Exception as e:
                sys.stderr.write("{0}\n".format(e))

    def _collect_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(self.clock.time()))
        metrics = registry.dump_metrics()
        metrics_data = []
        for key in metrics.keys():
            for value_key in metrics[key].keys():
                metrics_data.append({
                    'metric': "{0}{1}.{2}".format(self.prefix, key, value_key),
                    'value': metrics[key][value_key],
                    'timestamp': timestamp,
                    'tags': self.tags,
                })
        return metrics_data

