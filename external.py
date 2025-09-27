import pygame as pg
import numpy as np
import json

print("numpy", np.__version__)

if __name__ == "__main__":
    print("\nwrong file opened brochacho, it's main.py. Why'd you even open this?\n")

class Settings:
    def __init__(self):
        with open("EmuSettings.json", 'r') as f:
            self.settings = json.load(f)