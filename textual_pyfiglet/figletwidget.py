"""Module for the FigletWidget class.

Import FigletWidget into your project to use it."""

from __future__ import annotations
import os
from platformdirs import user_data_dir

from textual.message import Message
from textual.widgets import Static
from textual.reactive import reactive

from textual_pyfiglet.pyfiglet import Figlet, fonts
from textual_pyfiglet.config import check_for_extended_fonts

are_extended_fonts_installed: bool = check_for_extended_fonts()


class _InnerFiglet(Static):
    """The Inner Figlet contains the actual PyFiglet object.
    This nested layout is necessary for things to work properly."""

    figlet_input:  reactive[str] = reactive('', always_update=True)
    figlet_output: reactive[str] = reactive('', layout=True)
    font:          reactive[str] = reactive('standard')

    # Note: Indeed its a bit odd that justify is not also a reactive... I had to go into
    # the pyfiglet source code to create a setter method for justify. (It previously
    # only had a getter method). It seems to work identically without being reactive.
    # I don't know why.

    def __init__(self, *args, font, justify, **kwargs) -> None:
        """Private class for the FigletWidget. Same as Static except for `font` and `justify` args.   
        Don't use this class. Use FigletWidget instead. """
        
        super().__init__(*args, **kwargs)
        self.figlet = Figlet(font=font, justify=justify)
        self.font = font

    def watch_font(self, value: str) -> None:
        self.figlet.setFont(font=value)
        self.watch_figlet_input(self.figlet_input)

    def watch_figlet_input(self, value: str) -> None:

        if not self.parent or self.parent.size.width == 0:
            return
        self.figlet.width = self.parent.size.width

        if value == '':
            self.figlet_output = ''
        else:
            self.figlet_output = self.figlet.renderText(value)

    def render(self) -> str:
        return self.figlet_output


class FigletWidget(Static):
    """Adds PyFiglet ability to the Static widget.
    
    See init docstring for more info."""

    DEFAULT_CSS = """
    FigletWidget {
        width: auto;
        height: auto;
        padding: 0;
    }
    """

    are_extended_fonts_installed = are_extended_fonts_installed
    """This is a convenience variable, so the class can easily check 
    if the extended fonts pack has been installed."""

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
            '''The FigletWidget that was updated.'''

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
            content: A Rich renderable, or string containing console markup.
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

        Remember you can download more fonts. To download the extended fonts pack:
        pip install textual-pyfiglet[fonts]
        """
        super().__init__(*args, **kwargs)
        self.stored_text = str(self.renderable)
        self.renderable = ''
        self.font = font
        self.justify = justify

        # NOTE: Figlet also has a "direction" argument
        # TODO Add Direction argument

    def compose(self):
        self._inner_figlet = _InnerFiglet(
            self.stored_text,       # <-- this must be positional to maintain compatibility
            id='inner_figlet',      # with older versions of Textual. (the arg was renamed)
            font=self.font,
            justify=self.justify
        )
        yield self._inner_figlet

    def on_mount(self):
        self.update(self.stored_text)

    def on_resize(self):
        self.update()

    def update(self, new_text: str | None = None) -> None:
        '''Update the PyFiglet area with the new text.    
        Note that this over-rides the standard update method in the Static widget.   
        Unlike the Static widget, this method does not take a Rich renderable.   
        It can only take a text string. Figlet needs a normal string to work properly.

        Args:
            new_text: The text to update the PyFiglet widget with. Default is None.'''
        
        if new_text is not None:
            self.stored_text = new_text

        # self._inner_figlet.update(self.stored_text)
        self._inner_figlet.figlet_input = self.stored_text
        self.post_message(self.Updated(self))

    def set_font(self, font: str) -> None:
        """Set the font for the PyFiglet widget.   
        The widget will update with the new font automatically.
        
        Pass in the name of the font as a string:
        ie 'calvin_s', 'small', etc.
        
        Args:
            font: The name of the font to set."""
        
        # self._inner_figlet.figlet.setFont(font=font)
        self._inner_figlet.font = font
        self.update()

    def set_justify(self, justify: str) -> None:
        """Set the justification for the PyFiglet widget.   
        The widget will update with the new justification automatically.
        
        Pass in the justification as a string:   
        options are: 'left', 'center', 'right', 'auto'
        
        Args:
            justify: The justification to set."""
        
        self._inner_figlet.figlet.justify = justify
        self.update()

    def get_fonts_list(self, get_all: bool = True) -> list:
        """Scans the fonts folder.   
        Returns a list of all font filenames (without extensions).
        
        Args:
            get_all: If True, returns all fonts. If False, returns only the base fonts."""

        if not get_all:
            return self.base_fonts

        # first get the path of the fonts package:
        base_fonts_folder = os.path.dirname(fonts.__file__)
        base_fonts_folder_contents = os.listdir(base_fonts_folder)    # list of all files in the fonts folder
        fonts_list = []

        for filename in base_fonts_folder_contents:
            if filename.endswith('.flf') or filename.endswith('.tlf'):
                fonts_list.append(os.path.splitext(filename)[0])

        user_fonts_folder = user_data_dir('pyfiglet', appauthor=False)
        user_fonts_folder_contents = os.listdir(user_fonts_folder)

        for filename in user_fonts_folder_contents:
            if filename.endswith('.flf') or filename.endswith('.tlf'):
                fonts_list.append(os.path.splitext(filename)[0])

        return fonts_list
    
    def copy_figlet_to_clipboard(self) -> None:
        """Copy the PyFiglet text to the clipboard."""
        self.app.copy_to_clipboard(str(self._inner_figlet.renderable))

    def return_figlet_as_string(self) -> str:
        """Return the PyFiglet text as a string."""
        return str(self._inner_figlet.renderable)
    
