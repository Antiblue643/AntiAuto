import pygame as pg
import numpy as np
import random

class Settings:
    def __init__(self):
        self.hz = 3.58e6 #3.58MHz
        self.fps = self.hz/59666.6666667 #roughly 60Hz
        self.showFPS = True #Always show FPS in the top left
        
        self.perepherals = ["keyboard", "mouse"] #avaliable perepherals: keyboard, mouse, gamepad, microphone (only 2 at a time)
        
        self.showSplash = False #show splash screen on boot
        self.startupJingle = False #toggle the startup jingle on boot
        
        
        self.corruptDisplay = False #mess with drawPixel to fuck with the screen (This affects nothing, and is entirely reversable)
        self.corruptLevel = 1 #multiplier for level of corruption, affects some random values