# expect: ok
from tpy import float64

class Sample:
    value: float64
    def __init__(self, value: float64):
        self.value = value

class Gap:
    pass

def describe(x: Sample | Gap) -> str:
    match x:
        case Sample():
            return "sample"
        case Gap():
            return "gap"

def main():
    stream: list[Sample | Gap] = [Sample(1.0), Gap()]
    for x in stream:
        print(describe(x))

main()
