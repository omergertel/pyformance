class BaseMetric(object):

    """
    Abstract class for grouping common properties of metrics, such as tags
    """

    def __init__(self, tags=None):
        self.tags = tags or {}

    def get_tags(self):
        return self.tags
