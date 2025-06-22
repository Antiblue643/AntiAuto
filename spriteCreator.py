# Converts a PNG to a sprite function for The AntiAuto

import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os

# Load color palette from colors.hex
def load_palette(path="resources/colors.hex"):
    palette = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip().split()[0]
            if len(line) == 6:
                r = int(line[0:2], 16)
                g = int(line[2:4], 16)
                b = int(line[4:6], 16)
                palette.append((r, g, b))
    return palette

def closest_color_index(rgb, palette):
    # Returns the index of the closest color in the palette
    diffs = [(sum((c1-c2)**2 for c1, c2 in zip(rgb, p)), i) for i, p in enumerate(palette)]
    return min(diffs)[1]

def png_to_sprite_function(png_path, func_name="sprite"):
    palette = load_palette()
    img = Image.open(png_path).convert("RGB")
    width, height = img.size
    pixels = list(img.getdata())
    data = []
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            rgb = pixels[idx]
            color_idx = closest_color_index(rgb, palette)
            data.append(color_idx)
    code = f"def {func_name}(x, y):\n"
    code += f"    sprite = [\n"
    # Print 1 row per line for readability
    for y in range(height):
        row = data[y*width:(y+1)*width]
        code += f"        {', '.join(str(c) for c in row)},\n"
    code += f"    ]\n"
    code += f"    for i in range({height}):\n"
    code += f"        for j in range({width}):\n"
    code += f"            if sprite[i * {width} + j] != 0:\n"
    code += f"                screen.draw_pixel(x + j, y + i, sprite[i * {width} + j])\n"
    return code

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select PNG", filetypes=[("PNG files", "*.png")])
    if not file_path:
        print("No file selected.")
        return
    func_name = os.path.splitext(os.path.basename(file_path))[0]
    code = png_to_sprite_function(file_path, func_name)
    print(code)

if __name__ == "__main__":
    main()