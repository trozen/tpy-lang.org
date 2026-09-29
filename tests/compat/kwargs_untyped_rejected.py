# expect: error Unpack[TypedDict]
from tpy import int32

def show(**opts: int32) -> None:
    print(len(opts))

def main():
    show(a=1, b=2)

main()
