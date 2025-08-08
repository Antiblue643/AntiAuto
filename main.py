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

def splash():
    if os.path.exists("temp.py"):
        os.remove("temp.py")
    if settings.settings.get("showSplash"):
        screen.clear()
        screen.draw_aai(0, 0, "resources/splash.aai")
        screen.update(False, False)
        time.sleep(1.5)
    if settings.settings.get("startupJingle"):
        for note in ["E3", "A3", "E4"]:
            audio.beep(note, 0.5)
            audio.rest(0.1)



if __name__ == "__main__":
    try:
        while True:
            try:
                splash()
                parser.parse_keys("bios.aaph" if settings.settings.get("useBios") else "FE.aaph")
                parser.run()
            except SystemExit:
                parser.reset()
                audio.panic()
                break
            except Exception as e:
                print(f"Program error: {e}")
            finally:
                parser.reset()
    finally:
        parser.reset()
        pg.quit()