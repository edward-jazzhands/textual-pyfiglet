"""Module for the FigletWidget class.

Import FigletWidget into your project to use it."""

from __future__ import annotations
import os
# from platformdirs import user_data_dir
import importlib.util

from collections import deque

from textual.app import ComposeResult
from textual.containers import Center
from textual.strip import Strip
from textual.widget import Widget
from textual.widgets import Footer
from textual.geometry import Region
from textual.color import Gradient, Color

from rich.segment import Segment
from rich.style import Style

# For type checking:
from rich.console import RenderableType
from textual.visual import SupportsVisual, Visual

# For the widget:
from textual.message import Message
from textual.widgets import Static
from textual.reactive import reactive
from textual.content import Content

# Textual-Pyfiglet imports:
from textual_pyfiglet.pyfiglet import Figlet #, fonts

from rich.text import Text

# Line API stuff
# from rich.segment import Segment
# from rich.style import Style
# from textual.strip import Strip
# from textual.widget import Widget



class _InnerFiglet(Static):
    """The Inner Figlet contains the actual PyFiglet class.
    This nested layout is necessary for things to work properly."""

    DEFAULT_CSS = """
    _InnerFiglet {
        width: 100%;
        height: 100%;
    }
    """

    figlet_input:  reactive[str] = reactive('', always_update=True)
    figlet_output: reactive[str] = reactive('', layout=True)
    font:          reactive[str] = reactive('standard')
    figlet_lines: list = []

    # Note: Indeed its a bit odd that justify is not also a reactive... I had to go into
    # the pyfiglet source code to create a setter method for justify. (It previously
    # only had a getter method). It seems to work identically without being reactive.
    # I don't know why.

    def __init__(self, *args, font:str, justify:str, **kwargs) -> None:
        """Private class for the FigletWidget.
        Don't use this class. Use FigletWidget instead. """
        
        super().__init__(*args, **kwargs)
        self.figlet = Figlet(font=font, justify=justify) #~ <-- Create the PyFiglet object
        self.font = font

    def watch_font(self, value: str) -> None:

        try:
            self.figlet.setFont(font=value)
        except Exception as e:
            self.log.error(f"Error setting font: {e}")

        # this seems to be necessary to update the figlet object after setting the font?
        self.watch_figlet_input(self.figlet_input)

    def watch_figlet_input(self, value: str) -> None:

        if not self.parent or self.parent.size.width == 0:
            return
         
        if self.figlet.width != self.parent.size.width:
            self.figlet.width = self.parent.size.width

        if value == '':
            self.figlet_output = ''
        else:
            try:
                figlet_render = self.figlet.renderText(value)  #~ <-- this is where the magic happens
            except Exception as e:
                self.log.error(f"Error rendering PyFiglet: {e}")
                return
            
            figlet_render = figlet_render.rstrip()      # remove trailing whitespace
            self.figlet_lines = figlet_render.split('\n')
            self.fig_width = len(self.figlet_lines[0])
            self.fig_height = len(self.figlet_lines)

            self.log.debug(Text(
                f"Figlet width: {self.fig_width}, Figlet height: {self.fig_height}", style="bold yellow"
            ))

            # if self.parent.styles.is_auto_width:
            #     self.parent.styles.width = self.fig_width

            if self.parent.styles.is_auto_height:
                self.styles.height = self.fig_height

            self.figlet_output = figlet_render

    def render(self) -> Content:
        return Content(self.figlet_output)
    
    # def render_line(self, y: int) -> Strip:
    #     """Render a line of the widget. y is relative to the top of the widget."""

    #     # white = Style.parse("on white")  # Get a style object for a white background
    #     # black = Style.parse("on black")  # Get a style object for a black background

    #     self.log.debug(Text(f"Render_line called with y value: {y}", style="bold red"))

    #     if not self.figlet_output:
    #         return Strip.blank(self.size.width)

    #     segments = [Segment(self.figlet_lines[y]),]
    #     # segment = Segment(self.figlet_lines[y], Style(bold=True))

    #     return Strip(segments)
    


    # def __init__(self, splash: list[str], gradient: Gradient) -> None:
    #     super().__init__()

    #     self.splash = splash
    #     self.line_colors = deque([Style(color=color.rich_color) for color in gradient.colors])

    #     self.set_interval(interval=0.08, callback=self.refresh, repeat=0)

    # def render_lines(self, crop: Region) -> list[Strip]:
    #     self.line_colors.rotate()
    #     return super().render_lines(crop)

    # def render_line(self, y: int) -> Strip:
    #     return Strip([Segment(self.splash[y], style=self.line_colors[y])])



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

    if importlib.util.find_spec("textual_pyfiglet_fonts") is not None:
        extended_fonts_installed = True
    else:
        extended_fonts_installed = False

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


    def __init__(
        self,
        content: RenderableType | SupportsVisual = "",
        *,
        font: str = "calvin_s",
        justify: str = "center",
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
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

        super().__init__(
            name=name, id=id, classes=classes, disabled=disabled, markup=markup
        )
        self.stored_text = str(content)
        self.font = font
        self.justify = justify
        self.expand = expand
        self.shrink = shrink
        self._content = content
        self._visual: Visual | None = None

        self.gradient_color_1:str = "hotpink"
        self.gradient_color_2:str = "blue"
        self.gradient_quality:int = 30

        # NOTE: Figlet also has a "direction" argument


    # def compose(self) -> ComposeResult:

    #     splash = self.make_splash(self.stored_text, self.font)
    #     gradient = self.make_gradient(self.gradient_color_1, self.gradient_color_2, self.gradient_quality)

    #     splash_width = len(max(splash, key=len))
    #     splash_height = len(splash)

    #     self.log(f"Splash width: {splash_width} | Term width: {self.size.width}")
    #     self.log(f"Splash height: {splash_height} | Term height: {self.size.height}")

    #     animated_splash = AnimatedSplash(splash, gradient)
    #     animated_splash.styles.width = splash_width
    #     animated_splash.styles.height = splash_height

    #     with Center(id="center"):
    #         yield animated_splash
    #     yield Footer()


    def compose(self) -> ComposeResult:

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
        
        fonts_list = []
        fonts_list.extend(self.base_fonts)

        if self.extended_fonts_installed:
            import textual_pyfiglet_fonts

            # get the path of the fonts package:
            fonts_module_path = os.path.dirname(textual_pyfiglet_fonts.__file__) 

            # add extended fonts to the list:
            for font_file in os.listdir(fonts_module_path):
                if os.path.isdir(os.path.join(fonts_module_path, font_file)):
                    continue        # skip directories
                if font_file.endswith('.flf') or font_file.endswith('.tlf'):
                    fonts_list.append(os.path.splitext(font_file)[0])
                
        return fonts_list


    def get_figlet_as_string(self) -> str:
        """Return the PyFiglet text as a string."""
        return self._inner_figlet.figlet_output
    
    def copy_figlet_to_clipboard(self) -> None:
        """Copy the PyFiglet text to the clipboard."""

        figlet_as_string = self.get_figlet_as_string()
        self.log(f"Copying PyFiglet text to clipboard: {figlet_as_string}")

        self.app.copy_to_clipboard(figlet_as_string)



    # def make_splash(self, text: str, font: str) -> list[str]:

    #     figlet_obj = Figlet(font=font, justify="left", width=self.size.width-10)
    #     figlet = figlet_obj.renderText(text)

    #     return figlet.splitlines()

    # def make_gradient(self, color1: str, color2: str, quality: int) -> Gradient:
    #     "Use color names, ie. 'red', 'blue'"

    #     parsed_color1 = Color.parse(color1)
    #     parsed_color2 = Color.parse(color2)

    #     stop1 = (0.0, parsed_color1)
    #     stop2 = (0.5, parsed_color2)
    #     stop3 = (1.0, parsed_color1)
    #     return Gradient(stop1, stop2, stop3, quality=quality)
        
