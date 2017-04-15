import sys
import os
import shutil
import tempfile
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

from pyformance import MetricsRegistry
from pyformance.reporters.csv_reporter import CsvReporter
from tests import ManualClock, TimedTestCase


class TestCsvReporter(TimedTestCase):

    def setUp(self):
        super(TestCsvReporter, self).setUp()
        self.clock = ManualClock()
        self.path = tempfile.mktemp()
        self.registry = MetricsRegistry(clock=self.clock)
        self.maxDiff = None

    def tearDown(self):
        super(TestCsvReporter, self).tearDown()
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def test_report_now(self):
        g1 = self.registry.gauge("gauge1")
        g1.set_value(123)

        with CsvReporter(
            registry=self.registry, reporting_interval=1, clock=self.clock,
            path=self.path) as r:
            r.report_now()

        output_filename = os.path.join(self.path, "gauge1.csv")

        output = open(output_filename).read()
        self.assertEqual(output.splitlines(), [
          'timestamp\tvalue', '1970-01-01 00:00:00\t123'
        ])


if __name__ == "__main__":
    unittest.main()
