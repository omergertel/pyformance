# -*- coding: utf-8 -*-

import base64
import logging

from six.moves import urllib

from .reporter import Reporter

LOG = logging.getLogger(__name__)

DEFAULT_INFLUX_SERVER = '127.0.0.1'
DEFAULT_INFLUX_PORT = 8086
DEFAULT_INFLUX_DATABASE = "metrics"
DEFAULT_INFLUX_USERNAME = None
DEFAULT_INFLUX_PASSWORD = None
DEFAULT_INFLUX_PROTOCOL = "http"

class InfluxReporter(Reporter):

    """
    InfluxDB reporter using native http api
    (based on https://influxdb.com/docs/v1.1/guides/writing_data.html)
    """

    def __init__(self, registry=None, reporting_interval=5, prefix="",
                 database=DEFAULT_INFLUX_DATABASE, server=DEFAULT_INFLUX_SERVER,
                 username=DEFAULT_INFLUX_USERNAME,
                 password=DEFAULT_INFLUX_PASSWORD,
                 port=DEFAULT_INFLUX_PORT, protocol=DEFAULT_INFLUX_PROTOCOL,
                 autocreate_database=False, clock=None):
        super(InfluxReporter, self).__init__(
            registry, reporting_interval, clock)
        self.prefix = prefix
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.protocol = protocol
        self.server = server
        self.autocreate_database = autocreate_database
        self._did_create_database = False

    def _create_database(self):
        url = "%s://%s:%s/query" % (self.protocol, self.server, self.port)
        q = urllib.parse.quote("CREATE DATABASE %s" % self.database)
        request = urllib.request.Request(url + "?q=" + q)
        if self.username:
            auth = _encode_username(self.username, self.password)
            request.add_header("Authorization", "Basic %s" % auth.decode('utf-8'))
        try:
            response = urllib.request.urlopen(request)
            _result = response.read()
            # Only set if we actually were able to get a successful response
            self._did_create_database = True
        except urllib.error.URLError as err:
            LOG.warning("Cannot create database %s to %s: %s",
                        self.database, self.server, err.reason)

    def report_now(self, registry=None, timestamp=None):
        if self.autocreate_database and not self._did_create_database:
            self._create_database()
        timestamp = timestamp or int(round(self.clock.time()))
        metrics = (registry or self.registry).dump_metrics()
        post_data = []
        for key, metric_values in metrics.items():
            if not self.prefix:
                table = key
            else:
                table = "%s.%s" % (self.prefix, key)
            values = ",".join(["%s=%s" % (k, v if type(v) is not str \
                                               else '"{}"'.format(v))
                              for (k, v) in metric_values.items()])
            line = "%s %s %s" % (table, values, timestamp)
            post_data.append(line)
        post_data = "\n".join(post_data)
        path = "/write?db=%s&precision=s" % self.database
        url = "%s://%s:%s%s" % (self.protocol, self.server, self.port, path)
        request = urllib.request.Request(url, post_data.encode("utf-8"))
        if self.username:
            auth = _encode_username(self.username, self.password)
            request.add_header("Authorization", "Basic %s" % auth.decode('utf-8'))
        try:
            response = urllib.request.urlopen(request)
            response.read()
        except urllib.error.URLError as err:
            LOG.warning("Cannot write to %s: %s",
                        self.server, err.reason)


def _encode_username(username, password):
    auth_string = ('%s:%s' % (username, password)).encode()
    return base64.b64encode(auth_string)
