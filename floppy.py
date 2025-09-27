import runpy
import os
import re
import importlib.util

diskpath = 'disk/'

if __name__ == "__main__":
    print("\nwrong file opened brochacho, it's main.py\n")

class Parser:
    def __init__(self):
        self.special_imports = {
            'screen':      'from display import Display as d\ndisplay = d()',
            'audio':       'from audio import Audio as a\naudio = a()',
            'essentials': (
                'import pygame as pg\n'
                'from display import Display as d\n'
                'screen = d()\n'
                'from audio import Audio as a\n'
                'audio = a()'
            ),
            'main':        'import pygame as pg',
            'floppy':      'from floppy import Parser as aap\nparser = aap()'
        }

        self.key = {
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
            'play_note': 'play_wave',
            'draw_dot': 'draw_pixel',
            'tone(': 'play_wave(',
            'screen.type': 'screen.draw_string',
        }

        self.special_keys = {
            ('b', 'CTRL'): 'raise SystemExit',
            ('F4', 'CTRL'): 'screen.clear()',
            ('F9', 'CTRL'): 'raise ValueError("Intentional Crash")',
        }
        self.visited = set()

    # locate custom modules on disk
    def resolve_module(self, module_name, base_dir):
        rel_path = module_name.replace('.', os.sep)
        candidates = [
            os.path.join(base_dir, rel_path),
            os.path.join(diskpath, rel_path)
        ]
        for c in candidates:
            for ext in ('.aap', '.aam'):
                if os.path.exists(c + ext):
                    return c + ext
        return None

    def parse_file(self, filename, base_dir):
        if filename in self.visited:
            return []
        self.visited.add(filename)

        with open(filename, 'r') as f:
            lines = f.readlines()

        processed = []
        for line in lines:
            indentation = len(line) - len(line.lstrip())
            spaces = ' ' * indentation
            processed_line = line.lstrip()

            # detect imports
            m = re.match(r'^\s*import\s+([\w\.]+)\s*$', processed_line)
            if m:
                module_name = m.group(1)

                # 1) Special shorthands (screen/audio/essentials/...)
                if module_name in self.special_imports:
                    processed.append(spaces + self.special_imports[module_name] + '\n')
                    continue

                # 2) custom module (search disk for .aap/.aam)
                mod_path = self.resolve_module(module_name, os.path.dirname(filename))
                if mod_path:
                    processed.extend(self.parse_file(mod_path, os.path.dirname(mod_path)))
                    continue

                # 3) Native Python module
                if importlib.util.find_spec(module_name) is not None:
                    processed.append(spaces + processed_line.rstrip() + '\n')
                    continue

                raise FileNotFoundError(
                    f"Module '{module_name}' not found (custom or Python)."
                )

            # normal key replacements-
            for k, v in self.key.items():
                processed_line = processed_line.replace(k, v)

            # key/mouse held macros
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
                continue

            # special key injection
            if 'for event in pg.event.get()' in processed_line:
                processed.append(spaces + processed_line + '\n')
                for (key, mod), action in self.special_keys.items():
                    processed.append(
                        f"{spaces}    if event.type == pg.KEYDOWN and "
                        f"event.key == pg.K_{key} and "
                        f"pg.key.get_mods() & pg.KMOD_{mod}:\n"
                        f"{spaces}        {action}\n"
                    )
                    processed.append(spaces + '    pg.event.set_grab(True)\n')
            else:
                processed.append(spaces + processed_line.rstrip() + '\n')

        return processed

    def parse_keys(self, filename):
        file_path = os.path.join(diskpath, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Program file not found: {file_path}")

        self.visited.clear()
        header = [
            '#    / \\    WARNING!!!!!!\n',
            '#   / | \\   THIS IS A TEMP FILE!\n',
            '#  /  !  \\  DO NOT EDIT!\n',
            '# /_______\\ YOUR CHANGES WILL NOT SAVE!\n\n'
        ]
        processed = header + self.parse_file(file_path, os.path.dirname(file_path))
        with open('temp.py', 'w') as f:
            f.writelines(processed)

    def reset(self):
        if os.path.exists('temp.py'):
            os.remove('temp.py')

    def run(self):
        if os.path.exists('temp.py'):
            try:
                runpy.run_path('temp.py')
            except Exception as e:
                try:
                    self.parse_keys('crash.aaph')
                    self.run()
                    print(f"An error has occurred: {e}")
                except Exception:
                    print("Umm, the crash handler also failed... How did you get here?")
        else:
            print('No temp.py to run.')