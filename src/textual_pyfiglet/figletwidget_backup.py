"""Module for the FigletWidget class.

Import FigletWidget into your project to use it."""

#! BACKUP VERSION CONTAINS LOG MESSAGES

# STANDARD LIBRARY IMPORTS
from __future__ import annotations
from typing_extensions import Literal, get_args
from collections import deque

# Textual and Rich imports
from textual.strip import Strip
from textual.color import Gradient, Color
from textual.css.scalar import Scalar #, Unit
from textual.message import Message
from textual.widgets import Static
from textual.widget import Widget
from textual.reactive import reactive
from textual.timer import Timer
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

# Textual-Pyfiglet imports:
from textual_pyfiglet.pyfiglet import Figlet, FigletError, figlet_format
from textual_pyfiglet.pyfiglet.fonts import ALL_FONTS   # not the actual fonts, just the names.

# LITERALS: 
JUSTIFY_OPTIONS = Literal['left', 'center', 'right', 'auto']
COLOR_MODE = Literal['color', 'gradient', 'none']


class FigletWidget(Static):

    DEFAULT_CSS = "FigletWidget {width: auto;}"

    figlet_input:  reactive[str] = reactive[str]('', always_update=True) 
    "Master input. You can use this, or use the methods: `set_text()` / `update()`."

    color1: reactive[str | None] = reactive[str | None]('')
    "You can use this, or use the `set_color1()` method."

    color2: reactive[str | None] = reactive[str | None]('')
    "You can use this, or use the `set_color2()` method."

    animated: reactive[bool] = reactive[bool](False, always_update=True)
    "You can use this, or use the methods: `set_animated()` / `toggle_animated()`."

    _font:          reactive[ALL_FONTS] = reactive[ALL_FONTS]('ansi_regular')
    "Use the `set_font()` method so you get auto-completion for available fonts."

    _justify:       reactive[JUSTIFY_OPTIONS] = reactive[JUSTIFY_OPTIONS]('auto') 
    "Use the `set_justify()` method so you get auto-completion for available justifications."            

    _color_mode:    reactive[COLOR_MODE] = reactive[COLOR_MODE]('none', always_update=True)
    "Used internally. Do not set this directly. Use the `color1` and `color2` properties instead."    

    fig_height_reported: reactive[int] = reactive[int](0)
    _figlet_lines:  reactive[list[str]] = reactive(list, layout=True)     


    class Updated(Message):
        """This is here to provide a message to the app that the widget has been updated.
        You might need this to trigger something else in your app resizing, adjusting, etc.
        The size of FIG fonts can vary greatly, so this might help you adjust other widgets.
        
        available properties:
        - width (width of the widget)
        - height (height of the widget)
        - fig_width (width render setting of the Pyfiglet object)
        - widget/control (the FigletWidget that was updated)
        """

        def __init__(self, widget: FigletWidget) -> None:
            super().__init__()
            assert isinstance(widget.parent, Widget)

            self.widget = widget
            "The FigletWidget that was updated."
            
            self.width = widget.size.width
            "The width of the widget. This is the size of the widget as it appears to Textual."
            self.height = widget.size.height
            "The height of the widget. This is the size of the widget as it appears to Textual."

            self.parent_width = widget.parent.size.width
            "The width of the parent widget or container that is holding the FigletWidget."

            self.fig_width = widget.figlet.width
            """This is the width of the Pyfiglet object. It's the internal width setting
            used by the Pyfiglet object to render the text. It's not the same as the widget width."""

        @property
        def control(self) -> FigletWidget:
            return self.widget

    def __init__(
        self,
        content: str = "",
        *,
        font: ALL_FONTS = "standard",
        justify: JUSTIFY_OPTIONS = "auto", 
        color1: str | None = None,
        color2: str | None = None,
        animate: bool = False,
        animation_quality: str | int = "auto",
        animation_interval: float = 0.08,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Create a FigletWidget.

        Args:
            content: A Rich renderable, or string containing console markup.
            font (PyFiglet): Font to use for the ASCII art. Default is "standard".
            justify (PyFiglet): Justification for the text. Default is "auto".
                (The auto mode will switch to right if the direction is right-to-left.)
            color1 (Gradient): Set color for the figlet - also First color for the gradient
            color2 (Gradient): Second color for the gradient. Unused if None.
            animate: Whether to animate the gradient.
            animation_quality: How many colors the animation gradient should have.
                Default is "auto", which will set the quality to the number of lines in the widget.
            animation_interval: How long to wait between frames of the animation, in seconds.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.

        FUN NOTE: If you've read this far, here's a tip. I've spent a lot of time with
        figlet and so I'm very familiar with the fonts. The class comes with an attribute
        called 'favorite_fonts'. This is a dictionary of the fonts I like best.
        Access it with `FigletWidget.favorite_fonts`.
        """
        super().__init__(name=name, id=id, classes=classes)

        self.figlet = Figlet()               #~ <-- Create the PyFiglet object

        # NOTE: The FigletWidget has to wait for the Widget to be fully mounted before
        # it can know its maximum width and set the render size. There is a full write-up
        # of how this works here:              #? INSERT WRITEUP HERE

        try:
            string = str(content)
        except Exception as e:
            self.log.error(f"FigletWidget Error converting input to string: {e}")
            raise e

        self.set_reactive(FigletWidget.figlet_input, string)
        self.set_reactive(FigletWidget._font, font)                  
        self.set_reactive(FigletWidget._justify, justify)
        if color1 is not None:                
            self.set_reactive(FigletWidget.color1, color1)
        if color2 is not None:            
            self.set_reactive(FigletWidget.color2, color2)
        self.set_reactive(FigletWidget.animated, animate)
        self._animation_interval = animation_interval
        self._gradient_quality = animation_quality

        self.line_colors: deque[Style] = deque()   
        self.color = None
        self.gradient = None
        self.interval_timer: Timer | None = None        
  
        #! NOTE: Figlet also has a "direction" argument. Add here?         

        #~ COLORS / GRADIENT ~#

        if not color1 and not color2:          # if no style,
            self.set_reactive(FigletWidget._color_mode, 'none')  # set to none
        elif color1 and not color2:            # only color 1
            self.set_reactive(FigletWidget._color_mode, 'color')  # set to color
        elif color1 and color2:
            self.set_reactive(FigletWidget._color_mode, 'gradient')  # set to gradient
        else:
            raise Exception("If you're seeing this error, something is wrong with the color mode.")

    def on_mount(self):

        self.log(
            f"WIDTH SETTING: {self.styles.width} \n"
            f"HEIGHT SETTING: {self.styles.height} \n"
            f"Parent: {self.parent} \n"
        )      

        if self.animated:
            self.interval_timer = self.set_interval(interval=self._animation_interval, callback=self.refresh)

    #############################
    #~ SETTER / GETTER METHODS ~#
    #############################

    # (type ignore is because of overriding update in incompatible manner)
    def update(self, new_text: str) -> None:  # type: ignore
        '''Update the PyFiglet area with the new text.    
        Note that this over-rides the standard update method in the Static widget.   
        Unlike the Static widget, this method does not take a Rich renderable.   
        It can only take a text string. Figlet needs a normal string to work properly.

        Args:
            new_text: The text to update the PyFiglet widget with. Default is None.'''

        self.figlet_input = new_text

    def set_text(self, text: str) -> None:
        """Alias for update()."""
        self.update(text)

    def set_font(self, font: ALL_FONTS) -> None:
        """Set the font for the PyFiglet widget.   
        The widget will update with the new font automatically.        
        Args:
            font: The name of the font to set."""
        
        self._font = font

    def set_justify(self, justify: JUSTIFY_OPTIONS) -> None:
        """Set the justification for the PyFiglet widget.   
        The widget will update with the new justification automatically.        
        Args:
            justify: The justification to set."""
        
        self._justify = justify

        # NOTE: I had to go into the Pyfiglet source code to create a setter method for justify
        # to allow changing it in real-time. (It previously only had a getter method).        

    def set_animated(self, animated: bool) -> None:
        """Set the animated state of the PyFiglet widget.   
        The widget will update with the new animated state automatically.        
        Args:
            animated: True if the widget should be animated, False if not."""
        
        self.animated = animated

    def toggle_animated(self) -> None:
        """Toggle the animated state of the PyFiglet widget.   
        The widget will update with the new animated state automatically."""
        
        self.animated = not self.animated

    def set_color1(self, color: str | None) -> None:
        """Set the first color for the PyFiglet widget.   
        The widget will update with the new color automatically.        
        Args:
            color: The first color to set."""
        
        self.color1 = color

    def set_color2(self, color: str | None) -> None:
        """Set the second color for the PyFiglet widget.   
        The widget will update with the new color automatically.        
        Args:
            color: The second color to set."""
        
        self.color2 = color

    def set_gradient_quality(self, quality: str | int) -> None:
        """Set the gradient quality for the PyFiglet widget.   
        The widget will update with the new gradient quality automatically.        
        Args:
            quality: The gradient quality to set. Can be 'auto' or an integer."""
        
        if quality == 'auto':
            self._gradient_quality = len(self._figlet_lines) * 2
            self._color_mode = self._color_mode   # trigger the reactive to update the color mode.
            return
        elif isinstance(quality, int):
            if 3 <= quality <= 100:
                self._gradient_quality = quality
                self._color_mode = self._color_mode   # trigger the reactive to update the color mode.
                return

        raise Exception("Invalid gradient quality. Must be 'auto' or an integer between 1 and 100.")
    
    def set_animation_speed(self, interval: float) -> None: 
        """Set the animation interval for the PyFiglet widget.   
        The widget will update with the new animation interval automatically.        
        Args:
            interval: The animation interval to set. Must be a float between 0.05 and 1.0."""
        
        if not 0.05 <= interval <= 1.0:
            raise Exception("Animation interval must be greater than 0.05 and less than 1.0.")
        self._animation_interval = interval
        self.animated = False   # stop the animation if it's running
        self.animated = True    # restart the animation with the new interval

    def get_fonts_list(self) -> list[str]:
        """Returns a list of all fonts."""

        return list(get_args(ALL_FONTS))     # Extract list from the Literal


    def get_figlet_as_string(self) -> str:
        """Return the PyFiglet text as a string."""

        return self.figlet_render

    @classmethod
    def figlet_quick(
            cls,
            text: str,
            font: ALL_FONTS = "standard",
            width: int = 80,
            justify: JUSTIFY_OPTIONS = "auto"
        ):
        """This is a standalone class method. It just provides quick access to the figlet_format
        function in the pyfiglet package.  
        It also adds type hinting / auto-completion for the fonts list."""
        return figlet_format(text=text, font=font, width=width, justify=justify)

    ##############
    #~ WATCHERS ~#
    ##############

    def watch_figlet_input(self, old_value, new_value: str) -> None:

        self.log(Text.from_markup(
            "[bold yellow]watch_figlet_input triggered. \n"
            f"[green]widget style width: {self.styles.width} \n"
            f"widget style height: {self.styles.height} \n"
        ))  
        if self.gradient:
            self.log(f"gradient steps: {len(self.gradient.colors)}")

        if new_value == '':
            self.log("Figlet input is empty.")
            self._figlet_lines = ['']
            self.mutate_reactive(FigletWidget._figlet_lines) 
        else:
            self._figlet_lines = self.render_figlet(new_value)     #~ <- where the render happens
            self.mutate_reactive(FigletWidget._figlet_lines)          

        self.post_message(self.Updated(self))             

    def watch__color_mode(self, old_value: COLOR_MODE, new_value: COLOR_MODE) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch__color_mode triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))

        if new_value == 'none':
            self.line_colors = deque([Style()])
            self.gradient = None   # reset the gradient if it was set
            
        elif new_value == 'color':
            try:
                if self.color1:
                    my_color_obj = Color.parse(self.color1)   # An invalid color will raise a ColorParseError
                elif self.color2:
                    my_color_obj = Color.parse(self.color2)
                else:
                    raise Exception("Color mode is set to color, but no colors are set.")
            except Exception as e:
                self.log.error(f"Error parsing color: {e}")
                raise e
            else:
                self.line_colors = deque([Style(color=my_color_obj.rich_color)])
                self.gradient = None   # reset the gradient if it was set

        elif new_value == 'gradient':
            if self._gradient_quality == 'auto':
                animation_quality = len(self._figlet_lines) * 2
            elif isinstance(self._gradient_quality, int):
                animation_quality = self._gradient_quality
            else:
                raise Exception("Invalid animation quality. Must be 'auto' or an integer.")

            try:
                assert self.color1 and self.color2, "Color mode is set to gradient, but colors are not set."
                self.gradient = self.make_gradient(self.color1, self.color2, animation_quality)
            except Exception as e:
                self.log.error(f"Error creating gradient: {e}")
                raise e
            self.line_colors = deque([Style(color=color.rich_color) for color in self.gradient.colors])  # sets both

        else:
            raise Exception(f"Invalid color mode: {new_value}")

    def watch_color1(self, old_value: str, new_value: str) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch_color1 triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))

        assert isinstance(new_value, str)

        if not new_value and not self.color2:
            self.log("Color 1 is empty, and color 2 is empty. Setting color mode to none.")
            self._color_mode = 'none'
        elif not new_value and self.color2:    
            self.log("Color 1 is empty, but color 2 is set. Setting color mode to color.")
            self._color_mode = 'color'
        elif new_value and not self.color2:
            self.log("Color 1 is set, but color 2 is empty. Setting color mode to color.")
            self._color_mode = 'color'
        elif new_value and self.color2:
            self.log("Color 1 and color 2 are both set. Setting color mode to gradient.")
            self._color_mode = 'gradient'

    def watch_color2(self, old_value: str, new_value: str) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch_color2 triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))

        assert isinstance(new_value, str)

        if not new_value and not self.color1:
            self.log("Color 2 is empty, and color 1 is empty. Setting color mode to none.")
            self._color_mode = 'none'
        if not new_value and self.color1:
            self.log("Color 2 is empty, but color 1 is set. Setting color mode to color.")
            self._color_mode = 'color'
        if new_value and not self.color1:
            self.log("Color 2 is set, but color 1 is empty. Setting color mode to color.")
            self._color_mode = 'color'
        elif new_value and self.color1:
            self.log("Color 2 and color 1 are both set. Setting color mode to gradient.")
            self._color_mode = 'gradient'

    def watch_animated(self, old_value: bool, new_value: bool) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch_animated triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))

        if self.gradient:
            if new_value:
                if self.interval_timer:
                    self.interval_timer.resume()
                else:
                    self.interval_timer = self.set_interval(
                        interval=self._animation_interval, callback=self.refresh
                    )
            else:
                if self.interval_timer:
                    self.interval_timer.stop()
                    self.interval_timer = None

    def watch__font(self, old_value: str, new_value: str) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch_font triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))

        try:
            self.figlet.setFont(font=new_value)
        except Exception as e:
            self.log.error(f"Error setting font: {e}")

        self.watch_figlet_input(self.figlet_input, self.figlet_input)   # trigger reactive

    def watch__justify(self, old_value: str, new_value: str) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch_justify triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))
                
        if old_value == new_value:
            self.log("Justify has not changed. Returning.")
            return

        try:
            self.figlet.justify = new_value
        except Exception as e:
            self.log.error(f"Error setting justify: {e}")

        self.watch_figlet_input(self.figlet_input, self.figlet_input)   # trigger reactive

    def watch_fig_height_reported(self, old_value: int, new_value: int) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch_fig_height_reported triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))

        self._color_mode = self._color_mode   # trigger the reactive to update the color mode.

    #####################
    #~ RENDERING LOGIC ~#
    #####################

    def make_gradient(self, color1: str, color2: str, quality: int) -> Gradient:
        "Use color names, ie. 'red', 'blue'"

        try:
            parsed_color1 = Color.parse(color1)
            parsed_color2 = Color.parse(color2)
        except Exception as e:
            self.log.error(f"Error parsing color: {e}")
            raise e

        stop1 = (0.0, parsed_color1)        # 3 stops so that it fades in and out.
        stop2 = (0.5, parsed_color2)
        stop3 = (1.0, parsed_color1)
        return Gradient(stop1, stop2, stop3, quality=quality)
        
    def on_resize(self) -> None:
        self.log(Text.from_markup("[bold blue]on_resize triggered."))
        self.refresh_size()

    def refresh_size(self):

        if self.size.width == 0 or self.size.height == 0:        # <- this prevents crashing on boot.
            self.log(Text.from_markup("[bold red]refresh_size triggered, but size is 0. Returning."))
            return 

        assert isinstance(self.parent, Widget)          # This is for type hinting. 
        assert isinstance(self.styles.width, Scalar)    # These should always pass if it reaches here.

        if self.styles.width.is_auto:  
            self.log(Text.from_markup(
                "[bold red]Width in Auto mode. Setting render target width to parent width "
                f"of {self.parent.size.width}"))                   
            self.call_after_refresh(self._set_size, 'auto')
        # if not in auto, the Figlet's render target is the size of the figlet.
        else:     
            self.log(Text.from_markup(
                "[bold red]Width is NOT Auto mode. Setting render target width to "
                f"size of self at: {self.size.width}"))             
            self.call_after_refresh(self._set_size, 'not_auto')

    def _set_size(self, mode: str) -> None:
        "Used internally by refresh_size()"

        assert isinstance(self.parent, Widget)     # For type hinting. 

        if mode == 'auto':
            self.figlet.width = self.parent.size.width
        elif mode == 'not_auto':
            self.figlet.width = self.size.width
        else:
            raise Exception(f"Invalid mode: {mode}. Must be 'auto' or 'not_auto'.")
        
        self.figlet_input = self.figlet_input   # trigger the reactive to update the figlet.

    # These two functions below are the secret sauce to making the auto sizing work.
    # They are both over-rides, and they are called by the Textual framework 
    # to determine the size of the widget.
    def get_content_width(self, container, viewport) -> int:

        if self._figlet_lines:
            self.fig_width_reported = len(max(self._figlet_lines, key=len)) 
            return self.fig_width_reported
        else:
            return 0

    def get_content_height(self, container, viewport, width) -> int:

        if self._figlet_lines:
            self.fig_height_reported = len(self._figlet_lines)
            return self.fig_height_reported
        else:
            return 0        
        
    def render_figlet(self, figlet_input: str) -> list[str]:
        self.log(Text.from_markup(
            "[bold yellow]render_figlet triggered. [/bold yellow] "
            f"Figlet width setting: {self.figlet.width} \n"
        ))        

        try:
            self.figlet_render = self.figlet.renderText(figlet_input)
        except FigletError as e:
            self.log.error(f"Pyfiglet returned an error when attempting to render: {e}")
            raise e
        except Exception as e:
            self.log.error(f"Unexpected error occured when rendering figlet: {e}")
            raise e
        else:
            render_lines:list[str] = self.figlet_render.splitlines()   # convert into list of lines

            while True:
                lines_cleaned = []
                for i, line in enumerate(render_lines):
                    if i == 0 and all(c == ' ' for c in line):  # if first line and blank
                        pass
                    elif i == len(render_lines)-1 and all(c == ' ' for c in line):  # if last line and blank
                        pass
                    else:
                        lines_cleaned.append(line)
            
                if lines_cleaned == render_lines:   # if there's no changes, 
                    break                           # loop is done
                else:                               # If lines_cleaned is different, that means there was
                    render_lines = lines_cleaned    # a change. So set render_lines to lines_cleaned and restart loop.

            if lines_cleaned == []:  # if the figlet output is blank, return empty list
                self.log.error("Figlet output was blank. Returning empty list.")
                return ['']
            
            if self.styles.width and self.styles.width.is_auto:  # if the width is auto, we need to trim the lines
                startpoints = []
                for line in lines_cleaned:
                    for c in line:
                        if c != ' ':                 # find first character that is not space
                            startpoints.append(line.index(c))           # get the index
                            break              
                figstart = min(startpoints)   # lowest number in this list is the start of the figlet
                shortened_fig = [line[figstart:].rstrip() for line in lines_cleaned]   # cuts before and after
                return shortened_fig
            else:
                return lines_cleaned
            
    def render_lines(self, crop) -> list[Strip]:
        if self.gradient and self.animated:
            self.line_colors.rotate()
        return super().render_lines(crop)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        if y >= len(self._figlet_lines):           # if the line is out of range, return blank
            return Strip.blank(self.size.width)
        try:
            self._figlet_lines[y]
        except IndexError as e:
            self.log.error(f"render_line failed for line {y} | {e}")
            return Strip.blank(self.size.width)
        else:
            color_index = y % len(self.line_colors)
            segments = [Segment(self._figlet_lines[y], style=self.line_colors[color_index])]
            return Strip(segments)           
            
