# SCRIPTS WITH HELPS TO MAKE THIS
# import config, random
# import subprocess, time, termios, sys, tty, asyncio


# def coords_finder(seconds):
#     while True:
#         coords = subprocess.run(
#             [
#                 "hyprctl", "cursorpos"#cursor-pos
#             ], capture_output = True, text = True#outputs
#         )
#         clean_coords = coords.stdout.strip()#cleaning "_...(strips)"
#         print(f":, {clean_coords:<30}", end = "\r", flush = True)
#         time.sleep(seconds)

# async def keyboard_detector(stop):
#     fd = sys.stdin.fileno()
#     old = termios.tcgetattr(fd)

#     try:
#         tty.setcbreak(fd)
#         while True:
#             key = await asyncio.to_thread(sys.stdin.read, 1)
#             if key.lower() == "y":
#                 stop.set()
#                 return
#             print(key)
#     finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)

# async def auto_clicker_matter(seconds):
#     x = int(config.x)
#     y = int(config.y)
#     while True:
#         config.pixel_speed = random.randint(0, 20)

#         subprocess.run(["hyprctl", "dispatch", "movecursor", str(x), str(y)])
#         subprocess.run(["ydotool", "click", "0xC0"])

#         print(config.x_pixel_speed, config.y_pixel_speed)
#         time.sleep(seconds)


# async def auto_click_buttons(seconds):
#     y = 415
#     while True:
#         subprocess.run(["hyprctl", "dispatch", "movecursor", "1485", str(y)])
#         subprocess.run(["ydotool", "click", "0xC0"])
#         await asyncio.sleep(seconds)
#         y += 129
#         await asyncio.sleep(seconds)
#         if y >= 940: break

# async def auto_click_buttons_upgrades(seconds):
#     x = 450
#     while True:
#         subprocess.run(["hyprctl", "dispatch", "movecursor", str(x), "930"])
#         subprocess.run(["ydotool", "click", "0xC0"])
#         await asyncio.sleep(seconds)
#         x += 93
#         await asyncio.sleep(seconds)
#         if x >= 822.5: break

# async def auto_click_meteorite(seconds):
#     x, y, dx = 465, 410, 30          # dx — направление по x (+10 вправо / -10 влево)
#     y_center = (410 + 870) // 2      # 640 — докуда доходим, потом рестарт

#     while True:
#         subprocess.run(["hyprctl", "dispatch", "movecursor", str(x), str(y)])
#         subprocess.run(["ydotool", "click", "0xC0"])
#         # subprocess.run(["ydotool", "click", "0xC0"])   # если нужен клик

#         x += dx
#         if x <= 465 or x >= 1360:    # край строки: прижали, развернулись, шаг вниз
#             x = 465 if x <= 465 else 1360
#             dx = -dx
#             y += 30

#         if y > y_center:             # прошли центр — начинаем заново
#             x, y, dx = 465, 410, 30

#         await asyncio.sleep(seconds)



# GLOBAL SCRIPT

import asyncio
import errno
import os
import socket
import struct

from config import buttons


HOLD = 0.003#duration clicks-moves per sec | lower - can lagged | higher - good | already settings is recommend duration
STEP = 60#pixel-speed

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
    '''moving the cursor(logic)'''
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
    '''optimizer + logic-move'''
    loop = asyncio.get_running_loop()
    await loop.sock_sendall(ydoo, event)
    await loop.sock_sendall(ydoo, SYN)


async def click(ydoo, x, y, hold=HOLD, settle=0):
    '''clicker'''
    await move(x, y)
    await asyncio.sleep(settle)

    try:
        await button(ydoo, DOWN)
        await asyncio.sleep(hold)
    finally:
        await button(ydoo, UP)


async def pause_until(deadline):
    '''stopper'''
    await asyncio.sleep(
        max(0, deadline - asyncio.get_running_loop().time())
    )


async def meteorites(ydoo, lock):
    '''farming meteorites on the screen'''
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
    '''clicking on the hole(matter)'''
    loop = asyncio.get_running_loop()

    while True:
        async with lock:
            deadline = loop.time() + 0.05
            await click(ydoo, 960, 540)

        await pause_until(deadline)


async def button_s(ydoo, lock):
    '''buttons which clicking(x, y) | cfg inconfig/buttons | [[0 cfg - skill's], [1 cfg - upgrades]]'''
    while True:
        async with lock:
            for x, y in buttons:
                await click(ydoo, x, y, hold=0.05, settle=0.05)
                await asyncio.sleep(0.1)

        # Даём остальным задачам работать между сериями.
        await asyncio.sleep(10)
