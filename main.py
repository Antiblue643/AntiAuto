import pygame as pg
import time
import os
from display import Display as d
from floppy import Parser as p
from audio import Audio as a

screen = d()
parser = p()
audio = a()

def reset_key_repeat():
    pg.key.set_repeat()  # Reset to no key repeat

reset_key_repeat()  # Initial reset

def bios():
    if os.path.exists("temp.py"):
        os.remove("temp.py")
        print("leftover temp.py deleted, didya crash? Syntax error? 🤔")
    else:
        print("No temp.py to delete... Safe for now... 😝")
    screen.showSplash()
    time.sleep(3)
    audio.beep("B2", 0.1)
    time.sleep(0.1)
    audio.beep("A4", 0.1)


bios()

if __name__ == "__main__":
    try:
        while True:
            try:
                parser.parse_keys("FE.aaph")
                parser.run()
            except SystemExit:
                parser.reset()
                break
            except Exception as e:
                print(f"Program error: {e}")
            finally:
                reset_key_repeat()  # Reset key repeat after each program
                parser.reset()
    finally:
        parser.reset()
        reset_key_repeat()  # One final reset before quitting
        pg.quit()