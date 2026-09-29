# expect: error not yet supported by C++ code generation
class R:
    x: int
    def __init__(self, x: int):
        self.x = x

def pick(items: list[R]) -> tuple[R, bool]:
    return (items[0], True)

def main():
    items = [R(1)]
    t = pick(items)
    r, ok = t
    print(r.x, ok)

main()
