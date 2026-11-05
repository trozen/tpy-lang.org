# expect: ok
def main():
    pairs = [(x, y) for x in range(3) for y in range(x)]
    print(pairs)
    grid = [[r * 3 + c for c in range(3)] for r in range(2)]
    print([v for row in grid for v in row if v % 2 == 0])

main()
