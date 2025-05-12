"""Textual-PyFiglet
A Textual widget by Edward Jazzhands.

To import:
```
from textual_pyfiglet import FigletWidget
```

You can also import the original PyFiglet.
```
# Class version:
from textual_pyfiglet.pyfiglet import Figlet

# Function version:
from textual_pyfiglet.pyfiglet import figlet_format
```

Package standards:
- Type Checking (Pyright and MyPy) - strict
- Linting - Ruff
- Formatting - Black - max 110 characters / line
"""

from textual_pyfiglet.figletwidget import FigletWidget

__all__ = ["FigletWidget"]
