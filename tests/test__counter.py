from pyformance.meters import Counter
from tests import TimedTestCase


class CounterTestCase(TimedTestCase):

    def setUp(self):
        super(CounterTestCase, self).setUp()
        self.counter = Counter()

    def tearDown(self):
        super(CounterTestCase, self).tearDown()

    def test__inc(self):
        before = self.counter.get_count()
        self.counter.inc()
        after = self.counter.get_count()
        self.assertEqual(before + 1, after)

    def test__dec(self):
        before = self.counter.get_count()
        self.counter.dec()
        after = self.counter.get_count()
        self.assertEqual(before - 1, after)
