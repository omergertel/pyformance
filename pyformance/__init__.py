__import__('pkg_resources').declare_namespace(__name__)

from .registry import timer, counter, meter, histogram
from .meters.timer import call_too_long
