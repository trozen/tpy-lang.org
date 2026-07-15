# expect: ok
# tpy: ext_module
from tpy.extern import export

@export
def triple(x: int) -> int:
    return x * 3
