# expect: ok
class Res:
    name: str
    def __init__(self, name: str):
        self.name = name
    def __del__(self) -> None:
        print("released", self.name)

def use() -> None:
    r = Res("a")
    print("using", r.name)

def main():
    use()
    print("after")

main()
