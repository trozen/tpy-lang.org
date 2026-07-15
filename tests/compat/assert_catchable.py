# expect: ok
def main():
    try:
        assert 1 == 2, "impossible"
    except Exception:
        print("caught assert")

main()
