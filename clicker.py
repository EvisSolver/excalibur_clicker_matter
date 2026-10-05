from config import *
import subprocess, time, termios, sys, tty, asyncio


def auto_clicker(seconds):
    while True:
        subprocess.run(
            [
                "ydotool", "mousemove", "--absolute",#sh-script 
                str(x), str(y)#coords
            ], check = True
        )
        subprocess.run(
            [
                "ydotool", "click", "0xC0"
            ], check = True
        )
        time.sleep(seconds)

async def coords_finder(seconds):
    while True:
        coords = subprocess.run(
            [
                "hyprctl", "cursorpos"#cursor-pos
            ], capture_output = True, text = True#outputs
        )
        clean_coords = coords.stdout.strip()#cleaning "_...(strips)"
        print(f":, {clean_coords:<30}", end = "\r", flush = True)
        await asyncio.sleep(seconds)

async def keyboard_detector():
    while True:
        termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        
        key = sys.stdin.read(1)
        state["key"] = key
        if state["key"] == "f":
            print("closed")
            break