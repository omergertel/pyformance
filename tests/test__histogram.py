from tests import TimedTestCase
from pyformance.meters import Histogram


class HistogramTestCase(TimedTestCase):

    def test__a_sample_of_100_from_1000(self):
        hist = Histogram(100, 0.99)
        for i in range(1000):
            hist.add(i)

        self.assertEqual(1000, hist.get_count())
        self.assertEqual(100, hist.sample.get_size())
        snapshot = hist.get_snapshot()
        self.assertEqual(100, snapshot.get_size())

        for i in snapshot.values:
            self.assertTrue(0 <= i and i <= 1000)

        self.assertEqual(999, hist.get_max())
        self.assertEqual(0, hist.get_min())
        self.assertEqual(499.5, hist.get_mean())
        self.assertAlmostEqual(83416.6666, hist.get_var(), delta=0.0001)

    def test__a_sample_of_100_from_10(self):
        hist = Histogram(100, 0.99)
        for i in range(10):
            hist.add(i)

        self.assertEqual(10, hist.get_count())
        self.assertEqual(10, hist.sample.get_size())
        snapshot = hist.get_snapshot()
        self.assertEqual(10, snapshot.get_size())

        for i in snapshot.values:
            self.assertTrue(0 <= i and i <= 10)

        self.assertEqual(9, hist.get_max())
        self.assertEqual(0, hist.get_min())
        self.assertEqual(4.5, hist.get_mean())
        self.assertAlmostEqual(9.1666, hist.get_var(), delta=0.0001)

    def test__a_long_wait_should_not_corrupt_sample(self):
        hist = Histogram(10, 0.015, clock=self.clock)

        for i in range(1000):
            hist.add(1000 + i)
            self.clock.add(0.1)

        self.assertEqual(hist.get_snapshot().get_size(), 10)
        for i in hist.sample.get_snapshot().values:
            self.assertTrue(1000 <= i and i <= 2000)

        self.clock.add(15 * 3600)  # 15 hours, should trigger rescale
        hist.add(2000)
        self.assertEqual(hist.get_snapshot().get_size(), 2)
        for i in hist.sample.get_snapshot().values:
            self.assertTrue(1000 <= i and i <= 3000)

        for i in range(1000):
            hist.add(3000 + i)
            self.clock.add(0.1)
        self.assertEqual(hist.get_snapshot().get_size(), 10)
        for i in hist.sample.get_snapshot().values:
            self.assertTrue(3000 <= i and i <= 4000)
