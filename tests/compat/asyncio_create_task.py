# expect: ok
import asyncio

async def fetch(n: int) -> int:
    await asyncio.sleep(0.01)
    return n

async def amain() -> None:
    t = asyncio.create_task(fetch(40))
    u = asyncio.create_task(fetch(2))
    print(await t + await u)

asyncio.run(amain())
