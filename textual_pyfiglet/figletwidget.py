from __future__ import annotations

from .pyfiglet import Figlet

from textual.app import App, on
from textual.message import Message
from textual.containers import Horizontal, Container, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, TextArea, Select


class FigletWidget(Static):
    """Adds simple PyFiglet ability to the Static widget.    
    NOTE: The width and height are set to auto, so the widget will expand to fit the text.    
    The size of the PyFiglet widget can vary greatly depending on the font and text.    
    The default is auto so it will expand or contract automatically.    
    In your own app you might wish to change this to a fixed size.    
    See __init__ for more details."""

    DEFAULT_CSS = """
    FigletWidget {
        width: auto;
        height: auto;
    }
    """

    class Updated(Message):
        """This is here to provide a message to the app that the widget has been updated.
        You might need this to trigger something else in your app resizing, adjusting, etc.
        The size of FIG fonts can vary greatly, so this might help you adjust other widgets."""

        def __init__(self, widget: FigletWidget) -> None:
            super().__init__()
            self.widget = widget

        @property
        def control(self) -> FigletWidget:
            """This is required to be able to use the 'selector' property
            when using the message handler."""

            return self.widget



    def __init__(self, *args, font: str = "calvin_s", **kwargs) -> None:
        """A custom widget for turning text into ASCII art using PyFiglet.
        This args section is copied from the Static widget. It's the same except for the font argument.

        This class is designed to be an easy drop in replacement for the Static widget.
        The only new argument is 'font', which has a default set to one of the smallest fonts.
        You can replace any Static widget with this and it should just work (aside from the size)

        Args:
            renderable: A Rich renderable, or string containing console markup.
            font (PyFiglet): Font to use for the ASCII art. Default is "calvin_s".
            expand: Expand content if required to fill container.
            shrink: Shrink content if required to fill container.
            markup: True if markup should be parsed and rendered.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
            disabled: Whether the static is disabled or not.

        Included fonts:
        - standard
        - small
        - calvin_s
        - slant
        - small slant
        - modular
        - chunky
        - broadway_kb
        - cybermedium

        Remember you can always download more fonts. To download the extended fonts pack:
        # TODO Add me here when I have the link

        You can also download individual fonts online and drop them in the fonts folder.
        """
        super().__init__(*args, **kwargs)
        self.stored_text = str(self.renderable)
        self.font = font
        self.screen_width = self.app.size.width
        self.figlet = Figlet(font=font, width=self.screen_width - 8)

        # NOTE: Figlet also has "direction" and "justify" arguments,
        # but I'm not using them here yet. Should probably be added in the future.
        # TODO Add Direction and Justify arguments

    def on_mount(self):
        self.update()

    def update(self, new_text: str | None = None):
        """Update the PyFiglet area with the new text.    
        Note that this over-rides the standard update method in the Static widget!   
        This does NOT take any rich renderable like the Static widget does.
        It can only take a text string.

        Args:
            new_text: The text to update the PyFiglet widget with. Default is None.
        """

        if new_text is not None:
            self.stored_text = new_text
        self.renderable = self.figlet.renderText(self.stored_text)

        # this line is important
        # this makes textual reset the widget size to whatever the new renderable is
        self.set_styles("width: auto; height: auto;")   
        
        # Necessay to refresh the widget to apply the changes
        self.refresh()

        # Post a message to the app that the widget has been updated
        self.post_message(self.Updated(self))

    def change_font(self, font: str) -> None:
        self.figlet.setFont(font=font)
        self.update()

    def change_width(self, width: int) -> None:
        self.figlet.width = width
        self.update()
