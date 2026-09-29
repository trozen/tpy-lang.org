# expect: ok
from tpy import float64, Own

class Vec:
    x: float64
    y: float64
    def __init__(self, x: float64, y: float64):
        self.x = x
        self.y = y
    def __add__(self, o: "Vec") -> "Own[Vec]":
        return Vec(self.x + o.x, self.y + o.y)

def main():
    v = Vec(1.0, 2.0) + Vec(3.0, 4.0)
    print(v.x, v.y)

main()
