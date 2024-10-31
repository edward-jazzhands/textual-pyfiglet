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
import importlib.resources
from platformdirs import user_data_dir
# import configparser

# from .pyfiglet import fonts


def check_for_extended_fonts() -> str:
    """This function will check if fonts have been installed.   
    This check will run every time the package is imported, so you can install the fonts at any time.
    
    Returns one of three conditions:
    1) installed - the fonts are already installed.
    2) not_installed - did not detect fonts pack.
    3) just_installed - the fonts were just installed right now. """

    package_name = "textual_pyfiglet_fonts"

    user_fonts_folder = user_data_dir('pyfiglet', appauthor=False)     # get user data dir

    if os.path.exists(os.path.join(user_fonts_folder, '.fonts_installed')):   #look for flag file
        return 'installed'

    # check if the fonts package is installed
    if importlib.util.find_spec(package_name) is not None:
        fonts_module = importlib.import_module(package_name)
    else:
        return 'not_installed'
    
    # if we're here, the fonts package must be recently installed.
    
    fonts_module_path = os.path.dirname(fonts_module.__file__)   # get the path to the fonts package
    fonts_pack_list: list = os.listdir(fonts_module_path)       # get list of files in fonts package

    # copy all files to the user fonts folder
    for font_file in fonts_pack_list:
        if not font_file.endswith('.py') and not font_file.endswith('__pycache__'):
            font_path = os.path.join(fonts_module_path, font_file)
            new_font_path = os.path.join(user_fonts_folder, font_file)
            try:
                shutil.copyfile(font_path, new_font_path)
            except Exception as e:
                print(f"Error copying font: {font_file} - {e}")

    return 'just_installed'