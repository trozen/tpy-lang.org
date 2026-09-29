# expect: error Unknown function or type: 'tuple'
def main():
    xs: list[int] = [1, 2]
    print(tuple(xs))

main()
