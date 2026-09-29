# expect: ok
from tpy import int32, float64

def scale(x: float64, factor: float64 = 2.0) -> float64:
    return x * factor

def label(name: str, unit: str = "C", precision: int32 = 1) -> str:
    return name + " [" + unit + "]"

def main():
    print(scale(3.0))
    print(scale(3.0, 10.0))
    print(scale(3.0, factor=0.5))
    print(label("temp", precision=2))

main()
