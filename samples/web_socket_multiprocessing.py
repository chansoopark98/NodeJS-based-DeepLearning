import asyncio
from concurrent.futures import ProcessPoolExecutor

async def sub_main():
    print('Hello from subprocess')

def sub_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(sub_main())

async def start(executor):
    await asyncio.get_event_loop().run_in_executor(executor, sub_loop)

if __name__ == '__main__':
    executor = ProcessPoolExecutor()
    asyncio.get_event_loop().run_until_complete(start(executor))