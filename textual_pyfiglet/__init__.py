"""To import in your own project:
#$ from textual-pyfiglet import FigletWidget

To install the extended fonts collection:
#$ pip install textual-pyfiglet[fonts]

# NOTE: You can also download FIG fonts from the internet and just drop them in the fonts folder.
See the readme for more information.

I made sure to preserve the original PyFiglet CLI for reference.
You can access the original CLI with the following command:
#$ python -m textual_pyfiglet.pyfiglet

The original PyFiglet CLI has a demo that can be accessed like this (verbatim, with the spaces):
#$ python -m textual_pyfiglet.pyfiglet some text here

In order to change fonts with the original demo, you can use the -f flag like this:
#$ python -m textual_pyfiglet.pyfiglet -f small Hey hows it going?

"""

# tells us if extended fonts has been installed
# you might want access to this yourself
from .config import extended_fonts_installed      
extended_fonts_installed: bool

from .figletwidget import FigletWidget
