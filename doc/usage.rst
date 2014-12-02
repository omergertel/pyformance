Usage
=====



Reporters
---------

A simple call which will periodically push out your metrics to [Hosted Graphite](https://www.hostedgraphite.com/) 
using the HTTP Interface. 


.. code-block:: python

    registry = MetricsRegistry()	
    #Push metrics contained in registry to hosted graphite every 10s for the account specified by Key
	reporter = HostedGraphiteReporter(registry, 10, "XXXXXXXX-XXX-XXXXX-XXXX-XXXXXXXXXX")
    # Some time later we increment metrics
    histogram = registry.histogram("test.histogram")
    histogram.add(0)
	histogram.add(10)
	histogram.add(25)



Advanced
--------

Decorators
~~~~~~~~~~

The simplest and easiest way to use the PyFormance library.

*Counter*

You can use the 'count_calls' decorator to count the number of times a function is called.

.. code-block:: python

    >>> from pyformance import counter, count_calls
    >>> @count_calls
    ... def test():
    ...     pass
    ... 
    >>> for i in range(10):
    ...     test()
    ... 
    >>> print counter("test_calls").get_count()
    10


*Timer*

You can use the 'time_calls' decorator to time the execution of a function and get distributtion data from it.

.. code-block:: python

    >>> import time
    >>> from pyformance import timer, time_calls
    >>> @time_calls
    ... def test():
    ...     time.sleep(0.1)
    ... 
    >>> for i in range(10):
    ...     test()
    ... 
    >>> print timer("test_calls").get_mean()
    0.100820207596


With statement
~~~~~~~~~~~~~~
You can also use a timer using the with statement

.. code-block:: python

    >>> from time import sleep
    >>> from pyformance import timer
    >>> with timer("test").time():
    ...    sleep(0.1)
    >>> print timer("test_calls").get_mean()
    0.10114598274230957
    


Regex Grouping
~~~~~~~~~~~~~~
Useful when working with APIs. A RegexRegistry allows to group API
calls and measure from a single location instead of having to define
different timers in different places.   

.. code-block:: python

    >>> from pyformance.registry import RegexRegistry
    >>> reg = RegexRegistry(pattern='^/api/(?P<model>)/\d+/(?P<verb>)?$')
    >>> def rest_api_request(path):
    ...     with reg.timer(path).time():
    ...         # do stuff
    >>> print reg.dump_metrics()
