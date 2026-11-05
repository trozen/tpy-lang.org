# expect: ok
import asyncio
import collections


async def work() -> None:
    q: asyncio.Queue[int] = asyncio.Queue()
    await q.put(1)
    print(await q.get())


def main():
    c = collections.Counter(["a", "b", "a"])
    print(c["a"])
    asyncio.run(work())

main()
