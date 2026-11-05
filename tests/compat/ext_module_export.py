# expect: ok
__tpy__ = {"mod": "ext"}
from tpy.extern import export

@export
def triple(x: int) -> int:
    return x * 3
