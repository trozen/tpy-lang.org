# expect: ok
class Animal:
    name: str
    def __init__(self, name: str):
        self.name = name
    def sound(self) -> str:
        return "..."

class Dog(Animal):
    def __init__(self, name: str):
        super().__init__(name)
    def sound(self) -> str:
        return "woof"

def main():
    d = Dog("rex")
    print(d.name, d.sound())

main()
