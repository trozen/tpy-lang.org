# expect: ok
def main():
    b = b"ab\x00c"
    print(len(b))

main()
