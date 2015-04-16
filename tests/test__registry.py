from pyformance import MetricsRegistry
from pyformance.meters import Meter
from tests import TimedTestCase


class RegistryTestCase(TimedTestCase):


    def setUp(self):
        super(RegistryTestCase, self).setUp()
        self.registry = MetricsRegistry(TimedTestCase.clock)

    def tearDown(self):
        super(RegistryTestCase, self).tearDown()

    def test__add(self):
        self.registry.add('foo', Meter(TimedTestCase.clock))
