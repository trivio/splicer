from ..field import Field


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

    # @dataset.aggregate(returns="INTEGER",initial=0)
    # def count(state):
    #  return state+1

    # @dataset.aggregate(returns="FLOAT", initial=(0,0.0))
    # def avg((count, sum), val):
    #  return count+1, sum+val

    # @avg.finalize
    # def avg((count, sum)):
    #  return sum count
