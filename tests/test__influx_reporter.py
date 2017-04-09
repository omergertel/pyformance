from pyformance.reporters import influx  # just a syntax/sanity check


def test_initializes():
    influx.InfluxReporter()
