# expect: ok
class Timer:
    label: str
    def __init__(self, label: str):
        self.label = label
    def __enter__(self) -> "Timer":
        print("start", self.label)
        return self
    def __exit__(self, a, b, c) -> bool:
        print("stop", self.label)
        return False

def main():
    with Timer("job") as t:
        print("working in", t.label)

main()
