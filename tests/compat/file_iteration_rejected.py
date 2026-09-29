# expect: error Cannot iterate over type TextIO
def main():
    with open("probe.txt") as f:
        for line in f:
            print(line)

main()
