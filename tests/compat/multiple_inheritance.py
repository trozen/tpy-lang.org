# expect: ok
class A:
    def a(self) -> str:
        return "a"

class B:
    def b(self) -> str:
        return "b"

class C(A, B):
    pass

def main():
    c = C()
    print(c.a(), c.b())

main()
