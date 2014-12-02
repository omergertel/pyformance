import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

from pyformance import MetricsRegistry
from pyformance.reporters.console_reporter import ConsoleReporter
from tests import TimedTestCase


class TestConsoleReporter(TimedTestCase):

    def setUp(self):
        super(TestConsoleReporter, self).setUp()
        self.output = StringIO()
        self.registry = MetricsRegistry(clock=self.clock)
        self.maxDiff = None
        self.clock.now = 0

    def tearDown(self):
        super(TestConsoleReporter, self).tearDown()
        self.clock.now = 0

    def test_report_now(self):
        r = ConsoleReporter(
            registry=self.registry, reporting_interval=1, stream=self.output, clock=self.clock)
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
                         '== 1970-01-01 00:00:01 ===================================',
                         'counter-2:', '               count = -2',
                         'gsimple:', '               value = 42',
                         'gcb:', '               value = 123',
                         't1:', '             1m_rate = 0',
                         '      999_percentile = 1',
                         '            15m_rate = 0',
                         '       99_percentile = 1',
                         '           mean_rate = 1.0',
                         '       95_percentile = 1',
                         '                 min = 1',
                         '             5m_rate = 0',
                         '               count = 1.0',
                         '       75_percentile = 1',
                         '             std_dev = 0.0',
                         '                 max = 1',
                         '                 avg = 1.0',
                         'hist:', '               count = 10.0',
                         '      999_percentile = 512',
                         '       99_percentile = 512',
                         '                 min = 1',
                         '       95_percentile = 512',
                         '       75_percentile = 160.0',
                         '             std_dev = 164.948510485',
                         '                 max = 512',
                         '                 avg = 102.3',
                         'm1:', '               count = 1.0',
                         '             1m_rate = 0',
                         '            15m_rate = 0',
                         '             5m_rate = 0',
                         '           mean_rate = 1.0',
                         'c1:', '               count = 1', ''].sort())


if __name__ == "__main__":
    unittest.main()
