import pygame as pg
import numpy as np
import random

class Settings:
    def __init__(self):
        self.hz = 3.58e6 #3.58MHz
        self.fps = self.hz/59666.6666667 #roughly 60Hz
        self.perepherals = ["keyboard", "mouse"] #avaliable perepherals: keyboard, mouse, gamepad, microphone (only 2 at a time)