class BaseMetric(object):

    """
    Abstract class for grouping common properties of metrics, such as tags
    """

    def __init__(self, key, tags=None):
        self.key = key
        self.tags = tags or {}

    def get_tags(self):
        return self.tags

    def get_key(self):
        return self.key

    def __hash__(self):
        if not self.tags:
            return hash(self.key)

        return hash((self.key, frozenset(self.tags.items())))

    def __eq__(self, other):
        if not isinstance(other, BaseMetric):
            return False

        return self.key == other.key and set(self.tags) == set(other.tags)