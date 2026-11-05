# expect: ok
def main():
    with open("probe.txt") as f:
        for line in f:
            print(line)

main()
