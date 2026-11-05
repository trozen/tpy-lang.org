# expect: ok
from subprocess import PIPE, Popen

def main():
    p = Popen(["echo", "hello"], stdout=PIPE)
    assert p.stdout is not None
    print(p.stdout.read(), p.wait())

main()
