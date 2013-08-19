from __future__ import absolute_import
import math
import inspect


def init(dataset):
  for name,func in inspect.getmembers(math, inspect.isbuiltin):
    # builtins can't have attributes, which is where we store
    # the type info
    f = lambda *args: func(*args)
    dataset.add_function(
      name,
      f,
      returns=dict(name=name, type='NUMBER')
    )
