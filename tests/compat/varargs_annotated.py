# expect: ok
from tpy import int32

def total(*xs: int32) -> int32:
    t: int32 = 0
    for x in xs:
        t += x
    return t

def main():
    print(total(1, 2, 3))

main()
