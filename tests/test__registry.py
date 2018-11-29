from pyformance import MetricsRegistry
from pyformance.meters import Meter, BaseMetric
from tests import TimedTestCase


class RegistryTestCase(TimedTestCase):
    def setUp(self):
        super(RegistryTestCase, self).setUp()
        self.registry = MetricsRegistry(TimedTestCase.clock)

    def tearDown(self):
        super(RegistryTestCase, self).tearDown()

    def test__add(self):
        self.registry.add("foo", Meter(TimedTestCase.clock))

    def test_updating_counter(self):
        self.registry.counter("test_counter").inc()
        self.registry.counter("test_counter").inc()
        self.assertEqual(self.registry.counter("test_counter").get_count(), 2)

    def test_updating_counter_with_tags(self):
        self.registry.counter("test_counter", {"weather": "sunny"}).inc()
        self.registry.counter("test_counter", {"weather": "sunny"}).inc()
        self.assertEqual(self.registry.counter("test_counter", {"weather": "sunny"}).get_count(), 2)

    def test_updating_counters_with_same_key_different_tags(self):
        self.registry.counter("test_counter", {"weather": "sunny", "cloudy": False}).inc()
        self.registry.counter("test_counter", {"weather": "rainy", "cloudy": True}).inc()
        self.registry.counter("test_counter", {"cloudy": False, "weather": "sunny"}).inc()
        self.registry.counter("test_counter", {"cloudy": True, "weather": "rainy"}).inc()

        self.assertEqual(self.registry.counter(
            "test_counter",
            {"weather": "sunny", "cloudy": False}
        ).get_count(), 2)
        self.assertEqual(self.registry.counter(
            "test_counter",
            {"weather": "rainy", "cloudy": True}
        ).get_count(), 2)

    def test_get_metrics(self):
        self.registry.counter("test_counter").inc()
        self.assertEqual(self.registry.get_metrics("test_counter"), {"count": 1})
        self.registry.gauge("test_gauge").set_value(10)
        self.assertEqual(self.registry.get_metrics("test_gauge"), {"value": 10})

    def test_dump_metrics(self):
        self.registry.counter("test_counter", {"tag1": "val1"}).inc()
        self.assertEqual(self.registry.dump_metrics(), {"test_counter": {"count": 1}})

    def test_dump_metrics_with_tags(self):
        self.registry.counter("test_counter", {"tag1": "val1"}).inc()
        self.assertEqual(
            self.registry.dump_metrics(key_is_metric=True),
            {BaseMetric("test_counter", {"tag1": "val1"}): {"count": 1}}
        )
