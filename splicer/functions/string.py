from __future__ import absolute_import
import string
import inspect

def null_if_arg_is_null(f):
  """
  Wrap a standard python function which inspects the args for None values.
  If they're present the function returns None as it's value otherwise
  returns the results of calling the function.S
  """
  def _(s, *args):
    if s is None:
      return None
    else:
      return f(s, *args)
  _.__name__ = f.__name__
  return _


def init(dataset):
  for name, func in inspect.getmembers(string, inspect.isfunction):
    if name == 'count':
      continue

    
    dataset.add_function(
      name,
      null_if_arg_is_null(func),
      returns=dict(name=name, type="STRING")
    )

  @dataset.function(returns=dict(name="length", type="INTEGER"))
  def length(s):
    return len(s)
