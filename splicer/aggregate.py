class Aggregate(object):
  def __init__(self, function, returns, initial=None, finalize=None):
    self.function = function
    self.returns = returns
    self.initial  = initial
    self.finalize = finalize
    self.state = None

  def __call__(self, *args):
    return args