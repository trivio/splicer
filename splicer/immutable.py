import inspect

class ImmutableMixin(object):
  """
  Mixin used to provide immutable object support (kind of).

  This class allows you to quickly construct a new object
  based off an existing one.
  """

  def __eq__(self, other):
    other_slots = getattr(other, '__slots__', ())
    slots = self.__slots__
    if len(slots) != other_slots:
      return False

    return all([
      getattr(self, s) == getattr(other,o) 
      for s,o in zip(slots, other_slots)
    ])


  def new(self, **parts):
    """
    Returns a copy of the existing object with the specidied attrs
    overwritten.
    """
    attrs = {attr:getattr(self, attr) for attr in self.__slots__}
    attrs.update(parts)

    arg_spec = inspect.getargspec(self.__class__.__init__)
    args = []
    for arg in arg_spec.args[1:]:
      args.append(attrs.pop(arg))

    args.extend(attrs.pop(arg_spec.varargs, ()))

    return self.__class__(*args, **attrs)
