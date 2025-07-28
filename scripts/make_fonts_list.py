# This file is used to generate a list of all available fonts
# in the rich_pyfiglet.pyfiglet.fonts module.

import os
from pyfiglet import fonts

ext_fonts_pkg = os.path.dirname(fonts.__file__)

all_files: list[str] = []
for root, dirs, files in os.walk(ext_fonts_pkg):
    for file in files:
        # Create relative path from package root
        rel_path = os.path.relpath(os.path.join(root, file), ext_fonts_pkg)
        all_files.append(rel_path)

all_files = sorted(all_files)

# write all_files out to a file:
with open("src/textual_pyfiglet/fonts_list.py", "w") as f:
    f.write("from typing import Literal \n\n")
    f.write("ALL_FONTS = Literal[\n")
    for file in all_files:
        if file.endswith(".flf") or file.endswith(".tlf"):
            # remove the extension
            font_name = file[:-4]
            f.write(f'"{font_name}",\n')
    f.write("]\n")
