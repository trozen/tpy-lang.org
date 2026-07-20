# expect: ok
from typing import Any, ClassVar, cast

class Settings:
    default_port: ClassVar[int] = 8080

def as_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    return cast(int, value)

def main():
    line = input()
    value: Any = 42
    print(line, as_int(value), Settings.default_port)

main()
