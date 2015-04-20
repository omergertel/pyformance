import os
import socket
from pyformance.registry import meter_calls
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
        self.assertEqual('{"agent": {"host": "%s", "pid": %s, "version": "0.3.1"}, "components": [{"duration": 1, "guid": "com.github.pyformance", "metrics": {"Component/c1/count": 1, "Component/counter-2/count": -2, "Component/hist/75_percentile": 160.0, "Component/hist/95_percentile": 512, "Component/hist/999_percentile": 512, "Component/hist/99_percentile": 512, "Component/hist/avg": 102.3, "Component/hist/count": 10.0, "Component/hist/max": 512, "Component/hist/min": 1, "Component/hist/std_dev": 164.94851048466947, "Component/m1/15m_rate": 0, "Component/m1/1m_rate": 0, "Component/m1/5m_rate": 0, "Component/m1/count": 1.0, "Component/m1/mean_rate": 1.0, "Component/t1/15m_rate": 0, "Component/t1/1m_rate": 0, "Component/t1/5m_rate": 0, "Component/t1/75_percentile": 1, "Component/t1/95_percentile": 1, "Component/t1/999_percentile": 1, "Component/t1/99_percentile": 1, "Component/t1/avg": 1.0, "Component/t1/count": 1.0, "Component/t1/max": 1, "Component/t1/mean_rate": 1.0, "Component/t1/min": 1, "Component/t1/std_dev": 0.0, "Component/t1/sum": 1.0}, "name": "%s"}]}'
                         % (socket.gethostname(), os.getpid(), socket.gethostname()),
                         output)
