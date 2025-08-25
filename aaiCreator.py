import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageSequence
import os

BASE25 = "0123456789ABCDEFGHIJKLMNO"  # 24 colors + transparent

def load_palette(path="resources/colors.txt"):
    palette = []
    with open(path, "r") as f:
        for i, line in enumerate(f):
            if i > 24:
                break
            if line.strip() and not line.startswith("#"):
                line = line.strip().split()[0]
            if len(line) == 6:
                r = int(line[0:2], 16)
                g = int(line[2:4], 16)
                b = int(line[4:6], 16)
                palette.append((r, g, b))
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
        result += BASE25[color_val] + BASE25[run]
        i += run
    return result

def image_to_aai(image_path):
    palette = load_palette()
    img = Image.open(image_path)
    base_width, base_height = img.size

    if base_width > 256 or base_height > 192:
        raise ValueError("Image exceeds 256x192 limit.")

    frames = []
    for frame in ImageSequence.Iterator(img):
        frame = frame.convert("RGBA")
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
                    # First try to find an exact match
                    color_idx = -1
                    for i, pal_color in enumerate(palette):
                        if (r, g, b) == pal_color:
                            color_idx = i
                            break
                    
                    # If no exact match found, then find closest
                    if color_idx == -1:
                        color_idx = closest_color_index((r, g, b), palette)
                        
                data.append(color_idx)

        frames.append(rle_encode(data))

    frame_count = len(frames)
    output_lines = [f"aai_{base_width}x{base_height}_F{frame_count}"] + frames
    return "\n".join(output_lines)

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

    try:
        aai_data = image_to_aai(file_path)
    except Exception as e:
        print(f"Error: {e}")
        return

    out_path = os.path.splitext(os.path.basename(file_path))[0] + ".aai"
    with open(out_path, "w") as f:
        f.write(aai_data)
    print(f"AAI image written to {out_path}")

if __name__ == "__main__":
    main()
