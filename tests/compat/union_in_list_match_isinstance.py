# expect: ok
from tpy import float64

class Sample:
    value: float64
    def __init__(self, value: float64):
        self.value = value

class Gap:
    def __init__(self):
        pass

def main():
    stream: list[Sample | Gap] = [Sample(20.5), Gap(), Sample(21.5)]
    good = 0
    for x in stream:
        match x:
            case Sample(value=v):
                good += 1
            case _:
                pass
    print(good, len(stream))
    s = stream[0]
    print(isinstance(s, Sample))

main()
