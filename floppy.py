#parses the program to a temporary file to be used by the main script
#It gets messy sometimes, y'know? Code generating code.


import runpy
import os
import re

diskpath = 'disk/'

class Parser:
    def __init__(self):
        self.key = {
            'import main': 'import pygame as pg',
            'import screen': 'from display import Display as d\ndisplay = d()',
            'import floppy': 'from floppy import Parser as aap\nparser = aap()',
            'import essentials': 'import pygame as pg\nfrom display import Display as d\nscreen = d()\nfrom audio import Audio as a\naudio = a()\nbeep = audio.beep\nplay_note = audio.play_note',
            'get_events': 'event in pg.event.get()',
            'quit_event': 'event.type == pg.QUIT',
            'key_down_event': 'event.type == pg.KEYDOWN',
            'key_': 'event.key == pg.K_',
            'init_mods': 'pg.key.get_mods()',
            'keymod_': 'pg.KMOD_',
            'left_click': "event.type == pg.MOUSEBUTTONDOWN and event.button == 1",
            'middle_click': "event.type == pg.MOUSEBUTTONDOWN and event.button == 2",
            'right_click': "event.type == pg.MOUSEBUTTONDOWN and event.button == 3",
            'scroll_up': 'event.type == pg.MOUSEBUTTONDOWN and event.button == 4',
            'scroll_down': 'event.type == pg.MOUSEBUTTONDOWN and event.button == 5',
            'obtain_keys_held()': 'pg.key.get_pressed()',
            'keycode_': 'pg.K_',
            #Attempt some vectormaster stuffs
            'draw_dot': 'draw_pixel',
            'tone': 'play_note' #Volume & frequency will need to be swapped
        }

    def parse_keys(self, filename): #take all the lines, parse them, remove comments, and put them into a temporary file
        file_path = os.path.join(diskpath, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Program file not found: {file_path}")
            
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        processed_lines = []
        for i, line in enumerate(lines):
            indentation = len(line) - len(line.lstrip())
            spaces = ' ' * indentation
            processed_line = line.lstrip()

            for k, v in self.key.items():
                processed_line = processed_line.replace(k, v)

            processed_line = re.sub(
                r'key_held_([a-zA-Z0-9_]+)',
                r'pg.key.get_pressed()[pg.K_\1]',
                processed_line
            )
            processed_line = re.sub(
                r'mouse_held_([0-2])',
                r'pg.mouse.get_pressed()[\1]',
                processed_line
            )

            if processed_line.lstrip().startswith('#'):
                processed_line = ''
            
            processed_line = processed_line.rstrip()

            # If this is the event loop, insert special key logic right after
            if 'for event in pg.event.get()' in processed_line:
                processed_lines.append(spaces + processed_line + '\n')
                special = spaces + '    ' + (
                    'if event.type == pg.KEYDOWN and event.key == pg.K_b and pg.key.get_mods() & pg.KMOD_CTRL:\n'
                    + spaces + '        raise SystemExit\n'
                )
                processed_lines.append(special)
            elif processed_line:
                processed_lines.append(spaces + processed_line + '\n')

        # Write all processed lines to temp.py
        with open('temp.py', 'w') as file:
            file.writelines(processed_lines)
    def reset(self):
        if os.path.exists('temp.py'):
            os.remove('temp.py')
    def run(self):
        if os.path.exists('temp.py'):
            try:
                runpy.run_path('temp.py')
            except Exception as e:
                print(f"#!#!#!#!# Program error: {e} #!#!#!#!#")
        else:
            print('No file to run or the temp file was not found at ' + diskpath + 'temp.py for some reason. (How???)')
