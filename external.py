import pygame as pg
import numpy as np
import random
import json

print("numpy", np.__version__)

class Settings:
    def __init__(self):
        with open("EmuSettings.json", 'r') as f:
            self.settings = json.load(f)