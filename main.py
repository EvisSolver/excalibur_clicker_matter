import asyncio
import errno
import os
import socket
import struct


from config import buttons


HOLD = 0.003
STEP = 60

runtime = os.environ["XDG_RUNTIME_DIR"]
signature = os.environ["HYPRLAND_INSTANCE_SIGNATURE"]

HYPR = f"{runtime}/hypr/{signature}/.socket.sock"
if not os.path.exists(HYPR):
    HYPR = f"/tmp/hypr/{signature}/.socket.sock"

YDOO = os.environ.get("YDOTOOL_SOCKET") or f"{runtime}/.ydotool_socket"
if not os.path.exists(YDOO):
    YDOO = "/tmp/.ydotool_socket"

# input_event для 64-битной little-endian Linux.
DOWN = struct.pack("<qqHHi", 0, 0, 1, 0x110, 1)
UP = struct.pack("<qqHHi", 0, 0, 1, 0x110, 0)
SYN = struct.pack("<qqHHi", 0, 0, 0, 0, 0)



async def move(x, y):
    loop = asyncio.get_running_loop()

    async with asyncio.timeout(2):
        while True:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.setblocking(False)
                try:
                    s.connect(HYPR)
                except OSError as error:
                    if error.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                        raise
                else:
                    await loop.sock_sendall(
                        s, f"dispatch movecursor {x} {y}".encode()
                    )

                    reply = b""
                    while len(reply) < 2:
                        chunk = await loop.sock_recv(s, 64)
                        if not chunk:
                            break
                        reply += chunk

                    if reply != b"ok":
                        raise RuntimeError(f"Hyprland: {reply!r}")
                    return

            # Очередь подключений занята — повторяем с новым сокетом.
            await asyncio.sleep(0.001)


async def button(ydoo, event):
    loop = asyncio.get_running_loop()
    await loop.sock_sendall(ydoo, event)
    await loop.sock_sendall(ydoo, SYN)


async def click(ydoo, x, y, hold=HOLD, settle=0):
    await move(x, y)
    await asyncio.sleep(settle)

    try:
        await button(ydoo, DOWN)
        await asyncio.sleep(hold)
    finally:
        await button(ydoo, UP)


async def pause_until(deadline):
    await asyncio.sleep(
        max(0, deadline - asyncio.get_running_loop().time())
    )


async def meteorites(ydoo, lock):
    loop = asyncio.get_running_loop()
    x, y, dx = 465, 410, STEP

    while True:
        async with lock:
            deadline = loop.time() + 0.005
            await click(ydoo, x, y)

        edge = 1360 if dx > 0 else 465
        if x == edge:
            if y == 870:
                x, y, dx = 465, 410, STEP
            else:
                y = min(y + STEP, 870)
                dx = -dx
        else:
            x = max(465, min(x + dx, 1360))

        await pause_until(deadline)


async def center(ydoo, lock):
    loop = asyncio.get_running_loop()

    while True:
        async with lock:
            deadline = loop.time() + 0.05
            await click(ydoo, 960, 540)

        await pause_until(deadline)


async def buttons(ydoo, lock):
    while True:
        async with lock:
            for x, y in buttons:
                await click(ydoo, x, y, hold=0.05, settle=0.05)
                await asyncio.sleep(0.1)

        # Даём остальным задачам работать между сериями.
        await asyncio.sleep(10)


async def main():
    lock = asyncio.Lock()

    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as ydoo:
        ydoo.setblocking(False)
        await asyncio.get_running_loop().sock_connect(ydoo, YDOO)

        tasks = [
            asyncio.create_task(job(ydoo, lock))
            for job in (meteorites, center, buttons)
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