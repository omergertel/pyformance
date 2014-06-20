import platform
if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest


class ManualClock(object):

    def __init__(self):
        super(ManualClock, self).__init__()
        self.now = 0

    def add(self, value):
        self.now = self.now + value

    def time(self):
        return self.now


class TimedTestCase(unittest.TestCase):
    clock = ManualClock()
