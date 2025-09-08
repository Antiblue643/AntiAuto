#!/usr/bin/env python
import pygame as pg
import os
import sys
from pathlib import Path

project_dir = Path(__file__).parent #no idea if this stuff works
sys.path.append(str(project_dir))

from display import Display as d
from floppy import Parser as p
from audio import Audio as a
from external import Settings as s

screen = d()
parser = p()
audio = a()
settings = s()

if __name__ == "__main__":
    try:
        while True:
            try:
                if os.path.exists("temp.py"):
                    os.remove("temp.py")
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