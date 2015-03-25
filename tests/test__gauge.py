from pyformance.meters import CallbackGauge
from tests import TimedTestCase


class CallbackGaugeTestCase(TimedTestCase):

    def setUp(self):
        super(CallbackGaugeTestCase, self).setUp()
        self._value = None
        self.gauge = CallbackGauge(self._get_val)

    def tearDown(self):
        super(CallbackGaugeTestCase, self).tearDown()

    def _get_val(self):
        return self._value

    def test__value(self):
        self._value = 123
        self.assertEqual(self.gauge.get_value(), self._value)
