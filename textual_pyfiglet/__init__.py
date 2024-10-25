"""To import in your own project:   
from textual-pyfiglet import FigletWidget

To install the extended fonts collection:   
pip install textual-pyfiglet[fonts]

You can also download FIG fonts from the internet and just drop them in the fonts folder.   
See the readme for more information.
 
You can access the original PyFiglet CLI with the following command:   
python -m textual_pyfiglet.pyfiglet
"""

# tells us if extended fonts has been installed
# you might want access to this yourself
from .config import extended_fonts_installed      
extended_fonts_installed: bool

from .figletwidget import FigletWidget
