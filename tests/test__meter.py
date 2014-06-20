from pyformance.meters import Meter
from tests import TimedTestCase


class MeterTestCase(TimedTestCase):

    def setUp(self):
        super(MeterTestCase, self).setUp()
        self.meter = Meter(TimedTestCase.clock)

    def tearDown(self):
        super(MeterTestCase, self).tearDown()

    def test__one_minute_rate(self):
        self.meter.mark(3)
        self.clock.add(5)
        self.meter.tick()

        # the EWMA has a rate of 0.6 events/sec after the first tick
        self.assertAlmostEqual(
            0.6, self.meter.get_one_minute_rate(), delta=0.000001)

        self.clock.add(60)
        # the EWMA has a rate of 0.22072766 events/sec after 1 minute
        self.assertAlmostEqual(
            0.22072766, self.meter.get_one_minute_rate(), delta=0.000001)

        self.clock.add(60)
        # the EWMA has a rate of 0.08120117 events/sec after 2 minute
        self.assertAlmostEqual(
            0.08120117, self.meter.get_one_minute_rate(), delta=0.000001)

    def test__five_minute_rate(self):
        self.meter.mark(3)
        self.clock.add(5)
        self.meter.tick()

        # the EWMA has a rate of 0.6 events/sec after the first tick
        self.assertAlmostEqual(
            0.6, self.meter.get_five_minute_rate(), delta=0.000001)

        self.clock.add(60)
        # the EWMA has a rate of 0.49123845 events/sec after 1 minute
        self.assertAlmostEqual(
            0.49123845, self.meter.get_five_minute_rate(), delta=0.000001)

        self.clock.add(60)
        # the EWMA has a rate of 0.40219203 events/sec after 2 minute
        self.assertAlmostEqual(
            0.40219203, self.meter.get_five_minute_rate(), delta=0.000001)

    def test__fifteen_minute_rate(self):
        self.meter.mark(3)
        self.clock.add(5)
        self.meter.tick()

        # the EWMA has a rate of 0.6 events/sec after the first tick
        self.assertAlmostEqual(
            0.6, self.meter.get_fifteen_minute_rate(), delta=0.000001)

        self.clock.add(60)
        # the EWMA has a rate of 0.56130419 events/sec after 1 minute
        self.assertAlmostEqual(
            0.56130419, self.meter.get_fifteen_minute_rate(), delta=0.000001)

        self.clock.add(60)
        # the EWMA has a rate of 0.52510399 events/sec after 2 minute
        self.assertAlmostEqual(
            0.52510399, self.meter.get_fifteen_minute_rate(), delta=0.000001)

    def test__mean_rate(self):
        self.meter.mark(60)
        self.clock.add(60)
        self.meter.tick()
        val = self.meter.get_mean_rate()
        self.assertEqual(1, val)
