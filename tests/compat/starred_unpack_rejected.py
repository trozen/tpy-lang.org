# expect: error
def main():
    xs: list[int] = [1, 2, 3]
    a, *rest = xs
    print(a, rest)

main()
