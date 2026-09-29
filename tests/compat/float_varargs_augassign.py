# expect: error Augmented assignment
from tpy import float64

def total(*values: float64) -> float64:
    t = 0.0
    for v in values:
        t += v
    return t
