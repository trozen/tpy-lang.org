# expect: error cannot build a tuple from a sequence
def main():
    xs: list[int] = [1, 2]
    print(tuple(xs))

main()
