import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def get_hex_colors(image_path):
    img = Image.open(image_path).convert("RGB")
    colors = img.getdata()
    unique_colors = list(dict.fromkeys(colors))  # preserve order, remove duplicates
    hex_colors = ['{:02x}{:02x}{:02x}'.format(*color) for color in unique_colors]
    return hex_colors

def extract_fname(path_string):
    # Find the position of the last '/'
    last_slash_index = path_string.rfind('/')

    # If no '/' is found, assume the segment starts from the beginning
    if last_slash_index == -1:
        segment_start_index = 0
    else:
        segment_start_index = last_slash_index + 1

    # Extract the part of the string after the last '/'
    after_slash = path_string[segment_start_index:]

    # Find the position of the first '.' in the 'after_slash' part
    first_dot_index = after_slash.find('.')

    # If a '.' is found, extract the part before it
    if first_dot_index != -1:
        return after_slash[:first_dot_index]
    else:
        # If no '.' is found, the entire 'after_slash' part is the segment
        return after_slash

def select_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if not file_path:
        return
    try:
        hex_colors = get_hex_colors(file_path)
        output = f"# {extract_fname(file_path).upper()} COLORS\n\n"
        for idx, hex_code in enumerate(hex_colors):
            output += f"{hex_code} #{idx},\n"
        text.delete(1.0, tk.END)
        text.insert(tk.END, output)
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Palette Generator")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

btn = tk.Button(frame, text="Select Image", command=select_image)
btn.pack()

text = tk.Text(frame, width=50, height=20)
text.pack()

root.mainloop()