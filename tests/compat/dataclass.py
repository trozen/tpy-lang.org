# expect: ok
from dataclasses import dataclass

@dataclass
class P:
    x: int
    y: int

def main():
    print(P(1, 2).x)

main()
