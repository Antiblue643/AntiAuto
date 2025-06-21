from external import pg

#The display is a 256x192 per-pixel display. It has 24 colors, and 3 layers (0 is for the solid background color, 1 is for characters, 2 is for a per-pixel layer).
NATIVE_WIDTH = 256
NATIVE_HEIGHT = 192

icon = pg.image.load("resources/icon.png")
screen = pg.display.set_mode((NATIVE_WIDTH, NATIVE_HEIGHT), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF)
display_surface = pg.Surface((NATIVE_WIDTH, NATIVE_HEIGHT)).convert()
back_buffer = pg.Surface((NATIVE_WIDTH, NATIVE_HEIGHT)).convert()  # Add hardware acceleration
pg.display.set_caption("AAngine")
pg.display.set_icon(icon)

#takes longer to draw pixels when maximized?

splash = pg.image.load("resources/splash.png")

pg.init()

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
            with open('chars.txt', "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//") or "Positions" in line:
                        continue
                    parts = line.split()
                    if len(parts) == 2:
                        name, idx = parts
                        try:
                            char_map[name] = int(idx)
                        except ValueError:
                            continue
        except FileNotFoundError:
            #really bruh
            quit("Where's the file for the characters? You didn't delete it, did you?\nMake sure it's named chars.txt!")
        # Add space as ' ' for convenience if not present
        if "space" in char_map:
            char_map[" "] = char_map["space"]
        return char_map

    def showSplash(self):
        screen.blit(splash, (0, 0))
        pg.display.update()

    def loadFont(self):
        #The font is an 128x128 monocolor bitmap image, with 8x8 characters.
        self.font = pg.image.load("resources/chars.png")  
    def parseFont(self):
        # Every 8x8 tile is a character, meaning there are 256 characters
        # The image is 128x128, so we have 16x16 characters
        for y in range(16):
            for x in range(16):
                char_index = y * 16 + x
                self.fonts.append(pg.Surface((8, 8)))
                self.fonts[char_index].blit(self.font, (0, 0), (x * 8, y * 8, 8, 8))

    def loadColors(self):
        with open("resources/colors.hex", "r") as f:
            self.colors = f.read().split("\n")
            # Pre-cache all colors
            for i, hex_color in enumerate(self.colors):
                if hex_color:  # Skip empty lines
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    self.color_cache[i] = (r, g, b)

    def draw_pixel(self, x, y, color=23):
        x = int(x)
        y = int(y)
        if 0 <= color < len(self.colors) and 0 <= x < NATIVE_WIDTH and 0 <= y < NATIVE_HEIGHT:
            back_buffer.set_at((x, y), self.color_cache.get(color, self.color_cache[color]))
    def draw_line(self, x1, y1, x2, y2, color):
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        pg.draw.line(back_buffer, self.color_cache[color], (x1, y1), (x2, y2))

    def draw_char(self, x, y, char, color1=0, color2=23): #color1 is the background color (black in the chars.png), color2 is the foreground color (white in the chars.png)

        if 0 <= char <= len(self.fonts):
            for i in range(8):
                for j in range(8):
                    pixel_color = self.fonts[char].get_at((i, j))
                    # Check if the pixel is white (foreground) or black (background)
                    if pixel_color[0] > 128:  # If the red component is bright, it's white
                        self.draw_pixel(x + i, y + j, color2)
                    else:
                        self.draw_pixel(x + i, y + j, color1)

    def draw_string(self, x, y, string, color1=0, color2=23):
        x = int(x)
        y = int(y)
        current_x = x
        i = 0
        while i < len(string):
            if string[i] == ':' and ':' in string[i+1:]:
                # Try to find the next colon
                end = string.find(':', i+1)
                if end != -1:
                    emoji_name = string[i+1:end]
                    if emoji_name in self.char_map:
                        self.draw_char(current_x, y, self.char_map[emoji_name], color1, color2)
                        current_x += 8
                        i = end + 1
                        continue
            char = string[i]
            if char in self.char_map:
                self.draw_char(current_x, y, self.char_map[char], color1, color2)
            current_x += 8
            i += 1

    def clear(self, color=0):
        self.current_background = color
        back_buffer.fill(self.color_cache[color])

    def update(self):
        # Swap buffers
        display_surface.blit(back_buffer, (0, 0))
        self._scale_to_screen()
        pg.display.update()
        self.clock.tick()
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
        self.screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF)
        self.needs_rescale = True  # Force rescale on window resize

    def shift(self, x, y):
        back_buffer.scroll(x, y)
    
    def get_fps(self):
        return self.clock.get_fps()