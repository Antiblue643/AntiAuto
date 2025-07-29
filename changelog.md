# Changelog

<details><summary>0.0.0α</summary>
Inital release
</details>

<details><summary>0.0.1α</summary>
Added a template for the basic structure of the Antiauto Programs, changed emoji wrapper to {}, added support for wrapping strings and newlines, added characters for gamepad symbols (completing the full character set), created an image converter, fixed framerate issues, and added more experiments.
</details>

<details><summary>0.0.2α</summary>
Added many new functions for the display (mouse support, update with clear, panic), added panic for audio, added support for characters to be vertically flipped and removed the mini-alphabet in the chars.txt file (freeing up a whopping 57 characters), reverted the gamepad button characters, added mouse button characters and the horizontal arrow, added characters demo & a character map updater tool. I'm hoping to update the OS a lot more so that it doesn't copy the VectorMaster.
</details>

<details><summary>0.0.3α</summary>
Fixed the mouse position handling, added characters for curly brackets, added methods in the parser for getting mouse buttons and keys pressed down, removed some unused parser keys, added a basic paint program demo, added more experiments, refactored some code, updated comments, added mouse control to the file explorer, and added many new methods of drawing to the display (rect, circle, and triangle).
</details>

<details><summary>0.0.4α</summary>
Made it so that the notepad saves .aat (AntiAuto Text) files instead of .txt, tweaked and made some minor changes to some demos, added new characters, redid paint app (saves .aai files (antiauto image)), added some more options to settings, added click events to the parser, outline support for rects, and added icons in the file explorer.
</details>

<details><summary>0.0.5α</summary>
Realized that -1 for the color index creates a transparent effect, added support for GIFs and APNGs in the sprite creator, completely redid the tobyfox demo (Now called deltarune_battle), and made more experiments.
</details>

<details><summary>0.0.6α</summary>
Updated characters (and fixed some flipped ones in the process), shrunk gitignore, refactored some code and demos, added Webp support for the sprite creator, added experiments, and added file sizes to the file explorer.
</details>

<details><summary>0.0.7α</summary>Added what probably is the worst browser ever, support for brackets for color formatting in draw_string(): [bg, fg], [e] (This doesn't effect past functions using the color1/color2 arguments), removed the need to add the resize handler to scripts, tweaked the notepad a bit, added some support for Vectormaster (Although the coordinate systems will need to be translated), added RLE to the paint program and sprite creator, added another experiment, and added more characters.
</details>

<details><summary>0.0.8α</summary>
Added the ability to draw images with the draw_aai() function (it needs x, y, width, height, and file path.) Renamed the sprite creator to aaiCreator.py and added the ability to get the raw RLE data (normal aai data), updated the draw_string() function, added a 64x64 mode to the paint app, hid the file extensions in the file explorer (can be shown by pressing E), and updated/changed some experiments.
<h4>0.0.8α Info!</h4>
Since the new method of drawing aai images need a path, it is reccomended that you have your program in a folder, with a script and your images in it, so that the images don't fill up disk/
</details>

<details><summary>0.0.9α</summary>
Updated the file explorer UI, limited the amount of items in a folder to 9, removed the need to include the special key (it now gets added during the parsing process), removed the expansions, removed an experiment, renamed colors.hex to colors.txt, updated the .aai format ("aai_WxH_DATADATADATA..."), updated the character map, and tweaked some demos. Close to 1.0!
</details>

<details><summary>0.0.9β</summary>
Added a cursor, prepared for .aam handling, made a changelog, removed most experiments.
</details>