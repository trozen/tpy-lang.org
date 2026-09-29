# expect: error readonly[list
from tpy import Own, float64

class Reading:
    values: list[float64]
    def __init__(self, values: Own[list[float64]]):
        self.values = values
    @property
    def mean(self) -> float64:
        return sum(self.values) / len(self.values)
