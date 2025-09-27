#take a file, strip it, and convert it into binary
import os
import random
from PIL import Image

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

BASE25 = '0123456789ABCDEFGHIJKLMNO'

class Disassembler:
    def __init__(self):
        pass

    def disassemble(self, file, strip=True):
        with open(file, 'rb') as f:
            #try to compress as much as possible
            byte_data = f.read()
            if strip:
                byte_data = byte_data.strip()
                byte_data = byte_data.replace(b'\x00', b'N')  # remove null bytes
                byte_data = byte_data.replace(b'\n', b'')  # remove newlines
                byte_data = byte_data.replace(b'\r', b'')  # remove carriage returns
                byte_data = byte_data.replace(b' ', b'')  # remove spaces
                byte_data = byte_data.replace(b'\t', b'')  # remove tabs
            
        
        binary_data = ''.join(f'{byte:08b}' for byte in byte_data)
        
        return binary_data
    
    def reassemble(self, byte):
        #reassemble a single byte and return a char.
        if len(byte) != 8 or any(b not in '01' for b in byte):
            return ''
        return chr(int(byte, 2))

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

class DebugThings:
    def __init__(self):
        pass

    def create_random_aai(self, frames=1):
        width, height = 64, 64
        with open('random.aai', 'w') as f:
            f.write(f'aai_{width}x{height}_F{frames}\n')
            for _ in range(frames):
                # Generate random color indices (0-23 for colors, 24 for transparent)
                data = [random.choice(list(range(24)) + [-1]) for _ in range(width * height)]
                rle = rle_encode(data)
                f.write(rle + '\n')

    def reverse_aai(self, file):
        # Parse .aai file and create a gif. Doesn't work well that much.
        palette = load_palette()
        with open(file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines or not lines[0].startswith("aai_"):
            print("Invalid .aai file header.")
            return

        # Parse header
        header = lines[0]
        try:
            dims, frame_info = header.split("_")[1:3]
            width, height = map(int, dims.lower().split("x"))
            frame_count = int(frame_info[1:])
        except Exception:
            print("Malformed .aai header.")
            return

        frames = []
        for frame_line in lines[1:]:
            pixels = []
            i = 0
            while i < len(frame_line):
                color_char = frame_line[i]
                run_char = frame_line[i + 1]
                color_idx = BASE25.find(color_char)
                run_len = BASE25.find(run_char)
                if color_idx == 24:  # transparent
                    color = (0, 0, 0, 0)
                elif 0 <= color_idx < len(palette):
                    rgb = palette[color_idx]
                    color = (*rgb, 255)
                else:
                    # fallback for invalid color index
                    color = (0, 0, 0, 255)
                pixels.extend([color] * run_len)
                i += 2
            # Pad if needed
            while len(pixels) < width * height:
                pixels.append((0, 0, 0, 0))
            img = Image.new("RGBA", (width, height))
            img.putdata(pixels[:width * height])
            frames.append(img)

        if not frames:
            print("No frames found.")
            return

        frames[0].save(
            "out.gif",
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
            disposal=2,
            transparency=0
        )
        print(f"GIF saved as out.gif")


if __name__ == "__main__":
    disassembler = Disassembler()
    debug_tools = DebugThings()

    choice = input("Choose a tool:\n1. Disassemble a file\n2. Create random .aai file\n3. Reverse .aai file\nEnter choice (1/2/3): ")
    if choice == '1':
        bd = input("Enter file path to disassemble: ")
        if not os.path.exists(bd):
            print("File does not exist.")
            exit(1)
        strip = input("Strip? (y/n): ").lower() == 'y'
        binary_data = disassembler.disassemble(bd, strip=strip)
        with open('dis_output.bin', 'wb') as f:
            f.write(int(binary_data, 2).to_bytes((len(binary_data) + 7) // 8, byteorder='big'))
        print("Disassembly complete. Output written to dis_output.bin")
    elif choice == '2':
        frames = int(input("Enter number of frames (default 1): ") or 1)
        debug_tools.create_random_aai(frames=frames)
        print("Random .aai file created as random.aai")
    elif choice == '3':
        aai_file = input("Enter .aai file path to reverse: ")
        if not os.path.exists(aai_file):
            print("File does not exist.")
            exit(1)
        debug_tools.reverse_aai(aai_file)


