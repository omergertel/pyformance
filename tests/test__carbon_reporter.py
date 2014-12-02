import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

from pyformance import MetricsRegistry
from pyformance.reporters.carbon_reporter import CarbonReporter
from tests import TimedTestCase


class TestCarbonReporter(TimedTestCase):

    def setUp(self):
        super(TestCarbonReporter, self).setUp()
        self.output = StringIO()
        self.registry = MetricsRegistry(clock=self.clock)
        self.maxDiff = None

    def connect(self, *args):
        # part of fake socket interface
        pass

    def sendall(self, data):
        # part of fake socket interface
        self.output.write(data)

    def close(self):
        # part of fake socket interface
        pass

    def tearDown(self):
        super(TestCarbonReporter, self).tearDown()

    def test_report_now(self):
        r = CarbonReporter(
            registry=self.registry, reporting_interval=1, clock=self.clock,
            socket_factory=lambda: self)
        h1 = self.registry.histogram("hist")
        for i in range(10):
            h1.add(2 ** i)
        gcb = self.registry.gauge("gcb", lambda: 123)
        gsimple = self.registry.gauge("gsimple").set_value(42)
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
        r.report_now()
        self.assertEqual(self.output.getvalue().splitlines().sort(), [
            'counter-2.count -2 1',
            'c1.count 1 1',
            'gsimple.value 42 1',
            'gcb.value 123 1',
            't1.1m_rate 0 1',
            't1.999_percentile 1 1',
            't1.15m_rate 0 1',
            't1.99_percentile 1 1',
            't1.mean_rate 1.0 1',
            't1.95_percentile 1 1',
            't1.min 1 1',
            't1.5m_rate 0 1',
            't1.count 1.0 1',
            't1.75_percentile 1 1',
            't1.std_dev 0.0 1',
            't1.max 1 1',
            't1.avg 1.0 1',
            'hist.count 10.0 1',
            'hist.999_percentile 512 1',
            'hist.99_percentile 512 1',
            'hist.min 1 1',
            'hist.95_percentile 512 1',
            'hist.75_percentile 160.0 1',
            'hist.std_dev 164.948510485 1',
            'hist.max 512 1',
            'hist.avg 102.3 1',
            'm1.count 1.0 1',
            'm1.1m_rate 0 1',
            'm1.15m_rate 0 1',
            'm1.5m_rate 0 1',
            'm1.mean_rate 1.0 1',
        ].sort())


if __name__ == "__main__":
    unittest.main()
