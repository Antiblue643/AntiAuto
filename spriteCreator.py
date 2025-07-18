import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageSequence
import os

# Base-25 character set (24 colors + 1 transparent)
BASE25 = "0123456789ABCDEFGHIJKLMNO"  # 'O' is index 24, used for transparent

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
    if len(palette) > 24:
        print("Warning: using only first 24 colors from palette.")
    return palette[:24]

def closest_color_index(rgb, palette):
    diffs = [(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb, p)), i) for i, p in enumerate(palette)]
    return min(diffs)[1]

def rle_encode(data):
    result = ""
    i = 0
    while i < len(data):
        color = data[i]
        run = 1
        while run < 24 and i + run < len(data) and data[i + run] == color:
            run += 1
        color_val = 24 if color == -1 else color
        color_char = BASE25[color_val]
        run_char = BASE25[run]
        result += color_char + run_char
        i += run
    return result

def image_to_rle_sprite_function(image_path, func_name="sprite"):
    palette = load_palette()
    img = Image.open(image_path)
    base_width, base_height = img.size

    if base_width > 256 or base_height > 192:
        raise ValueError("Image exceeds 256x192 limit.")

    is_animated = getattr(img, "is_animated", False) and getattr(img, "n_frames", 1) > 1
    frames = []

    for frame_index, frame in enumerate(ImageSequence.Iterator(img)):
        frame = frame.convert("RGBA")

        # Ensure frame is full canvas
        if frame.size != (base_width, base_height):
            full_frame = Image.new("RGBA", (base_width, base_height))
            full_frame.paste(frame, (0, 0))
            frame = full_frame

        pixels = list(frame.getdata())
        data = []
        for y in range(base_height):
            for x in range(base_width):
                idx = y * base_width + x
                r, g, b, a = pixels[idx]
                if a < 128:
                    color_idx = -1
                else:
                    color_idx = closest_color_index((r, g, b), palette)
                data.append(color_idx)

        encoded = rle_encode(data)

        # Sanity check
        if len(encoded) % 2 != 0:
            raise ValueError(f"Frame {frame_index} RLE string has odd length.")
        total_pixels = sum(BASE25.index(encoded[i+1]) for i in range(0, len(encoded), 2))
        if total_pixels != base_width * base_height:
            raise ValueError(f"Frame {frame_index} decoded to {total_pixels} pixels (expected {base_width * base_height})")

        frames.append(f'"{encoded}"')

    # Generate code
    header = f"def {func_name}(x, y"
    if is_animated:
        header += ", frame=0"
    header += "):\n"

    body = "    data = "
    if is_animated:
        body += f"[{', '.join(frames)}]\n"
        body += "    sprite = data[frame % len(data)]\n"
    else:
        body += frames[0] + "\n"
        body += "    sprite = data\n"

    decode_block = f"""    width = {base_width}
    height = {base_height}
    base25 = "0123456789ABCDEFGHIJKLMNO"
    idx = 0
    i = 0
    while i + 1 < len(sprite):
        raw_color = base25.index(sprite[i])
        color = -1 if raw_color == 24 else raw_color
        run = base25.index(sprite[i + 1])
        for _ in range(run):
            row = idx // width
            col = idx % width
            if color != -1:
                screen.draw_pixel(x + col, y + row, color)
            idx += 1
        i += 2
"""

    return header + body + decode_block

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image Files", "*.png *.gif *.apng *.webp")]
    )
    if not file_path:
        print("No file selected.")
        return

    func_name = os.path.splitext(os.path.basename(file_path))[0]
    try:
        code = image_to_rle_sprite_function(file_path, func_name)
    except Exception as e:
        print(f"Error: {e}")
        return

    with open("spriteOutput.txt", "w") as f:
        f.write(code)
    print("Sprite function written to spriteOutput.txt")

if __name__ == "__main__":
    main()
