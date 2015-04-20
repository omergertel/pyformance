from pyformance.meters import Timer
from tests import TimedTestCase


class TimerTestCase(TimedTestCase):

    def setUp(self):
        super(TimerTestCase, self).setUp()
        self.timer = Timer()

    def tearDown(self):
        super(TimerTestCase, self).tearDown()

    def test__start_stop_clear(self):
        context = self.timer.time()
        self.clock.add(1)
        context.stop()

        self.assertEqual(self.timer.get_count(), 1)

        self.timer.clear()

        self.assertEqual(self.timer.get_count(), 0)
