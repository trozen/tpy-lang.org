# expect: error f-string
def main():
    squares = [x * x for x in range(5)]
    print(f"squares={squares}")

main()
