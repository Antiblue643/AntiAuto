# Converts an Image to a sprite function for The AntiAuto

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageSequence
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

def image_to_sprite_function(image_path, func_name="sprite"):
    palette = load_palette()
    img = Image.open(image_path)
    width, height = img.size

    # Check if the image is animated (multiple frames)
    is_animated = getattr(img, "is_animated", False) and getattr(img, "n_frames", 1) > 1

    frames = []
    for frame in ImageSequence.Iterator(img):
        frame = frame.convert("RGBA")
        pixels = list(frame.getdata())
        data = []
        for y in range(height):
            for x in range(width):
                idx = y * width + x
                rgba = pixels[idx]
                if len(rgba) == 4 and rgba[3] < 128:
                    color_idx = -1  # Transparent
                else:
                    rgb = rgba[:3]
                    color_idx = closest_color_index(rgb, palette)
                data.append(color_idx)
        frames.append(data)

    if not is_animated or len(frames) == 1:
        # Static sprite: no frame argument, just draw the single frame
        code = f"def {func_name}(x, y):\n"
        code += f"    sprite = [\n"
        frame_data = frames[0]
        for y in range(height):
            row = frame_data[y*width:(y+1)*width]
            code += f"        {', '.join(str(c) for c in row)},\n"
        code += f"    ]\n"
        code += f"    for i in range({height}):\n"
        code += f"        for j in range({width}):\n"
        code += f"            idx = i * {width} + j\n"
        code += f"            if sprite[idx] != -1:\n"
        code += f"                screen.draw_pixel(x + j, y + i, sprite[idx])\n"
    else:
        # Animated sprite: frame argument, select frame
        code = f"def {func_name}(x, y, frame=0):\n"
        code += f"    frames = [\n"
        for frame_data in frames:
            code += "        ["
            for y in range(height):
                row = frame_data[y*width:(y+1)*width]
                code += f"{', '.join(str(c) for c in row)}, "
            code += "],\n"
        code += f"    ]\n"
        code += f"    sprite = frames[frame % len(frames)]\n"
        code += f"    for i in range({height}):\n"
        code += f"        for j in range({width}):\n"
        code += f"            idx = i * {width} + j\n"
        code += f"            if sprite[idx] != -1:\n"
        code += f"                screen.draw_pixel(x + j, y + i, sprite[idx])\n"
    return code

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select PNG", filetypes=[("All", ["*.png", "*.gif", "*.apng", "*.webp"]), ("PNG files", "*.png"), ("GIF files", "*.gif"), ("APNG files", "*.apng"), ("Webp files", "*.gif")])
    if not file_path:
        print("No file selected.")
        return
    func_name = os.path.splitext(os.path.basename(file_path))[0]
    code = image_to_sprite_function(file_path, func_name)
    with open("spriteOutput.txt", "w") as f:
        f.write(code)

if __name__ == "__main__":
    main()