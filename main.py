import asyncio, socket
from clicker import *


async def main():
    '''starting the courutine'''
    lock = asyncio.Lock()

    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as ydoo:
        ydoo.setblocking(False)
        await asyncio.get_running_loop().sock_connect(ydoo, YDOO)

        tasks = [
            asyncio.create_task(job(ydoo, lock))
            for job in (meteorites, center, button_s)
        ]
        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass