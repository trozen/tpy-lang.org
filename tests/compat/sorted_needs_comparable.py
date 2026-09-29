# expect: error Comparable
from tpy import float64

def main():
    by_sensor: dict[str, list[float64]] = {}
    by_sensor["a"] = [1.0]
    for name, vals in sorted(by_sensor.items()):
        print(name, len(vals))

main()
