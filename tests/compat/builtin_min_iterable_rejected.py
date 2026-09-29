# expect: error No matching overload for min
def main():
    xs: list[int] = [3, 1, 2]
    print(min(xs))

main()
