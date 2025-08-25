from external import pg, Settings as s
import re
import random

# The display is a 256x192 per-pixel display.
NATIVE_WIDTH = 256
NATIVE_HEIGHT = 192

icon = pg.image.load("resources/icon.png")
screen = pg.display.set_mode((NATIVE_WIDTH, NATIVE_HEIGHT), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF)
display_surface = pg.Surface((NATIVE_WIDTH, NATIVE_HEIGHT)).convert()
back_buffer = pg.Surface((NATIVE_WIDTH, NATIVE_HEIGHT)).convert()  # Add hardware acceleration
pg.display.set_caption("AntiAuto")
pg.display.set_icon(icon)
settings = s()

pg.init()

BASE25 = "0123456789ABCDEFGHIJKLMNO"

pg.mouse.set_visible(False)
cursorimg = pg.image.load('resources/cursor.png')

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
        self.frame = 0
        
        # Load resources after initializing caches
        self.loadFont()
        self.parseFont()
        self.loadColors()

    def load_char_map(self):
        """Load the character map from chars.txt"""
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

    def loadFont(self):
        """Load the font file."""
        # The font is an 128x128 monocolor bitmap image, with 8x8 characters.
        self.font = pg.image.load("resources/chars.png")  
    
    def parseFont(self):
        """Parse the font into 8x8 tiles."""
        # Every 8x8 tile is a character, meaning there are 256 characters
        for y in range(16):
            for x in range(16):
                char_index = y * 16 + x
                # Create a new surface with alpha for each character
                char_surface = pg.Surface((8, 8), flags=pg.SRCALPHA).convert_alpha()
                char_surface.blit(self.font, (0, 0), (x * 8, y * 8, 8, 8))
                self.fonts.append(char_surface)

    def loadColors(self):
        """Load the colors, usually automatically called."""
        try:
            palette_map = {
                'alpha': '# ALPHA COLORS',
                'ink': '# INK COLORS',
                'ink-c': '# INK-C COLORS'
            }
            header = palette_map.get(settings.settings.get("model"))
            if not header:
                quit("Unknown palette selected in settings!")

            with open("resources/colors.txt", "r") as f:
                file_lines = f.readlines()

            # Find header
            start_idx = None
            for i, line in enumerate(file_lines):
                if line.strip().lower() == header.lower():
                    start_idx = i + 1
                    break
            if start_idx is None:
                quit(f"Could not find header {header} in colors.txt")

            # Read until next header or end of file
            section_colors = []
            for line in file_lines[start_idx:]:
                if line.strip().startswith('#'):
                    break
                if line.strip() and not line.startswith('#'):
                    hex_color = line.split('#')[0].strip()
                    section_colors.append(hex_color)

            self.colors = section_colors

            # Pre-cache all colors
            for i, hex_color in enumerate(self.colors):
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                self.color_cache[i] = (r, g, b)

        except FileNotFoundError:
            quit("No colors file found!")


    def _normalize_color(self, color):
        """Wrap real colors into palette range; keep -1 as transparent."""
        if color >= 0:
            return color % len(self.colors)
        return color


    def draw_pixel(self, x, y, color=23):
        color = self._normalize_color(color)
        if color == -1:
            return  # transparent
        if 0 <= x < NATIVE_WIDTH and 0 <= y < NATIVE_HEIGHT:
            back_buffer.set_at((int(x), int(y)), self.color_cache.get(color, (255, 0, 255)))


    def draw_line(self, x1, y1, x2, y2, color=23):
        color = self._normalize_color(color)
        if color == -1:
            return
        pg.draw.line(back_buffer, self.color_cache[color], (int(x1), int(y1)), (int(x2), int(y2)))


    def draw_rect(self, x1, y1, x2, y2, color=23, outlineColor=None):
        color = self._normalize_color(color)
        if color != -1:
            pg.draw.rect(back_buffer, self.color_cache[color],
                        (int(x1), int(y1), int(x2) - int(x1), int(y2) - int(y1)))
        if outlineColor is not None:
            outlineColor = self._normalize_color(outlineColor)
            if outlineColor != -1:
                pg.draw.rect(back_buffer, self.color_cache[outlineColor],
                            (int(x1), int(y1), int(x2) - int(x1), int(y2) - int(y1)), 1)


    def draw_ellipse(self, x, y, radiusX, radiusY, color=23):
        color = self._normalize_color(color)
        if color == -1:
            return
        pg.draw.ellipse(back_buffer, self.color_cache[color],
                        (int(x) - int(radiusX), int(y) - int(radiusY), int(radiusX) * 2, int(radiusY) * 2))


    def draw_triangle(self, x1, y1, x2, y2, x3, y3, color=23):
        color = self._normalize_color(color)
        if color == -1:
            return
        pg.draw.polygon(back_buffer, self.color_cache[color], [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))])


    def draw_char(self, x, y, char, color1=-1, color2=23):
        color1 = self._normalize_color(color1)
        color2 = self._normalize_color(color2)
        flip = False
        if isinstance(char, tuple):
            char_idx, flip = char
        else:
            char_idx = char
        if 0 <= char_idx < len(self.fonts):
            font_surface = self.fonts[char_idx].copy()
            if flip:
                font_surface = pg.transform.flip(font_surface, True, False)
            for i in range(8):
                for j in range(8):
                    pixel_color = font_surface.get_at((i, j))
                    if pixel_color[0] > 128:  # white (foreground)
                        if color2 != -1:
                            self.draw_pixel(x + i, y + j, color2)
                    else:
                        if color1 != -1:
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

        string = str(string) #BLAHG

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
        """Decode a base-25 RLE string"""
        flat = []
        i = 0
        while i + 1 < len(rle):
            try:
                raw = BASE25.index(rle[i])
                color = -1 if raw == 24 else raw
                run = BASE25.index(rle[i + 1])
                flat.extend([color] * run)
                i += 2
            except ValueError:
                # Skip invalid character and move on
                i += 1
        return flat

    def draw_aai(self, x, y, path="resources/logo.aai", frame=0):
        try:
            with open(path, "r") as f:
                lines = f.read().strip().splitlines()

            # New format: first line is aai_WxH_, rest are frames
            if lines[0].startswith("aai_") and "x" in lines[0]:
                dim = lines[0].split("_")[1].split("x")
                w, h = int(dim[0]), int(dim[1])
                frames = lines[1:]
                #The #F in aai_WxH_#F is the frame count, purely for programmer use.

                # If no extra lines, maybe it's old format in disguise
                if not frames:
                    raise ValueError(f"Possible old format in {path}.\nNew format: aai_WxH_#F\nDATADATADATA\nDATADATADATA\n...") #sorry for spam

                chosen_frame = frames[frame % len(frames)]
                flat = self.rle_decode(chosen_frame)

            # Adjust length to match dimensions
            max_pixels = w * h
            if len(flat) > max_pixels:
                flat = flat[:max_pixels]
            elif len(flat) < max_pixels:
                flat.extend([-1] * (max_pixels - len(flat)))

            # Draw pixels
            for i, color in enumerate(flat):
                if color != -1:
                    xi, yi = (i % w) + x, (i // w) + y
                    self.draw_pixel(xi, yi, color)

        except (FileNotFoundError, ValueError, IndexError) as e:
            print(f"Error loading AAI file: {e}")

    def clear(self, color=0):
        color = self._normalize_color(color)
        self.current_background = color
        back_buffer.fill(self.color_cache[color])

    def ghost(self, transparency):
        """
        Ghost a frame of the screen by blending it with the previous frame.
        Periodically clears ghosting to prevent burn-in effects.
        """
        # Clear ghosting every 128 frames to prevent burn-in
        if self.frame % 128 == 1: #1 because if it's 0 it won't show the splash.
            back_buffer.fill(self.color_cache[self.current_background])
            return

        # Ensure transparency is between 0 and 1
        transparency = max(0.0, min(1.0, transparency))
        
        # Create a copy of the current back buffer
        current_frame = back_buffer.copy()
        
        # Blend the current frame with the display surface (previous frame)
        current_frame.set_alpha(int(transparency * 255))
        back_buffer.blit(display_surface, (0, 0))  # Draw previous frame first
        back_buffer.blit(current_frame, (0, 0))    # Blend current frame on top

    def update(self, clear=False, drawCursor=True): #include clear for convenience
        if clear:
            self.clear(0)
        if settings.settings.get("showFPS"):
            self.draw_string(0, 0, self.get_fps() + " " + str(self.frame), 0, 23)
        if settings.settings.get("showMousePos"):
            mx, my = self.getMousePos()
            self.draw_line(mx, 0, mx, NATIVE_HEIGHT - 1, 12)
            self.draw_line(0, my, NATIVE_WIDTH - 1, my, 12)
            self.draw_string(mx + 8, my, f"[12,22]{mx}, {my}[e]")
        # Draw the custom cursor onto the back_buffer
        if drawCursor:
            cursor_pos = self.getMousePos()
            self.draw_aai(cursor_pos[0], cursor_pos[1], "resources/cursor.aai")
        if settings.settings.get("model") != "alpha":
            self.clock.tick(15) #suffer
            self.ghost(0.7)
        else:
            self.clock.tick(60)
        self.frame += 1
        # Swap buffers
        display_surface.blit(back_buffer, (0, 0))
        self._scale_to_screen()
        pg.display.update()
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
            return (128, 96)

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