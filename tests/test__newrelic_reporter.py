import os
import socket
from pyformance.reporters.newrelic_reporter import NewRelicReporter

from pyformance import MetricsRegistry
from tests import TimedTestCase


class TestNewRelicReporter(TimedTestCase):

    def setUp(self):
        super(TestNewRelicReporter, self).setUp()
        self.registry = MetricsRegistry(clock=self.clock)
        self.maxDiff = None

    def tearDown(self):
        super(TestNewRelicReporter, self).tearDown()

    def test_report_now(self):
        r = NewRelicReporter(
            'license_key',
            registry=self.registry, reporting_interval=1, clock=self.clock)
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
        output = r.collect_metrics(self.registry)
        self.assertEqual('{"agent": {"host": "%s", "pid": %s, "version": "0.3.1"}, "components": [{"duration": 1, "guid": "com.github.pyformance", "metrics": {"c1": {"count": 1}, "counter-2": {"count": -2}, "hist": {"75_percentile": 160.0, "95_percentile": 512, "999_percentile": 512, "99_percentile": 512, "avg": 102.3, "count": 10.0, "max": 512, "min": 1, "std_dev": 164.94851048466947}, "m1": {"15m_rate": 0, "1m_rate": 0, "5m_rate": 0, "count": 1.0, "mean_rate": 1.0}, "t1": {"15m_rate": 0, "1m_rate": 0, "5m_rate": 0, "75_percentile": 1, "95_percentile": 1, "999_percentile": 1, "99_percentile": 1, "avg": 1.0, "count": 1.0, "max": 1, "mean_rate": 1.0, "min": 1, "std_dev": 0.0, "sum": 1.0}}, "name": "gregor"}]}'
                         % (socket.gethostname(), os.getpid()),
                         output)


if __name__ == "__main__":
    unittest.main()
