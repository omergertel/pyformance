import os
import mock

try:
    from urllib2 import Request
except ImportError:
    from urllib.request import Request

from pyformance.reporters.influx import InfluxReporter
from pyformance import MetricsRegistry
from tests import TimedTestCase


class TestInfluxReporter(TimedTestCase):
    def setUp(self):
        super(TestInfluxReporter, self).setUp()
        self.registry = MetricsRegistry()

    def tearDown(self):
        super(TestInfluxReporter, self).tearDown()

    def test_report_now(self):
        influx_reporter = InfluxReporter(registry=self.registry)

        with mock.patch("influxdb.InfluxDBClient.write_points") as patch:
            influx_reporter.report_now()
            patch.assert_called()


    def test_create_database(self):
        r1 = InfluxReporter(registry=self.registry, autocreate_database=True)
        with mock.patch("influxdb.InfluxDBClient.write_points") as patch:
            r1.report_now()
            patch.assert_called()