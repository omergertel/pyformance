# -*- coding: utf-8 -*-

import base64
import logging
from datetime import datetime

try:
    from urllib2 import quote, urlopen, Request, URLError
except ImportError:
    from urllib.error import URLError
    from urllib.parse import quote
    from urllib.request import urlopen, Request

from influxdb import InfluxDBClient

from .reporter import Reporter

LOG = logging.getLogger(__name__)

DEFAULT_INFLUX_SERVER = "127.0.0.1"
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

    def __init__(
        self,
        registry=None,
        reporting_interval=5,
        prefix="",
        database=DEFAULT_INFLUX_DATABASE,
        server=DEFAULT_INFLUX_SERVER,
        username=DEFAULT_INFLUX_USERNAME,
        password=DEFAULT_INFLUX_PASSWORD,
        port=DEFAULT_INFLUX_PORT,
        protocol=DEFAULT_INFLUX_PROTOCOL,
        autocreate_database=False,
        clock=None,
    ):
        super(InfluxReporter, self).__init__(registry, reporting_interval, clock)
        self.prefix = prefix
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.protocol = protocol
        self.server = server
        self.autocreate_database = autocreate_database
        self._did_create_database = False
        self._influxDBClient = None

    def _get_connection(self):
        if self._influxDBClient is None:
            self._influxDBClient = InfluxDBClient(host=self.server,
                                                  port=self.port,
                                                  username=self.username,
                                                  password=self.password,
                                                  database=self.database)
        return self._influxDBClient

    def _create_database(self):
        try:
            self._get_connection()
            self._influxDBClient.create_database(self.database)
            self._did_create_database = True
        except Exception as err:
            LOG.warning(
                "Cannot create database %s to %s, %s",
                self.database,
                self.server
            )

    def report_now(self, registry=None, timestamp=None):
        if self.autocreate_database and not self._did_create_database:
            self._create_database()
        timestamp = timestamp or datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        metrics = (registry or self.registry).dump_metrics()
        json_body = []
        client = self._get_connection()
        for key, metric_values in metrics.items():
            if not self.prefix:
                measurement = key
            else:
                measurement = "%s.%s" % (self.prefix, key)
            fields = {k: v for (k, v) in metric_values.items()}
            tags = {}
            json_body.append({"measurement": measurement,
                              "tags": tags,
                              "time": timestamp,
                              "fields": fields})
        try:
            client.write_points(json_body)
        except URLError as err:
            LOG.warning("Cannot write to %s: %s", self.server, err.reason)

