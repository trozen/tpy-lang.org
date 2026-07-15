# expect: ok
from tpy import noalloc, Float64, readonly

@noalloc
def mean(xs: readonly[list[Float64]]) -> Float64:
    tmp: list[Float64] = []      # allocates -- should be rejected
    for x in xs:
        tmp.append(x)
    return sum(tmp) / len(tmp)
