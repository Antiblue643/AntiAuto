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
- 0.0.0: Inital release (6/20/25)
- 0.0.1: Added a template for a basic structure of the Antiauto Programs, changed emoji wrapper to {}, added support for wrapping strings and newlines, added characters for gamepad symbols (completing the full character set), created an image converter, fixed framerate issues, and added more experiments. (6/22/25)
- 0.0.2: Added many new functions for the display (mouse support, update with clear, panic), added panic for audio, added support for characters to be vertically flipped and removed the mini-alphabet in the chars.txt file (freeing up a whopping 57 characters), reverted the gamepad button characters, added mouse button characters and the horizontal arrow, added characters demo & a character map updater tool. I'm hoping to update the OS a lot more so that it doesn't copy the VectorMaster.