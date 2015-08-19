# -*- coding: utf-8 -*-
import urllib2
import base64

from .reporter import Reporter

DEFAULT_INFLUX_SERVER = '127.0.0.1'
DEFAULT_INFLUX_PORT = 8086
DEFAULT_INFLUX_DATABASE = "metrics"
DEFAULT_INFLUX_USERNAME = None
DEFAULT_INFLUX_PASSWORD = None
DEFAULT_INFLUX_PROTOCOL = "http"


class InfluxReporter(Reporter):

    """
    InfluxDB reporter using native http api
    (based on https://influxdb.com/docs/v0.9/guides/writing_data.html)
    """

    def __init__(self, registry=None, reporting_interval=5, prefix="",
                 database=DEFAULT_INFLUX_DATABASE, server=DEFAULT_INFLUX_SERVER,
                 username=DEFAULT_INFLUX_USERNAME,
                 password=DEFAULT_INFLUX_PASSWORD,
                 port=DEFAULT_INFLUX_PORT, protocol=DEFAULT_INFLUX_PROTOCOL,
                 clock=None):
        super(InfluxReporter, self).__init__(
            registry, reporting_interval, clock)
        self.prefix = prefix
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.protocol = protocol
        self.server = server

    def report_now(self, registry=None, timestamp=None):
        timestamp = timestamp or int(round(self.clock.time()))
        metrics = (registry or self.registry).dump_metrics()
        post_data = []
        for key, metric_values in metrics.iteritems():
            if not self.prefix:
                table = key
            else:
                table = "%s.%s" % (self.prefix, key)
            values = ",".join(["%s=%s" % (k, v)
                              for (k, v) in metric_values.iteritems()])
            line = "%s %s %s" % (table, values, timestamp)
            post_data.append(line)
        post_data = "\n".join(post_data)
        path = "/write?db=%s&precision=s" % self.database
        url = "%s://%s:%s%s" % (self.protocol, self.server, self.port, path)
        request = urllib2.Request(url, post_data)
        if self.username:
            auth = base64.encodestring(
                '%s:%s' % (self.username, self.password))[:-1]
            request.add_header("Authorization", "Basic %s" % auth)
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, err:
            if err.code == 404:
                raise RuntimeError("Cannot write to %s: Database %r not found. %s" %
                                   (self.server, self.database, err.reason))
            raise RuntimeError("Cannot write to %s: %s %s" %
                               (self.server, err.code, err.reason))
        _result = response.read()
