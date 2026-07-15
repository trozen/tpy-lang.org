# expect: ok
from tpy import Int32, Float64

def scale(x: Float64, factor: Float64 = 2.0) -> Float64:
    return x * factor

def label(name: str, unit: str = "C", precision: Int32 = 1) -> str:
    return name + " [" + unit + "]"

def main():
    print(scale(3.0))
    print(scale(3.0, 10.0))
    print(scale(3.0, factor=0.5))
    print(label("temp", precision=2))

main()
