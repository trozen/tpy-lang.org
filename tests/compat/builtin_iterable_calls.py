# expect: ok
def main():
    xs = [3, 1, 2]
    print(min(xs), max(xs), max(["aa", "b"], key=lambda s: len(s)))
    print(sorted(xs, reverse=True))
    it = iter(xs)
    print(next(it, -1))
    print(*xs, sep=", ")

main()
