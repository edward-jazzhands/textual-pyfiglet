from __future__ import annotations
from typing import cast
import os

from textual.message import Message
from textual.widgets import Static
from textual.containers import Container

from .pyfiglet import Figlet, fonts


class _InnerFiglet(Static):
    """This is a placeholder widget that will contain the PyFiglet text.
    It's used to calculate the size of the PyFiglet text, and then the FigletWidget
    will adjust its size to fit the text."""

    DEFAULT_CSS = """
    FigletWidget {
        margin: 0;
        padding: 0;
    }
    """

    def __init__(self, *args, font, justify, **kwargs) -> None:
        """Private class for the FigletWidget.
        Args:
            renderable: A Rich renderable, or string containing console markup.
            font (PyFiglet): Font to use for the ASCII art. Default is "calvin_s".
            expand: Expand content if required to fill container.
            shrink: Shrink content if required to fill container.
            markup: True if markup should be parsed and rendered.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
            disabled: Whether the static is disabled or not."""
        
        super().__init__(*args, **kwargs)
        self.stored_text = None             # we init with no stored text
        self.font = font
        self.justify = justify
        self.figlet = Figlet(font=font, justify=justify)

    def update(self, new_text: str | None = None) -> None:
        """Custom update method for the FigletWidget.
        This method is private so docstring is in the FigletWidget class."""
        if new_text is not None:
            self.stored_text = new_text

        # for dev debugging
        # self.log.debug(
        #     f'parent.size.width: {self.parent.size.width}  |  parent.size.height: {self.parent.size.height} \n'
        #     f'  self.size.width: {self.size.width}   |  self.size.height:   {self.size.height}'
        # )

        if self.parent.size.width == 0:
            self.log.error('parent.size.width is 0. Exiting update.')
            return
        self.figlet.width = self.parent.size.width

        self.renderable = self.figlet.renderText(self.stored_text)

        # this line is very key to the widget resizing properly
        # activates textual's layout system in some magical way. 
        self.refresh(layout=True)

        # More dev debugging
        # self.log.debug(f'update EXIT:   parent.size: {self.parent.size} \n                 self.size: {self.size}')


class FigletWidget(Static):
    """Adds simple PyFiglet ability to the Static widget.

    The easiest way to use this widget is to place it inside of a container, 
    to act as its parent container.

    See __init__ for more details."""
    

    DEFAULT_CSS = """
    FigletWidget {
        width: auto;
        height: auto;
        padding: 0;
    }
    """

    base_fonts = [
        'calvin_s',
        'chunky',
        'cybermedium',
        'small_slant',
        'small',
        'smblock',
        'smbraille',
        'standard',
        'stick_letters',
        'tmplr'
    ]

    class Updated(Message):
        """This is here to provide a message to the app that the widget has been updated.
        You might need this to trigger something else in your app resizing, adjusting, etc.
        The size of FIG fonts can vary greatly, so this might help you adjust other widgets."""

        def __init__(self, widget: FigletWidget) -> None:
            super().__init__()
            self.widget = widget

        @property
        def control(self) -> FigletWidget:
            return self.widget


    def __init__(self, *args, font: str = "calvin_s", justify: str = "center", **kwargs) -> None:
        """A custom widget for turning text into ASCII art using PyFiglet.
        This args section is copied from the Static widget. It's the same except for the font argument.

        This class is designed to be an easy drop in replacement for the Static widget.
        The only new argument is 'font', which has a default set to one of the smallest fonts.
        You can replace any Static widget with this and it should work (aside from the size).

        The widget will try to adjust its render area to fit inside of its parent container.
        The easiest way to use this widget is to place it inside of a container.
        Resize the parent container, and then call the `update()` method.

        Args:
            renderable: A Rich renderable, or string containing console markup.
            font (PyFiglet): Font to use for the ASCII art. Default is "calvin_s".
            justify (PyFiglet): Justification for the text. Default is "center".
            expand: Expand content if required to fill container.
            shrink: Shrink content if required to fill container.
            markup: True if markup should be parsed and rendered.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
            disabled: Whether the static is disabled or not.

        Included fonts:
        - calvin_s
        - chunky
        - cybermedium
        - small_slant
        - small
        - smblock
        - smbraille
        - standard
        - stick_letters
        - tmplr

        Remember you can always download more fonts. To download the extended fonts pack:
        pip install textual-pyfiglet[fonts]

        You can also download individual fonts online and drop them in the fonts folder.
        """
        super().__init__(*args, **kwargs)
        self.stored_text = str(self.renderable)
        self.font = font
        self.justify = justify

        # NOTE: Figlet also has a "direction" argument
        # TODO Add Direction arguments

    def compose(self):
        yield _InnerFiglet(self.stored_text, id='inner_figlet', font=self.font, justify=self.justify)

    def on_mount(self):
        self._inner_figlet = cast(_InnerFiglet, self.query_one('#inner_figlet'))
        self.update(new_text=self.stored_text)

    def on_resize(self):
        self._inner_figlet.update()

    def update(self, new_text: str|None = None) -> None:
        '''Update the PyFiglet area with the new text.    
        Note that this over-rides the standard update method in the Static widget.   
        Unlike the Static widget, this method does not take a Rich renderable.   
        It can only take a text string. Figlet needs a normal string to work properly.

        Args:
            new_text: The text to update the PyFiglet widget with. Default is None.'''

        if new_text is not None:
            self.stored_text = new_text
        self._inner_figlet.update(new_text=self.stored_text)

    def set_font(self, font: str) -> None:
        """Set the font for the PyFiglet widget.   
        The widget will update with the new font automatically.
        
        Pass in the name of the font as a string:
        ie 'calvin_s', 'small', etc.
        
        Args:
            font: The name of the font to set."""
        
        self._inner_figlet.figlet.setFont(font=font)
        self.update()

    def set_justify(self, justify: str) -> None:
        """Set the justification for the PyFiglet widget.   
        The widget will update with the new justification automatically.
        
        Pass in the justification as a string:   
        options are: 'left', 'center', 'right', 'auto'
        
        Args:
            justify: The justification to set."""
        
        self._inner_figlet.figlet.setJustify(justify=justify)
        self.update()

    def get_fonts_list(self, get_all: bool = True) -> list:
        """Scans the fonts folder.   
        Returns a list of all font filenames (without extensions).
        
        Args:
            get_all: If True, returns all fonts. If False, returns only the base fonts."""

        if not get_all:
            return self.base_fonts

        # first get the path of the fonts package:
        package_path = os.path.dirname(fonts.__file__)
        path_list = os.listdir(package_path)
        fonts_list = []

        for filename in path_list:
            if filename.endswith('.flf') or filename.endswith('.tlf'):
                fonts_list.append(os.path.splitext(filename)[0])
        return fonts_list
