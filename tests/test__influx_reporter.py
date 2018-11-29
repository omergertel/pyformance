import mock

try:
    from urllib2 import Request
except ImportError:
    from urllib.request import Request

from pyformance.reporters.influx import InfluxReporter, _format_tag_value
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

        with mock.patch("pyformance.reporters.influx.urlopen") as patch:
            influx_reporter.report_now()
            patch.assert_called()

    def test_create_database(self):
        r1 = InfluxReporter(registry=self.registry, autocreate_database=True)
        with mock.patch("pyformance.reporters.influx.urlopen") as patch:
            r1.report_now()
            if patch.call_count != 2:
                raise AssertionError(
                    "Expected 2 calls to 'urlopen'. Received: {}".format(
                        patch.call_count
                    )
                )

    def test_gauge_without_tags(self):
        self.registry.gauge("cpu").set_value(65)
        influx_reporter = InfluxReporter(
            registry=self.registry,
            clock=self.clock,
            autocreate_database=False
        )

        with mock.patch.object(influx_reporter, "_try_send",
                               wraps=influx_reporter._try_send) as send_mock:
            influx_reporter.report_now()

            expected_url = "http://127.0.0.1:8086/write?db=metrics&precision=s"
            expected_data = "cpu value=65 " + self.clock.time_string()
            send_mock.assert_called_once_with(expected_url, expected_data)

    def test_gauge_with_tags(self):
        tags = {"region": "us - west"}
        self.registry.gauge(key="cpu", tags=tags).set_value(65)
        influx_reporter = InfluxReporter(
            registry=self.registry,
            clock=self.clock,
            autocreate_database=False
        )

        with mock.patch.object(influx_reporter, "_try_send",
                               wraps=influx_reporter._try_send) as send_mock:
            influx_reporter.report_now()

            expected_url = "http://127.0.0.1:8086/write?db=metrics&precision=s"
            expected_data = "cpu,region=us\\ -\\ west value=65 " + \
                            self.clock.time_string()
            send_mock.assert_called_once_with(expected_url, expected_data)

    def test_counter_with_tags(self):
        tags = {"host": "server1"}
        counter = self.registry.counter(key="cpu", tags=tags)

        for i in range(5):
            counter.inc(1)

        influx_reporter = InfluxReporter(
            registry=self.registry,
            clock=self.clock,
            autocreate_database=False
        )

        with mock.patch.object(influx_reporter, "_try_send",
                               wraps=influx_reporter._try_send) as send_mock:
            influx_reporter.report_now()

            expected_url = "http://127.0.0.1:8086/write?db=metrics&precision=s"
            expected_data = "cpu,host=server1 count=5 " + \
                            self.clock.time_string()
            send_mock.assert_called_once_with(expected_url, expected_data)

    def test_count_calls_with_tags(self):
        tags = {"host": "server1"}
        counter = self.registry.counter(key="cpu", tags=tags)

        for i in range(5):
            counter.inc(1)

        influx_reporter = InfluxReporter(
            registry=self.registry,
            clock=self.clock,
            autocreate_database=False
        )

        with mock.patch.object(influx_reporter, "_try_send",
                               wraps=influx_reporter._try_send) as send_mock:
            influx_reporter.report_now()

            expected_url = "http://127.0.0.1:8086/write?db=metrics&precision=s"
            expected_data = "cpu,host=server1 count=5 " + \
                            self.clock.time_string()
            send_mock.assert_called_once_with(expected_url, expected_data)

    def test__format_tag_value(self):
        self.assertEqual(_format_tag_value("no_special_chars"), "no_special_chars")
        self.assertEqual(_format_tag_value("has space"), "has\ space")
        self.assertEqual(_format_tag_value("has,comma"), "has\,comma")
        self.assertEqual(_format_tag_value("has=equals"), "has\=equals")