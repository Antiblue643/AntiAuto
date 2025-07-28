import pygame as pg
import time
import os
from display import Display as d
from floppy import Parser as p
from audio import Audio as a
from external import Settings as s

screen = d()
parser = p()
audio = a()
settings = s()

def reset_key_repeat():
    pg.key.set_repeat()  # Reset to no key repeat

reset_key_repeat()  # Initial reset

def bios():
    if os.path.exists("temp.py"):
        os.remove("temp.py")
    if settings.showSplash:
        screen.clear()
        screen.draw_aai(0, 0, "resources/splash.aai")
        screen.update()
        time.sleep(1.5)
    if settings.startupJingle:
        for note in ["E3", "A3", "E4"]:
            audio.beep(note, 0.5)
            time.sleep(0.1)


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