# -*- coding: utf-8 -*-
from __future__ import print_function
import json
import os
import socket
import sys

if sys.version_info[0] > 2:
    import urllib.request as urllib
    import urllib.error as urlerror
else:
    import urllib2 as urllib
    import urllib2 as urlerror

from pyformance.__version__ import __version__

from .reporter import Reporter

DEFAULT_CARBON_SERVER = '0.0.0.0'
DEFAULT_CARBON_PORT = 2003


class NewRelicReporter(Reporter):
    """
    Reporter for new relic
    """

    MAX_METRICS_PER_REQUEST = 10000
    PLATFORM_URL = 'https://platform-api.newrelic.com/platform/v1/metrics'

    def __init__(self, license_key, registry=None, name=socket.gethostname(), reporting_interval=5, prefix="",
                 clock=None):
        super(NewRelicReporter, self).__init__(
            registry, reporting_interval, clock)
        self.name = name
        self.prefix = prefix

        self.http_headers = {'Accept': 'application/json',
                             'Content-Type': 'application/json',
                             'X-License-Key': license_key}


    def report_now(self, registry=None, timestamp=None):
        metrics = self.collect_metrics(registry or self.registry)
        if metrics:
            try:
                # XXX: better use http-keepalive/pipelining somehow?
                request = urllib.Request(self.PLATFORM_URL, metrics.encode() if sys.version_info[0] > 2 else metrics)
                for k, v in self.http_headers.items():
                    request.add_header(k, v)
                result = urllib.urlopen(request)
                if isinstance(result, urlerror.HTTPError):
                    raise result
            except Exception as e:
                print(e, file=sys.stderr)

    @property
    def agent_data(self):
        """Return the agent data section of the NewRelic Platform data payload

        :rtype: dict

        """
        return {'host': socket.gethostname(),
                'pid': os.getpid(),
                'version': __version__}

    def create_metrics(self, input):
        results = {}
        for key in input.keys():

            for value_key in input[key].keys():
                full_key = 'Component/%s%s/%s' % (self.prefix, key, value_key)
                results[full_key.replace('.', '/')] = input[key][value_key]
        return results

    def collect_metrics(self, registry):
        body = {
            'agent': self.agent_data,
            'components': [{
                'guid': 'com.github.pyformance',
                'name': self.name,
                'duration': self.reporting_interval,
                'metrics': self.create_metrics(registry.dump_metrics())
            }]
        }

        return json.dumps(body, ensure_ascii=False, sort_keys=True)
