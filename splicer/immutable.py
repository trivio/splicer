import inspect
from typing import Any


# TODO: deprecate this in favor of namedtuples
class ImmutableMixin(object):
    """
    Mixin used to provide immutable object support (kind of).

    This class allows you to quickly construct a new object
    based off an existing one.
    """

    def __eq__(self, other: Any) -> bool:
        other_slots = getattr(other, "__slots__", ())
        slots = tuple(self.__slots__)
        if len(slots) != other_slots:
            return False

        return all(
            [getattr(self, s) == getattr(other, o) for s, o in zip(slots, other_slots)]
        )

    def new(self, **parts: Any) -> Any:
        """
        Returns a copy of the existing object with the specified attrs
        overwritten.
        """
        attrs = {attr: getattr(self, attr) for attr in self.__slots__}
        attrs.update(parts)

        arg_spec = inspect.getfullargspec(self.__class__.__init__)

        args = []
        for arg in arg_spec.args[1:]:
            args.append(attrs.pop(arg))

        if arg_spec.varargs is not None:
            args.extend(attrs.pop(arg_spec.varargs, ()))

        return self.__class__(*args, **attrs)
