# expect: ok
import os
import platform
import signal
import sys
from subprocess import Popen
from types import FrameType

got: list[int] = []

def on_term(signum: int, frame: FrameType | None) -> None:
    got.append(signum)

def main():
    print(sys.platform, platform.system(), platform.machine())
    signal.signal(signal.SIGTERM, on_term)
    signal.raise_signal(signal.SIGTERM)
    print(len(got))
    try:
        signal.raise_signal(signal.SIGINT)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    p = Popen(["sleep", "5"])
    os.kill(p.pid, signal.SIGKILL)
    pid, status = os.waitpid(p.pid, 0)
    print(os.waitstatus_to_exitcode(status))

main()
