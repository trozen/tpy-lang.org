# expect: ok
from tpy import Float64, Own

class Vec:
    x: Float64
    y: Float64
    def __init__(self, x: Float64, y: Float64):
        self.x = x
        self.y = y
    def __add__(self, o: "Vec") -> "Own[Vec]":
        return Vec(self.x + o.x, self.y + o.y)

def main():
    v = Vec(1.0, 2.0) + Vec(3.0, 4.0)
    print(v.x, v.y)

main()
