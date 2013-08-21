from . import aggregates
from . import math
from . import string
from . import relational

def init(dataset):
  aggregates.init(dataset)
  math.init(dataset)
  string.init(dataset)
  relational.init(dataset)
