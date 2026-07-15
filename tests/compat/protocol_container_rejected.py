# expect: error container element
from typing import Protocol
from tpy import dynamic

@dynamic
class Speaker(Protocol):
    def sound(self) -> str: ...

class Dog:
    def __init__(self):
        pass
    def sound(self) -> str:
        return "woof"

class Cat:
    def __init__(self):
        pass
    def sound(self) -> str:
        return "meow"

def speak(s: Speaker) -> str:
    return s.sound()

def main():
    pets: list[Speaker] = [Dog(), Cat()]
    for p in pets:
        print(speak(p))

main()
