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
- (TODO) **Music**: A music playback program
- **FE**: The (hidden) File explorer
- **Template**: A (hidden) starting template for the main structure of programs (for more info read the comments in the pixels demo, or look at how floppy.py handles things 🤷‍♂️)

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

## Non-Engine Tools
- **spriteCreator.py**: Converts images/animations into functions to be used into programs (png, gif, apng, webp).
- **progdebug.py**: Parses programs without running them & deleting the temp.py
- **charmap_updater.py**: Changes indices of the character map if something has been deleted (sometimes unreliable).
- **audiotest.py**: Various tests for the audio system.
- **vectorUpgrader.py**: Updates Vectormaster programs to the Antiauto's format.

## Dependencies

- Python 3.10+ (I'm using 3.13.1)
- Pygame 2.5.0+ (I'm using 2.6.1)
- Numpy 2.1.3+ (I'm using 2.1.3)

## Controls

- Mouse: Navigate
- Escape: Back/Exit
- Ctrl+B: Force quit running program

## Releases
- 0.0.0α: Inital release (6/20/25)
- 0.0.1α: Added a template for the basic structure of the Antiauto Programs, changed emoji wrapper to {}, added support for wrapping strings and newlines, added characters for gamepad symbols (completing the full character set), created an image converter, fixed framerate issues, and added more experiments. (6/22/25)
- 0.0.2α: Added many new functions for the display (mouse support, update with clear, panic), added panic for audio, added support for characters to be vertically flipped and removed the mini-alphabet in the chars.txt file (freeing up a whopping 57 characters), reverted the gamepad button characters, added mouse button characters and the horizontal arrow, added characters demo & a character map updater tool. I'm hoping to update the OS a lot more so that it doesn't copy the VectorMaster.
- 0.0.3α: Fixed the mouse position handling, added characters for curly brackets, added methods in the parser for getting mouse buttons and keys pressed down, removed some unused parser keys, added a basic paint program demo, added more experiments, refactored some code, updated comments, added mouse control to the file explorer, and added many new methods of drawing to the display (rect, circle, and triangle).
- 0.0.4α: Made it so that the notepad saves .aat (AntiAuto Text) files instead of .txt, tweaked and made some minor changes to some demos, added new characters, redid paint app (saves .aai files (antiauto image)), added some more options to settings, added click events to the parser, outline support for rects, and added icons in the file explorer.
- 0.0.5α: Realized that -1 for the color index creates a transparent effect, added support for GIFs and APNGs in the sprite creator, completely redid the tobyfox demo (Now called deltarune_battle), and made more experiments.
- 0.0.6α: Updated characters (and fixed some flipped ones in the process), shrunk gitignore, refactored some code and demos, added Webp support for the sprite creator, added experiments, and added file sizes to the file explorer.
- 0.0.7α: Added what probably is the worst browser ever, support for brackets for color formatting in draw_string(): [bg, fg], [e] (This doesn't effect past functions using the color1/color2 arguments), removed the need to add the resize handler to scripts, tweaked the notepad a bit, added some support for Vectormaster (Although the coordinate systems will need to be translated), added RLE to the paint program and sprite creator, added another experiment, and added more characters.
- 0.0.8α: Added the ability to draw images with the draw_aai() function (it needs x, y, width, height, and file path.) Renamed the sprite creator to aaiCreator.py and added the ability to get the raw RLE data (normal aai data), updated the draw_string() function, added a 64x64 mode to the paint app, hid the file extensions in the file explorer (can be shown by pressing E), and updated/changed some experiments.
### 0.0.8α Info!
Since the new method of drawing aai images need a path, it is reccomended that you have your program in a folder, with a script and your images in it, so that the images don't fill up disk/

## The future?
I'm hoping to add more features to the AntiAuto, such as:
- More demos
- More experiments
- Plenty of optimizations
- Extra settings
- Better GUI
- Better OS

I'm considering rewriting the whole thing in C or C++ or some other lower-level language for compatibility.