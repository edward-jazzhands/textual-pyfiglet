"""To import in your own project:
#$ from textual-pyfiglet import FigletWidget

To install the extended fonts collection:
#$ pip install textual-pyfiglet[fonts]

I made sure to preserve the original PyFiglet CLI for reference.
You can access the original CLI with the following command:
#$ python -m textual_pyfiglet.pyfiglet

The original PyFiglet CLI has a demo that can be accessed like this (verbatim, with the spaces):
#$ python -m textual_pyfiglet.pyfiglet some text here

In order to change fonts with the original demo, you can use the -f flag like this:
#$ python -m textual_pyfiglet.pyfiglet -f slant Hey hows it going?

To see all installed fonts (scans fonts folder):
#$ python -m textual_pyfiglet.pyfiglet --list_fonts

# NOTE: You can also download FIG fonts from the internet and just drop them in the fonts folder.
See the readme for more information.
"""

import os
import shutil
import importlib
import configparser

from .figletwidget import FigletWidget
from .pyfiglet import fonts

config = configparser.ConfigParser()
try:
    with importlib.resources.path(__package__, 'config.ini') as config_path:
        cfgfile = config.read(config_path)
except FileNotFoundError:
    raise FileNotFoundError("config.ini not found")
if not cfgfile:
    raise FileNotFoundError("config.ini not found")

extended_fonts_installed = config.getboolean('DEFAULT', 'extended_fonts_installed')

def check_for_extended_fonts():
    """If the extended fonts are not installed, this function will check if they've been installed.
    This check will run every time the package is imported, so you can install the fonts at any time."""

    package_name = "textual_pyfiglet_fonts"

    # check if the fonts package is installed
    if importlib.util.find_spec(package_name) is not None:
        fonts_module = importlib.import_module(package_name)
    else:
        return

    xtra_fonts_path = os.path.dirname(fonts_module.__file__)    # get the path to the xtra fonts folder
    fonts_folder = os.path.dirname(fonts.__file__)              # get the path to the main fonts folder

    # get list of files in xtra_fonts_path
    xtra_fonts = os.listdir(xtra_fonts_path)

    # copy all fonts to the fonts folder
    for font in xtra_fonts:
        font_path = os.path.join(xtra_fonts_path, font)
        new_font_path = os.path.join(fonts_folder, font)
        try:
            shutil.copyfile(font_path, new_font_path)
        except Exception as e:
            print(f"Error copying font: {font} - {e}")

    config['DEFAULT']['extended_fonts_installed'] = "True"

    # Write the changes back to the INI file
    with importlib.resources.path(__package__, 'config.ini') as config_file:
        with open(config_file, 'w') as f:
            config.write(f)


if not extended_fonts_installed:
    check_for_extended_fonts()







