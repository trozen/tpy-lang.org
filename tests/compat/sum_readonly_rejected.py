# expect: error readonly[list
from tpy import Own, Float64

class Reading:
    values: list[Float64]
    def __init__(self, values: Own[list[Float64]]):
        self.values = values
    @property
    def mean(self) -> Float64:
        return sum(self.values) / len(self.values)
