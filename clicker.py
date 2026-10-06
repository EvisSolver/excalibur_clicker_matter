import config, random
import subprocess, time, termios, sys, tty, asyncio


def coords_finder(seconds):
    while True:
        coords = subprocess.run(
            [
                "hyprctl", "cursorpos"#cursor-pos
            ], capture_output = True, text = True#outputs
        )
        clean_coords = coords.stdout.strip()#cleaning "_...(strips)"
        print(f":, {clean_coords:<30}", end = "\r", flush = True)
        time.sleep(seconds)

async def keyboard_detector(stop):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)
        while True:
            key = await asyncio.to_thread(sys.stdin.read, 1)
            if key.lower() == "y":
                stop.set()
                return
            print(key)
    finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)

async def auto_clicker_matter(seconds):
    x = int(config.x)
    y = int(config.y)
    while True:
        config.pixel_speed = random.randint(0, 20)

        subprocess.run(["hyprctl", "dispatch", "movecursor", str(x), str(y)])
        subprocess.run(["ydotool", "click", "0xC0"])

        print(config.x_pixel_speed, config.y_pixel_speed)
        time.sleep(seconds)


async def auto_click_buttons(seconds):
    y = 415
    while True:
        subprocess.run(["hyprctl", "dispatch", "movecursor", "1485", str(y)])
        subprocess.run(["ydotool", "click", "0xC0"])
        await asyncio.sleep(seconds)
        y += 129
        await asyncio.sleep(seconds)
        if y >= 940: break

async def auto_click_buttons_upgrades(seconds):
    x = 450
    while True:
        subprocess.run(["hyprctl", "dispatch", "movecursor", str(x), "930"])
        subprocess.run(["ydotool", "click", "0xC0"])
        await asyncio.sleep(seconds)
        x += 93
        await asyncio.sleep(seconds)
        if x >= 822.5: break

async def auto_click_meteorite(seconds):
    x, y, dx = 465, 410, 30          # dx — направление по x (+10 вправо / -10 влево)
    y_center = (410 + 870) // 2      # 640 — докуда доходим, потом рестарт

    while True:
        subprocess.run(["hyprctl", "dispatch", "movecursor", str(x), str(y)])
        subprocess.run(["ydotool", "click", "0xC0"])
        # subprocess.run(["ydotool", "click", "0xC0"])   # если нужен клик

        x += dx
        if x <= 465 or x >= 1360:    # край строки: прижали, развернулись, шаг вниз
            x = 465 if x <= 465 else 1360
            dx = -dx
            y += 30

        if y > y_center:             # прошли центр — начинаем заново
            x, y, dx = 465, 410, 30

        await asyncio.sleep(seconds)