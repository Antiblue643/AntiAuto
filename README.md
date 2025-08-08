# Welcome to The AntiAuto!

The AntiAuto is a Fantasy computer. I made this with Python and Pygame. In the universe for my Snapverse 
games, The AntiAuto is a desktop computer, and a successor to the Vectormaster.

The disk has 2 folders: demos/ and experimental/

Demos are like the VectorMaster, simple, mostly-working demos.
The experimental folder however, is code I use for testing or messing around. That means it may include code that might work, might not work, or outright crash the emulator.

Also, the pxo folder is for pixelorama (image editing)

**Tested on Windows 11 and Manjaro Linux**

## Features

### Engine Features
- Per-Pixel based graphics rendering system
- Resizable display window
- Built-in sample playback
- Custom AntiAuto Program scripting language (Python-like syntax)
- File browser interface

### Graphics Capabilities
- Per-Pixel display
- 24 colors
- String and character with custom font
- Screen clearing and updating
- Pixel, line, rect, ellipse, triangle, and aai image drawing.

### Audio System
- 4 sound channels (L, C1, C2, R)
- A beeper
- 29 samples
- 5-bit volume (0-31)

### Demo Programs
- **Starfield**: Starfield with trailing effects
- **Lines**: Cool line patterns
- **Pixels**: Random Pixels
- **Audio**: Audio tester/visualizer
- **Ball**: A bouncy ball/bubble physics demo
- **Deltarune Battle**: An Undertale/Deltarune-style battle system demo
- **Sorting**: A sorting algorithm demo
- *And more!*

### System Programs
- **Notepad**: A Notepad
- **Paint**: A paint program
- **Browser**: A very bad browser
- **FE**: The (hidden) File explorer
- **Template**: A (hidden) starting template for the main structure of programs (for more info read the comments in the pixels demo, or look at how floppy.py handles things 🤷‍♂️)

### Input Handling
- Keyboard input support
- Event-based input processing
- Window resize handling
- Program exit controls

## Getting Started

1. Run the main program to launch Antiauto
2. Use the built-in file browser to navigate through available demos
3. Select a demo using the arrow keys and Enter
4. Press Ctrl+B to exit any running program
5. Use Escape to navigate back or exit the file browser

## Non-Engine Tools
- **aaiCreator.py**: Converts images/animations into functions to be used into programs (png, gif, webp).
- **progdebug.py**: Parses programs without running them & deleting the temp.py
- **charmap_updater.py**: Changes indices of the character map if something has been deleted (sometimes unreliable).
- **audiotest.py**: Various tests for the audio system.

## Dependencies

- Python 3.10+ (I'm using 3.13.1)
- Pygame 2.5.0+ (I'm using 2.6.1)
- Numpy 2.1.3+ (I'm using 2.1.3)

## Controls

- Mouse: Navigate
- Escape: Back/Exit
- Ctrl+B: Force quit running program

### Where's releases?
In the new file, changelog.md!

## The future?
I'm hoping to add more features to the AntiAuto, such as:
- More demos
- More experiments
- Plenty of optimizations
- Extra settings
- Better GUI
- Better OS
- Possible rewrite in another language?

## Contributions
I'd really appreciate feedback/suggestions, as well as tips/ways to fix my terrible code, or just some programs you've created to show off!