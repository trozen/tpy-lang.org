# expect: ok
from typing import Protocol, runtime_checkable

@runtime_checkable
class Named(Protocol):
    def name(self) -> str: ...

class Dog:
    def name(self) -> str:
        return "rex"

def show(x: Named) -> None:
    print(x.name())

def main():
    show(Dog())

main()
