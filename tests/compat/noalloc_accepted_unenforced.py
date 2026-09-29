# expect: ok
from tpy import noalloc, float64, readonly

@noalloc
def mean(xs: readonly[list[float64]]) -> float64:
    tmp: list[float64] = []      # allocates -- should be rejected
    for x in xs:
        tmp.append(x)
    return sum(tmp) / len(tmp)
