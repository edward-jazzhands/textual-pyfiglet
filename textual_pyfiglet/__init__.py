"""### To import textual_pyfiglet:
from textual_pyfiglet import FigletWidget

### You can also import the original PyFiglet:
from textual_pyfiglet.pyfiglet import Figlet         <-- Class version
from textual_pyfiglet.pyfiglet import figlet_format  <-- Function version

### To install the extended fonts collection:   
pip install textual-pyfiglet[fonts]

You can also download FIG fonts from the internet and just drop them in the fonts folder.   
See the readme for more information.
 
You can access the original PyFiglet CLI with the following command:   
python -m textual_pyfiglet.pyfiglet
"""
from textual_pyfiglet.figletwidget import FigletWidget

from textual_pyfiglet.config import check_for_extended_fonts

# If recently installed, this copies the fonts to the user directory.
are_extended_fonts_installed: bool = check_for_extended_fonts()


