from . import aggregates
from . import math
from . import string

def init(dataset):
  aggregates.init(dataset)
  math.init(dataset)
  string.init(dataset)