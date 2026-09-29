# expect: ok
from tpy import float64

def main():
    xs: list[float64] = [3.0, 1.0, 2.0]
    xs.sort()
    print(xs)
    ys = sorted(xs, key=lambda v: -v)
    print(ys)

main()
