"""The config parsing exists just to check whether or not the extended fonts collection
has been downloaded. If not, it checks on startup if it has been downloaded.
If it detects the download, it will copy the fonts collection into the main folder,
and then set downloaded = True in the ini file.

This is a hacky way to do it. I believe there's code in PyFiglet
for using folders in the user's documents, or shared folders.
One of my goals is converting this hacky method over to something
that utilizes the user folder. But it might require re-writing
Some of the PyFiglet code."""


import os
import shutil
import importlib
import configparser

from .pyfiglet import fonts

def load_cfg_parser():

    config = configparser.ConfigParser()

    try:
        with importlib.resources.path(__package__, 'config.ini') as config_path:
            cfgfile = config.read(config_path)
    except FileNotFoundError:
        raise FileNotFoundError("config.ini not found")
    if not cfgfile:
        raise FileNotFoundError("config.ini not found")
    
    return config

def check_for_extended_fonts(cfgparse):
    """If the extended fonts are not installed, this function will check if they've been installed.
    This check will run every time the package is imported, so you can install the fonts at any time."""

    package_name = "textual_pyfiglet_fonts"

    # check if the fonts package is installed
    if importlib.util.find_spec(package_name) is not None:
        fonts_module = importlib.import_module(package_name)
    else:
        return False

    xtra_fonts_path = os.path.dirname(fonts_module.__file__)    # get the path to the xtra fonts folder
    fonts_folder = os.path.dirname(fonts.__file__)              # get the path to the main fonts folder

    # get list of files in xtra_fonts_path
    xtra_fonts:list[str] = os.listdir(xtra_fonts_path)

    # copy all fonts to the fonts folder
    for font in xtra_fonts:
        if font.endswith('.flf') or font.endswith('.tlf'):
            font_path = os.path.join(xtra_fonts_path, font)
            new_font_path = os.path.join(fonts_folder, font)
            try:
                shutil.copyfile(font_path, new_font_path)
            except Exception as e:
                print(f"Error copying font: {font} - {e}")

    cfgparse['DEFAULT']['extended_fonts_installed'] = "True"

    # Write the changes back to the INI file
    with importlib.resources.path(__package__, 'config.ini') as config_file:
        with open(config_file, 'w') as f:
            cfgparse.write(f)

    return True


cfgparse = load_cfg_parser()

extended_fonts_installed = cfgparse.getboolean('DEFAULT', 'extended_fonts_installed')
if not extended_fonts_installed:
    extended_fonts_installed = check_for_extended_fonts(cfgparse)