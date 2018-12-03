from pyformance import MetricsRegistry, time_calls, timer
from pyformance.meters import Meter, BaseMetric
from tests import TimedTestCase
from pyformance.decorators import get_qualname


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

    def test_time_calls_with_registry(self):
        registry = MetricsRegistry()

        @time_calls(registry=registry, tags={"tag1": "val1"})
        def timed_func():
            pass

        timed_func()

        stats = registry.get_metrics(key="timed_func_calls", tags={"tag1": "val1"})
        print(registry.get_metrics(key="timed_func_calls", tags={"tag1": "val1"}))
        self.assertEqual(stats["count"], 1)
        self.assertTrue(stats["mean_rate"])

    def test_time_calls(self):
        @time_calls
        def timed_func():
            pass

        timed_func()
        func_timer = timer("timed_func_calls")
        self.assertEqual(func_timer.get_count(), 1)
        self.assertTrue(func_timer.get_mean())

    def test_get_qualname(self):
        def foo():
            pass

        self.assertEqual(get_qualname(foo), "foo")
