# -*- coding: utf-8 -*-
import sys
import socket
import logging
import logging.handlers
from six import iteritems
import json

from .reporter import Reporter

DEFAULT_SYSLOG_ADDRESS = '/dev/log'
DEFAULT_SYSLOG_SOCKTYPE = socket.SOCK_DGRAM
DEFAULT_SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_USER


class SysLogReporter(Reporter):

    """
    Syslog is a way for network devices to send event messages to a logging server
    """

    def __init__(self, registry=None, reporting_interval=5, tag="pyformance", clock=None,
                 address=DEFAULT_SYSLOG_ADDRESS, socktype=DEFAULT_SYSLOG_SOCKTYPE,
                 facility=DEFAULT_SYSLOG_FACILITY):
        super(SysLogReporter, self).__init__(registry, reporting_interval, clock)

        handler = logging.handlers.SysLogHandler(address=address, facility=facility, socktype=socktype)
        handler.append_nul = False

        if tag is not None and tag != '':
            if sys.version_info >= (3,3):
                handler.ident = tag + ': '
            else:
                formatter = logging.Formatter('{}: %(message)s'.format(tag))
                handler.setFormatter(formatter)

        logger = logging.getLogger('pyformance')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        self.logger = logger


    def report_now(self, registry=None, timestamp=None):
        metrics = self._collect_metrics(registry or self.registry, timestamp)
        if metrics:
            self.logger.info(metrics)


    def _collect_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(self.clock.time()))

        metrics_data = {'timestamp': timestamp}
        metrics = registry.dump_metrics()
        for metric_name, metric in iteritems(metrics):
            for metric_key, metric_value in iteritems(metric):
                metrics_data['{}.{}'.format(metric_name, metric_key)] = metric_value
        result = json.dumps(metrics_data, sort_keys=True)
        return result


