# expect: error Cannot reassign global
class Obj:
    x: int
    def __init__(self, x: int):
        self.x = x

g: Obj = Obj(0)

def swap() -> None:
    global g
    g = Obj(1)

swap()
