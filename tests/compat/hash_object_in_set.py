# expect: ok
from tpy import uint64

class Tag:
    name: str
    def __init__(self, name: str):
        self.name = name
    def __eq__(self, o: "Tag") -> bool:
        return self.name == o.name
    def __hash__(self) -> uint64:
        return hash(self.name)

def main():
    s: set[Tag] = set()
    s.add(Tag("a"))
    s.add(Tag("a"))
    print(len(s))

main()
