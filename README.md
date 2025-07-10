# Welcome to The AntiAuto!

The AntiAuto is a Fantasy computer. I made this with Python and Pygame. In the universe for my Snapverse 
games, The AntiAuto is a desktop computer, and a successor to the Vectormaster.

The disk has 2 folders: demos/ and experimental/

Demos are like the VectorMaster, simple, mostly-working demos.
The experimental folder however, is code I use for testing or messing around. That means it may include code that might work, might not work, or outright crash the emulator.

Also, the pxo folder is for pixelorama (image editing)

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
- **Notepad**: A simple notepad
- **Toby Fox**: A very (slightly less) buggy Undertale/Deltarune-style battle system demo
- **Music**: A test script for playing music
- **Sorting**: A sorting algorithm demo
- *And more!*

### Input Handling
- Keyboard input support
- Event-based input processing
- Window resize handling
- Program exit controls

## Getting Started

1. Run the main program to launch VectorMaster
2. Use the built-in file browser to navigate through available demos
3. Select a demo using the arrow keys and Enter
4. Press Ctrl+B to exit any running program
5. Use Escape to navigate back or exit the file browser

## Dependencies

- Python 3.10+ (I'm using 3.13.1)
- Pygame 2.5.0+ (I'm using 2.6.1)

## Controls

- Arrow keys: Navigate menus and control demos
- Enter: Select/Confirm
- Escape: Back/Exit
- Ctrl+B: Force quit running program
- Space: Reset/Restart (in supported demos)

## Releases
- 0.0.0α: Inital release (6/20/25)
- 0.0.1α: Added a template for a basic structure of the Antiauto Programs, changed emoji wrapper to {}, added support for wrapping strings and newlines, added characters for gamepad symbols (completing the full character set), created an image converter, fixed framerate issues, and added more experiments. (6/22/25)
- 0.0.2α: Added many new functions for the display (mouse support, update with clear, panic), added panic for audio, added support for characters to be vertically flipped and removed the mini-alphabet in the chars.txt file (freeing up a whopping 57 characters), reverted the gamepad button characters, added mouse button characters and the horizontal arrow, added characters demo & a character map updater tool. I'm hoping to update the OS a lot more so that it doesn't copy the VectorMaster.
- 0.0.3α: Fixed the mouse position handling, added characters for curly brackets, added methods in the parser for getting mouse buttons and keys pressed down, removed some unused parser keys, added a basic paint program demo, added more experiments, refactored some code, updated comments, added mouse control to the file explorer, and added many new methods of drawing to the display (rect, circle, and triangle).
- 0.0.4α: Made it so that the notepad saves .aat (AntiAuto Text) files instead of .txt, tweaked and made some minor changes to some demos, added new characters, redid paint app (saves .aai files (antiauto image)), added some more options to settings, added click events to the parser, outline support for rects, and added icons in the file explorer.
- 0.0.5α: Realized that -1 for the color index creates a transparent effect, added support for GIFs and APNGs in the sprite creator, completely redid the tobyfox demo (Now called deltarune_battle), and made more experiments.
- 0.0.6α: Updated characters (and fixed some flipped ones in the process), shrunk gitignore, refactored some code and demos, added Webp support for the sprite creator, added experiments, and added file sizes to the file explorer.

## The future?
I'm hoping to add more features to the AntiAuto, such as:
- More demos
- More experiments
- Plenty of optimizations
- Extra settings
- Better GUI
- Better OS

I'm considering rewriting the whole thing in C or C++ for compatibility, but I don't know if I will do that. If I do, it will be a while before I do it. It'll either be a rewrite or fork.