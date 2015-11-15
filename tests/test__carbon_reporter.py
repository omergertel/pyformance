from six import BytesIO, PY3
from pyformance import MetricsRegistry
from pyformance.reporters.carbon_reporter import CarbonReporter
from tests import TimedTestCase
import pickle

class TestCarbonReporter(TimedTestCase):

    def setUp(self):
        super(TestCarbonReporter, self).setUp()
        self.output = BytesIO()
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

    def capture_test_metrics(self):
        self.clock.now = 1
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

    def test_report_now_plain(self):
        r = CarbonReporter(
            registry=self.registry, reporting_interval=1, clock=self.clock,
            socket_factory=lambda: self)
        self.capture_test_metrics()
        r.report_now()
        test_data = sorted(self.output.getvalue().decode().splitlines())
        expected_data = sorted([
            'counter-2.count -2 2',
            'c1.count 1 2',
            'gsimple.value 42 2',
            'gcb.value 123 2',
            't1.1m_rate 0 2',
            't1.999_percentile 1 2',
            't1.15m_rate 0 2',
            't1.99_percentile 1 2',
            't1.mean_rate 1.0 2',
            't1.95_percentile 1 2',
            't1.min 1 2',
            't1.50_percentile 1 2',
            't1.5m_rate 0 2',
            't1.count 1.0 2',
            't1.75_percentile 1 2',
            't1.std_dev 0.0 2',
            't1.max 1 2',
            't1.sum 1.0 2',
            't1.avg 1.0 2',
            'hist.count 10.0 2',
            'hist.999_percentile 512 2',
            'hist.99_percentile 512 2',
            'hist.min 1 2',
            'hist.95_percentile 512 2',
            'hist.75_percentile 160.0 2',
            'hist.std_dev 164.94851048466947 2' \
                if PY3 else 'hist.std_dev 164.948510485 2',
            'hist.max 512 2',
            'hist.avg 102.3 2',
            'm1.count 1.0 2',
            'm1.1m_rate 0 2',
            'm1.15m_rate 0 2',
            'm1.5m_rate 0 2',
            'm1.mean_rate 1.0 2',
        ])
        self.assertEqual(test_data, expected_data)

    def test_report_now_pickle(self):
        r = CarbonReporter(
            registry=self.registry, reporting_interval=1, clock=self.clock,
            socket_factory=lambda: self, pickle_protocol=True)
        self.capture_test_metrics()
        r.report_now()
        test_data = sorted(pickle.loads(self.output.getvalue()[4:]))
        expected_data = sorted([
            ('counter-2.count', (2, -2.0)),
            ('c1.count', (2, 1)),
            ('gsimple.value', (2, 42.0)),
            ('gcb.value', (2, 123.0)),
            ('t1.1m_rate', (2, 0.0)),
            ('t1.999_percentile', (2, 1)),
            ('t1.15m_rate', (2, 0.0)),
            ('t1.99_percentile', (2, 1)),
            ('t1.mean_rate', (2, 1)),
            ('t1.95_percentile', (2, 1)),
            ('t1.min', (2, 1)),
            ('t1.50_percentile', (2, 1)),
            ('t1.5m_rate', (2, 0.0)),
            ('t1.count', (2, 1)),
            ('t1.75_percentile', (2, 1)),
            ('t1.std_dev', (2, 0.0)),
            ('t1.max', (2, 1)),
            ('t1.sum', (2, 1)),
            ('t1.avg', (2, 1)),
            ('hist.count', (2, 10.0)),
            ('hist.999_percentile', (2, 512.0)),
            ('hist.99_percentile', (2, 512.0)),
            ('hist.min', (2, 1)),
            ('hist.95_percentile', (2, 512.0)),
            ('hist.75_percentile', (2, 160.0)),
            ('hist.std_dev', (2, 164.94851048466947)),
            ('hist.max', (2, 512.0)),
            ('hist.avg', (2, 102.3)),
            ('m1.count', (2, 1)),
            ('m1.1m_rate', (2, 0.0)),
            ('m1.15m_rate', (2, 0.0)),
            ('m1.5m_rate', (2, 0.0)),
            ('m1.mean_rate', (2, 1))
        ])
        self.assertEqual(test_data, expected_data)


if __name__ == "__main__":
    unittest.main()
