from typing import Any, TypeVar, Protocol
from abc import abstractmethod

from ..field import Field

A=TypeVar("A", bound="Comparable")
B=TypeVar("B", bound="Comparable")

class Comparable(Protocol):
    ## based on https://github.com/python/typing/issues/59
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __lt__(self: A, other: A) -> bool:
        pass

    def __gt__(self: A, other: A) -> bool:
        return (not self < other) and self != other

    def __le__(self: A, other: A) -> bool:
        return self < other or self == other

    def __ge__(self: A, other: A) -> bool:
        return (not self < other)


def init(dataset):
    dataset.add_aggregate(
        "count",
        func=lambda state: state + 1,
        returns=Field(name="count", type="INTEGER"),
        initial=0,
    )

    dataset.add_aggregate(
        "min", func=min, returns=Field(name="min", type="INTEGER"), initial=float("Inf")
    )

    dataset.add_aggregate(
        "max",
        func=max,
        returns=Field(name="max", type="INTEGER"),
        initial=float("-Inf"),
    )
    
    # TODO: define max_by
    dataset.add_aggregate(
        "min_by",
        func=min_by,
        returns=Field(name="min_by", type="STRING"), #TODO someday add TypeVar's to Field
        initial=None,
        finalize=min_by_finalize
    )


    # @dataset.aggregate(returns="INTEGER",initial=0)
    # def count(state):
    #  return state+1

    # @dataset.aggregate(returns="FLOAT", initial=(0,0.0))
    # def avg((count, sum), val):
    #  return count+1, sum+val

    # @avg.finalize
    # def avg((count, sum)):
    #  return sum count


    

def min_by(previous:tuple[A,B], value:A, sel:B) -> tuple[A,B]:
    if previous is None or previous[1] > sel:
        return (value, sel)
    else:
        return previous

def min_by_finalize(final:tuple[A,B]) -> A:
    return final[0]

