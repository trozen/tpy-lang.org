# expect: error Augmented assignment
from tpy import Float64

def total(*values: Float64) -> Float64:
    t = 0.0
    for v in values:
        t += v
    return t
