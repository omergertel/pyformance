import logging
import time
from threading import Thread, Event
import six
from ..registry import global_registry, get_qualname


LOG = logging.getLogger(__name__)

class Reporter(object):
    def create_thread(self):
        # noinspection PyAttributeOutsideInit
        self._loop_thread = Thread(
            target=self._loop,
            name="pyformance reporter {0}".format(get_qualname(type(self))),
        )
        self._loop_thread.setDaemon(True)

    def __init__(self, registry=None, reporting_interval=30, clock=None):
        self.registry = registry or global_registry()
        self.reporting_interval = reporting_interval
        self.clock = clock or time
        self._stopped = Event()
        self.create_thread()

    def start(self):
        if self._stopped.is_set():
            return False

        r = str(self._loop_thread)
        if "stopped" in r:
            # has to be recreated in a celery worker
            self.create_thread()
        elif "started" in r:
            # already started
            return False

        self._loop_thread.start()
        return True

    def stop(self):
        self._stopped.set()

    def _loop(self):
        next_loop_time = time.time()
        while not self._stopped.is_set():
            try:
                self.report_now(self.registry)
            except Exception as e:
                LOG.error("Exception caught while reporting metrics", exc_info=e)
                pass
            next_loop_time += self.reporting_interval
            wait = max(0, next_loop_time - time.time())
            if six.PY2:
                time.sleep(wait)
            elif self._stopped.wait(timeout=wait):
                # wait is faster/better in Python 3
                # See http://stackoverflow.com/questions/29082268/python-time-sleep-vs-event-wait
                break  # true if timeout
        # self._stopped.clear()

    def report_now(self, registry=None, timestamp=None):
        raise NotImplementedError(self.report_now)
