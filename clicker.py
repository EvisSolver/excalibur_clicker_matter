
import subprocess, time

while True:
    subprocess.run(
        [
            "ydotool", "click", "0xC0"
        ], check = True
    )
    time.sleep(1)