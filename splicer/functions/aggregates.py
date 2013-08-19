from ..field import Field

def init(dataset):
  dataset.add_aggregate(
    "count", 
    func=lambda state: state + 1,
    returns=Field(name="count", type="INTEGER"),
    initial=0
  )
    