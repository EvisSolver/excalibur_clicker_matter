from config import *
import subprocess, time


def auto_clicker():
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
        time.sleep(3)

def coords_finder():
    while True:
        coords = subprocess.run(
            [
                "hyprctl", "cursorpos"
            ], capture_output = True, text = True
        )
        clean_coords = coords.stdout.strip()
        print(f":, {clean_coords:<30}", end = "\r", flush = True)
        time.sleep(0.01)
coords_finder()