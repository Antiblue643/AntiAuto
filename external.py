import pygame as pg
import numpy as np
import random

print("numpy", np.__version__)

class Settings:
    def __init__(self):
        self.hz = 3.58e6 #3.58MHz
        self.fps = self.hz/59666.6666667 #roughly 60Hz
       
        self.showFPS = False #Always show FPS in the top left
        self.showMousePos = False #show the mouse position
                
        self.showSplash = True #show splash screen on boot
        self.startupJingle = True #toggle the startup jingle on boot
        
        self.corruptDisplay = False #mess with drawPixel to fuck with the screen (This affects nothing, and is entirely reversable)
        self.corruptLevel = 1 #multiplier for level of corruption, affects some random values