# expect: ok
from tpy import Int32

def total(*xs: Int32) -> Int32:
    t: Int32 = 0
    for x in xs:
        t += x
    return t

def main():
    print(total(1, 2, 3))

main()
