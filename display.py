from external import pg, Settings as s
import re
import random

# The display is a 256x192 per-pixel display. It has 24 colors.
NATIVE_WIDTH = 256
NATIVE_HEIGHT = 192

icon = pg.image.load("resources/icon.png")
screen = pg.display.set_mode((NATIVE_WIDTH, NATIVE_HEIGHT), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF)
display_surface = pg.Surface((NATIVE_WIDTH, NATIVE_HEIGHT)).convert()
back_buffer = pg.Surface((NATIVE_WIDTH, NATIVE_HEIGHT)).convert()  # Add hardware acceleration
pg.display.set_caption("AAngine")
pg.display.set_icon(icon)
settings = s()

splash = pg.image.load("resources/splash.png")

cl = settings.corruptLevel

pg.init()

BASE25 = "0123456789ABCDEFGHIJKLMNO"

class Display:
    def __init__(self):
        self.fonts = []
        self.char_map = self.load_char_map()
        self.colors = []
        self.color_cache = {}  # Initialize color cache first
        self.current_background = 0
        self.clock = pg.time.Clock()
        self.cached_size = (NATIVE_WIDTH, NATIVE_HEIGHT)
        self.scaled_surface = None
        self.needs_rescale = True
        
        # Load resources after initializing caches
        self.loadFont()
        self.parseFont()
        self.loadColors()

    def load_char_map(self):
        char_map = {}
        try:
            with open('resources/chars.txt', "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) == 2:
                        name, idx = parts
                        try:
                            if idx.endswith('f'):
                                char_map[name] = (int(idx[:-1]), True)  # (index, flip)
                            else:
                                char_map[name] = (int(idx), False)
                        except ValueError:
                            continue
        except FileNotFoundError:
            #really bruh
            quit("Where's the file for the characters? You didn't delete it, did you?\nMake sure it's named chars.txt and in the resources folder!")
        # Add space as ' ' for convenience if not present
        if "space" in char_map:
            char_map[" "] = char_map["space"]
        return char_map

    def showSplash(self):
        screen.blit(splash, (0, 0))
        pg.display.update()

    def loadFont(self):
        # The font is an 128x128 monocolor bitmap image, with 8x8 characters.
        self.font = pg.image.load("resources/chars.png")  
    
    def parseFont(self):
        # Every 8x8 tile is a character, meaning there are 256 characters
        for y in range(16):
            for x in range(16):
                char_index = y * 16 + x
                # Create a new surface with alpha for each character
                char_surface = pg.Surface((8, 8), flags=pg.SRCALPHA).convert_alpha()
                char_surface.blit(self.font, (0, 0), (x * 8, y * 8, 8, 8))
                self.fonts.append(char_surface)

    def loadColors(self):
        try:
            with open("resources/colors.hex", "r") as f:
                self.colors = f.read().split("\n")
                # Pre-cache all colors
                for i, hex_color in enumerate(self.colors):
                    if hex_color:  # Skip empty lines
                        r = int(hex_color[0:2], 16)
                        g = int(hex_color[2:4], 16)
                        b = int(hex_color[4:6], 16)
                        self.color_cache[i] = (r, g, b)  # Store as RGB tuple
        except FileNotFoundError:
            quit("No colors file found!")

    def draw_pixel(self, x, y, color=23):
        x = int(x)
        y = int(y)
        if settings.corruptDisplay:
            #x = x + ((y + cl & 8 - color) - y)
            color += (x & 8 ^ (y + random.randint(-cl, cl)) % 24)
        if 0 <= color < len(self.colors) and 0 <= x < NATIVE_WIDTH and 0 <= y < NATIVE_HEIGHT:
            back_buffer.set_at((x, y), self.color_cache.get(color, (255, 0, 255)))

    def draw_line(self, x1, y1, x2, y2, color=23):
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        pg.draw.line(back_buffer, self.color_cache[color], (x1, y1), (x2, y2))

    def draw_rect(self, x1, y1, x2, y2, color=23, outlineColor=None):
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        # Draw filled rectangle
        pg.draw.rect(back_buffer, self.color_cache[color], (x1, y1, x2 - x1, y2 - y1))
        # Draw outline if outlineColor is not None
        if outlineColor is not None:
            pg.draw.rect(back_buffer, self.color_cache[outlineColor], (x1, y1, x2 - x1, y2 - y1), 1)
    
    def draw_ellipse(self, x, y, radiusX, radiusY, color=23):
        x = int(x)
        y = int(y)
        radiusX = int(radiusX)
        radiusY = int(radiusY)
        pg.draw.ellipse(back_buffer, self.color_cache[color], (x - radiusX, y - radiusY, radiusX * 2, radiusY * 2))

    def draw_triangle(self, x1, y1, x2, y2, x3, y3, color=23):
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        x3 = int(x3)
        y3 = int(y3)
        pg.draw.polygon(back_buffer, self.color_cache[color], [(x1, y1), (x2, y2), (x3, y3)])

    def draw_char(self, x, y, char, color1=-1, color2=23):
        flip = False
        if isinstance(char, tuple):
            char_idx, flip = char
        else:
            char_idx = char
        if 0 <= char_idx < len(self.fonts):
            # Make a copy so flipping doesn't affect the original
            font_surface = self.fonts[char_idx].copy()
            if flip:
                font_surface = pg.transform.flip(font_surface, True, False)
            for i in range(8):
                for j in range(8):
                    pixel_color = font_surface.get_at((i, j))
                    # Check if the pixel is white (foreground) or black (background)
                    if pixel_color[0] > 128:  # If the red component is bright, it's white
                        self.draw_pixel(x + i, y + j, color2)
                    else:
                        self.draw_pixel(x + i, y + j, color1)

    def draw_string(self, x, y, string, default_bg=0, default_fg=23):
        x = int(x)
        y = int(y)
        current_x = x
        current_y = y
        char_width = 8
        char_height = 8
        max_x = NATIVE_WIDTH

        current_bg = default_bg
        current_fg = default_fg

        tag_regex = re.compile(r'\[(-?\d{1,2}),(-?\d{1,2})\]|\[e\]')
        segments = []
        pos = 0

        # Step 1: Tokenize into [ (text, bg, fg) ]
        while pos < len(string):
            tag_match = tag_regex.match(string, pos)
            if tag_match:
                if tag_match.group(0) == '[e]':
                    current_bg = default_bg
                    current_fg = default_fg
                else:
                    current_bg = int(tag_match.group(1))
                    current_fg = int(tag_match.group(2))
                pos = tag_match.end()
                continue

            char = string[pos]
            if char == '\n':
                segments.append(('\n', None, None))  # Special handling for newline
                pos += 1
                continue

            # Emoji
            if char == '{':
                end = string.find('}', pos)
                if end != -1:
                    emoji_name = string[pos+1:end]
                    if emoji_name in self.char_map:
                        segments.append((f'{{{emoji_name}}}', current_bg, current_fg))
                        pos = end + 1
                        continue

            segments.append((char, current_bg, current_fg))
            pos += 1

        # Step 2: Draw with wrapping
        current_x = x
        current_y = y
        for text, bg, fg in segments:
            if text == '\n':
                current_x = x
                current_y += char_height
                continue

            # Handle emoji separately
            if text.startswith('{') and text.endswith('}'):
                emoji_name = text[1:-1]
                if current_x + char_width > max_x:
                    current_x = x
                    current_y += char_height
                self.draw_char(current_x, current_y, self.char_map[emoji_name], bg, fg)
                current_x += char_width
                continue

            # Regular character
            if current_x + char_width > max_x:
                current_x = x
                current_y += char_height
            if text in self.char_map:
                self.draw_char(current_x, current_y, self.char_map[text], bg, fg)
            current_x += char_width


    def rle_decode(self, rle):
        flat = []
        i = 0
        while i + 1 < len(rle):
            raw = BASE25.index(rle[i])
            color = -1 if raw == 24 else raw
            run = BASE25.index(rle[i + 1])
            flat.extend([color] * run)
            i += 2
        return flat

    def draw_aai(self, x, y, w=64, h=64, path="resources/no_icon.aai"):
        cache = []
        with open(path, "r") as f:
            cache = f.read()
        
        # Decode RLE
        flat = self.rle_decode(cache)
        
        # Fill the back_buffer with decoded pixel data
        index = 0
        for i in range(w * h):
            color = flat[index]
            if color != -1:
                xi, yi = (i % w) + x, (i // w) + y
                self.draw_pixel(xi, yi, color)
            index += 1

    def clear(self, color=0):
        self.current_background = color
        back_buffer.fill(self.color_cache[color])

    def update(self, clear=False): #include clear for convenience
        if clear:
            self.clear(0)
        if settings.showFPS:
            self.draw_string(0, 0, self.get_fps(), 0, 23)
        if settings.showMousePos:
            mx, my = self.getMousePos()
            self.draw_line(mx, 0, mx, NATIVE_HEIGHT - 1, 12)
            self.draw_line(0, my, NATIVE_WIDTH - 1, my, 12)
            self.draw_string(mx, my, f"[12,22]{mx}, {my}[e]")
        # Swap buffers
        display_surface.blit(back_buffer, (0, 0))
        self._scale_to_screen()
        pg.display.update()
        self.clock.tick(settings.fps)
        # Remove automatic clearing of back buffer
        # The clear() method should be called explicitly when needed

    def _scale_to_screen(self):
        # Get the window size
        window_size = screen.get_size()
        
        # Calculate the scaling factor while preserving aspect ratio
        scale_factor = min(window_size[0] / NATIVE_WIDTH, 
                          window_size[1] / NATIVE_HEIGHT)
        
        # Calculate the new dimensions
        new_width = int(NATIVE_WIDTH * scale_factor)
        new_height = int(NATIVE_HEIGHT * scale_factor)
        
        # Only recreate scaled surface if size changed
        if (new_width, new_height) != self.cached_size or self.scaled_surface is None:
            self.cached_size = (new_width, new_height)
            self.scaled_surface = pg.Surface((new_width, new_height)).convert()
            self.needs_rescale = True
        
        # Calculate position to center the scaled surface
        pos_x = (window_size[0] - new_width) // 2
        pos_y = (window_size[1] - new_height) // 2
        
        # Only scale if needed
        if self.needs_rescale:
            pg.transform.scale(back_buffer, (new_width, new_height), self.scaled_surface)
            self.needs_rescale = False
        else:
            # Just update the portion that changed
            pg.transform.scale(back_buffer, (new_width, new_height), self.scaled_surface)
        
        screen.fill((0, 0, 0))  # Fill black bars
        screen.blit(self.scaled_surface, (pos_x, pos_y))
    
    def handle_resize(self, event):
        if self.screen is not None:
            pg.display.set_mode((event.w, event.h), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF)
            self.cached_size = (event.w, event.h)
            self.needs_rescale = True  # Force rescale on window resize

    def shift(self, x, y):
        back_buffer.scroll(x, y)
    
    def panic(self):
        self.clear(0)
        self.update()

    def getMousePos(self):
        # Get mouse position in window coordinates
        mx, my = pg.mouse.get_pos()
        window_w, window_h = screen.get_size()
        scale_factor = min(window_w / NATIVE_WIDTH, window_h / NATIVE_HEIGHT)
        new_width = int(NATIVE_WIDTH * scale_factor)
        new_height = int(NATIVE_HEIGHT * scale_factor)
        offset_x = (window_w - new_width) // 2
        offset_y = (window_h - new_height) // 2

        # Check if mouse is inside the scaled display area
        if offset_x <= mx < offset_x + new_width and offset_y <= my < offset_y + new_height:
            # Map mouse position to native display coordinates
            native_x = int((mx - offset_x) / scale_factor)
            native_y = int((my - offset_y) / scale_factor)
            return (native_x, native_y)
        else:
            # Outside display area; return None or clamp to edge
            return (0, 0)

    def getMouseButtons(self):
        # Get the state of the mouse buttons
        return pg.mouse.get_pressed()

    def get_fps(self, type="str"):
        if type == "str":
            fps = self.clock.get_fps().__round__(2)
            return str(fps)
        elif type == "int":
            fps = self.clock.get_fps().__round__(0)
            return int(float(fps))