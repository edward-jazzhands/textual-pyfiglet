# Textual-Pyfiglet Changelog

## 2025-03-01 0.6.0 - The Animation update

- Color, gradient, and animation modes have been added. There are 5 new arguments in the constructor:
  - color1
  - color2
  - animate: Boolean to toggle on/off
  - animation_quality: Auto mode uses the figlet height by default.
  - animation_interval: Speed in seconds as a float.
- The fonts list is now a string literal collection to give auto-complete. Choosing a font is now much easier.
- The full fonts collection is now included by default. Deleted the extended fonts package from PyPI. This should also solve any issues with PyInstaller or other packaging tools.
- Much of the widget was re-written from the ground up to switch to using the LineAPI.
- Platformdirs has been removed as a dependency. (Now there's no dependencies.)
- Completely revamped the demo. Added Textual-Slidecontainer for the menu bar. Also added new options to show off the color and animation features.
- Changed package manager and build system from Poetry to uv
- Converted Makefile into Justfile
- Deleted config.py and other code related to managing the fonts (no longer needed).
- Removed Inner/Outer architecture, decided it was overcomplicating things. Converted it to one large class.
- Added a help section for the demo.
- Added a `figlet_quick` class method onto FigletWidget which is a bridge to `pyfiglet.figlet_format`

## 2024-11-16 0.5.5

- Fixed bug caused by Textual 0.86 renaming arg in Static widget.

## 2024-11-01 0.5.2

- Fixed typo in README.md

## 2024-10-29 0.5.1

- Fixed all wording in docstings that weren't up to date

## 2024-10-29 0.5.0

- Switched fonts folder to user directory using platformdirs
- Added platformdirs as dependency.
- Switched the _InnerFiglet to use reactives
- Added a Justify option and set_justify method
- Added return_figlet_as_string method

## 2024-10-26 0.4.2

- Added copy text to clipboard button
- Fixed bug with starting text
- Updated text showing container sizes to reflect the new inner/outer system

## 2024-10-26 0.4.0

- Enormous improvement to container logic with inner/outer containers.
- Fixed up docstrings in numerous places
- Updated readme to reflect changes in usage

## 2024-10-25 0.3.5

- Fixed dependency problems in pyproject.toml
- Fixed some mistakes in documentation
- Cleaned up unused code

## 2024-10-24 0.3.2

- Fixed 2 bugs in config.py
- Wrote a full usage guide
- Moved list scanning logic to figletwidget.py

## 2024-10-23 0.2.0

- Fixed the resizing issue
- Greatly improved the demo again
- Moved CSS to a separate file

## 2024-10-22 0.1.2

- Significantly improved the demo.
- Swapped some fonts
- Expanded makefile
- Created base fonts backup folder

## 2024-10-22 0.1.0

Start of Textual-Pyfiglet project. Main changes:

- Fork of PyFiglet. Git history of PyFiglet is maintained.
- Switched build tools to Poetry.
- Removed almost all fonts, leaving only 10 (moved to asset pack, see below)
- pyfiglet folder moved to inside textual_pyfiglet
- removed tools folder. (Scripts for running the CLI, not needed anymore)
- Command line tool to run the original demo is added to the makefile
- 519 fonts moved to asset pack: textual-pyfiglet-fonts
  Asset pack is installed by: pip install textual-pyfiglet[fonts]