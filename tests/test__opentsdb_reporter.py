import os
import socket
import mock

from pyformance.reporters.opentsdb_reporter import OpenTSDBReporter
from pyformance import MetricsRegistry
from tests import TimedTestCase


class TestOpenTSDBReporter(TimedTestCase):
    def setUp(self):
        super(TestOpenTSDBReporter, self).setUp()
        self.registry = MetricsRegistry(clock=self.clock)
        self.maxDiff = None

    def tearDown(self):
        super(TestOpenTSDBReporter, self).tearDown()

    def test_report_now(self):
        r = OpenTSDBReporter(application_name="app", write_key="key", registry=self.registry, reporting_interval=1,
                             clock=self.clock, prefix="prefix.", url="http://opentsdb.com/api/put")
        h1 = self.registry.histogram("hist")
        for i in range(10):
            h1.add(2 ** i)
        t1 = self.registry.timer("t1")
        m1 = self.registry.meter("m1")
        m1.mark()
        with t1.time():
            c1 = self.registry.counter("c1")
            c2 = self.registry.counter("counter-2")
            c1.inc()
            c2.dec()
            c2.dec()
            self.clock.add(1)
        output = r._collect_metrics(registry=self.registry)
        self.assertEqual(len(output), 31)
        for data in output:
            assert data['metric'].startswith("prefix.")

    def test_send_request(self):
        r = OpenTSDBReporter(application_name="app", write_key="key", registry=self.registry, reporting_interval=1,
                             clock=self.clock, prefix="prefix.", url="http://opentsdb.com/api/put")
        h1 = self.registry.histogram("hist")
        for i in range(10):
            h1.add(2 ** i)
        t1 = self.registry.timer("t1")
        m1 = self.registry.meter("m1")
        m1.mark()
        with t1.time():
            c1 = self.registry.counter("c1")
            c2 = self.registry.counter("counter-2")
            c1.inc()
            c2.dec()
            c2.dec()
            self.clock.add(1)
        with mock.patch("pyformance.reporters.opentsdb_reporter.urllib.urlopen") as patch:
            r.report_now()
            patch.assert_called()
