# expect: error Unpack[TypedDict]
from tpy import Int32

def show(**opts: Int32) -> None:
    print(len(opts))

def main():
    show(a=1, b=2)

main()
