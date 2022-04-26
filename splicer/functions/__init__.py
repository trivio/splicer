# type: ignore
from . import aggregates, filesystem, math, relational, string


def init(dataset):
    aggregates.init(dataset)
    math.init(dataset)
    string.init(dataset)
    filesystem.init(dataset)
    relational.init(dataset)
